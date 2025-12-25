#!/usr/bin/env python3
"""
Test LLM integration and RAG pipeline.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.retrieval.vector_store import FAISSVectorStore
from backend.retrieval.search import CodeSearchEngine
from backend.llm.rag_pipeline import RAGPipeline
from backend.llm.llm_client import MockLLMClient
from backend.llm.query_constructor import QueryConstructor
from backend.parsing.chunker import CodeChunk
from backend.retrieval.indexer import Indexer
from backend.utils import get_logger

logger = get_logger(__name__)


# Simple embedding generator
class SimpleEmbeddingGenerator:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def generate_embedding(self, text: str):
        if not text:
            return None
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        return [float(hash_bytes[i % len(hash_bytes)]) / 255.0 for i in range(self.dimension)]
    
    def generate_embeddings(self, texts, batch_size=32, show_progress=True):
        return [self.generate_embedding(t) for t in texts]
    
    def get_dimension(self):
        return self.dimension


def setup_test_system():
    """Setup test system with sample code."""
    logger.info("=" * 60)
    logger.info("SETUP: Creating Test System")
    logger.info("=" * 60)
    
    # Sample code chunks
    chunks = [
        CodeChunk(
            content="""def authenticate_user(username, password):
    '''Authenticate user credentials.'''
    user = database.get_user(username)
    if user and verify_password(password, user.password_hash):
        session = create_session(user)
        return session
    return None""",
            metadata={
                'type': 'function',
                'name': 'authenticate_user',
                'language': 'python',
                'file_path': 'auth/authentication.py',
                'start_line': 10,
                'end_line': 17,
                'content': 'def authenticate_user(username, password): ...'
            }
        ),
        CodeChunk(
            content="""def send_notification(user_id, message, channel='email'):
    '''Send notification to user.'''
    user = get_user(user_id)
    if channel == 'email':
        send_email(user.email, message)
    elif channel == 'sms':
        send_sms(user.phone, message)
    log_notification(user_id, channel, message)""",
            metadata={
                'type': 'function',
                'name': 'send_notification',
                'language': 'python',
                'file_path': 'notifications/sender.py',
                'start_line': 25,
                'end_line': 32,
                'content': 'def send_notification(user_id, message, channel): ...'
            }
        )
    ]
    
    # Setup vector store and index
    generator = SimpleEmbeddingGenerator()
    vector_store = FAISSVectorStore(dimension=384)
    indexer = Indexer(generator, vector_store)
    indexer.index_chunks(chunks)
    
    # Create search engine
    search_engine = CodeSearchEngine(vector_store, generator)
    
    logger.info("✅ Test system ready")
    return search_engine


def test_query_constructor():
    """Test query parsing."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: Query Constructor")
    logger.info("=" * 60)
    
    constructor = QueryConstructor()
    
    queries = [
        "How does user authentication work?",
        "Find the login function in Python",
        "Explain the send_email method",
        "Debug authentication error"
    ]
    
    for query in queries:
        logger.info(f"\nQuery: '{query}'")
        parsed = constructor.parse_query(query)
        logger.info(f"  Intent: {parsed['intent']}")
        logger.info(f"  Filters: {parsed['filters']}")
        logger.info(f"  Enhanced: {parsed['enhanced_query'][:60]}...")


def test_rag_pipeline(search_engine):
    """Test complete RAG pipeline."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: RAG Pipeline")
    logger.info("=" * 60)
    
    # Use mock LLM for testing
    llm_client = MockLLMClient()
    pipeline = RAGPipeline(search_engine, llm_client, top_k=3)
    
    queries = [
        "How is user authentication handled?",
        "How do I send notifications to users?",
        "Explain the authentication process"
    ]
    
    for query in queries:
        logger.info(f"\n{'─' * 60}")
        logger.info(f"Query: '{query}'")
        
        response = pipeline.query(query, include_context=False)
        
        logger.info(f"\n✅ Response Generated")
        logger.info(f"Intent: {response['query_info']['intent']}")
        logger.info(f"Sources: {response['num_sources']}")
        
        logger.info(f"\nAnswer:\n{response['answer'][:200]}...")
        
        logger.info(f"\nSources:")
        for i, source in enumerate(response['sources'], 1):
            logger.info(f"  {i}. {source['name']} ({source['file']}, lines {source['lines']})")


def main():
    """Run all tests."""
    logger.info("🚀 Starting LLM Integration Tests\n")
    
    # Setup
    search_engine = setup_test_system()
    
    # Test 1: Query Constructor
    test_query_constructor()
    
    # Test 2: RAG Pipeline
    test_rag_pipeline(search_engine)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ All LLM tests completed!")
    logger.info("=" * 60)
    logger.info("\nNote: Using MockLLMClient for testing.")
    logger.info("In production, use GeminiClient or OpenAIClient with real API keys.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
