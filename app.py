"""
🚀 PAUL GRAHAM ESSAYS RAG SYSTEM - MAIN ENTRY POINT

This is the main entry point for the RAG (Retrieval-Augmented Generation) system
that enables intelligent conversations with Paul Graham's essay collection.

WHAT THIS FILE DOES:
- Sets up the Python path to find our source code
- Imports and runs the Streamlit web application
- Serves as the single command to start the entire system

HOW TO RUN:
    streamlit run app.py

ARCHITECTURE OVERVIEW:
    app.py (this file)
        ↓
    src/frontend/streamlit_app.py (Web UI)
        ↓
    src/services/rag_service.py (RAG Orchestration)
        ↓
    src/clients/bedrock_client.py (AWS Bedrock API)
        ↓
    AWS Bedrock Knowledge Base (Vector Search + AI Generation)

The system uses AWS Bedrock Knowledge Base to:
1. Search through Paul Graham's essays using vector similarity
2. Retrieve the most relevant content chunks
3. Generate AI responses using Claude 3 Haiku
4. Provide source citations for transparency

Built for AI Engineer take-home assessment.
"""

import sys
from pathlib import Path

# Add src to path so Python can find our modules
sys.path.append(str(Path(__file__).parent / "src"))

from frontend.streamlit_app import main

if __name__ == "__main__":
    main()