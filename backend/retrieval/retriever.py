"""
Multi-Stage Retrieval System
Implements advanced retrieval with filtering, re-ranking, and context expansion.
"""

from typing import List, Dict, Optional, Tuple
from backend.retrieval.vector_store import VectorStore
from backend.retrieval.embeddings import EmbeddingGenerator
from backend.utils import get_logger

logger = get_logger(__name__)


class MultiStageRetriever:
    """Multi-stage retrieval with filtering and re-ranking."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator,
        top_k: int = 20,
        top_n: int = 5
    ):
        """
        Initialize multi-stage retriever.
        
        Args:
            vector_store: Vector store for similarity search
            embedding_generator: Embedding generator for queries
            top_k: Number of candidates to retrieve initially
            top_n: Number of final results to return
        """
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.top_k = top_k
        self.top_n = top_n
        
        logger.info(f"MultiStageRetriever initialized (top_k={top_k}, top_n={top_n})")
    
    def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None,
        context_window: int = 3
    ) -> List[Dict]:
        """
        Retrieve relevant code chunks using multi-stage approach.
        
        Args:
            query: Search query
            filters: Metadata filters (e.g., {'language': 'python'})
            context_window: Number of surrounding chunks to include
        
        Returns:
            List of retrieved results with metadata and context
        """
        logger.info(f"Retrieving results for query: '{query[:50]}...'")
        
        # Stage 1: Vector Search
        candidates = self._vector_search(query, filters)
        
        if not candidates:
            logger.warning("No candidates found")
            return []
        
        logger.info(f"Stage 1 (Vector Search): {len(candidates)} candidates")
        
        # Stage 2: Re-ranking
        reranked = self._rerank_results(query, candidates)
        logger.info(f"Stage 2 (Re-ranking): Top {len(reranked)} results")
        
        # Stage 3: Contextual Expansion
        expanded = self._expand_context(reranked, context_window)
        logger.info(f"Stage 3 (Context Expansion): Added context to {len(expanded)} results")
        
        return expanded[:self.top_n]
    
    def _vector_search(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Stage 1: Perform vector similarity search.
        
        Args:
            query: Search query
            filters: Metadata filters
        
        Returns:
            List of candidate results
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return []
        
        # Search vector store
        results = self.vector_store.search(
            query_vector=query_embedding,
            k=self.top_k,
            filter_dict=filters
        )
        
        return results
    
    def _rerank_results(
        self,
        query: str,
        candidates: List[Dict]
    ) -> List[Dict]:
        """
        Stage 2: Re-rank results by relevance.
        
        Simple re-ranking based on:
        - Vector similarity score
        - Query term matching
        - Code type preference (functions > classes > imports)
        
        Args:
            query: Search query
            candidates: Candidate results from vector search
        
        Returns:
            Re-ranked results
        """
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        for result in candidates:
            metadata = result.get('metadata', {})
            content = metadata.get('content', '')
            
            # Base score (from vector similarity - lower is better for L2 distance)
            base_score = 1.0 / (1.0 + result.get('score', 0))
            
            # Boost for query term matches in content
            content_lower = content.lower() if content else ''
            term_matches = sum(1 for term in query_terms if term in content_lower)
            term_boost = term_matches * 0.1
            
            # Boost for code type
            code_type = metadata.get('type', '')
            type_boost = {
                'function': 0.3,
                'class': 0.2,
                'module_level': 0.1,
                'import': 0.05
            }.get(code_type, 0.0)
            
            # Boost for name matching
            name = metadata.get('name', '')
            name_boost = 0.2 if name and any(term in name.lower() for term in query_terms) else 0.0
            
            # Calculate final score
            final_score = base_score + term_boost + type_boost + name_boost
            result['rerank_score'] = final_score
        
        # Sort by rerank score (higher is better)
        reranked = sorted(candidates, key=lambda x: x.get('rerank_score', 0), reverse=True)
        
        return reranked
    
    def _expand_context(
        self,
        results: List[Dict],
        context_window: int = 3
    ) -> List[Dict]:
        """
        Stage 3: Add surrounding context to results.
        
        Args:
            results: Results to expand
            context_window: Number of lines to add before/after
        
        Returns:
            Results with expanded context
        """
        for result in results:
            metadata = result.get('metadata', {})
            
            # Add context information
            result['context'] = {
                'before_lines': context_window,
                'after_lines': context_window,
                'file_path': metadata.get('file_path', ''),
                'start_line': metadata.get('start_line', 0),
                'end_line': metadata.get('end_line', 0)
            }
            
            # Add relevance explanation
            result['relevance_explanation'] = self._explain_relevance(result, metadata)
        
        return results
    
    def _explain_relevance(self, result: Dict, metadata: Dict) -> str:
        """Generate explanation for why this result is relevant."""
        explanations = []
        
        code_type = metadata.get('type', 'code')
        name = metadata.get('name')
        
        if name:
            explanations.append(f"{code_type.capitalize()} '{name}'")
        else:
            explanations.append(f"{code_type.capitalize()} block")
        
        language = metadata.get('language')
        if language:
            explanations.append(f"in {language}")
        
        file_path = metadata.get('file_path', '')
        if file_path:
            from pathlib import Path
            file_name = Path(file_path).name
            explanations.append(f"from {file_name}")
        
        return " ".join(explanations)


class HybridRetriever(MultiStageRetriever):
    """Hybrid retrieval combining multiple strategies."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator,
        top_k: int = 20,
        top_n: int = 5,
        use_keyword_search: bool = True
    ):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_store: Vector store
            embedding_generator: Embedding generator
            top_k: Initial candidates
            top_n: Final results
            use_keyword_search: Also use keyword-based search
        """
        super().__init__(vector_store, embedding_generator, top_k, top_n)
        self.use_keyword_search = use_keyword_search
    
    def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None,
        context_window: int = 3
    ) -> List[Dict]:
        """
        Hybrid retrieval combining vector and keyword search.
        
        Args:
            query: Search query
            filters: Metadata filters
            context_window: Context lines
        
        Returns:
            Combined and ranked results
        """
        logger.info(f"Hybrid retrieval for: '{query[:50]}...'")
        
        # Get vector search results
        vector_results = super().retrieve(query, filters, context_window)
        
        # Optionally combine with keyword search
        if self.use_keyword_search:
            keyword_results = self._keyword_search(query, filters)
            
            # Merge results (deduplicate by chunk_id)
            seen_ids = set()
            merged_results = []
            
            for result in vector_results + keyword_results:
                chunk_id = result.get('metadata', {}).get('chunk_id')
                if chunk_id and chunk_id not in seen_ids:
                    seen_ids.add(chunk_id)
                    merged_results.append(result)
            
            logger.info(f"Merged {len(merged_results)} unique results")
            return merged_results[:self.top_n]
        
        return vector_results
    
    def _keyword_search(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Simple keyword-based search as fallback.
        
        Args:
            query: Search query
            filters: Metadata filters
        
        Returns:
            Keyword search results
        """
        # This would search through stored metadata
        # For now, returns empty (vector search is primary)
        logger.debug("Keyword search not yet implemented")
        return []
