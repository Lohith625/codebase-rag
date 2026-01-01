"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


# Mock the initialize_system function before importing app
def mock_initialize_system():
    """Mock system initialization for testing."""
    from backend.retrieval.vector_store import FAISSVectorStore
    from backend.retrieval.embeddings import EmbeddingGenerator
    from backend.retrieval.search import CodeSearchEngine
    from backend.llm.rag_pipeline import RAGPipeline
    from backend.llm.llm_client import MockLLMClient
    from backend.retrieval.indexer import Indexer
    import backend.api.main as main_module
    
    # Simple embedding for testing
    class SimpleEmbedding:
        def __init__(self):
            self.dimension = 384
        def get_dimension(self):
            return 384
        def generate_embedding(self, text):
            import hashlib
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            return [float(hash_bytes[i % len(hash_bytes)]) / 255.0 for i in range(384)]
        def generate_embeddings(self, texts, batch_size=32, show_progress=True):
            return [self.generate_embedding(t) for t in texts]
    
    embedding_generator = SimpleEmbedding()
    vector_store = FAISSVectorStore(dimension=384)
    search_engine = CodeSearchEngine(vector_store, embedding_generator)
    llm_client = MockLLMClient()
    rag_pipeline = RAGPipeline(search_engine, llm_client, top_k=5)
    indexer = Indexer(embedding_generator, vector_store)
    
    # Set global variables
    main_module.vector_store = vector_store
    main_module.embedding_generator = embedding_generator
    main_module.search_engine = search_engine
    main_module.rag_pipeline = rag_pipeline
    main_module.indexer = indexer


# Patch before importing app
import backend.api.main
backend.api.main.initialize_system = mock_initialize_system

from backend.api.main import app

client = TestClient(app)

# Initialize system for tests
mock_initialize_system()


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert 'version' in data


def test_stats_endpoint():
    """Test stats endpoint."""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert 'indexed_vectors' in data or 'status' in data


def test_query_endpoint():
    """Test query endpoint."""
    payload = {
        "query": "test query",
        "language": "python",
        "top_k": 3
    }
    
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 'answer' in data
    assert 'sources' in data


def test_explain_endpoint():
    """Test explain endpoint."""
    payload = {
        "code": "def test(): pass",
        "language": "python"
    }
    
    response = client.post("/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 'explanation' in data
