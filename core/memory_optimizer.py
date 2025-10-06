"""
Memory optimization utilities for Z.E.U.S. Virtual Assistant

This module provides memory management optimizations for:
- Document processing and chunking
- AI model memory usage
- UI component memory management
- Adaptive memory scaling
"""

import gc
import sys
import weakref
import threading
import logging
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import psutil


@dataclass
class MemoryPool:
    """Memory pool for reusable objects"""
    name: str
    objects: List[Any]
    max_size: int
    created_count: int = 0
    reused_count: int = 0


class MemoryOptimizer:
    """
    Memory optimization manager for the application
    """
    
    def __init__(self, max_memory_mb: int = 1024):
        """
        Initialize memory optimizer
        
        Args:
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_memory_mb = max_memory_mb
        self.logger = logging.getLogger(__name__)
        
        # Memory pools for object reuse
        self.memory_pools: Dict[str, MemoryPool] = {}
        
        # Weak references to track large objects
        self.tracked_objects: Set[weakref.ref] = set()
        
        # Memory optimization callbacks
        self.optimization_callbacks: List[Callable] = []
        
        # Memory usage tracking
        self.peak_memory_mb = 0.0
        self.optimization_count = 0
        
        # Document memory management
        self.document_cache_limit = 5  # Maximum documents in memory
        self.chunk_cache_limit = 1000  # Maximum chunks in memory
        
        # AI model memory management
        self.model_memory_limit_mb = 500  # Maximum memory for AI models
        
        # Initialize memory pools
        self._initialize_memory_pools()
    
    def _initialize_memory_pools(self):
        """Initialize memory pools for common objects"""
        # String pool for document chunks
        self.memory_pools['document_chunks'] = MemoryPool(
            name='document_chunks',
            objects=[],
            max_size=100
        )
        
        # List pool for temporary collections
        self.memory_pools['temp_lists'] = MemoryPool(
            name='temp_lists',
            objects=[],
            max_size=50
        )
        
        # Dictionary pool for temporary data structures
        self.memory_pools['temp_dicts'] = MemoryPool(
            name='temp_dicts',
            objects=[],
            max_size=50
        )
    
    def get_current_memory_usage(self) -> float:
        """
        Get current memory usage in MB
        
        Returns:
            Current memory usage in MB
        """
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            
            # Update peak memory tracking
            if memory_mb > self.peak_memory_mb:
                self.peak_memory_mb = memory_mb
            
            return memory_mb
        except Exception as e:
            self.logger.error(f"Error getting memory usage: {e}")
            return 0.0
    
    def check_memory_pressure(self) -> bool:
        """
        Check if system is under memory pressure
        
        Returns:
            True if memory pressure is detected
        """
        current_memory = self.get_current_memory_usage()
        memory_ratio = current_memory / self.max_memory_mb
        
        return memory_ratio > 0.8  # 80% threshold
    
    def optimize_document_memory(self, documents: List[Any], force: bool = False) -> int:
        """
        Optimize memory usage for document storage
        
        Args:
            documents: List of document objects
            force: Force optimization even if not under pressure
            
        Returns:
            Number of documents optimized
        """
        if not force and not self.check_memory_pressure():
            return 0
        
        optimized_count = 0
        
        try:
            # Sort documents by last access time (if available)
            sorted_docs = sorted(
                documents,
                key=lambda d: getattr(d, 'last_accessed', datetime.min),
                reverse=False  # Oldest first
            )
            
            # Remove excess documents from memory
            while len(sorted_docs) > self.document_cache_limit:
                doc = sorted_docs.pop(0)
                
                # Clear document content but keep metadata
                if hasattr(doc, 'text_content'):
                    doc.text_content = None
                if hasattr(doc, 'chunks'):
                    doc.chunks = []
                
                optimized_count += 1
                self.logger.debug(f"Optimized document: {getattr(doc, 'filename', 'unknown')}")
            
            # Optimize remaining documents
            for doc in sorted_docs:
                if hasattr(doc, 'chunks') and len(doc.chunks) > self.chunk_cache_limit:
                    # Keep only most relevant chunks
                    doc.chunks = doc.chunks[:self.chunk_cache_limit]
                    optimized_count += 1
            
            if optimized_count > 0:
                self.logger.info(f"Optimized {optimized_count} documents for memory usage")
                self.optimization_count += 1
            
            return optimized_count
            
        except Exception as e:
            self.logger.error(f"Error optimizing document memory: {e}")
            return 0
    
    def optimize_ai_model_memory(self, ai_engine: Any) -> bool:
        """
        Optimize AI model memory usage
        
        Args:
            ai_engine: AI engine instance
            
        Returns:
            True if optimization was performed
        """
        try:
            if not hasattr(ai_engine, 'models_loaded') or not ai_engine.models_loaded:
                return False
            
            current_memory = self.get_current_memory_usage()
            
            # If memory usage is high, consider unloading models temporarily
            if current_memory > self.max_memory_mb * 0.9:
                self.logger.warning("Critical memory usage - considering model unloading")
                
                # Clear model caches if available
                if hasattr(ai_engine, 'clear_model_cache'):
                    ai_engine.clear_model_cache()
                
                # Force garbage collection
                gc.collect()
                
                self.optimization_count += 1
                return True
            
            # Optimize model memory usage
            if hasattr(ai_engine, 'optimize_memory'):
                ai_engine.optimize_memory()
                self.optimization_count += 1
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error optimizing AI model memory: {e}")
            return False
    
    def optimize_ui_memory(self, ui_components: List[Any]) -> int:
        """
        Optimize UI component memory usage
        
        Args:
            ui_components: List of UI components
            
        Returns:
            Number of components optimized
        """
        optimized_count = 0
        
        try:
            for component in ui_components:
                # Clear large text widgets if not visible
                if hasattr(component, 'chat_display'):
                    text_widget = component.chat_display
                    if hasattr(text_widget, 'get') and hasattr(text_widget, 'delete'):
                        content_length = len(text_widget.get("1.0", "end"))
                        
                        # If content is very large, trim it
                        if content_length > 100000:  # 100KB of text
                            # Keep only recent content
                            lines = text_widget.get("1.0", "end").split('\n')
                            if len(lines) > 1000:
                                # Keep last 500 lines
                                recent_content = '\n'.join(lines[-500:])
                                text_widget.delete("1.0", "end")
                                text_widget.insert("1.0", recent_content)
                                optimized_count += 1
                
                # Clear cached images or large data
                if hasattr(component, 'clear_cache'):
                    component.clear_cache()
                    optimized_count += 1
            
            if optimized_count > 0:
                self.logger.info(f"Optimized {optimized_count} UI components for memory usage")
                self.optimization_count += 1
            
            return optimized_count
            
        except Exception as e:
            self.logger.error(f"Error optimizing UI memory: {e}")
            return 0
    
    def get_object_from_pool(self, pool_name: str, factory_func: Callable = None) -> Any:
        """
        Get object from memory pool or create new one
        
        Args:
            pool_name: Name of the memory pool
            factory_func: Function to create new object if pool is empty
            
        Returns:
            Object from pool or newly created object
        """
        if pool_name not in self.memory_pools:
            return factory_func() if factory_func else None
        
        pool = self.memory_pools[pool_name]
        
        if pool.objects:
            obj = pool.objects.pop()
            pool.reused_count += 1
            return obj
        else:
            if factory_func:
                obj = factory_func()
                pool.created_count += 1
                return obj
            return None
    
    def return_object_to_pool(self, pool_name: str, obj: Any):
        """
        Return object to memory pool for reuse
        
        Args:
            pool_name: Name of the memory pool
            obj: Object to return to pool
        """
        if pool_name not in self.memory_pools:
            return
        
        pool = self.memory_pools[pool_name]
        
        if len(pool.objects) < pool.max_size:
            # Clear object state before returning to pool
            if hasattr(obj, 'clear'):
                obj.clear()
            elif isinstance(obj, list):
                obj.clear()
            elif isinstance(obj, dict):
                obj.clear()
            
            pool.objects.append(obj)
    
    def track_large_object(self, obj: Any, size_threshold_mb: float = 10.0):
        """
        Track large objects for memory monitoring
        
        Args:
            obj: Object to track
            size_threshold_mb: Size threshold in MB for tracking
        """
        try:
            obj_size_mb = sys.getsizeof(obj) / (1024 * 1024)
            
            if obj_size_mb > size_threshold_mb:
                weak_ref = weakref.ref(obj, self._object_cleanup_callback)
                self.tracked_objects.add(weak_ref)
                self.logger.debug(f"Tracking large object: {obj_size_mb:.1f}MB")
        
        except Exception as e:
            self.logger.error(f"Error tracking large object: {e}")
    
    def _object_cleanup_callback(self, weak_ref):
        """Callback when tracked object is garbage collected"""
        self.tracked_objects.discard(weak_ref)
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """
        Force garbage collection and return statistics
        
        Returns:
            Dictionary with garbage collection statistics
        """
        before_memory = self.get_current_memory_usage()
        
        # Force collection for all generations
        collected = {}
        for generation in range(3):
            collected[f'gen_{generation}'] = gc.collect(generation)
        
        after_memory = self.get_current_memory_usage()
        freed_mb = before_memory - after_memory
        
        stats = {
            'total_collected': sum(collected.values()),
            'memory_freed_mb': round(freed_mb, 2),
            'before_memory_mb': round(before_memory, 2),
            'after_memory_mb': round(after_memory, 2)
        }
        stats.update(collected)
        
        if freed_mb > 1:  # Log if significant memory was freed
            self.logger.info(f"Garbage collection freed {freed_mb:.1f}MB")
        
        return stats
    
    def optimize_string_memory(self, strings: List[str]) -> List[str]:
        """
        Optimize memory usage for string collections
        
        Args:
            strings: List of strings to optimize
            
        Returns:
            Optimized list of strings
        """
        if not strings:
            return strings
        
        try:
            # Use string interning for repeated strings
            interned_strings = []
            seen_strings = {}
            
            for s in strings:
                if s in seen_strings:
                    interned_strings.append(seen_strings[s])
                else:
                    # Intern the string if it's not too large
                    if len(s) < 1000:
                        interned_s = sys.intern(s)
                        seen_strings[s] = interned_s
                        interned_strings.append(interned_s)
                    else:
                        interned_strings.append(s)
            
            return interned_strings
            
        except Exception as e:
            self.logger.error(f"Error optimizing string memory: {e}")
            return strings
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive memory statistics
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            current_memory = self.get_current_memory_usage()
            memory_ratio = current_memory / self.max_memory_mb
            
            # Pool statistics
            pool_stats = {}
            for name, pool in self.memory_pools.items():
                pool_stats[name] = {
                    'objects_available': len(pool.objects),
                    'max_size': pool.max_size,
                    'created_count': pool.created_count,
                    'reused_count': pool.reused_count,
                    'reuse_ratio': pool.reused_count / max(pool.created_count, 1)
                }
            
            # Garbage collection statistics
            gc_stats = gc.get_stats()
            
            return {
                'current_memory_mb': round(current_memory, 2),
                'peak_memory_mb': round(self.peak_memory_mb, 2),
                'memory_limit_mb': self.max_memory_mb,
                'memory_usage_percent': round(memory_ratio * 100, 1),
                'optimization_count': self.optimization_count,
                'tracked_objects': len(self.tracked_objects),
                'memory_pools': pool_stats,
                'gc_stats': gc_stats,
                'memory_pressure': self.check_memory_pressure()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting memory statistics: {e}")
            return {'error': str(e)}
    
    def add_optimization_callback(self, callback: Callable):
        """
        Add callback for memory optimization events
        
        Args:
            callback: Function to call during optimization
        """
        self.optimization_callbacks.append(callback)
    
    def perform_comprehensive_optimization(self) -> Dict[str, Any]:
        """
        Perform comprehensive memory optimization
        
        Returns:
            Dictionary with optimization results
        """
        self.logger.info("Starting comprehensive memory optimization")
        
        before_memory = self.get_current_memory_usage()
        results = {
            'before_memory_mb': round(before_memory, 2),
            'optimizations_performed': []
        }
        
        try:
            # Clear memory pools
            for pool in self.memory_pools.values():
                pool.objects.clear()
            results['optimizations_performed'].append('cleared_memory_pools')
            
            # Force garbage collection
            gc_stats = self.force_garbage_collection()
            results['gc_stats'] = gc_stats
            results['optimizations_performed'].append('garbage_collection')
            
            # Notify optimization callbacks
            for callback in self.optimization_callbacks:
                try:
                    callback('comprehensive_optimization')
                    results['optimizations_performed'].append('callback_optimization')
                except Exception as e:
                    self.logger.error(f"Error in optimization callback: {e}")
            
            after_memory = self.get_current_memory_usage()
            freed_memory = before_memory - after_memory
            
            results.update({
                'after_memory_mb': round(after_memory, 2),
                'memory_freed_mb': round(freed_memory, 2),
                'optimization_success': freed_memory > 0
            })
            
            self.optimization_count += 1
            self.logger.info(f"Comprehensive optimization completed - freed {freed_memory:.1f}MB")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error during comprehensive optimization: {e}")
            results['error'] = str(e)
            return results


# Global memory optimizer instance
_memory_optimizer: Optional[MemoryOptimizer] = None


def get_memory_optimizer() -> MemoryOptimizer:
    """Get the global memory optimizer instance"""
    global _memory_optimizer
    if _memory_optimizer is None:
        _memory_optimizer = MemoryOptimizer()
    return _memory_optimizer


def initialize_memory_optimizer(max_memory_mb: int = 1024) -> MemoryOptimizer:
    """Initialize global memory optimizer"""
    global _memory_optimizer
    if _memory_optimizer is None:
        _memory_optimizer = MemoryOptimizer(max_memory_mb)
    return _memory_optimizer