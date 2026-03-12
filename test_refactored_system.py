#!/usr/bin/env python3
"""
Comprehensive test script for the refactored RAG system.
This demonstrates all components and their interactions.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config import load_config
from services.rag_service import RAGService
from services.ingestion_service import DataIngestionService
from clients.opensearch_client import OpenSearchServerlessClient
from models.chat_models import MessageRole, ChatMessage


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n🔍 {title}")
    print("-" * 40)


def test_configuration():
    """Test configuration loading."""
    print_header("CONFIGURATION TEST")
    
    config = load_config()
    print(f"✅ Configuration loaded successfully")
    print(f"   - AWS Region: {config.aws_region}")
    print(f"   - Knowledge Base ID: {config.knowledge_base_id}")
    print(f"   - Model ID: {config.llm_model_id}")
    print(f"   - OpenSearch Collection: {config.opensearch_collection_name}")
    
    return config


def test_opensearch_connection(config):
    """Test OpenSearch connection and explore indices."""
    print_header("OPENSEARCH CONNECTION TEST")
    
    try:
        os_client = OpenSearchServerlessClient(config)
        
        # Test connection
        print_section("Connection Info")
        info = os_client.get_collection_info()
        if info['success']:
            print(f"✅ Connected to OpenSearch collection")
            print(f"   - Collection: {info['collection_name']}")
            print(f"   - Host: {info['host']}")
            print(f"   - Cluster Health: {info['cluster_health']['status']}")
        else:
            print(f"❌ OpenSearch connection failed: {info['error']}")
            return False
        
        # List indices
        print_section("Indices Information")
        indices_info = os_client.list_indices()
        if indices_info['success']:
            print(f"📊 Found {indices_info['total_indices']} indices:")
            for index_name, stats in indices_info['indices'].items():
                if 'error' not in stats:
                    print(f"   - {index_name}: {stats['doc_count']:,} docs, {stats['size_bytes']:,} bytes")
                else:
                    print(f"   - {index_name}: {stats['error']}")
        else:
            print(f"❌ Could not list indices: {indices_info['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenSearch test failed: {e}")
        return False


def test_knowledge_base_operations(config):
    """Test Knowledge Base operations."""
    print_header("KNOWLEDGE BASE OPERATIONS TEST")
    
    try:
        rag_service = RAGService(config)
        
        # Test system status
        print_section("System Status")
        status = rag_service.get_system_status()
        
        if status['knowledge_base']['success']:
            print("✅ Knowledge Base accessible")
            kb_info = status['knowledge_base']
            print(f"   - Test response length: {kb_info['test_response_length']} chars")
            print(f"   - Sources found: {kb_info['sources_found']}")
        else:
            print(f"❌ Knowledge Base error: {status['knowledge_base']['error']}")
            return False
        
        # Test retrieval only
        print_section("Document Retrieval Test")
        retrieval_result = rag_service.kb_client.retrieve_documents("What is a startup?", max_results=3)
        print(f"📚 Retrieved {retrieval_result.total_results} documents in {retrieval_result.retrieval_time_ms:.1f}ms")
        
        for i, source in enumerate(retrieval_result.sources, 1):
            print(f"   Source {i} (score: {source.score:.3f}): {source.get_display_content(100)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Knowledge Base test failed: {e}")
        return False


def test_rag_workflows(config):
    """Test different RAG workflows."""
    print_header("RAG WORKFLOWS TEST")
    
    try:
        rag_service = RAGService(config)
        test_query = "What does Paul Graham say about learning programming?"
        
        # Test integrated approach
        print_section("Integrated Knowledge Base Approach")
        response1 = rag_service.chat_with_knowledge_base(test_query)
        print(f"✅ Integrated response ({len(response1.content)} chars):")
        print(f"   {response1.content[:200]}...")
        print(f"   Sources: {len(response1.sources) if response1.sources else 0}")
        
        # Test separate steps approach
        print_section("Separate Steps Approach")
        response2 = rag_service.chat_with_separate_steps(test_query)
        print(f"✅ Separate steps response:")
        print(f"   - Retrieval time: {response2.retrieval_result.retrieval_time_ms:.1f}ms")
        print(f"   - Generation time: {response2.generation_result.generation_time_ms:.1f}ms")
        print(f"   - Response length: {len(response2.message.content)} chars")
        print(f"   - Sources: {len(response2.message.sources) if response2.message.sources else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG workflows test failed: {e}")
        return False


def test_ingestion_service(config):
    """Test ingestion service (informational)."""
    print_header("INGESTION SERVICE TEST")
    
    try:
        ingestion_service = DataIngestionService(config)
        
        # Get Knowledge Base info
        print_section("Knowledge Base Information")
        kb_info = ingestion_service.get_knowledge_base_info()
        if kb_info['success']:
            print(f"✅ Knowledge Base details:")
            print(f"   - Name: {kb_info['name']}")
            print(f"   - Status: {kb_info['status']}")
            print(f"   - Description: {kb_info.get('description', 'N/A')}")
            print(f"   - Created: {kb_info.get('created_at', 'N/A')}")
        else:
            print(f"❌ Could not get KB info: {kb_info['error']}")
        
        # List data sources
        print_section("Data Sources")
        ds_info = ingestion_service.list_data_sources()
        if ds_info['success']:
            print(f"📁 Found {ds_info['total_count']} data sources:")
            for ds in ds_info['data_sources']:
                print(f"   - {ds['name']} ({ds['status']}): {ds.get('description', 'No description')}")
        else:
            print(f"❌ Could not list data sources: {ds_info['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ingestion service test failed: {e}")
        return False


def test_chat_conversation(config):
    """Test a multi-turn conversation."""
    print_header("MULTI-TURN CONVERSATION TEST")
    
    try:
        rag_service = RAGService(config)
        
        # Simulate a conversation
        conversation = [
            "What is Y Combinator?",
            "Who founded it?",
            "What advice does Paul Graham give to startups?"
        ]
        
        chat_history = []
        
        for i, question in enumerate(conversation, 1):
            print_section(f"Turn {i}: {question}")
            
            # Get response
            response = rag_service.chat_with_knowledge_base(question, chat_history)
            
            # Add to history
            chat_history.append(ChatMessage(role=MessageRole.USER, content=question))
            chat_history.append(response)
            
            print(f"✅ Response: {response.content[:150]}...")
            print(f"   Sources: {len(response.sources) if response.sources else 0}")
        
        print(f"\n💬 Conversation completed with {len(chat_history)} messages")
        return True
        
    except Exception as e:
        print(f"❌ Conversation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Refactored RAG System Tests")
    
    # Test configuration
    config = test_configuration()
    if not config:
        return
    
    # Run all tests
    tests = [
        ("OpenSearch Connection", lambda: test_opensearch_connection(config)),
        ("Knowledge Base Operations", lambda: test_knowledge_base_operations(config)),
        ("RAG Workflows", lambda: test_rag_workflows(config)),
        ("Ingestion Service", lambda: test_ingestion_service(config)),
        ("Chat Conversation", lambda: test_chat_conversation(config))
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The refactored system is working correctly.")
        print("\n🚀 You can now run the Streamlit app with: streamlit run app.py")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()