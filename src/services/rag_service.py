"""
🔧 RAG SERVICE - ORCHESTRATES RETRIEVAL AND GENERATION OPERATIONS

This is the core service that orchestrates the RAG (Retrieval-Augmented Generation) pipeline
for the Paul Graham Essays chatbot system.

WHAT THIS SERVICE DOES:
- Coordinates between the frontend and AWS Bedrock Knowledge Base
- Manages chat sessions and conversation history
- Provides two RAG approaches: integrated (recommended) and separate steps
- Handles system status monitoring and health checks
- Formats responses for the frontend display

KEY COMPONENTS:
1. RAGService: Main orchestrator for chat operations
2. ChatSessionManager: Manages conversation history and sessions

ARCHITECTURE FLOW:
    Streamlit App → RAGService → BedrockKnowledgeBaseClient → AWS Bedrock → AI Response

The service provides two approaches:
1. INTEGRATED (Recommended): Single API call to Bedrock handles everything
   - Vector search + AI generation in one step
   - Automatic context preparation
   - Built-in source citations
   
2. SEPARATE STEPS: Manual control over each RAG step
   - Explicit document retrieval
   - Manual context preparation  
   - Separate AI generation call

USAGE:
    # Initialize service
    rag_service = RAGService(config)
    
    # Chat with integrated approach (recommended)
    response = rag_service.chat_with_knowledge_base("What is founder mode?")
    
    # Chat with separate steps (more control)
    response = rag_service.chat_with_separate_steps("How to get startup ideas?")
"""

import time
from typing import List, Optional

from models.chat_models import (
    ChatMessage, MessageRole, RAGResponse, 
    RetrievalResult, GenerationResult
)
from clients.bedrock_client import BedrockKnowledgeBaseClient, BedrockLLMClient
from config import Config


class RAGService:
    """
    Main RAG service that orchestrates retrieval and generation.
    
    This service provides two approaches:
    1. Knowledge Base integrated (retrieve + generate in one call) - Recommended
    2. Separate retrieval and generation (more control)
    """
    
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize clients
        self.kb_client = BedrockKnowledgeBaseClient(config)
        self.llm_client = BedrockLLMClient(config)
    
    def chat_with_knowledge_base(self, message: str, chat_history: List[ChatMessage] = None) -> ChatMessage:
        """
        🎯 MAIN CHAT FUNCTION: This is the primary way users interact with Paul Graham's essays
        
        This function orchestrates the entire RAG (Retrieval-Augmented Generation) process:
        1. Takes user's question
        2. Calls Bedrock Knowledge Base to get AI response + sources
        3. Packages the result into a clean ChatMessage object
        
        This is the "integrated approach" - Bedrock handles everything internally:
        - Vector search through essays
        - Context preparation
        - AI response generation
        - Source citation
        
        Args:
            message: User's question (e.g., "How do I get startup ideas?")
            chat_history: Previous conversation messages for context
            
        Returns:
            ChatMessage object containing:
            - AI-generated response
            - Source citations from Paul Graham essays
            - Session ID for conversation continuity
        """
        # 🔄 Delegate to Bedrock client to do the heavy lifting
        # This single call handles the entire RAG pipeline
        result = self.kb_client.retrieve_and_generate(message, chat_history)
        
        # 📦 Package the result into a standardized ChatMessage format
        # This makes it easy for the frontend to display the response
        return ChatMessage(
            role=MessageRole.ASSISTANT,        # Mark this as an AI response
            content=result['response'],         # The actual AI-generated answer
            sources=result['sources'],          # Essay chunks used as sources
            session_id=result.get('session_id') # For conversation continuity
        )
    
    def chat_with_separate_steps(self, message: str, chat_history: List[ChatMessage] = None) -> RAGResponse:
        """
        Chat using separate retrieval and generation steps.
        
        This approach gives more control over the RAG pipeline:
        1. Retrieve relevant documents
        2. Prepare context
        3. Generate response
        
        Args:
            message: User message
            chat_history: Previous chat messages
            
        Returns:
            RAGResponse with detailed breakdown of each step
        """
        # Step 1: Retrieve relevant documents
        retrieval_result = self.kb_client.retrieve_documents(message, max_results=5)
        
        # Step 2: Prepare context from retrieved documents
        context = self._prepare_context(retrieval_result.sources)
        
        # Step 3: Generate response using context
        generation_result = self.llm_client.generate_response(message, context)
        
        # Step 4: Create response message
        response_message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=generation_result.response,
            sources=retrieval_result.sources
        )
        
        return RAGResponse(
            message=response_message,
            retrieval_result=retrieval_result,
            generation_result=generation_result,
            success=True
        )
    
    def _prepare_context(self, sources: List) -> str:
        """Prepare context string from retrieved sources."""
        if not sources:
            return ""
        
        context_parts = []
        for i, source in enumerate(sources[:3], 1):  # Use top 3 sources
            context_parts.append(f"Source {i}: {source.content}")
        
        return "\n\n".join(context_parts)
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status."""
        # Test Knowledge Base connection only
        kb_status = self.kb_client.test_connection()
        
        return {
            'knowledge_base': kb_status,
            'config': {
                'knowledge_base_id': self.config.knowledge_base_id,
                'model_id': self.config.llm_model_id,
                'region': self.config.aws_region
            }
        }


class ChatSessionManager:
    """Manages chat sessions and history."""
    
    def __init__(self):
        self.sessions = {}
    
    def add_message(self, session_id: str, message: ChatMessage):
        """Add message to session history."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append(message)
    
    def get_history(self, session_id: str, max_messages: int = 10) -> List[ChatMessage]:
        """Get chat history for session."""
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id][-max_messages:]
    
    def clear_session(self, session_id: str):
        """Clear session history."""
        if session_id in self.sessions:
            del self.sessions[session_id]