#!/usr/bin/env python3
"""
Simple test for Z.E.U.S. performance optimizations
No background threads, just basic functionality validation.
"""

import sys
import time
import logging
import psutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all performance modules can be imported"""
    logger.info("Testing imports...")
    
    try:
        from core.performance_monitor import PerformanceMonitor, ResourceLimits
        from core.memory_optimizer import MemoryOptimizer
        from core.background_processor import BackgroundProcessor
        logger.info("✅ All imports successful")
        return True
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def test_memory_optimizer_basic():
    """Test basic memory optimizer functionality"""
    logger.info("Testing memory optimizer...")
    
    try:
        from core.memory_optimizer import MemoryOptimizer
        
        optimizer = MemoryOptimizer(max_memory_mb=1024)
        
        # Test memory usage check
        memory_usage = optimizer.get_current_memory_usage()
        logger.info(f"Current memory: {memory_usage:.1f}MB")
        
        # Test memory pressure check
        pressure = optimizer.check_memory_pressure()
        logger.info(f"Memory pressure: {pressure}")
        
        # Test garbage collection
        gc_stats = optimizer.force_garbage_collection()
        logger.info(f"GC stats: {gc_stats}")
        
        # Test memory statistics
        stats = optimizer.get_memory_statistics()
        logger.info(f"Memory stats keys: {list(stats.keys())}")
        
        logger.info("✅ Memory optimizer basic test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Memory optimizer test failed: {e}")
        return False

def test_performance_monitor_basic():
    """Test basic performance monitor functionality"""
    logger.info("Testing performance monitor...")
    
    try:
        from core.performance_monitor import PerformanceMonitor, ResourceLimits
        
        # Create monitor but don't start monitoring thread
        limits = ResourceLimits(max_memory_mb=1024)
        monitor = PerformanceMonitor(limits)
        
        # Test metrics collection (single call, no loop)
        metrics = monitor._collect_metrics()
        logger.info(f"Collected metrics: memory={metrics.memory_usage_mb:.1f}MB")
        
        # Test cache operations
        monitor.cache_result("test_key", "test_value")
        cached = monitor.get_cached_result("test_key")
        assert cached == "test_value", "Cache test failed"
        
        # Test response time tracking
        monitor.record_response_time(100.0)
        assert len(monitor.response_times) == 1, "Response time tracking failed"
        
        logger.info("✅ Performance monitor basic test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Performance monitor test failed: {e}")
        return False

def test_ai_engine_basic():
    """Test basic AI engine functionality"""
    logger.info("Testing AI engine...")
    
    try:
        from core.ai_engine import AIEngine
        
        # Create AI engine (will use fallback mode)
        ai_engine = AIEngine()
        
        # Test basic response generation
        response = ai_engine.generate_response("Hello")
        assert response and len(response) > 0, "No response generated"
        logger.info(f"Generated response: {response[:50]}...")
        
        # Test memory optimization
        ai_engine.optimize_memory()
        
        # Test model status
        status = ai_engine.get_model_status()
        assert 'models_loaded' in status, "Invalid status"
        logger.info(f"Model status: {status}")
        
        logger.info("✅ AI engine basic test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ AI engine test failed: {e}")
        return False

def test_document_processor_basic():
    """Test basic document processor functionality"""
    logger.info("Testing document processor...")
    
    try:
        from core.document_processor import DocumentProcessor
        import tempfile
        import os
        
        processor = DocumentProcessor()
        
        # Create test file
        test_content = "This is a test document for validation."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Test text extraction
            extracted = processor.extract_text(temp_file)
            assert test_content in extracted, "Text extraction failed"
            
            # Test chunking
            chunks = processor.chunk_document_optimized(extracted)
            assert len(chunks) > 0, "No chunks created"
            
            logger.info(f"Extracted {len(extracted)} chars, created {len(chunks)} chunks")
            logger.info("✅ Document processor basic test passed")
            return True
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
    except Exception as e:
        logger.error(f"❌ Document processor test failed: {e}")
        return False

def test_memory_constraint():
    """Test memory constraint compliance"""
    logger.info("Testing memory constraint...")
    
    try:
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        
        logger.info(f"Current memory usage: {memory_mb:.1f}MB")
        
        if memory_mb > 1024:
            logger.error(f"❌ Memory exceeds 1GB: {memory_mb:.1f}MB")
            return False
        
        logger.info("✅ Memory constraint test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Memory constraint test failed: {e}")
        return False

def main():
    """Run simple performance tests"""
    logger.info("Z.E.U.S. Simple Performance Test")
    logger.info("=" * 35)
    
    # Get initial memory
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 * 1024)
    logger.info(f"Initial memory: {initial_memory:.1f}MB")
    
    # Run tests
    tests = [
        ("Imports", test_imports),
        ("Memory Optimizer", test_memory_optimizer_basic),
        ("Performance Monitor", test_performance_monitor_basic),
        ("AI Engine", test_ai_engine_basic),
        ("Document Processor", test_document_processor_basic),
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
            logger.error(f"❌ {test_name} failed: {e}")
    
    # Final results
    final_memory = process.memory_info().rss / (1024 * 1024)
    
    logger.info("\n" + "=" * 35)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info(f"Final memory: {final_memory:.1f}MB")
    
    if final_memory > 1024:
        logger.error(f"❌ Memory exceeds 1GB limit")
        return False
    
    if passed == total:
        logger.info("✅ ALL TESTS PASSED!")
        logger.info("✅ Performance optimizations implemented successfully")
        logger.info("✅ Memory usage within 1GB constraint")
        return True
    else:
        logger.error(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)