"""
AWS Bedrock client for Knowledge Base operations and LLM inference.
"""

import json
import time
import boto3
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError

from models.chat_models import ChatMessage, Source, RetrievalResult, GenerationResult
from config import Config


class BedrockKnowledgeBaseClient:
    """Client for AWS Bedrock Knowledge Base operations."""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize AWS session
        session = boto3.Session(
            region_name=config.aws_region,
            profile_name=config.aws_profile
        )
        
        # Initialize Bedrock clients
        self.bedrock_agent = session.client('bedrock-agent-runtime')
        self.bedrock_runtime = session.client('bedrock-runtime')
        
    def retrieve_documents(self, query: str, max_results: int = 5) -> RetrievalResult:
        """
        Retrieve relevant documents from the Knowledge Base.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            RetrievalResult with sources and metadata
        """
        start_time = time.time()
        
        try:
            response = self.bedrock_agent.retrieve(
                knowledgeBaseId=self.config.knowledge_base_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            )
            
            # Parse retrieval results
            sources = []
            for result in response.get('retrievalResults', []):
                content = result.get('content', {}).get('text', '')
                location = result.get('location', {})
                score = result.get('score', 0.0)
                
                source = Source(
                    content=content,
                    source_uri=location.get('s3Location', {}).get('uri', 'Unknown'),
                    score=score,
                    metadata=result.get('metadata', {})
                )
                sources.append(source)
            
            retrieval_time = (time.time() - start_time) * 1000
            
            return RetrievalResult(
                query=query,
                sources=sources,
                total_results=len(sources),
                retrieval_time_ms=retrieval_time
            )
            
        except ClientError as e:
            print(f"Error retrieving documents: {e}")
            return RetrievalResult(
                query=query,
                sources=[],
                total_results=0,
                retrieval_time_ms=(time.time() - start_time) * 1000
            )
    
    def retrieve_and_generate(self, query: str, chat_history: List[ChatMessage] = None) -> Dict[str, Any]:
        """
        🔥 CORE RAG FUNCTION: This is where the magic happens!
        
        This function performs the complete RAG pipeline in one AWS Bedrock API call:
        1. Takes user question
        2. Searches Paul Graham essays (vector search in OpenSearch)
        3. Retrieves most relevant chunks
        4. Sends chunks + question to Claude 3 Haiku
        5. Returns AI-generated answer with source citations
        
        Args:
            query: The user's question (e.g., "What is founder mode?")
            chat_history: Previous conversation for context (optional)
            
        Returns:
            Dictionary containing:
            - 'response': AI-generated answer
            - 'sources': List of essay chunks used to generate the answer
            - 'session_id': Bedrock session ID for conversation continuity
            - 'success': Whether the operation succeeded
        """
        # Start timing the operation for performance monitoring
        start_time = time.time()
        
        try:
            # 📝 STEP 1: Build the request payload for AWS Bedrock
            # This tells Bedrock exactly what we want it to do
            request = {
                # The user's question goes here
                'input': {'text': query},
                
                # Configuration for the RAG operation
                'retrieveAndGenerateConfiguration': {
                    'type': 'KNOWLEDGE_BASE',  # Use Knowledge Base (not external sources)
                    
                    'knowledgeBaseConfiguration': {
                        # Our specific Knowledge Base ID (contains Paul Graham essays)
                        'knowledgeBaseId': self.config.knowledge_base_id,  # "I8WQVOKH3T"
                        
                        # Which AI model to use for generating the answer
                        'modelArn': f'arn:aws:bedrock:{self.config.aws_region}::foundation-model/{self.config.llm_model_id}',
                        
                        # How to search for relevant information
                        'retrievalConfiguration': {
                            'vectorSearchConfiguration': {
                                # Get top 5 most relevant essay chunks
                                'numberOfResults': 5
                            }
                        }
                    }
                }
            }
            
            # 💬 STEP 2: Add conversation history for context (if provided)
            # This helps the AI understand the conversation flow
            if chat_history:
                session_history = []
                # Only keep the last 6 messages to avoid token limits
                for msg in chat_history[-6:]:
                    if msg.role.value == 'user':
                        session_history.append({'input': {'text': msg.content}})
                    elif msg.role.value == 'assistant':
                        session_history.append({'output': {'text': msg.content}})
                
                # Note: We're not adding session history to avoid parameter complexity
                # This could be enhanced in the future for better conversation flow
                if session_history:
                    pass  # Placeholder for future session management
            
            # 🚀 STEP 3: THE MAGIC HAPPENS HERE!
            # This single API call does everything:
            # - Searches through Paul Graham essays
            # - Finds relevant chunks
            # - Generates AI response
            # - Returns answer with sources
            response = self.bedrock_agent.retrieve_and_generate(**request)
            
            # 📖 STEP 4: Extract the AI-generated answer
            output = response.get('output', {})
            generated_text = output.get('text', '')
            
            # 📚 STEP 5: Extract source citations (which essays were used)
            sources = []
            citations = response.get('citations', [])
            
            # Process each citation to create clean source objects
            for citation in citations:
                for ref in citation.get('retrievedReferences', []):
                    location = ref.get('location', {})
                    
                    # Create a Source object with the essay content and metadata
                    source = Source(
                        content=ref.get('content', {}).get('text', ''),  # The actual essay text
                        source_uri=location.get('s3Location', {}).get('uri', 'Unknown'),  # File location
                        score=ref.get('metadata', {}).get('score', 0.0),  # Relevance score
                        metadata=ref.get('metadata', {})  # Additional metadata
                    )
                    sources.append(source)
            
            # ⏱️ Calculate how long the operation took
            generation_time = (time.time() - start_time) * 1000
            
            # 🎉 STEP 6: Return the complete result
            return {
                'response': generated_text,      # The AI's answer
                'sources': sources,              # Essay chunks used as sources
                'session_id': response.get('sessionId'),  # For conversation continuity
                'generation_time_ms': generation_time,    # Performance metric
                'success': True                  # Operation succeeded
            }
            
        except ClientError as e:
            # 💥 Handle AWS API errors gracefully
            print(f"Error in retrieve_and_generate: {e}")
            return {
                'response': f"I apologize, but I encountered an error: {str(e)}",
                'sources': [],
                'session_id': None,
                'generation_time_ms': (time.time() - start_time) * 1000,
                'success': False,
                'error': str(e)
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Bedrock Knowledge Base."""
        try:
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


class BedrockLLMClient:
    """Client for direct Bedrock LLM inference (without Knowledge Base)."""
    
    def __init__(self, config: Config):
        self.config = config
        
        session = boto3.Session(
            region_name=config.aws_region,
            profile_name=config.aws_profile
        )
        
        self.bedrock_runtime = session.client('bedrock-runtime')
    
    def generate_response(self, prompt: str, context: str = None) -> GenerationResult:
        """
        Generate response using Bedrock LLM directly.
        
        Args:
            prompt: User prompt
            context: Optional context from retrieval
            
        Returns:
            GenerationResult with response and metadata
        """
        start_time = time.time()
        
        try:
            # Prepare the full prompt
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            
            # Prepare request body for Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            }
            
            # Call Bedrock
            response = self.bedrock_runtime.invoke_model(
                modelId=self.config.llm_model_id,
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            generated_text = response_body.get('content', [{}])[0].get('text', '')
            
            generation_time = (time.time() - start_time) * 1000
            
            return GenerationResult(
                response=generated_text,
                model_used=self.config.llm_model_id,
                generation_time_ms=generation_time,
                token_count=response_body.get('usage', {}).get('output_tokens')
            )
            
        except ClientError as e:
            print(f"Error generating response: {e}")
            generation_time = (time.time() - start_time) * 1000
            
            return GenerationResult(
                response=f"Error generating response: {str(e)}",
                model_used=self.config.llm_model_id,
                generation_time_ms=generation_time
            )