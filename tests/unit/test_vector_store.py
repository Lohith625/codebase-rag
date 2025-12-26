"""
Unit tests for vector store.
"""

import pytest
import numpy as np
from backend.retrieval.vector_store import FAISSVectorStore


def test_faiss_initialization():
    """Test FAISS vector store initialization."""
    store = FAISSVectorStore(dimension=384)
    
    assert store.dimension == 384
    assert store.index.ntotal == 0


def test_add_vectors():
    """Test adding vectors to store."""
    store = FAISSVectorStore(dimension=384)
    
    # Create dummy vectors
    vectors = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
    metadata = [
        {'id': '1', 'type': 'function'},
        {'id': '2', 'type': 'class'},
        {'id': '3', 'type': 'import'}
    ]
    ids = ['chunk_1', 'chunk_2', 'chunk_3']
    
    store.add_vectors(vectors, metadata, ids)
    
    assert store.index.ntotal == 3
    assert len(store.metadata_store) == 3


def test_search():
    """Test vector search."""
    store = FAISSVectorStore(dimension=384)
    
    # Add vectors
    vectors = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
    metadata = [
        {'id': '1', 'type': 'function', 'name': 'test1'},
        {'id': '2', 'type': 'class', 'name': 'test2'},
        {'id': '3', 'type': 'import', 'name': 'test3'}
    ]
    
    store.add_vectors(vectors, metadata)
    
    # Search
    query_vector = [0.15] * 384
    results = store.search(query_vector, k=2)
    
    assert len(results) == 2
    assert 'metadata' in results[0]
    assert 'score' in results[0]


def test_search_with_filter():
    """Test filtered search."""
    store = FAISSVectorStore(dimension=384)
    
    vectors = [[0.1] * 384, [0.2] * 384]
    metadata = [
        {'type': 'function', 'language': 'python'},
        {'type': 'class', 'language': 'javascript'}
    ]
    
    store.add_vectors(vectors, metadata)
    
    # Search with filter
    query_vector = [0.15] * 384
    results = store.search(query_vector, k=5, filter_dict={'language': 'python'})
    
    assert len(results) == 1
    assert results[0]['metadata']['language'] == 'python'


def test_get_stats():
    """Test getting store statistics."""
    store = FAISSVectorStore(dimension=384)
    
    vectors = [[0.1] * 384, [0.2] * 384]
    metadata = [{'id': '1'}, {'id': '2'}]
    
    store.add_vectors(vectors, metadata)
    
    stats = store.get_stats()
    
    assert stats['total_vectors'] == 2
    assert stats['dimension'] == 384
