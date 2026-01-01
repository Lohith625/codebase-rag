#!/usr/bin/env python3
"""
Test the FastAPI endpoints.
"""

import sys
from pathlib import Path
import requests
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.utils import get_logger

logger = get_logger(__name__)

API_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint."""
    logger.info("=" * 60)
    logger.info("TEST 1: Health Check")
    logger.info("=" * 60)

    response = requests.get(f"{API_URL}/health")

    if response.status_code == 200:
        data = response.json()
        logger.info(f"✅ Health check passed")
        logger.info(f"   Status: {data['status']}")
        logger.info(f"   Version: {data['version']}")
        logger.info(f"   Index stats: {data['index_stats']}")
    else:
        logger.error(f"❌ Health check failed: {response.status_code}")


def test_query():
    """Test query endpoint."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Query Endpoint")
    logger.info("=" * 60)

    query_data = {
        "query": "How does authentication work?",
        "language": "python",
        "top_k": 3,
        "include_context": False,
    }

    logger.info(f"\nQuery: {query_data['query']}")

    response = requests.post(f"{API_URL}/query", json=query_data)

    if response.status_code == 200:
        data = response.json()
        logger.info(f"✅ Query successful")
        logger.info(f"   Processing time: {data['processing_time']:.2f}s")
        logger.info(f"   Sources found: {data['num_sources']}")
        logger.info(f"\n   Answer: {data['answer'][:150]}...")
    else:
        logger.error(f"❌ Query failed: {response.status_code}")
        logger.error(f"   {response.text}")


def test_explain():
    """Test explain endpoint."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Explain Endpoint")
    logger.info("=" * 60)

    code_snippet = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

    explain_data = {"code": code_snippet, "language": "python"}

    logger.info(f"\nCode to explain:")
    logger.info(code_snippet)

    response = requests.post(f"{API_URL}/explain", json=explain_data)

    if response.status_code == 200:
        data = response.json()
        logger.info(f"✅ Explanation generated")
        logger.info(f"\n   Explanation: {data['explanation'][:150]}...")
    else:
        logger.error(f"❌ Explain failed: {response.status_code}")


def test_stats():
    """Test stats endpoint."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Stats Endpoint")
    logger.info("=" * 60)

    response = requests.get(f"{API_URL}/stats")

    if response.status_code == 200:
        data = response.json()
        logger.info(f"✅ Stats retrieved")
        logger.info(f"   Indexed vectors: {data.get('indexed_vectors', 0)}")
        logger.info(f"   Dimension: {data.get('dimension', 0)}")
        logger.info(f"   Status: {data.get('status', 'unknown')}")
    else:
        logger.error(f"❌ Stats failed: {response.status_code}")


def main():
    """Run all API tests."""
    logger.info("🚀 Testing Codebase RAG API\n")
    logger.info(f"API URL: {API_URL}")
    logger.info(f"Make sure the API server is running!\n")

    try:
        # Test 1: Health
        test_health()

        # Test 2: Query
        test_query()

        # Test 3: Explain
        test_explain()

        # Test 4: Stats
        test_stats()

        logger.info("\n" + "=" * 60)
        logger.info("✅ All API tests completed!")
        logger.info("=" * 60)

    except requests.exceptions.ConnectionError:
        logger.error("\n❌ Could not connect to API server")
        logger.error("   Make sure to run: python scripts/run_api.py")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
