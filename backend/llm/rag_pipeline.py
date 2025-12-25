"""
RAG Pipeline
Complete Retrieval-Augmented Generation pipeline.
"""

from typing import List, Dict, Optional
from backend.retrieval.search import CodeSearchEngine
from backend.llm.query_constructor import QueryConstructor
from backend.llm.prompts import create_search_prompt, create_explanation_prompt, create_debug_prompt
from backend.llm.llm_client import LLMClient
from backend.utils import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """Complete RAG pipeline for code assistance."""
    
    def __init__(
        self,
        search_engine: CodeSearchEngine,
        llm_client: LLMClient,
        top_k: int = 5
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            search_engine: Code search engine
            llm_client: LLM client
            top_k: Number of results to retrieve
        """
        self.search_engine = search_engine
        self.llm_client = llm_client
        self.query_constructor = QueryConstructor()
        self.top_k = top_k
        
        logger.info("RAGPipeline initialized")
    
    def query(
        self,
        user_query: str,
        language: Optional[str] = None,
        include_context: bool = True
    ) -> Dict:
        """
        Process user query through complete RAG pipeline.
        
        Args:
            user_query: User's natural language question
            language: Filter by programming language
            include_context: Include retrieved context in response
        
        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Processing query: '{user_query[:50]}...'")
        
        # Step 1: Parse and enhance query
        parsed_query = self.query_constructor.parse_query(user_query)
        logger.debug(f"Query intent: {parsed_query['intent']}")
        
        # Step 2: Retrieve relevant code
        filters = parsed_query.get('filters', {})
        if language:
            filters['language'] = language
        
        search_results = self.search_engine.search(
            query=parsed_query['enhanced_query'],
            language=filters.get('language'),
            code_type=filters.get('type')
        )
        
        logger.info(f"Retrieved {len(search_results)} code snippets")
        
        # Handle no results case
        if not search_results:
            return {
                'answer': "I couldn't find any relevant code for your query. Please try rephrasing or being more specific.",
                'sources': [],
                'query_info': parsed_query,
                'num_sources': 0
            }
        
        # Step 3: Create prompt with context
        prompt = create_search_prompt(user_query, search_results)
        
        # Step 4: Generate response with LLM
        logger.info("Generating LLM response...")
        answer = self.llm_client.generate(prompt, temperature=0.1, max_tokens=2048)
        
        # Step 5: Format response
        response = {
            'answer': answer,
            'sources': self._format_sources(search_results),
            'query_info': {
                'original': user_query,
                'intent': parsed_query['intent'],
                'filters_applied': filters
            },
            'num_sources': len(search_results)
        }
        
        if include_context:
            response['context'] = search_results
        
        logger.info("Query processed successfully")
        return response
    
    def explain_code(self, code: str, language: str = 'python') -> str:
        """
        Explain what a code snippet does.
        
        Args:
            code: Code to explain
            language: Programming language
        
        Returns:
            Explanation
        """
        prompt = create_explanation_prompt(code, language)
        return self.llm_client.generate(prompt)
    
    def debug_help(self, error_message: str, language: Optional[str] = None) -> Dict:
        """
        Help debug an error.
        
        Args:
            error_message: Error message or description
            language: Programming language
        
        Returns:
            Debug assistance
        """
        # Search for related code
        search_results = self.search_engine.search(
            query=error_message,
            language=language
        )
        
        # Generate debug help
        prompt = create_debug_prompt(error_message, search_results)
        answer = self.llm_client.generate(prompt)
        
        return {
            'analysis': answer,
            'related_code': self._format_sources(search_results)
        }
    
    def _format_sources(self, results: List[Dict]) -> List[Dict]:
        """Format source references for display."""
        sources = []
        
        for result in results:
            source = {
                'file': result.get('file_name', 'N/A'),
                'path': result.get('file_path', ''),
                'type': result.get('type', 'code'),
                'name': result.get('name', 'N/A'),
                'lines': f"{result.get('start_line', '?')}-{result.get('end_line', '?')}",
                'language': result.get('language', 'N/A'),
                'relevance': result.get('score', 0)
            }
            sources.append(source)
        
        return sources
