"""
Indexing Pipeline
Combines chunking, embedding, and vector storage.
"""

from typing import List, Dict, Optional
from pathlib import Path
from backend.parsing.chunker import CodeChunk
from backend.retrieval.embeddings import EmbeddingGenerator
from backend.retrieval.vector_store import VectorStore, FAISSVectorStore, PineconeVectorStore
from backend.utils import get_logger

logger = get_logger(__name__)


class Indexer:
    """Index code chunks into vector store."""
    
    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        vector_store: VectorStore
    ):
        """
        Initialize indexer.
        
        Args:
            embedding_generator: Embedding generator
            vector_store: Vector store
        """
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        
        logger.info("Indexer initialized")
    
    def index_chunks(
        self,
        chunks: List[CodeChunk],
        batch_size: int = 32
    ) -> int:
        """
        Index code chunks.
        
        Args:
            chunks: List of code chunks
            batch_size: Batch size for processing
        
        Returns:
            Number of chunks indexed
        """
        if not chunks:
            logger.warning("No chunks to index")
            return 0
        
        logger.info(f"Indexing {len(chunks)} chunks...")
        
        # Extract texts and metadata
        texts = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [chunk.chunk_id for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_generator.generate_embeddings(
            texts,
            batch_size=batch_size
        )
        
        # Filter out failed embeddings
        valid_data = [
            (emb, meta, id_)
            for emb, meta, id_ in zip(embeddings, metadatas, ids)
            if emb is not None
        ]
        
        if not valid_data:
            logger.error("No valid embeddings generated")
            return 0
        
        valid_embeddings, valid_metadata, valid_ids = zip(*valid_data)
        
        # Add to vector store
        self.vector_store.add_vectors(
            vectors=list(valid_embeddings),
            metadata=list(valid_metadata),
            ids=list(valid_ids)
        )
        
        logger.info(f"✅ Indexed {len(valid_embeddings)} chunks")
        return len(valid_embeddings)
    
    def save_index(self, path: Path):
        """Save the index to disk."""
        self.vector_store.save(path)
        logger.info(f"Index saved to {path}")
    
    def load_index(self, path: Path):
        """Load the index from disk."""
        self.vector_store.load(path)
        logger.info(f"Index loaded from {path}")
    
    def get_stats(self) -> Dict:
        """Get indexing statistics."""
        if hasattr(self.vector_store, 'get_stats'):
            return self.vector_store.get_stats()
        return {}
