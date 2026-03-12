"""
OpenSearch Serverless client for direct vector operations.
This shows how the Knowledge Base connects to OpenSearch for vector storage.
"""

import json
import boto3
from typing import List, Dict, Any, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from config import Config


class OpenSearchServerlessClient:
    """
    Client for OpenSearch Serverless operations.
    
    This demonstrates how AWS Bedrock Knowledge Base uses OpenSearch
    for vector storage and retrieval behind the scenes.
    """
    
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize AWS session
        session = boto3.Session(
            region_name=config.aws_region,
            profile_name=config.aws_profile
        )
        
        # Get credentials for OpenSearch authentication
        credentials = session.get_credentials()
        self.awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            config.aws_region,
            'aoss',  # OpenSearch Serverless service
            session_token=credentials.token
        )
        
        # Extract host from collection ARN
        # ARN format: arn:aws:aoss:region:account:collection/collection-id
        collection_id = config.opensearch_collection_arn.split('/')[-1]
        self.host = f"{collection_id}.{config.aws_region}.aoss.amazonaws.com"
        
        # Initialize OpenSearch client
        self.client = OpenSearch(
            hosts=[{'host': self.host, 'port': 443}],
            http_auth=self.awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30
        )
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the OpenSearch collection."""
        try:
            # Get cluster health
            health = self.client.cluster.health()
            
            # Get indices information
            indices = self.client.indices.get_alias("*")
            
            return {
                'collection_name': self.config.opensearch_collection_name,
                'collection_arn': self.config.opensearch_collection_arn,
                'host': self.host,
                'cluster_health': health,
                'indices': list(indices.keys()) if indices else [],
                'success': True
            }
            
        except Exception as e:
            return {
                'collection_name': self.config.opensearch_collection_name,
                'error': str(e),
                'success': False
            }
    
    def search_vectors(self, query_vector: List[float], index_name: str = None, size: int = 5) -> Dict[str, Any]:
        """
        Perform vector similarity search.
        
        Note: This is for demonstration purposes. In practice, the Knowledge Base
        handles vector search automatically.
        
        Args:
            query_vector: Query vector for similarity search
            index_name: Index to search (if None, searches all indices)
            size: Number of results to return
            
        Returns:
            Search results with scores and documents
        """
        try:
            # If no specific index, try to find the bedrock index
            if not index_name:
                indices = self.client.indices.get_alias("*")
                bedrock_indices = [idx for idx in indices.keys() if 'bedrock' in idx.lower()]
                if bedrock_indices:
                    index_name = bedrock_indices[0]
                else:
                    return {'error': 'No suitable index found', 'success': False}
            
            # Perform vector search
            search_body = {
                "size": size,
                "query": {
                    "knn": {
                        "vector_field": {  # This field name may vary
                            "vector": query_vector,
                            "k": size
                        }
                    }
                }
            }
            
            response = self.client.search(
                index=index_name,
                body=search_body
            )
            
            return {
                'hits': response.get('hits', {}),
                'took': response.get('took'),
                'total': response.get('hits', {}).get('total', {}),
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def get_document_by_id(self, doc_id: str, index_name: str) -> Dict[str, Any]:
        """Get a specific document by ID."""
        try:
            response = self.client.get(
                index=index_name,
                id=doc_id
            )
            
            return {
                'document': response.get('_source', {}),
                'found': response.get('found', False),
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def list_indices(self) -> Dict[str, Any]:
        """List all indices in the collection."""
        try:
            indices = self.client.indices.get_alias("*")
            
            index_info = {}
            for index_name in indices.keys():
                try:
                    stats = self.client.indices.stats(index=index_name)
                    index_info[index_name] = {
                        'doc_count': stats['indices'][index_name]['total']['docs']['count'],
                        'size_bytes': stats['indices'][index_name]['total']['store']['size_in_bytes']
                    }
                except:
                    index_info[index_name] = {'error': 'Could not get stats'}
            
            return {
                'indices': index_info,
                'total_indices': len(indices),
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }