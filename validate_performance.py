#!/usr/bin/env python3
"""
Performance validation script for Z.E.U.S. Virtual Assistant

This script validates that the performance optimizations work correctly
and that resource usage stays within the 1GB constraint.
"""

import sys
import time
import logging
import psutil
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_memory_usage():
    """Validate that memory usage stays within limits"""
    logger.info("Validating memory usage...")
    
    try:
        from core.performance_monitor import PerformanceMonitor, ResourceLimits
        from core.memory_optimizer import MemoryOptimizer
        
        # Create performance monitor with 1GB limit
        limits = ResourceLimits(max_memory_mb=1024)
        monitor = PerformanceMonitor(limits)
        optimizer = MemoryOptimizer(max_memory_mb=1024)
        
        # Get initial memory usage
        initial_memory = optimizer.get_current_memory_usage()
        logger.info(f"Initial memory usage: {initial_memory:.1f}MB")
        
        # Simulate some memory usage
        test_data = []
        for i in range(100):
            # Create moderate amounts of data
            data = [f"test_item_{j}" for j in range(1000)]
            test_data.append(data)
        
        # Check memory after data creation
        current_memory = optimizer.get_current_memory_usage()
        logger.info(f"Memory after data creation: {current_memory:.1f}MB")
        
        # Test memory optimization
        optimizer.perform_comprehensive_optimization()
        
        # Check memory after optimization
        optimized_memory = optimizer.get_current_memory_usage()
        logger.info(f"Memory after optimization: {optimized_memory:.1f}MB")
        
        # Validate memory constraint
        if optimized_memory > 1024:
            logger.error(f"Memory usage exceeds 1GB limit: {optimized_memory:.1f}MB")
            return False
        
        logger.info("✅ Memory usage validation passed")
        
        # Clean up
        monitor.stop_monitoring()
        return True
        
    except Exception as e:
        logger.error(f"Error in memory validation: {e}")
        return False

def validate_background_processing():
    """Validate background processing performance"""
    logger.info("Validating background processing...")
    
    try:
        from core.background_processor import BackgroundProcessor, TaskPriority
        
        processor = BackgroundProcessor(max_workers=2)
        
        # Test task execution
        results = []
        
        def test_task(task_id):
            time.sleep(0.1)  # Simulate work
            return f"task_{task_id}_completed"
        
        def result_callback(result):
            results.append(result)
        
        # Submit multiple tasks
        start_time = time.time()
        for i in range(5):
            processor.submit_task(
                name=f"Test Task {i}",
                function=test_task,
                args=(i,),
                callback=result_callback,
                priority=TaskPriority.NORMAL
            )
        
        # Wait for completion
        timeout = 10
        while len(results) < 5 and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        total_time = time.time() - start_time
        
        if len(results) != 5:
            logger.error(f"Not all tasks completed: {len(results)}/5")
            return False
        
        if total_time > 5:
            logger.error(f"Tasks took too long: {total_time:.2f}s")
            return False
        
        logger.info(f"✅ Background processing validation passed ({total_time:.2f}s)")
        
        # Clean up
        processor.stop()
        return True
        
    except Exception as e:
        logger.error(f"Error in background processing validation: {e}")
        return False

def validate_performance_monitoring():
    """Validate performance monitoring functionality"""
    logger.info("Validating performance monitoring...")
    
    try:
        from core.performance_monitor import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        
        # Wait for some metrics to be collected
        time.sleep(2)
        
        # Check that metrics are being collected
        if len(monitor.metrics_history) == 0:
            logger.error("No performance metrics collected")
            return False
        
        # Test performance summary
        summary = monitor.get_performance_summary()
        if 'status' not in summary:
            logger.error("Invalid performance summary")
            return False
        
        # Test response time tracking
        monitor.record_response_time(100)
        monitor.record_response_time(200)
        
        if len(monitor.response_times) < 2:
            logger.error("Response times not recorded properly")
            return False
        
        logger.info("✅ Performance monitoring validation passed")
        
        # Clean up
        monitor.stop_monitoring()
        return True
        
    except Exception as e:
        logger.error(f"Error in performance monitoring validation: {e}")
        return False

def validate_ai_engine_performance():
    """Validate AI engine performance optimizations"""
    logger.info("Validating AI engine performance...")
    
    try:
        from core.ai_engine import AIEngine
        
        # Create AI engine (will run in fallback mode without transformers)
        ai_engine = AIEngine()
        
        # Test response generation performance
        start_time = time.time()
        response = ai_engine.generate_response("Hello, how are you?")
        response_time = time.time() - start_time
        
        if response_time > 5.0:  # Should respond within 5 seconds
            logger.error(f"AI response too slow: {response_time:.2f}s")
            return False
        
        if not response or len(response) == 0:
            logger.error("AI engine returned empty response")
            return False
        
        # Test memory optimization
        ai_engine.optimize_memory()
        
        # Test model status
        status = ai_engine.get_model_status()
        if 'models_loaded' not in status:
            logger.error("Invalid AI engine status")
            return False
        
        logger.info(f"✅ AI engine performance validation passed ({response_time:.2f}s)")
        return True
        
    except Exception as e:
        logger.error(f"Error in AI engine validation: {e}")
        return False

def validate_document_processing_performance():
    """Validate document processing performance"""
    logger.info("Validating document processing performance...")
    
    try:
        from core.document_processor import DocumentProcessor
        import tempfile
        import os
        
        processor = DocumentProcessor()
        
        # Create a test document
        test_content = "This is a test document for performance validation. " * 1000
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Test text extraction performance
            start_time = time.time()
            extracted_text = processor.extract_text(temp_file)
            extraction_time = time.time() - start_time
            
            if extraction_time > 2.0:  # Should extract within 2 seconds
                logger.error(f"Text extraction too slow: {extraction_time:.2f}s")
                return False
            
            # Test chunking performance
            start_time = time.time()
            chunks = processor.chunk_document_optimized(extracted_text)
            chunking_time = time.time() - start_time
            
            if chunking_time > 1.0:  # Should chunk within 1 second
                logger.error(f"Document chunking too slow: {chunking_time:.2f}s")
                return False
            
            if len(chunks) == 0:
                logger.error("No chunks created from document")
                return False
            
            logger.info(f"✅ Document processing validation passed (extract: {extraction_time:.2f}s, chunk: {chunking_time:.2f}s)")
            return True
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
    except Exception as e:
        logger.error(f"Error in document processing validation: {e}")
        return False

def main():
    """Main validation function"""
    logger.info("Starting Z.E.U.S. Performance Validation")
    logger.info("=" * 50)
    
    # Get system information
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 * 1024)
    logger.info(f"Initial system memory usage: {initial_memory:.1f}MB")
    
    # Run validation tests
    tests = [
        ("Memory Usage", validate_memory_usage),
        ("Background Processing", validate_background_processing),
        ("Performance Monitoring", validate_performance_monitoring),
        ("AI Engine Performance", validate_ai_engine_performance),
        ("Document Processing", validate_document_processing_performance)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            if test_func():
                passed_tests += 1
            else:
                logger.error(f"❌ {test_name} test failed")
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
    
    # Final results
    logger.info("\n" + "=" * 50)
    logger.info("VALIDATION RESULTS")
    logger.info("=" * 50)
    
    final_memory = process.memory_info().rss / (1024 * 1024)
    memory_increase = final_memory - initial_memory
    
    logger.info(f"Tests passed: {passed_tests}/{total_tests}")
    logger.info(f"Final memory usage: {final_memory:.1f}MB")
    logger.info(f"Memory increase: {memory_increase:.1f}MB")
    
    # Check overall memory constraint
    if final_memory > 1024:
        logger.error(f"❌ CRITICAL: Memory usage exceeds 1GB limit: {final_memory:.1f}MB")
        return False
    
    if passed_tests == total_tests:
        logger.info("✅ ALL TESTS PASSED - Performance optimizations working correctly!")
        logger.info("✅ Memory usage stays within 1GB constraint")
        return True
    else:
        logger.error(f"❌ {total_tests - passed_tests} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)