"""
Unit tests for query constructor.
"""

import pytest
from backend.llm.query_constructor import QueryConstructor


def test_query_parsing():
    """Test query parsing."""
    constructor = QueryConstructor()
    
    query = "How does authentication work in Python?"
    parsed = constructor.parse_query(query)
    
    assert 'original_query' in parsed
    assert 'intent' in parsed
    assert 'enhanced_query' in parsed
    assert parsed['original_query'] == query


def test_intent_detection():
    """Test intent detection."""
    constructor = QueryConstructor()
    
    queries = {
        "Find the login function": "search",
        "Explain how authentication works": "explain",
        "Debug this error": "debug",
        "Show me an example": "example",
    }
    
    for query, expected_intent in queries.items():
        parsed = constructor.parse_query(query)
        assert parsed['intent'] == expected_intent


def test_filter_suggestion():
    """Test filter suggestion."""
    constructor = QueryConstructor()
    
    query = "Python authentication function"
    parsed = constructor.parse_query(query)
    
    filters = parsed['filters']
    assert 'language' in filters
    assert filters['language'] == 'python'


def test_query_enhancement():
    """Test query enhancement."""
    constructor = QueryConstructor()
    
    query = "auth system"
    parsed = constructor.parse_query(query)
    
    enhanced = parsed['enhanced_query']
    assert len(enhanced) > len(query)
