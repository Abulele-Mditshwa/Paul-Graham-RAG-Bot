"""
⚙️ CONFIGURATION SETTINGS FOR RAG SYSTEM

This file contains all the configuration settings for the Paul Graham Essays RAG system.
All the important IDs, model names, and parameters are defined here.

🚨 IMPORTANT FOR TESTERS/REVIEWERS:
The default values below are from the original developer's AWS account and will NOT work for you.
You MUST replace these with your own AWS resources:

1. Create your own Bedrock Knowledge Base with Paul Graham essays
2. Set up your own OpenSearch Serverless collection  
3. Ensure you have access to Claude 3 Haiku in your AWS account
4. Update the IDs below OR set environment variables

KEY COMPONENTS TO CONFIGURE:
1. AWS Settings (region, credentials)
2. Bedrock Knowledge Base ID (where essays are stored) - REPLACE WITH YOURS
3. OpenSearch Collection (vector database) - REPLACE WITH YOURS  
4. AI Model Selection (Claude 3 Haiku) - ENSURE ACCESS IN YOUR ACCOUNT
5. Chat Parameters (temperature, max tokens)

EXAMPLE IDS (DO NOT USE - REPLACE WITH YOUR OWN):
- Knowledge Base ID: I8WQVOKH3T (EXAMPLE - use your own)
- OpenSearch Collection: bedrock-knowledge-base-ciegft (EXAMPLE - use your own)
- Model: anthropic.claude-3-haiku-20240307-v1:0 (ensure access in your account)

To use your own settings:
1. Modify the defaults below with YOUR AWS resource IDs, OR
2. Set environment variables (they override defaults):
   - KNOWLEDGE_BASE_ID=your_kb_id
   - OPENSEARCH_COLLECTION_NAME=your_collection_name
   - AWS_REGION=your_region
   - LLM_MODEL_ID=your_model_id
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration settings for the AWS RAG chatbot."""
    
    # AWS Configuration
    aws_region: str = "us-east-1"  # Change to your preferred AWS region
    aws_profile: Optional[str] = None  # Set to your AWS profile name if using profiles
    
    # 🚨 CRITICAL: Bedrock Knowledge Base Configuration - REPLACE WITH YOUR OWN
    # This Knowledge Base ID belongs to the original developer and will NOT work for you
    # You must create your own Knowledge Base and replace this ID
    knowledge_base_id: str = "I8WQVOKH3T"  # ⚠️ REPLACE WITH YOUR KNOWLEDGE BASE ID
    
    # 🚨 CRITICAL: OpenSearch Serverless Configuration - REPLACE WITH YOUR OWN  
    # These are the original developer's resources and will NOT work for you
    # You must create your own OpenSearch collection and replace these values
    opensearch_collection_name: str = "bedrock-knowledge-base-ciegft"  # ⚠️ REPLACE WITH YOUR COLLECTION NAME
    opensearch_collection_arn: str = "arn:aws:aoss:us-east-1:603054822743:collection/0lgst053uz6h5fkvfb286"  # ⚠️ REPLACE WITH YOUR ARN
    
    # 🚨 IMPORTANT: Bedrock Model Configuration - ENSURE ACCESS IN YOUR ACCOUNT
    # Make sure you have access to Claude 3 Haiku in your AWS account and region
    # Request model access in AWS Bedrock console if needed
    llm_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"  # ⚠️ ENSURE ACCESS IN YOUR ACCOUNT
    
    # Chat Configuration - These can remain as defaults
    max_tokens: int = 1000
    temperature: float = 0.1
    top_p: float = 0.9

def load_config() -> Config:
    """
    Load configuration from environment variables.
    
    🚨 IMPORTANT FOR TESTERS:
    Set these environment variables with YOUR AWS resource IDs:
    
    export KNOWLEDGE_BASE_ID="your_knowledge_base_id"
    export OPENSEARCH_COLLECTION_NAME="your_collection_name" 
    export AWS_REGION="your_preferred_region"
    export LLM_MODEL_ID="your_model_id"
    
    Or modify the default values in the Config class above.
    """
    config = Config()
    
    # Override with environment variables if present
    config.aws_region = os.getenv("AWS_REGION", config.aws_region)
    config.aws_profile = os.getenv("AWS_PROFILE")
    
    # 🚨 CRITICAL: Replace these with your own AWS resource IDs
    config.knowledge_base_id = os.getenv("KNOWLEDGE_BASE_ID", config.knowledge_base_id)
    config.opensearch_collection_name = os.getenv("OPENSEARCH_COLLECTION_NAME", config.opensearch_collection_name)
    config.llm_model_id = os.getenv("LLM_MODEL_ID", config.llm_model_id)
    
    return config