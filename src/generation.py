"""Direct Claude interaction for fallback scenarios."""

import json
import boto3
from typing import Dict, Any

from config import Config

class ClaudeService:
    """Direct Claude interaction service for fallback scenarios."""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize Bedrock client
        session = boto3.Session(
            region_name=config.aws_region,
            profile_name=config.aws_profile
        )
        
        self.bedrock_runtime = session.client('bedrock-runtime')
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using Claude directly."""
        
        # Prepare the request body for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=self.config.llm_model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            result = json.loads(response['body'].read())
            
            if 'content' in result and len(result['content']) > 0:
                return result['content'][0]['text']
            else:
                raise ValueError("Unexpected response format from Claude")
                
        except Exception as e:
            print(f"Error calling Claude: {e}")
            raise