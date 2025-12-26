"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


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
    assert 'indexed_vectors' in data


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
