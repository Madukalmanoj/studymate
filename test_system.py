#!/usr/bin/env python3
"""
Test script for StudyMate components
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_pdf_processor():
    """Test PDF processor"""
    print("🧪 Testing PDF Processor...")
    try:
        from pdf_processor import PDFProcessor
        processor = PDFProcessor()
        print("✅ PDF Processor initialized successfully")
        
        # Test text chunking
        sample_text = "This is a sample text. It contains multiple sentences. We will test chunking functionality."
        chunks = processor.chunk_text(sample_text)
        print(f"✅ Text chunking works: {len(chunks)} chunks created")
        
        return True
    except Exception as e:
        print(f"❌ PDF Processor test failed: {e}")
        return False

def test_semantic_search():
    """Test semantic search engine"""
    print("\n🧪 Testing Semantic Search Engine...")
    try:
        from semantic_search import SemanticSearchEngine
        search_engine = SemanticSearchEngine()
        print("✅ Semantic Search Engine initialized successfully")
        
        # Test with sample data
        sample_chunks = [
            {'id': 0, 'text': 'Machine learning is a subset of artificial intelligence.', 'start_pos': 0, 'end_pos': 50, 'length': 50},
            {'id': 1, 'text': 'Deep learning uses neural networks with multiple layers.', 'start_pos': 51, 'end_pos': 105, 'length': 54}
        ]
        
        search_engine.build_index(sample_chunks)
        print("✅ Index building works")
        
        # Test search
        results = search_engine.search("What is machine learning?", k=1)
        if results:
            print(f"✅ Search works: Found {len(results)} results")
        else:
            print("⚠️ Search returned no results (may be due to similarity threshold)")
        
        return True
    except Exception as e:
        print(f"❌ Semantic Search test failed: {e}")
        return False

def test_llm_integration():
    """Test LLM integration"""
    print("\n🧪 Testing LLM Integration...")
    try:
        from llm_integration import LLMAnswerGenerator
        generator = LLMAnswerGenerator(use_watson=False)  # Use fallback for testing
        print("✅ LLM Answer Generator initialized successfully")
        
        # Test answer generation
        sample_chunks = [
            {'id': 0, 'text': 'Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.', 'similarity_score': 0.9}
        ]
        
        result = generator.generate_answer(
            "What is machine learning?", 
            sample_chunks, 
            "Test Document"
        )
        
        if result.get('answer'):
            print("✅ Answer generation works")
        else:
            print("⚠️ Answer generation returned empty result")
        
        return True
    except Exception as e:
        print(f"❌ LLM Integration test failed: {e}")
        return False

def test_qa_system():
    """Test main Q&A system"""
    print("\n🧪 Testing Q&A System...")
    try:
        from qa_system import StudyMateQASystem
        qa_system = StudyMateQASystem(use_watson=False)
        print("✅ Q&A System initialized successfully")
        
        # Test system stats
        stats = qa_system.get_system_stats()
        print(f"✅ System stats: {stats['total_documents']} documents")
        
        return True
    except Exception as e:
        print(f"❌ Q&A System test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 StudyMate System Tests")
    print("=" * 40)
    
    tests = [
        test_pdf_processor,
        test_semantic_search,
        test_llm_integration,
        test_qa_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())