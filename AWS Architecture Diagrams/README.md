# AWS Architecture Diagrams - Paul Graham RAG System

This folder contains professional AWS architecture diagrams for the Paul Graham Essays RAG (Retrieval-Augmented Generation) system.

## 🏗️ **Actual System Architecture**

**Important**: This system uses a **pre-configured AWS Bedrock Knowledge Base** with Paul Graham essays already ingested. No S3 storage is used for the essays.

### **Core Components:**
- **Frontend**: Streamlit web application
- **LLM**: Amazon Bedrock with Claude 3 Haiku
- **Knowledge Base**: AWS Bedrock Knowledge Base (ID: I8WQVOKH3T) - pre-loaded with essays
- **Vector Store**: OpenSearch Serverless (collection: bedrock-knowledge-base-ciegft)
- **Backend**: Python RAG service orchestrating the pipeline

## 📊 Available Diagrams

### 1. **01_rag_system_overview.png** - Corrected High-Level Architecture
- **Purpose**: Shows the actual system architecture without S3
- **Components**: 
  - Users → Streamlit Web App
  - AWS Bedrock Knowledge Base (pre-loaded with Paul Graham essays)
  - Claude 3 Haiku for AI generation
  - OpenSearch Serverless for vector search
- **Data Flow**: 8-step process from user question to AI response with sources

### 2. **02_detailed_data_flow.png** - Actual RAG Pipeline
- **Purpose**: Step-by-step breakdown of the real RAG process
- **Shows**:
  - Step 1: User input through Streamlit chat interface
  - Step 2: Python backend (RAG Service + Bedrock Client)
  - Step 3: AWS Bedrock Knowledge Base processing
  - Step 4: OpenSearch Serverless vector database (pre-loaded essays)
  - Step 5: AI response with source citations
- **Best for**: Understanding how the Knowledge Base orchestrates everything

### 3. **03_component_architecture.png** - Actual Technical Components
- **Purpose**: Detailed view of real system components and relationships
- **Layers**:
  - **Frontend**: Streamlit chat interface and session management
  - **Backend Services**: RAG orchestration and Bedrock client
  - **AWS Bedrock**: Pre-configured Knowledge Base with embedded essays
- **Best for**: Understanding the actual code organization and AWS setup

## 🎯 Use Cases

### **For Presentations**
- Use **01_rag_system_overview.png** for executive/business presentations
- Use **02_detailed_data_flow.png** for technical deep-dives
- Use **03_component_architecture.png** for development team discussions

### **For Documentation**
- Include in README files, technical specifications, or system documentation
- Reference in code comments or architectural decision records (ADRs)
- Use in onboarding materials for new team members

### **For Take-Home Project**
- Demonstrates understanding of AWS architecture
- Shows professional system design capabilities
- Illustrates RAG pipeline implementation knowledge

## 🔧 Technical Details

### **System Configuration**
- **Knowledge Base ID**: I8WQVOKH3T
- **OpenSearch Collection**: bedrock-knowledge-base-ciegft
- **AI Model**: Claude 3 Haiku (anthropic.claude-3-haiku-20240307-v1:0)
- **Region**: us-east-1

### **Key AWS Services**
1. **AWS Bedrock Knowledge Base**: Pre-configured with Paul Graham essays, manages complete RAG pipeline
2. **Claude 3 Haiku**: Provides fast, cost-effective AI responses via Bedrock
3. **OpenSearch Serverless**: Vector database integrated with Knowledge Base for semantic search
4. **Titan Text Embeddings V2**: Converts text to vectors (handled by Knowledge Base)

### **Data Flow Summary - CORRECTED**
```
1. User Question → Streamlit
2. Streamlit → Bedrock Knowledge Base (RAG Query)
3. Knowledge Base → OpenSearch (Vector Search)
4. OpenSearch → Knowledge Base (Relevant Chunks)
5. Knowledge Base → Claude 3 Haiku (Generate Request)
6. Claude 3 Haiku → Knowledge Base (AI Response)
7. Knowledge Base → Streamlit (Response + Sources)
8. Streamlit → User (Formatted Display)
```

**Key Point**: The Knowledge Base orchestrates the entire flow - it calls OpenSearch for vector search, then calls Claude for generation, and returns everything to your application in one API response.

## 🛠️ Regenerating Diagrams

To regenerate or modify the diagrams:

1. **Install dependencies**:
   ```bash
   pip install diagrams
   brew install graphviz
   ```

2. **Run the script**:
   ```bash
   python3 create_diagrams.py
   ```

3. **Customize**: Edit `create_diagrams.py` to modify layouts, colors, or components

## 📋 Diagram Specifications

- **Format**: PNG (high resolution)
- **Tool**: Python Diagrams library with Graphviz
- **Style**: Professional AWS architecture diagram standards
- **Colors**: AWS service colors and consistent theming
- **Layout**: Left-to-right and top-to-bottom flows for clarity

## 🎨 Design Principles

1. **Clarity**: Each diagram focuses on a specific aspect of the system
2. **Consistency**: Uses standard AWS icons and color schemes
3. **Flow**: Clear directional arrows showing data movement
4. **Grouping**: Logical clustering of related components
5. **Labeling**: Descriptive labels for all components and connections

---

**Generated**: March 12, 2026  
**System**: Paul Graham Essays RAG System  
**Architecture**: AWS Bedrock + Streamlit + Python