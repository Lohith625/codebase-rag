"""
Integration tests for RAG pipeline.
"""

import pytest
from backend.retrieval.vector_store import FAISSVectorStore
from backend.retrieval.search import CodeSearchEngine
from backend.llm.rag_pipeline import RAGPipeline
from backend.llm.llm_client import MockLLMClient
from backend.parsing.chunker import CodeChunk
from backend.retrieval.indexer import Indexer


class SimpleEmbedding:
    """Simple embedding for testing."""
    def __init__(self):
        self.dimension = 384
    
    def generate_embedding(self, text):
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        return [float(hash_bytes[i % len(hash_bytes)]) / 255.0 for i in range(384)]
    
    def generate_embeddings(self, texts, batch_size=32, show_progress=True):
        return [self.generate_embedding(t) for t in texts]
    
    def get_dimension(self):
        return 384


@pytest.fixture
def setup_system():
    """Setup test system."""
    embedding_gen = SimpleEmbedding()
    vector_store = FAISSVectorStore(dimension=384)
    
    # Index sample code
    chunks = [
        CodeChunk(
            content="def authenticate(user, password): return verify(user, password)",
            metadata={'type': 'function', 'name': 'authenticate', 'language': 'python'}
        )
    ]
    
    indexer = Indexer(embedding_gen, vector_store)
    indexer.index_chunks(chunks)
    
    search_engine = CodeSearchEngine(vector_store, embedding_gen)
    llm_client = MockLLMClient()
    pipeline = RAGPipeline(search_engine, llm_client, top_k=3)
    
    return pipeline


def test_full_query_pipeline(setup_system):
    """Test complete query pipeline."""
    pipeline = setup_system
    
    response = pipeline.query("How does authentication work?")
    
    assert 'answer' in response
    assert 'sources' in response
    assert 'num_sources' in response
    assert response['num_sources'] >= 0


def test_query_with_filters(setup_system):
    """Test query with language filter."""
    pipeline = setup_system
    
    response = pipeline.query("authentication", language="python")
    
    assert 'answer' in response
    assert 'query_info' in response


def test_explain_code(setup_system):
    """Test code explanation."""
    pipeline = setup_system
    
    code = "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
    explanation = pipeline.explain_code(code, "python")
    
    assert isinstance(explanation, str)
    assert len(explanation) > 0
