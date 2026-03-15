"""
🚀 PAUL GRAHAM ESSAYS RAG SYSTEM - MAIN ENTRY POINT

This is the main entry point for the RAG (Retrieval-Augmented Generation) system
that enables intelligent conversations with Paul Graham's essay collection.

🚨 IMPORTANT FOR TESTERS/REVIEWERS:
Before running this application, you MUST configure your own AWS resources:

1. Create your own Bedrock Knowledge Base with Paul Graham essays
2. Set up your own OpenSearch Serverless collection
3. Ensure access to Claude 3 Haiku in your AWS account
4. Update the configuration in src/config.py OR set environment variables:
   - KNOWLEDGE_BASE_ID="your_knowledge_base_id"
   - OPENSEARCH_COLLECTION_NAME="your_collection_name"
   - AWS_REGION="your_preferred_region"

The default configuration will NOT work as it uses the original developer's resources.

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

"""

import sys
from pathlib import Path

# Add src to path so Python can find our modules
sys.path.append(str(Path(__file__).parent / "src"))

from frontend.streamlit_app import main

if __name__ == "__main__":
    main()