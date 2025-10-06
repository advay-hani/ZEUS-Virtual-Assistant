#!/usr/bin/env python3
"""
Quick performance test for Z.E.U.S. Virtual Assistant
Tests the key performance optimizations without infinite loops.
"""

import sys
import time
import logging
import psutil
import gc

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_memory_optimizer():
    """Test memory optimizer functionality"""
    logger.info("Testing memory optimizer...")
    
    try:
        from core.memory_optimizer import MemoryOptimizer
        
        optimizer = MemoryOptimizer(max_memory_mb=1024)
        
        # Get initial memory
        initial_memory = optimizer.get_current_memory_usage()
        logger.info(f"Initial memory: {initial_memory:.1f}MB")
        
        # Create some test data
        test_data = []
        for i in range(50):
            data = [f"item_{j}" for j in range(500)]
            test_data.append(data)
        
        # Check memory after data creation
        after_memory = optimizer.get_current_memory_usage()
        logger.info(f"Memory after data creation: {after_memory:.1f}MB")
        
        # Test optimization
        results = optimizer.perform_comprehensive_optimization()
        
        # Check memory after optimization
        final_memory = optimizer.get_current_memory_usage()
        logger.info(f"Memory after optimization: {final_memory:.1f}MB")
        
        # Validate results
        if final_memory > 1024:
            logger.error(f"Memory exceeds 1GB: {final_memory:.1f}MB")
            return False
        
        logger.info("✅ Memory optimizer test passed")
        return True
        
    except Exception as e:
        logger.error(f"Memory optimizer test failed: {e}")
        return False

def test_background_processor():
    """Test background processor functionality"""
    logger.info("Testing background processor...")
    
    try:
        from core.background_processor import BackgroundProcessor, TaskPriority
        
        processor = BackgroundProcessor(max_workers=2, max_queue_size=10)
        
        # Test simple task
        results = []
        
        def simple_task(value):
            return value * 2
        
        def result_callback(result):
            results.append(result)
        
        # Submit a task
        task_id = processor.submit_task(
            name="Simple Test",
            function=simple_task,
            args=(5,),
            callback=result_callback,
            priority=TaskPriority.NORMAL
        )
        
        # Wait for completion (with timeout)
        start_time = time.time()
        while len(results) == 0 and time.time() - start_time < 5:
            time.sleep(0.1)
        
        # Check results
        if len(results) != 1 or results[0] != 10:
            logger.error(f"Unexpected result: {results}")
            return False
        
        # Get statistics
        stats = processor.get_processor_statistics()
        logger.info(f"Processor stats: {stats}")
        
        # Clean up
        processor.stop(timeout=2)
        
        logger.info("✅ Background processor test passed")
        return True
        
    except Exception as e:
        logger.error(f"Background processor test failed: {e}")
        return False

def test_ai_engine_optimization():
    """Test AI engine optimization"""
    logger.info("Testing AI engine optimization...")
    
    try:
        from core.ai_engine import AIEngine
        
        # Create AI engine (will use fallback mode)
        ai_engine = AIEngine()
        
        # Test response generation
        start_time = time.time()
        response = ai_engine.generate_response("Hello")
        response_time = time.time() - start_time
        
        if response_time > 2.0:
            logger.error(f"Response too slow: {response_time:.2f}s")
            return False
        
        if not response:
            logger.error("Empty response")
            return False
        
        # Test memory optimization
        ai_engine.optimize_memory()
        
        # Test status
        status = ai_engine.get_model_status()
        logger.info(f"AI engine status: {status}")
        
        logger.info(f"✅ AI engine test passed ({response_time:.2f}s)")
        return True
        
    except Exception as e:
        logger.error(f"AI engine test failed: {e}")
        return False

def test_document_processing():
    """Test document processing optimization"""
    logger.info("Testing document processing...")
    
    try:
        from core.document_processor import DocumentProcessor
        import tempfile
        import os
        
        processor = DocumentProcessor()
        
        # Create test file
        test_content = "This is a test document. " * 100
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Test text extraction
            start_time = time.time()
            text = processor.extract_text(temp_file)
            extract_time = time.time() - start_time
            
            if extract_time > 1.0:
                logger.error(f"Extraction too slow: {extract_time:.2f}s")
                return False
            
            # Test chunking
            start_time = time.time()
            chunks = processor.chunk_document_optimized(text)
            chunk_time = time.time() - start_time
            
            if chunk_time > 1.0:
                logger.error(f"Chunking too slow: {chunk_time:.2f}s")
                return False
            
            if len(chunks) == 0:
                logger.error("No chunks created")
                return False
            
            logger.info(f"✅ Document processing test passed (extract: {extract_time:.2f}s, chunk: {chunk_time:.2f}s)")
            return True
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
    except Exception as e:
        logger.error(f"Document processing test failed: {e}")
        return False

def test_memory_constraint():
    """Test that memory stays under 1GB"""
    logger.info("Testing 1GB memory constraint...")
    
    try:
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        
        logger.info(f"Current memory usage: {memory_mb:.1f}MB")
        
        if memory_mb > 1024:
            logger.error(f"Memory exceeds 1GB: {memory_mb:.1f}MB")
            return False
        
        logger.info("✅ Memory constraint test passed")
        return True
        
    except Exception as e:
        logger.error(f"Memory constraint test failed: {e}")
        return False

def main():
    """Run all performance tests"""
    logger.info("Starting Z.E.U.S. Performance Tests")
    logger.info("=" * 40)
    
    # Get initial memory
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 * 1024)
    logger.info(f"Initial memory: {initial_memory:.1f}MB")
    
    # Run tests
    tests = [
        ("Memory Optimizer", test_memory_optimizer),
        ("Background Processor", test_background_processor),
        ("AI Engine Optimization", test_ai_engine_optimization),
        ("Document Processing", test_document_processing),
        ("Memory Constraint", test_memory_constraint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                logger.error(f"❌ {test_name} failed")
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
    
    # Final results
    logger.info("\n" + "=" * 40)
    logger.info("TEST RESULTS")
    logger.info("=" * 40)
    
    final_memory = process.memory_info().rss / (1024 * 1024)
    memory_increase = final_memory - initial_memory
    
    logger.info(f"Tests passed: {passed}/{total}")
    logger.info(f"Final memory: {final_memory:.1f}MB")
    logger.info(f"Memory increase: {memory_increase:.1f}MB")
    
    if final_memory > 1024:
        logger.error(f"❌ CRITICAL: Memory exceeds 1GB: {final_memory:.1f}MB")
        return False
    
    if passed == total:
        logger.info("✅ ALL TESTS PASSED!")
        logger.info("✅ Performance optimizations working correctly")
        logger.info("✅ Memory usage within 1GB constraint")
        return True
    else:
        logger.error(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)