"""
Optimization Configuration
Settings for performance optimization.
"""

from typing import Dict, Any


# Embedding batch sizes for different providers
EMBEDDING_BATCH_SIZES = {
    'openai': 100,      # OpenAI allows large batches
    'huggingface': 32,  # Local models need smaller batches
}

# Cache settings
CACHE_CONFIG = {
    'query_cache_ttl': 24,        # hours
    'embedding_cache_ttl': 168,   # 7 days
    'enable_query_cache': True,
    'enable_embedding_cache': True,
}

# Vector search optimization
SEARCH_CONFIG = {
    'use_approximate': True,      # Use approximate search for speed
    'nprobe': 10,                 # FAISS search parameter
    'ef_search': 100,             # For HNSW indexes
}

# Chunking optimization
CHUNKING_CONFIG = {
    'max_chunk_size': 2000,       # Maximum chunk size
    'min_chunk_size': 100,        # Minimum chunk size
    'overlap_ratio': 0.2,         # 20% overlap
    'preserve_structure': True,   # Use AST-based chunking
}

# API optimization
API_CONFIG = {
    'rate_limit': '100/minute',   # Rate limiting
    'timeout': 30,                # Request timeout (seconds)
    'max_concurrent': 10,         # Max concurrent requests
}

# LLM optimization
LLM_CONFIG = {
    'max_retries': 3,
    'retry_delay': 1,             # seconds
    'timeout': 30,
    'temperature': 0.1,           # Low for consistency
    'max_tokens': 2048,
}


def get_optimization_config() -> Dict[str, Any]:
    """Get all optimization configurations."""
    return {
        'embedding': EMBEDDING_BATCH_SIZES,
        'cache': CACHE_CONFIG,
        'search': SEARCH_CONFIG,
        'chunking': CHUNKING_CONFIG,
        'api': API_CONFIG,
        'llm': LLM_CONFIG,
    }
