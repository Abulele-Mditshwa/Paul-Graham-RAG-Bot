"""
Data Ingestion Service - Shows how data would be ingested into Knowledge Base.

Note: This is for demonstration purposes. The Knowledge Base is already created
and populated, but this shows how the ingestion process would work.
"""

import json
import boto3
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from config import Config


class DataIngestionService:
    """
    Service for ingesting data into AWS Bedrock Knowledge Base.
    
    This demonstrates the ingestion pipeline:
    1. Document preprocessing
    2. Chunking strategies
    3. Embedding generation (handled by Bedrock)
    4. Vector storage in OpenSearch
    """
    
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize AWS clients
        session = boto3.Session(
            region_name=config.aws_region,
            profile_name=config.aws_profile
        )
        
        self.bedrock_agent = session.client('bedrock-agent')
        self.s3_client = session.client('s3')
    
    def start_ingestion_job(self, data_source_id: str) -> Dict[str, Any]:
        """
        Start an ingestion job for the Knowledge Base.
        
        Args:
            data_source_id: ID of the data source to ingest
            
        Returns:
            Ingestion job details
        """
        try:
            response = self.bedrock_agent.start_ingestion_job(
                knowledgeBaseId=self.config.knowledge_base_id,
                dataSourceId=data_source_id,
                description="Ingestion job started via RAG service"
            )
            
            return {
                'job_id': response['ingestionJob']['ingestionJobId'],
                'status': response['ingestionJob']['status'],
                'started_at': response['ingestionJob']['startedAt'],
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def get_ingestion_job_status(self, job_id: str, data_source_id: str) -> Dict[str, Any]:
        """Get status of an ingestion job."""
        try:
            response = self.bedrock_agent.get_ingestion_job(
                knowledgeBaseId=self.config.knowledge_base_id,
                dataSourceId=data_source_id,
                ingestionJobId=job_id
            )
            
            job = response['ingestionJob']
            return {
                'job_id': job['ingestionJobId'],
                'status': job['status'],
                'started_at': job.get('startedAt'),
                'updated_at': job.get('updatedAt'),
                'statistics': job.get('statistics', {}),
                'failure_reasons': job.get('failureReasons', []),
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def list_data_sources(self) -> Dict[str, Any]:
        """List all data sources for the Knowledge Base."""
        try:
            response = self.bedrock_agent.list_data_sources(
                knowledgeBaseId=self.config.knowledge_base_id
            )
            
            data_sources = []
            for ds in response.get('dataSourceSummaries', []):
                data_sources.append({
                    'data_source_id': ds['dataSourceId'],
                    'name': ds['name'],
                    'status': ds['status'],
                    'description': ds.get('description', ''),
                    'updated_at': ds.get('updatedAt')
                })
            
            return {
                'data_sources': data_sources,
                'total_count': len(data_sources),
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """Get detailed information about the Knowledge Base."""
        try:
            response = self.bedrock_agent.get_knowledge_base(
                knowledgeBaseId=self.config.knowledge_base_id
            )
            
            kb = response['knowledgeBase']
            return {
                'knowledge_base_id': kb['knowledgeBaseId'],
                'name': kb['name'],
                'description': kb.get('description', ''),
                'status': kb['status'],
                'role_arn': kb['roleArn'],
                'storage_configuration': kb['storageConfiguration'],
                'knowledge_base_configuration': kb['knowledgeBaseConfiguration'],
                'created_at': kb.get('createdAt'),
                'updated_at': kb.get('updatedAt'),
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }


class DocumentProcessor:
    """
    Document processing utilities for ingestion.
    
    This shows different chunking strategies that could be used
    before ingesting documents into the Knowledge Base.
    """
    
    @staticmethod
    def chunk_by_sentences(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Chunk text by sentences with overlap.
        
        Args:
            text: Input text to chunk
            max_chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        import re
        
        # Split by sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed max size, start new chunk
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                if overlap > 0 and len(current_chunk) > overlap:
                    current_chunk = current_chunk[-overlap:] + " " + sentence
                else:
                    current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @staticmethod
    def chunk_by_paragraphs(text: str, max_chunk_size: int = 1500) -> List[str]:
        """
        Chunk text by paragraphs.
        
        Args:
            text: Input text to chunk
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, Any]:
        """Extract metadata from a document file."""
        path = Path(file_path)
        
        return {
            'filename': path.name,
            'file_extension': path.suffix,
            'file_size': path.stat().st_size if path.exists() else 0,
            'created_at': time.ctime(path.stat().st_ctime) if path.exists() else None,
            'modified_at': time.ctime(path.stat().st_mtime) if path.exists() else None
        }