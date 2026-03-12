#!/usr/bin/env python3
"""Test AWS Bedrock Knowledge Base connection."""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config import load_config
from rag_service import BedrockRAGService

def main():
    """Test the Knowledge Base connection."""
    print("🧪 Testing AWS Bedrock Knowledge Base Connection")
    print("=" * 60)
    
    try:
        # Load configuration
        config = load_config()
        print(f"📋 Configuration:")
        print(f"   Knowledge Base ID: {config.knowledge_base_id}")
        print(f"   Model: {config.llm_model_id}")
        print(f"   Region: {config.aws_region}")
        
        # Initialize RAG service
        print(f"\n🔧 Initializing RAG service...")
        rag_service = BedrockRAGService(config)
        
        # Test connection
        print(f"\n🔍 Testing connection...")
        test_result = rag_service.test_connection()
        
        if test_result['success']:
            print(f"✅ Connection successful!")
            print(f"   Response length: {test_result['test_response_length']} characters")
            print(f"   Sources found: {test_result['sources_found']}")
        else:
            print(f"❌ Connection failed: {test_result.get('error', 'Unknown error')}")
            return False
        
        # Test a real query
        print(f"\n💬 Testing real query...")
        test_query = "What does Paul Graham say about startups?"
        print(f"   Query: {test_query}")
        
        result = rag_service.retrieve_and_generate(test_query)
        
        if result['success']:
            print(f"✅ Query successful!")
            print(f"   Response: {result['response'][:200]}...")
            print(f"   Sources: {len(result['sources'])}")
            
            if result['sources']:
                print(f"\n📚 Top sources:")
                for i, source in enumerate(result['sources'][:2], 1):
                    print(f"   {i}. {source['content'][:100]}...")
                    print(f"      Score: {source.get('score', 'N/A')}")
        else:
            print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
            return False
        
        print(f"\n🎉 All tests passed! Knowledge Base is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)