"""
Query Constructor
Parse and enhance user queries for better retrieval.
"""

import re
from typing import Dict, List, Optional
from backend.utils import get_logger

logger = get_logger(__name__)


class QueryConstructor:
    """Construct and enhance queries for code search."""
    
    def __init__(self):
        """Initialize query constructor."""
        self.code_patterns = {
            'function': r'\b(?:function|def|func|method)\s+(\w+)',
            'class': r'\b(?:class|struct|interface)\s+(\w+)',
            'variable': r'\b(?:var|let|const|variable)\s+(\w+)',
            'import': r'\b(?:import|require|include|from)\s+([\w.]+)',
        }
        logger.info("QueryConstructor initialized")
    
    def parse_query(self, query: str) -> Dict:
        """
        Parse user query to extract intent and entities.
        
        Args:
            query: User's natural language query
        
        Returns:
            Dictionary with parsed information
        """
        query_lower = query.lower()
        
        parsed = {
            'original_query': query,
            'intent': self._detect_intent(query_lower),
            'entities': self._extract_entities(query),
            'filters': self._suggest_filters(query_lower),
            'enhanced_query': self._enhance_query(query)
        }
        
        logger.debug(f"Parsed query: {parsed['intent']}")
        return parsed
    
    def _detect_intent(self, query: str) -> str:
        """Detect the intent of the query."""
        intent_keywords = {
            'search': ['find', 'search', 'locate', 'where is', 'show me'],
            'explain': ['explain', 'how does', 'what does', 'describe', 'tell me about'],
            'debug': ['debug', 'fix', 'error', 'bug', 'issue', 'problem'],
            'example': ['example', 'sample', 'demonstrate', 'show example'],
            'implement': ['how to', 'implement', 'create', 'build', 'make'],
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in query for keyword in keywords):
                return intent
        
        return 'search'  # Default intent
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract code entities from query."""
        entities = {
            'functions': [],
            'classes': [],
            'variables': [],
            'modules': []
        }
        
        # Extract function names
        for pattern_type, pattern in self.code_patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if pattern_type == 'function':
                entities['functions'].extend(matches)
            elif pattern_type == 'class':
                entities['classes'].extend(matches)
            elif pattern_type == 'variable':
                entities['variables'].extend(matches)
            elif pattern_type == 'import':
                entities['modules'].extend(matches)
        
        return entities
    
    def _suggest_filters(self, query: str) -> Dict:
        """Suggest metadata filters based on query."""
        filters = {}
        
        # Detect language
        languages = ['python', 'javascript', 'java', 'cpp', 'c', 'go', 'rust', 'typescript']
        for lang in languages:
            if lang in query:
                filters['language'] = lang
                break
        
        # Detect code type
        if any(word in query for word in ['function', 'def', 'method']):
            filters['type'] = 'function'
        elif any(word in query for word in ['class', 'struct']):
            filters['type'] = 'class'
        elif any(word in query for word in ['import', 'require']):
            filters['type'] = 'import'
        
        return filters
    
    def _enhance_query(self, query: str) -> str:
        """Enhance query with synonyms and expansions."""
        enhancements = {
            'auth': 'authentication authorization login',
            'db': 'database',
            'api': 'endpoint route handler',
            'ui': 'interface user-interface frontend',
            'test': 'testing unit-test',
        }
        
        enhanced = query
        for abbrev, expansion in enhancements.items():
            if abbrev in query.lower():
                enhanced = f"{query} {expansion}"
                break
        
        return enhanced
