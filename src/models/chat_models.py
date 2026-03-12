"""
Data models for chat functionality.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class MessageRole(Enum):
    """Enumeration for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Source:
    """Represents a source document with metadata."""
    content: str
    source_uri: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
    
    def get_display_content(self, max_length: int = 200) -> str:
        """Get truncated content for display."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."


@dataclass
class ChatMessage:
    """Represents a chat message with optional sources."""
    role: MessageRole
    content: str
    sources: Optional[List[Source]] = None
    timestamp: Optional[str] = None
    session_id: Optional[str] = None
    
    @property
    def role_str(self) -> str:
        """Get role as string for compatibility."""
        return self.role.value


@dataclass
class RetrievalResult:
    """Result from document retrieval."""
    query: str
    sources: List[Source]
    total_results: int
    retrieval_time_ms: float


@dataclass
class GenerationResult:
    """Result from text generation."""
    response: str
    model_used: str
    generation_time_ms: float
    token_count: Optional[int] = None


@dataclass
class RAGResponse:
    """Complete RAG response with retrieval and generation results."""
    message: ChatMessage
    retrieval_result: RetrievalResult
    generation_result: GenerationResult
    success: bool
    error_message: Optional[str] = None