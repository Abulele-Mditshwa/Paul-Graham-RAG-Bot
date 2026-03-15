#!/usr/bin/env python3
"""
Quick test to verify the Streamlit app can start without errors.
This simulates what happens when you run 'streamlit run app.py'
"""

import sys
from pathlib import Path

# Add src to path (same as app.py does)
sys.path.append(str(Path(__file__).parent / "src"))

def test_app_startup():
    """Test that the app can start without import errors."""
    print("🧪 Testing Streamlit app startup...")
    
    try:
        # Test the same import that app.py uses
        from frontend.streamlit_app import main
        print("✅ Import successful")
        
        # Test that we can create the app class
        from frontend.streamlit_app import StreamlitRAGApp
        print("✅ StreamlitRAGApp class available")
        
        # Test configuration loading
        from config import load_config
        config = load_config()
        print(f"✅ Configuration loaded (KB ID: {config.knowledge_base_id})")
        
        # Test RAG service
        from services.rag_service import RAGService
        rag_service = RAGService(config)
        print("✅ RAG service initialized")
        
        print("\n🎉 SUCCESS: App is ready to run!")
        print("You can now run: streamlit run app.py")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_app_startup()
    sys.exit(0 if success else 1)