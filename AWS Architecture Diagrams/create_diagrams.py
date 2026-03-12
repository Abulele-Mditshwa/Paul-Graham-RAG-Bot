#!/usr/bin/env python3
"""
Create AWS Architecture Diagrams for Paul Graham RAG System

This script creates professional AWS architecture diagrams showing:
1. High-level system overview
2. Detailed data flow
3. Component interactions

Requirements: pip install diagrams
"""

try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.aws.compute import EC2
    from diagrams.aws.database import ElastiCache  # Using ElastiCache as vector DB representation
    from diagrams.aws.ml import Bedrock
    from diagrams.aws.storage import S3
    from diagrams.aws.network import CloudFront
    from diagrams.onprem.client import Users
    from diagrams.programming.framework import React
    from diagrams.programming.language import Python
    
    print("✅ All diagram dependencies available")
    
    # Diagram 1: High-Level RAG System Architecture - CORRECTED
    with Diagram("Paul Graham RAG System - Corrected Architecture", 
                 show=False, 
                 direction="LR",
                 filename="01_rag_system_overview"):
        
        # User interaction
        users = Users("Users")
        
        with Cluster("Frontend"):
            streamlit = React("Streamlit\nWeb App")
        
        with Cluster("AWS Bedrock Services"):
            with Cluster("Knowledge Base (I8WQVOKH3T)"):
                bedrock_kb = Bedrock("Bedrock\nKnowledge Base\n(Pre-loaded Essays)")
                bedrock_llm = Bedrock("Claude 3 Haiku\n(LLM)")
            
            with Cluster("Vector Storage"):
                opensearch = ElastiCache("OpenSearch Serverless\n(bedrock-knowledge-base-ciegft)")
        
        # CORRECTED Data flow with proper directions
        users >> Edge(label="1. Chat Questions") >> streamlit
        streamlit >> Edge(label="2. RAG Query") >> bedrock_kb
        bedrock_kb >> Edge(label="3. Vector Search") >> opensearch
        opensearch >> Edge(label="4. Relevant Chunks") >> bedrock_kb
        bedrock_kb >> Edge(label="5. Generate Request") >> bedrock_llm
        bedrock_llm >> Edge(label="6. AI Response") >> bedrock_kb
        bedrock_kb >> Edge(label="7. Response + Sources") >> streamlit
        streamlit >> Edge(label="8. Formatted Display") >> users
    
    print("✅ Created: 01_rag_system_overview.png")
    
    # Diagram 2: Detailed Data Flow - CORRECTED
    with Diagram("RAG System - Corrected Data Flow", 
                 show=False, 
                 direction="TB",
                 filename="02_detailed_data_flow"):
        
        # User layer
        user = Users("User")
        
        with Cluster("Step 1: User Input"):
            chat_input = React("Streamlit\nChat Interface")
        
        with Cluster("Step 2: Python Backend"):
            rag_service = Python("RAG Service\nOrchestrator")
            bedrock_client = Python("Bedrock Client\n(API Calls)")
        
        with Cluster("Step 3: AWS Bedrock Knowledge Base"):
            kb_service = Bedrock("Knowledge Base\nService")
        
        with Cluster("Step 4: Internal KB Operations"):
            retrieval = Bedrock("Vector Search\n& Retrieval")
            generation = Bedrock("Claude 3 Haiku\nGeneration")
        
        with Cluster("Step 5: Vector Database"):
            vector_db = ElastiCache("OpenSearch Serverless\n(Pre-loaded Paul Graham Essays)")
        
        # CORRECTED flow with proper sequence
        user >> Edge(label="1. Question") >> chat_input
        chat_input >> Edge(label="2. Process") >> rag_service
        rag_service >> Edge(label="3. API Call") >> bedrock_client
        bedrock_client >> Edge(label="4. retrieve_and_generate()") >> kb_service
        kb_service >> Edge(label="5. Search") >> retrieval
        retrieval >> Edge(label="6. Query Vectors") >> vector_db
        vector_db >> Edge(label="7. Return Chunks") >> retrieval
        retrieval >> Edge(label="8. Context + Question") >> generation
        generation >> Edge(label="9. AI Response") >> kb_service
        kb_service >> Edge(label="10. Response + Citations") >> user
    
    print("✅ Created: 02_detailed_data_flow.png")
    
    # Diagram 3: Component Architecture - CORRECTED
    with Diagram("RAG System - Corrected Component Architecture", 
                 show=False, 
                 direction="LR",
                 filename="03_component_architecture"):
        
        with Cluster("Frontend (Streamlit)"):
            ui = React("Chat Interface")
            session_mgr = Python("Session Manager")
        
        with Cluster("Backend Services"):
            with Cluster("RAG Service Layer"):
                rag_orchestrator = Python("RAG Service")
                chat_manager = Python("Chat Manager")
            
            with Cluster("Client Layer"):
                bedrock_client = Python("Bedrock Client")
                config = Python("Configuration")
        
        with Cluster("AWS Bedrock Services"):
            with Cluster("Pre-configured Knowledge Base"):
                kb = Bedrock("Knowledge Base\n(I8WQVOKH3T)\nPre-loaded Essays")
                claude = Bedrock("Claude 3 Haiku\nLLM")
            
            with Cluster("Vector Storage"):
                opensearch_db = ElastiCache("OpenSearch Serverless\n(bedrock-knowledge-base-ciegft)")
        
        # CORRECTED Connections with proper flow direction
        ui >> Edge(label="User Input") >> rag_orchestrator
        session_mgr >> Edge(label="Chat History") >> chat_manager
        chat_manager >> Edge(label="Context") >> rag_orchestrator
        rag_orchestrator >> Edge(label="RAG Request") >> bedrock_client
        bedrock_client >> Edge(label="API Call") >> kb
        kb >> Edge(label="Vector Search") >> opensearch_db
        opensearch_db >> Edge(label="Relevant Chunks") >> kb
        kb >> Edge(label="Generate Request") >> claude
        claude >> Edge(label="AI Response") >> kb
        kb >> Edge(label="Response + Sources") >> bedrock_client
        bedrock_client >> Edge(label="Formatted Response") >> rag_orchestrator
        rag_orchestrator >> Edge(label="Display") >> ui
        config >> Edge(label="Settings") >> bedrock_client
    
    print("✅ Created: 03_component_architecture.png")
    
    print("\n🎉 All AWS architecture diagrams created successfully!")
    print("📁 Check the current directory for the generated PNG files:")
    print("   - 01_rag_system_overview.png")
    print("   - 02_detailed_data_flow.png") 
    print("   - 03_component_architecture.png")

except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("💡 To install: pip install diagrams")
    print("💡 Also need Graphviz: brew install graphviz")

except Exception as e:
    print(f"❌ Error creating diagrams: {e}")