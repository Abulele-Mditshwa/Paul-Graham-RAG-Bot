"""
⚙️ CONFIGURATION SETTINGS FOR RAG SYSTEM

This file contains all the configuration settings for the Paul Graham Essays RAG system.
All the important IDs, model names, and parameters are defined here.

KEY COMPONENTS CONFIGURED:
1. AWS Settings (region, credentials)
2. Bedrock Knowledge Base ID (where essays are stored)
3. OpenSearch Collection (vector database)
4. AI Model Selection (Claude 3 Haiku)
5. Chat Parameters (temperature, max tokens)

IMPORTANT IDS:
- Knowledge Base ID: I8WQVOKH3T (contains all Paul Graham essays)
- OpenSearch Collection: bedrock-knowledge-base-ciegft (vector storage)
- Model: anthropic.claude-3-haiku-20240307-v1:0 (AI for responses)

To use different settings, either:
1. Modify the defaults below, OR
2. Set environment variables (they override defaults)
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration settings for the AWS RAG chatbot."""
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_profile: Optional[str] = None
    
    # Bedrock Knowledge Base Configuration
    knowledge_base_id: str = "I8WQVOKH3T"
    
    # OpenSearch Serverless Configuration
    opensearch_collection_name: str = "bedrock-knowledge-base-ciegft"
    opensearch_collection_arn: str = "arn:aws:aoss:us-east-1:603054822743:collection/0lgst053uz6h5fkvfb286"
    
    # Bedrock Model Configuration - Claude 3 Haiku (working model)
    llm_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    
    # Chat Configuration
    max_tokens: int = 1000
    temperature: float = 0.1
    top_p: float = 0.9

def load_config() -> Config:
    """Load configuration from environment variables."""
    config = Config()
    
    # Override with environment variables if present
    config.aws_region = os.getenv("AWS_REGION", config.aws_region)
    config.aws_profile = os.getenv("AWS_PROFILE")
    config.knowledge_base_id = os.getenv("KNOWLEDGE_BASE_ID", config.knowledge_base_id)
    config.llm_model_id = os.getenv("LLM_MODEL_ID", config.llm_model_id)
    
    return config