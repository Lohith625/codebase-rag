#!/usr/bin/env python3
"""
Test embeddings and vector storage.
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.retrieval.vector_store import FAISSVectorStore
from backend.retrieval.indexer import Indexer
from backend.parsing.chunker import CodeChunk
from backend.utils import get_logger

logger = get_logger(__name__)


class SimpleEmbeddingGenerator:
    """Simple embedding generator for testing (no API needed)."""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        logger.info(f"SimpleEmbeddingGenerator initialized (dimension={dimension})")
    
    def generate_embedding(self, text: str):
        """Generate a simple hash-based embedding for testing."""
        if not text:
            return None
        
        # Simple hash-based embedding (for testing only)
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Expand to desired dimension
        embedding = []
        for i in range(self.dimension):
            embedding.append(float(hash_bytes[i % len(hash_bytes)]) / 255.0)
        
        return embedding
    
    def generate_embeddings(self, texts, batch_size=32, show_progress=True):
        """Generate embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            emb = self.generate_embedding(text)
            embeddings.append(emb)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    def get_dimension(self):
        return self.dimension


def test_embeddings():
    """Test embedding generation."""
    logger.info("=" * 60)
    logger.info("TEST 1: Embedding Generation")
    logger.info("=" * 60)
    
    # Use simple local embeddings (no download needed)
    generator = SimpleEmbeddingGenerator(dimension=384)
    
    # Test texts
    texts = [
        "def add(a, b): return a + b",
        "class Calculator: pass",
        "import numpy as np"
    ]
    
    logger.info(f"\nGenerating embeddings for {len(texts)} texts...")
    
    # Generate single embedding
    embedding = generator.generate_embedding(texts[0])
    logger.info(f"✅ Single embedding generated")
    logger.info(f"   Dimension: {len(embedding)}")
    logger.info(f"   First 5 values: {[f'{v:.4f}' for v in embedding[:5]]}")
    
    # Generate batch embeddings
    embeddings = generator.generate_embeddings(texts, show_progress=False)
    logger.info(f"\n✅ Batch embeddings generated: {len(embeddings)}")
    logger.info(f"   All non-None: {all(e is not None for e in embeddings)}")
    
    return generator, embeddings


def test_vector_store(generator, embeddings):
    """Test FAISS vector store."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Vector Store (FAISS)")
    logger.info("=" * 60)
    
    # Create vector store
    dimension = generator.get_dimension()
    vector_store = FAISSVectorStore(dimension=dimension)
    
    # Create metadata
    metadata = [
        {'text': 'def add(a, b): return a + b', 'type': 'function', 'language': 'python'},
        {'text': 'class Calculator: pass', 'type': 'class', 'language': 'python'},
        {'text': 'import numpy as np', 'type': 'import', 'language': 'python'}
    ]
    ids = ['chunk_1', 'chunk_2', 'chunk_3']
    
    # Add vectors
    logger.info(f"\nAdding {len(embeddings)} vectors to store...")
    vector_store.add_vectors(embeddings, metadata, ids)
    
    stats = vector_store.get_stats()
    logger.info(f"✅ Vectors added")
    logger.info(f"   Total vectors: {stats['total_vectors']}")
    logger.info(f"   Dimension: {stats['dimension']}")
    
    # Search without filter
    logger.info(f"\nSearching for similar vectors...")
    query_vector = embeddings[0]  # Use first embedding as query
    results = vector_store.search(query_vector, k=3)
    
    logger.info(f"✅ Search complete: {len(results)} results")
    for i, result in enumerate(results, 1):
        logger.info(f"\n   Result {i}:")
        logger.info(f"      Text: {result['metadata']['text']}")
        logger.info(f"      Type: {result['metadata']['type']}")
        logger.info(f"      Score: {result['score']:.4f}")
    
    # Search with filter
    logger.info(f"\n\nSearching with filter (type=function)...")
    filtered_results = vector_store.search(
        query_vector, 
        k=3, 
        filter_dict={'type': 'function'}
    )
    
    logger.info(f"✅ Filtered search complete: {len(filtered_results)} results")
    for i, result in enumerate(filtered_results, 1):
        logger.info(f"   Result {i}: {result['metadata']['type']} - {result['metadata']['text'][:40]}...")
    
    return vector_store


def test_indexer(generator, vector_store):
    """Test complete indexing pipeline."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Indexing Pipeline")
    logger.info("=" * 60)
    
    # Create sample chunks
    chunks = [
        CodeChunk(
            content="def hello(): print('Hello')",
            metadata={'type': 'function', 'name': 'hello', 'language': 'python'}
        ),
        CodeChunk(
            content="class World: pass",
            metadata={'type': 'class', 'name': 'World', 'language': 'python'}
        ),
        CodeChunk(
            content="import os",
            metadata={'type': 'import', 'language': 'python'}
        )
    ]
    
    logger.info(f"\nIndexing {len(chunks)} chunks...")
    
    indexer = Indexer(generator, vector_store)
    indexed_count = indexer.index_chunks(chunks, batch_size=10)
    
    logger.info(f"✅ Indexed {indexed_count} chunks")
    
    # Get stats
    stats = indexer.get_stats()
    logger.info(f"   Total in index: {stats['total_vectors']}")
    
    # Test save/load
    from config.settings import settings
    save_path = settings.vector_store_path / "test_index"
    
    logger.info(f"\nSaving index to {save_path}...")
    indexer.save_index(save_path)
    logger.info("✅ Index saved")
    
    # Test loading
    logger.info(f"\nLoading index from {save_path}...")
    new_vector_store = FAISSVectorStore(dimension=generator.get_dimension())
    new_indexer = Indexer(generator, new_vector_store)
    new_indexer.load_index(save_path)
    logger.info("✅ Index loaded")
    
    stats = new_indexer.get_stats()
    logger.info(f"   Loaded vectors: {stats['total_vectors']}")


def main():
    """Run all tests."""
    logger.info("🚀 Starting Embeddings & Vector Store Tests\n")
    
    # Test 1: Embeddings
    generator, embeddings = test_embeddings()
    
    # Test 2: Vector Store
    vector_store = test_vector_store(generator, embeddings)
    
    # Test 3: Indexer
    test_indexer(generator, vector_store)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ All tests completed successfully!")
    logger.info("=" * 60)
    logger.info("\nNote: Used simple hash-based embeddings for testing.")
    logger.info("In production, use OpenAI or HuggingFace embeddings.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
