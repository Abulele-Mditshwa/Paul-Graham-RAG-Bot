#!/usr/bin/env python3
"""
🧪 KNOWLEDGE BASE CONNECTION TEST

This script tests the connection to your AWS Bedrock Knowledge Base to ensure
everything is configured correctly before running the main application.

🚨 IMPORTANT FOR TESTERS:
Before running this test, ensure you have:
1. Configured your AWS credentials
2. Updated src/config.py with YOUR AWS resource IDs
3. Ensured access to Claude 3 Haiku in your Bedrock account

WHAT THIS TEST DOES:
- Loads your configuration settings
- Tests connection to Bedrock Knowledge Base
- Performs a sample query to verify functionality
- Validates that sources are being returned correctly

HOW TO RUN:
    python test_knowledge_base.py

EXPECTED OUTPUT:
- Configuration details (Knowledge Base ID, model, region)
- Connection test results
- Sample query response with sources
- Success confirmation

If any step fails, check your AWS configuration and credentials.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config import load_config
from services.rag_service import RAGService

def main():
    """Test the Knowledge Base connection and functionality."""
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
        rag_service = RAGService(config)
        
        # Test system status
        print(f"\n🔍 Testing system status...")
        status = rag_service.get_system_status()
        
        kb_status = status.get('knowledge_base', {})
        if kb_status.get('success'):
            print(f"✅ Knowledge Base connection successful!")
            print(f"   Test response length: {len(kb_status.get('test_response', ''))} characters")
        else:
            print(f"❌ Knowledge Base connection failed: {kb_status.get('error', 'Unknown error')}")
            return False
        
        # Test a real query using the main chat function
        print(f"\n💬 Testing real query...")
        test_query = "What does Paul Graham say about startups?"
        print(f"   Query: {test_query}")
        
        # Use the main chat function that the Streamlit app uses
        response_message = rag_service.chat_with_knowledge_base(test_query)
        
        if response_message.content:
            print(f"✅ Query successful!")
            print(f"   Response: {response_message.content[:200]}...")
            print(f"   Sources: {len(response_message.sources) if response_message.sources else 0}")
            
            if response_message.sources:
                print(f"\n📚 Top sources:")
                for i, source in enumerate(response_message.sources[:2], 1):
                    print(f"   {i}. {source.content[:100]}...")
                    print(f"      Score: {getattr(source, 'score', 'N/A')}")
        else:
            print(f"❌ Query failed: No response received")
            return False
        
        print(f"\n🎉 All tests passed! Knowledge Base is working correctly.")
        print(f"\n🚀 You can now run the Streamlit app with: streamlit run app.py")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print(f"\n🔧 Troubleshooting tips:")
        print(f"   1. Check your AWS credentials are configured")
        print(f"   2. Verify your Knowledge Base ID in src/config.py")
        print(f"   3. Ensure you have access to Claude 3 Haiku in Bedrock")
        print(f"   4. Check that your Knowledge Base is in 'Active' status")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)