"""
Search Interface
High-level interface for code search.
"""

from typing import List, Dict, Optional
from pathlib import Path
from backend.retrieval.retriever import MultiStageRetriever
from backend.retrieval.embeddings import EmbeddingGenerator
from backend.retrieval.vector_store import VectorStore
from backend.utils import get_logger

logger = get_logger(__name__)


class CodeSearchEngine:
    """High-level code search interface."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator
    ):
        """
        Initialize search engine.
        
        Args:
            vector_store: Vector store with indexed code
            embedding_generator: Embedding generator
        """
        self.retriever = MultiStageRetriever(
            vector_store=vector_store,
            embedding_generator=embedding_generator,
            top_k=20,
            top_n=5
        )
        
        logger.info("CodeSearchEngine initialized")
    
    def search(
        self,
        query: str,
        language: Optional[str] = None,
        file_type: Optional[str] = None,
        code_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for code using natural language query.
        
        Args:
            query: Natural language query
            language: Filter by programming language (e.g., 'python')
            file_type: Filter by file extension (e.g., '.py')
            code_type: Filter by code type ('function', 'class', etc.)
        
        Returns:
            List of search results
        """
        # Build filters
        filters = {}
        if language:
            filters['language'] = language
        if file_type:
            filters['extension'] = file_type
        if code_type:
            filters['type'] = code_type
        
        logger.info(f"Searching: '{query}' with filters: {filters}")
        
        # Retrieve results
        results = self.retriever.retrieve(
            query=query,
            filters=filters if filters else None,
            context_window=3
        )
        
        # Format results for display
        formatted_results = self._format_results(results)
        
        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results
    
    def _format_results(self, results: List[Dict]) -> List[Dict]:
        """Format results for user-friendly display."""
        formatted = []
        
        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            
            formatted_result = {
                'rank': i,
                'score': result.get('rerank_score', result.get('score', 0)),
                'type': metadata.get('type', 'unknown'),
                'name': metadata.get('name', 'N/A'),
                'language': metadata.get('language', 'unknown'),
                'file_path': metadata.get('file_path', ''),
                'file_name': Path(metadata.get('file_path', '')).name if metadata.get('file_path') else 'N/A',
                'start_line': metadata.get('start_line', 0),
                'end_line': metadata.get('end_line', 0),
                'content': metadata.get('content', ''),
                'explanation': result.get('relevance_explanation', ''),
                'context': result.get('context', {})
            }
            
            formatted.append(formatted_result)
        
        return formatted
    
    def search_by_function_name(self, function_name: str) -> List[Dict]:
        """Search for specific function by name."""
        return self.search(
            query=f"function {function_name}",
            code_type='function'
        )
    
    def search_by_class_name(self, class_name: str) -> List[Dict]:
        """Search for specific class by name."""
        return self.search(
            query=f"class {class_name}",
            code_type='class'
        )
    
    def search_similar_code(self, code_snippet: str, language: str = None) -> List[Dict]:
        """Find code similar to given snippet."""
        return self.search(
            query=code_snippet,
            language=language
        )
