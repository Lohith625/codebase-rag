#!/usr/bin/env python3
"""
Test multi-stage retrieval system.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.retrieval.vector_store import FAISSVectorStore
from backend.retrieval.retriever import MultiStageRetriever
from backend.retrieval.search import CodeSearchEngine
from backend.parsing.chunker import CodeChunk
from backend.retrieval.indexer import Indexer
from backend.utils import get_logger

logger = get_logger(__name__)


# Simple embedding generator (same as before)
class SimpleEmbeddingGenerator:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def generate_embedding(self, text: str):
        if not text:
            return None
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = []
        for i in range(self.dimension):
            embedding.append(float(hash_bytes[i % len(hash_bytes)]) / 255.0)
        return embedding
    
    def generate_embeddings(self, texts, batch_size=32, show_progress=True):
        return [self.generate_embedding(t) for t in texts]
    
    def get_dimension(self):
        return self.dimension


def setup_test_index():
    """Create a test index with sample code."""
    logger.info("=" * 60)
    logger.info("SETUP: Creating Test Index")
    logger.info("=" * 60)
    
    # Sample code chunks
    chunks = [
        CodeChunk(
            content="""def authenticate_user(username, password):
    '''Authenticate user with username and password.'''
    user = db.get_user(username)
    if user and verify_password(password, user.password_hash):
        return user
    return None""",
            metadata={
                'type': 'function',
                'name': 'authenticate_user',
                'language': 'python',
                'file_path': 'auth/authentication.py',
                'start_line': 10,
                'end_line': 16,
                'content': 'def authenticate_user(username, password):\n    ...'
            }
        ),
        CodeChunk(
            content="""class UserManager:
    '''Manages user accounts and permissions.'''
    def __init__(self, db):
        self.db = db
    
    def create_user(self, username, email):
        return self.db.create(username=username, email=email)""",
            metadata={
                'type': 'class',
                'name': 'UserManager',
                'language': 'python',
                'file_path': 'auth/user_manager.py',
                'start_line': 5,
                'end_line': 11,
                'content': 'class UserManager:\n    ...'
            }
        ),
        CodeChunk(
            content="""def process_payment(amount, card_token):
    '''Process payment using stripe.'''
    stripe.api_key = settings.STRIPE_KEY
    charge = stripe.Charge.create(
        amount=amount,
        currency='usd',
        source=card_token
    )
    return charge""",
            metadata={
                'type': 'function',
                'name': 'process_payment',
                'language': 'python',
                'file_path': 'payments/stripe.py',
                'start_line': 20,
                'end_line': 28,
                'content': 'def process_payment(amount, card_token):\n    ...'
            }
        ),
        CodeChunk(
            content="""def send_email(to, subject, body):
    '''Send email notification.'''
    msg = Message(subject=subject, recipients=[to])
    msg.body = body
    mail.send(msg)
    logger.info(f'Email sent to {to}')""",
            metadata={
                'type': 'function',
                'name': 'send_email',
                'language': 'python',
                'file_path': 'notifications/email.py',
                'start_line': 15,
                'end_line': 20,
                'content': 'def send_email(to, subject, body):\n    ...'
            }
        ),
        CodeChunk(
            content="""import logging
from flask import Flask, request
from config import settings""",
            metadata={
                'type': 'import',
                'language': 'python',
                'file_path': 'app.py',
                'start_line': 1,
                'end_line': 3,
                'content': 'import logging\nfrom flask import Flask...'
            }
        )
    ]
    
    # Create embedding generator and vector store
    generator = SimpleEmbeddingGenerator(dimension=384)
    vector_store = FAISSVectorStore(dimension=384)
    
    # Index chunks
    indexer = Indexer(generator, vector_store)
    indexed = indexer.index_chunks(chunks)
    
    logger.info(f"✅ Indexed {indexed} chunks")
    
    return generator, vector_store


def test_basic_retrieval(generator, vector_store):
    """Test basic retrieval."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: Basic Retrieval")
    logger.info("=" * 60)
    
    retriever = MultiStageRetriever(
        vector_store=vector_store,
        embedding_generator=generator,
        top_k=5,
        top_n=3
    )
    
    query = "user authentication"
    logger.info(f"\nQuery: '{query}'")
    
    results = retriever.retrieve(query)
    
    logger.info(f"\n✅ Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        logger.info(f"\n  {i}. {metadata.get('name', 'N/A')} ({metadata.get('type')})")
        logger.info(f"     Score: {result.get('rerank_score', 0):.4f}")
        logger.info(f"     File: {metadata.get('file_path', 'N/A')}")
        logger.info(f"     Explanation: {result.get('relevance_explanation', 'N/A')}")


def test_filtered_search(generator, vector_store):
    """Test search with filters."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Filtered Search")
    logger.info("=" * 60)
    
    retriever = MultiStageRetriever(
        vector_store=vector_store,
        embedding_generator=generator,
        top_k=5,
        top_n=3
    )
    
    query = "payment processing"
    filters = {'type': 'function'}
    
    logger.info(f"\nQuery: '{query}'")
    logger.info(f"Filters: {filters}")
    
    results = retriever.retrieve(query, filters=filters)
    
    logger.info(f"\n✅ Found {len(results)} results (filtered):")
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        logger.info(f"  {i}. {metadata.get('name')} - {metadata.get('file_path')}")


def test_search_engine(generator, vector_store):
    """Test high-level search engine."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Code Search Engine")
    logger.info("=" * 60)
    
    search_engine = CodeSearchEngine(
        vector_store=vector_store,
        embedding_generator=generator
    )
    
    # Test different search types
    queries = [
        ("How is user authentication handled?", None, None),
        ("email notification", 'python', 'function'),
        ("payment", None, 'function'),
    ]
    
    for query, lang, code_type in queries:
        logger.info(f"\n{'─' * 60}")
        logger.info(f"Query: '{query}'")
        if lang:
            logger.info(f"Language: {lang}")
        if code_type:
            logger.info(f"Code Type: {code_type}")
        
        results = search_engine.search(query, language=lang, code_type=code_type)
        
        logger.info(f"\n✅ Results ({len(results)}):")
        for result in results:
            logger.info(f"\n  Rank {result['rank']}: {result['name']}")
            logger.info(f"    Type: {result['type']}")
            logger.info(f"    File: {result['file_name']} (lines {result['start_line']}-{result['end_line']})")
            logger.info(f"    Score: {result['score']:.4f}")
            logger.info(f"    Why: {result['explanation']}")


def main():
    """Run all tests."""
    logger.info("🚀 Starting Retrieval System Tests\n")
    
    # Setup
    generator, vector_store = setup_test_index()
    
    # Test 1: Basic retrieval
    test_basic_retrieval(generator, vector_store)
    
    # Test 2: Filtered search
    test_filtered_search(generator, vector_store)
    
    # Test 3: Search engine
    test_search_engine(generator, vector_store)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ All retrieval tests completed!")
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
