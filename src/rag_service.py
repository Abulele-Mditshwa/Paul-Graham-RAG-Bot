"""AWS Bedrock Knowledge Base RAG Service."""

import json
import boto3
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from config import Config

@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    sources: Optional[List[Dict[str, Any]]] = None

class BedrockRAGService:
    """Service for RAG using AWS Bedrock Knowledge Base."""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize AWS clients
        session = boto3.Session(
            region_name=config.aws_region,
            profile_name=config.aws_profile
        )
        
        self.bedrock_agent = session.client('bedrock-agent-runtime')
        self.bedrock_runtime = session.client('bedrock-runtime')
    
    def retrieve_and_generate(self, query: str, chat_history: List[ChatMessage] = None) -> Dict[str, Any]:
        """
        Use Bedrock Knowledge Base to retrieve and generate response.
        """
        try:
            # Prepare the request for Knowledge Base
            request = {
                'input': {
                    'text': query
                },
                'retrieveAndGenerateConfiguration': {
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': self.config.knowledge_base_id,
                        'modelArn': f'arn:aws:bedrock:{self.config.aws_region}::foundation-model/{self.config.llm_model_id}',
                        'retrievalConfiguration': {
                            'vectorSearchConfiguration': {
                                'numberOfResults': 5
                            }
                        }
                    }
                }
            }
            
            # Add chat history if provided
            if chat_history:
                # Convert chat history to the format expected by Bedrock
                session_history = []
                for msg in chat_history[-6:]:  # Keep last 6 messages for context
                    if msg.role == 'user':
                        session_history.append({
                            'input': {'text': msg.content}
                        })
                    elif msg.role == 'assistant':
                        session_history.append({
                            'output': {'text': msg.content}
                        })
                
                if session_history:
                    request['sessionConfiguration'] = {
                        'kmsKeyArn': None  # Optional: Add KMS key for encryption
                    }
            
            # Call Bedrock Knowledge Base
            response = self.bedrock_agent.retrieve_and_generate(**request)
            
            # Extract response and sources
            output = response.get('output', {})
            generated_text = output.get('text', '')
            
            # Extract source citations
            citations = response.get('citations', [])
            sources = []
            
            for citation in citations:
                retrieved_refs = citation.get('retrievedReferences', [])
                for ref in retrieved_refs:
                    location = ref.get('location', {})
                    source_info = {
                        'content': ref.get('content', {}).get('text', ''),
                        'source': location.get('s3Location', {}).get('uri', 'Unknown'),
                        'score': ref.get('metadata', {}).get('score', 0.0)
                    }
                    sources.append(source_info)
            
            return {
                'response': generated_text,
                'sources': sources,
                'session_id': response.get('sessionId'),
                'success': True
            }
            
        except Exception as e:
            print(f"Error in retrieve_and_generate: {e}")
            return {
                'response': f"I apologize, but I encountered an error while processing your question: {str(e)}",
                'sources': [],
                'session_id': None,
                'success': False,
                'error': str(e)
            }
    
    def chat(self, message: str, chat_history: List[ChatMessage] = None) -> ChatMessage:
        """
        Process a chat message and return response.
        """
        result = self.retrieve_and_generate(message, chat_history)
        
        return ChatMessage(
            role='assistant',
            content=result['response'],
            sources=result['sources']
        )
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to AWS services."""
        try:
            # Test Knowledge Base access
            test_query = "What is a startup?"
            result = self.retrieve_and_generate(test_query)
            
            return {
                'knowledge_base_accessible': result['success'],
                'knowledge_base_id': self.config.knowledge_base_id,
                'model_id': self.config.llm_model_id,
                'test_response_length': len(result['response']),
                'sources_found': len(result['sources']),
                'success': result['success']
            }
            
        except Exception as e:
            return {
                'knowledge_base_accessible': False,
                'error': str(e),
                'success': False
            }