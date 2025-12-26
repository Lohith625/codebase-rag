"""
Advanced Search Features
Additional search capabilities.
"""

from typing import List, Dict, Optional
from backend.utils import get_logger

logger = get_logger(__name__)


class AdvancedSearch:
    """Advanced search features."""
    
    def __init__(self, search_engine):
        self.search_engine = search_engine
        logger.info("AdvancedSearch initialized")
    
    def search_by_complexity(
        self,
        query: str,
        min_complexity: int = 0,
        max_complexity: int = 100
    ) -> List[Dict]:
        """
        Search code by complexity range.
        
        Args:
            query: Search query
            min_complexity: Minimum complexity score
            max_complexity: Maximum complexity score
        
        Returns:
            Filtered results
        """
        results = self.search_engine.search(query)
        
        # Filter by complexity if available
        filtered = []
        for result in results:
            complexity = result.get('metadata', {}).get('complexity', {})
            score = complexity.get('cyclomatic_complexity', 0)
            
            if min_complexity <= score <= max_complexity:
                filtered.append(result)
        
        return filtered
    
    def search_recent(
        self,
        query: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Search recently modified code.
        
        Args:
            query: Search query
            days: Consider files modified within N days
        
        Returns:
            Filtered results
        """
        from datetime import datetime, timedelta
        
        results = self.search_engine.search(query)
        cutoff = datetime.now() - timedelta(days=days)
        
        # Filter by modification date
        filtered = []
        for result in results:
            modified = result.get('metadata', {}).get('modified_at')
            if modified:
                mod_date = datetime.fromisoformat(modified)
                if mod_date >= cutoff:
                    filtered.append(result)
        
        return filtered
    
    def search_by_author(
        self,
        query: str,
        author: str
    ) -> List[Dict]:
        """
        Search code by author.
        
        Args:
            query: Search query
            author: Author name/email
        
        Returns:
            Filtered results
        """
        results = self.search_engine.search(query)
        
        # Filter by author
        filtered = [
            r for r in results
            if author.lower() in r.get('metadata', {}).get('author', '').lower()
        ]
        
        return filtered
    
    def fuzzy_search(
        self,
        query: str,
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Fuzzy search with spelling tolerance.
        
        Args:
            query: Search query (may have typos)
            threshold: Similarity threshold
        
        Returns:
            Results with fuzzy matching
        """
        # Basic implementation - can be enhanced with libraries like fuzzywuzzy
        results = self.search_engine.search(query)
        return results  # TODO: Add actual fuzzy matching
