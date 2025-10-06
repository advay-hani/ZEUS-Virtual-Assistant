"""
Background processing utilities for Z.E.U.S. Virtual Assistant

This module provides background processing capabilities to maintain UI responsiveness
during heavy operations like document processing, AI inference, and file operations.
"""

import threading
import queue
import time
import logging
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import concurrent.futures


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BackgroundTask:
    """Background task definition"""
    id: str
    name: str
    function: Callable
    args: tuple
    kwargs: dict
    priority: TaskPriority
    callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None
    progress_callback: Optional[Callable] = None
    timeout_seconds: Optional[float] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def __lt__(self, other):
        """Enable comparison for priority queue"""
        if not isinstance(other, BackgroundTask):
            return NotImplemented
        return self.priority.value < other.priority.value


class BackgroundProcessor:
    """
    Background task processor for maintaining UI responsiveness
    """
    
    def __init__(self, max_workers: int = 4, max_queue_size: int = 100):
        """
        Initialize background processor
        
        Args:
            max_workers: Maximum number of worker threads
            max_queue_size: Maximum number of queued tasks
        """
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.logger = logging.getLogger(__name__)
        
        # Task management
        self.task_queue = queue.PriorityQueue(maxsize=max_queue_size)
        self.active_tasks: Dict[str, BackgroundTask] = {}
        self.completed_tasks: List[BackgroundTask] = []
        self.task_counter = 0
        
        # Thread pool for task execution
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="BackgroundProcessor"
        )
        
        # Processing state
        self.is_running = False
        self.processor_thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.tasks_processed = 0
        self.total_processing_time = 0.0
        self.failed_tasks = 0
        
        # Start processing
        self.start()
    
    def start(self):
        """Start background processing"""
        if self.is_running:
            return
        
        self.is_running = True
        self.processor_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True,
            name="BackgroundProcessor"
        )
        self.processor_thread.start()
        self.logger.info("Background processor started")
    
    def stop(self, timeout: float = 10.0):
        """
        Stop background processing
        
        Args:
            timeout: Timeout for graceful shutdown
        """
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel pending tasks
        while not self.task_queue.empty():
            try:
                _, task = self.task_queue.get_nowait()
                task.status = TaskStatus.CANCELLED
                self.completed_tasks.append(task)
            except queue.Empty:
                break
        
        # Shutdown executor
        self.executor.shutdown(wait=True, timeout=timeout)
        
        # Wait for processor thread
        if self.processor_thread and self.processor_thread.is_alive():
            self.processor_thread.join(timeout=timeout)
        
        self.logger.info("Background processor stopped")
    
    def submit_task(
        self,
        name: str,
        function: Callable,
        args: tuple = (),
        kwargs: dict = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
        timeout_seconds: Optional[float] = None
    ) -> str:
        """
        Submit a task for background processing
        
        Args:
            name: Task name for identification
            function: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            priority: Task priority
            callback: Success callback function
            error_callback: Error callback function
            progress_callback: Progress update callback
            timeout_seconds: Task timeout
            
        Returns:
            Task ID
        """
        if kwargs is None:
            kwargs = {}
        
        # Generate unique task ID
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{int(time.time())}"
        
        # Create task
        task = BackgroundTask(
            id=task_id,
            name=name,
            function=function,
            args=args,
            kwargs=kwargs,
            priority=priority,
            callback=callback,
            error_callback=error_callback,
            progress_callback=progress_callback,
            timeout_seconds=timeout_seconds
        )
        
        try:
            # Add to queue with priority (lower number = higher priority)
            priority_value = 5 - priority.value  # Invert for queue ordering
            self.task_queue.put((priority_value, task), timeout=1.0)
            
            self.logger.debug(f"Task submitted: {name} (ID: {task_id})")
            return task_id
            
        except queue.Full:
            self.logger.error(f"Task queue full, cannot submit task: {name}")
            raise RuntimeError("Background processor queue is full")
    
    def _processing_loop(self):
        """Main processing loop"""
        while self.is_running:
            try:
                # Get next task from queue
                try:
                    priority, task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Execute task
                self._execute_task(task)
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(1.0)  # Brief pause on error
    
    def _execute_task(self, task: BackgroundTask):
        """
        Execute a background task
        
        Args:
            task: Task to execute
        """
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self.active_tasks[task.id] = task
        
        self.logger.debug(f"Executing task: {task.name} (ID: {task.id})")
        
        try:
            # Submit to thread pool with timeout
            future = self.executor.submit(self._run_task_function, task)
            
            # Wait for completion with timeout
            timeout = task.timeout_seconds or 300  # Default 5 minute timeout
            task.result = future.result(timeout=timeout)
            
            # Task completed successfully
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Calculate processing time
            processing_time = (task.completed_at - task.started_at).total_seconds()
            self.total_processing_time += processing_time
            self.tasks_processed += 1
            
            self.logger.debug(f"Task completed: {task.name} ({processing_time:.2f}s)")
            
            # Call success callback
            if task.callback:
                try:
                    task.callback(task.result)
                except Exception as e:
                    self.logger.error(f"Error in task callback: {e}")
            
        except concurrent.futures.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = TimeoutError(f"Task timed out after {timeout} seconds")
            task.completed_at = datetime.now()
            self.failed_tasks += 1
            
            self.logger.warning(f"Task timed out: {task.name}")
            
            # Call error callback
            if task.error_callback:
                try:
                    task.error_callback(task.error)
                except Exception as e:
                    self.logger.error(f"Error in task error callback: {e}")
        
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = e
            task.completed_at = datetime.now()
            self.failed_tasks += 1
            
            self.logger.error(f"Task failed: {task.name} - {e}")
            
            # Call error callback
            if task.error_callback:
                try:
                    task.error_callback(e)
                except Exception as callback_error:
                    self.logger.error(f"Error in task error callback: {callback_error}")
        
        finally:
            # Move task from active to completed
            self.active_tasks.pop(task.id, None)
            self.completed_tasks.append(task)
            
            # Limit completed task history
            if len(self.completed_tasks) > 1000:
                self.completed_tasks = self.completed_tasks[-500:]
    
    def _run_task_function(self, task: BackgroundTask) -> Any:
        """
        Run the actual task function with progress tracking
        
        Args:
            task: Task to run
            
        Returns:
            Task result
        """
        # Create progress callback wrapper
        def progress_wrapper(progress: float, message: str = ""):
            if task.progress_callback:
                try:
                    task.progress_callback(progress, message)
                except Exception as e:
                    self.logger.error(f"Error in progress callback: {e}")
        
        # Add progress callback to kwargs if function supports it
        if 'progress_callback' in task.function.__code__.co_varnames:
            task.kwargs['progress_callback'] = progress_wrapper
        
        # Execute the function
        return task.function(*task.args, **task.kwargs)
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        Get status of a task
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status or None if not found
        """
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].status
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.id == task_id:
                return task.status
        
        return None
    
    def get_task_result(self, task_id: str) -> Any:
        """
        Get result of a completed task
        
        Args:
            task_id: Task ID
            
        Returns:
            Task result or None if not found/completed
        """
        for task in self.completed_tasks:
            if task.id == task_id and task.status == TaskStatus.COMPLETED:
                return task.result
        
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending or running task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if task was cancelled
        """
        # Check if task is active
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            # Note: Cannot actually stop running thread, but mark as cancelled
            return True
        
        return False
    
    def get_queue_size(self) -> int:
        """
        Get current queue size
        
        Returns:
            Number of pending tasks
        """
        return self.task_queue.qsize()
    
    def get_active_task_count(self) -> int:
        """
        Get number of active tasks
        
        Returns:
            Number of running tasks
        """
        return len(self.active_tasks)
    
    def get_processor_statistics(self) -> Dict[str, Any]:
        """
        Get processor performance statistics
        
        Returns:
            Dictionary with statistics
        """
        avg_processing_time = 0.0
        if self.tasks_processed > 0:
            avg_processing_time = self.total_processing_time / self.tasks_processed
        
        return {
            'is_running': self.is_running,
            'queue_size': self.get_queue_size(),
            'active_tasks': self.get_active_task_count(),
            'completed_tasks': len(self.completed_tasks),
            'tasks_processed': self.tasks_processed,
            'failed_tasks': self.failed_tasks,
            'success_rate': (self.tasks_processed - self.failed_tasks) / max(self.tasks_processed, 1),
            'avg_processing_time_seconds': round(avg_processing_time, 2),
            'total_processing_time_seconds': round(self.total_processing_time, 2),
            'max_workers': self.max_workers,
            'max_queue_size': self.max_queue_size
        }
    
    def clear_completed_tasks(self):
        """Clear completed task history"""
        self.completed_tasks.clear()
        self.logger.info("Cleared completed task history")
    
    def submit_document_processing_task(
        self,
        document_path: str,
        processor_function: Callable,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """
        Submit document processing task with appropriate priority
        
        Args:
            document_path: Path to document
            processor_function: Function to process document
            callback: Success callback
            error_callback: Error callback
            progress_callback: Progress callback
            
        Returns:
            Task ID
        """
        return self.submit_task(
            name=f"Process Document: {document_path}",
            function=processor_function,
            args=(document_path,),
            priority=TaskPriority.HIGH,
            callback=callback,
            error_callback=error_callback,
            progress_callback=progress_callback,
            timeout_seconds=120  # 2 minute timeout for document processing
        )
    
    def submit_ai_inference_task(
        self,
        query: str,
        ai_function: Callable,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """
        Submit AI inference task with appropriate priority
        
        Args:
            query: User query
            ai_function: AI inference function
            callback: Success callback
            error_callback: Error callback
            progress_callback: Progress callback
            
        Returns:
            Task ID
        """
        return self.submit_task(
            name=f"AI Inference: {query[:50]}...",
            function=ai_function,
            args=(query,),
            priority=TaskPriority.URGENT,
            callback=callback,
            error_callback=error_callback,
            progress_callback=progress_callback,
            timeout_seconds=30  # 30 second timeout for AI inference
        )
    
    def submit_file_operation_task(
        self,
        operation_name: str,
        file_function: Callable,
        args: tuple = (),
        kwargs: dict = None,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None
    ) -> str:
        """
        Submit file operation task with appropriate priority
        
        Args:
            operation_name: Name of the operation
            file_function: File operation function
            args: Function arguments
            kwargs: Function keyword arguments
            callback: Success callback
            error_callback: Error callback
            
        Returns:
            Task ID
        """
        return self.submit_task(
            name=f"File Operation: {operation_name}",
            function=file_function,
            args=args,
            kwargs=kwargs or {},
            priority=TaskPriority.NORMAL,
            callback=callback,
            error_callback=error_callback,
            timeout_seconds=60  # 1 minute timeout for file operations
        )


# Global background processor instance
_background_processor: Optional[BackgroundProcessor] = None


def get_background_processor() -> BackgroundProcessor:
    """Get the global background processor instance"""
    global _background_processor
    if _background_processor is None:
        _background_processor = BackgroundProcessor()
    return _background_processor


def initialize_background_processor(max_workers: int = 4, max_queue_size: int = 100) -> BackgroundProcessor:
    """Initialize global background processor"""
    global _background_processor
    if _background_processor is None:
        _background_processor = BackgroundProcessor(max_workers, max_queue_size)
    return _background_processor


def shutdown_background_processor():
    """Shutdown global background processor"""
    global _background_processor
    if _background_processor:
        _background_processor.stop()
        _background_processor = None