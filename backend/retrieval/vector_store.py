"""
Vector Store
Store and search embeddings using FAISS or Pinecone.
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path
import pickle
import numpy as np
from backend.utils import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Base class for vector stores."""

    def add_vectors(
        self,
        vectors: List[List[float]],
        metadata: List[Dict],
        ids: Optional[List[str]] = None,
    ):
        """Add vectors to the store."""
        raise NotImplementedError

    def search(
        self, query_vector: List[float], k: int = 5, filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar vectors."""
        raise NotImplementedError

    def save(self, path: Path):
        """Save the index."""
        raise NotImplementedError

    def load(self, path: Path):
        """Load the index."""
        raise NotImplementedError


class FAISSVectorStore(VectorStore):
    """Vector store using FAISS."""

    def __init__(self, dimension: int = 1536):
        """
        Initialize FAISS vector store.

        Args:
            dimension: Embedding dimension
        """
        import faiss

        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata_store = []
        self.id_to_index = {}

        logger.info(f"FAISSVectorStore initialized (dimension={dimension})")

    def add_vectors(
        self,
        vectors: List[List[float]],
        metadata: List[Dict],
        ids: Optional[List[str]] = None,
    ):
        """
        Add vectors to FAISS index.

        Args:
            vectors: List of embedding vectors
            metadata: List of metadata dicts
            ids: Optional list of IDs
        """
        if not vectors:
            logger.warning("No vectors to add")
            return

        # Convert to numpy array
        vectors_np = np.array(vectors, dtype=np.float32)

        # Add to index
        start_idx = self.index.ntotal
        self.index.add(vectors_np)

        # Store metadata
        for i, meta in enumerate(metadata):
            self.metadata_store.append(meta)

            if ids:
                self.id_to_index[ids[i]] = start_idx + i

        logger.info(
            f"Added {len(vectors)} vectors to index (total: {self.index.ntotal})"
        )

    def search(
        self, query_vector: List[float], k: int = 5, filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding
            k: Number of results
            filter_dict: Metadata filters (e.g., {'language': 'python'})

        Returns:
            List of results with metadata and scores
        """
        if self.index.ntotal == 0:
            logger.warning("Index is empty")
            return []

        # Convert query to numpy
        query_np = np.array([query_vector], dtype=np.float32)

        # Search (get more results if filtering)
        search_k = k * 10 if filter_dict else k
        distances, indices = self.index.search(
            query_np, min(search_k, self.index.ntotal)
        )

        # Collect results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata_store):
                continue

            metadata = self.metadata_store[idx]

            # Apply filters
            if filter_dict:
                if not self._matches_filter(metadata, filter_dict):
                    continue

            results.append(
                {"metadata": metadata, "score": float(dist), "index": int(idx)}
            )

            if len(results) >= k:
                break

        logger.debug(f"Found {len(results)} results")
        return results

    def _matches_filter(self, metadata: Dict, filter_dict: Dict) -> bool:
        """Check if metadata matches filter."""
        for key, value in filter_dict.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True

    def save(self, path: Path):
        """
        Save index and metadata to disk.

        Args:
            path: Directory to save to
        """
        import faiss

        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_path = path / "faiss_index.bin"
        faiss.write_index(self.index, str(index_path))

        # Save metadata
        metadata_path = path / "metadata.pkl"
        with open(metadata_path, "wb") as f:
            pickle.dump(
                {
                    "metadata_store": self.metadata_store,
                    "id_to_index": self.id_to_index,
                    "dimension": self.dimension,
                },
                f,
            )

        logger.info(f"Index saved to {path}")

    def load(self, path: Path):
        """
        Load index and metadata from disk.

        Args:
            path: Directory to load from
        """
        import faiss

        path = Path(path)

        # Load FAISS index
        index_path = path / "faiss_index.bin"
        if not index_path.exists():
            raise FileNotFoundError(f"Index not found: {index_path}")

        self.index = faiss.read_index(str(index_path))

        # Load metadata
        metadata_path = path / "metadata.pkl"
        with open(metadata_path, "rb") as f:
            data = pickle.load(f)
            self.metadata_store = data["metadata_store"]
            self.id_to_index = data["id_to_index"]
            self.dimension = data["dimension"]

        logger.info(f"Index loaded from {path} ({self.index.ntotal} vectors)")

    def get_stats(self) -> Dict:
        """Get index statistics."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "metadata_count": len(self.metadata_store),
        }


class PineconeVectorStore(VectorStore):
    """Vector store using Pinecone."""

    def __init__(self, index_name: str, dimension: int = 1536, metric: str = "cosine"):
        """
        Initialize Pinecone vector store.

        Args:
            index_name: Name of Pinecone index
            dimension: Embedding dimension
            metric: Distance metric
        """
        from pinecone import Pinecone
        from config.settings import settings

        self.index_name = index_name
        self.dimension = dimension

        # Initialize Pinecone
        pc = Pinecone(api_key=settings.pinecone_api_key)

        # Get or create index
        existing_indexes = [idx.name for idx in pc.list_indexes()]

        if index_name not in existing_indexes:
            logger.info(f"Creating Pinecone index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
            )

        self.index = pc.Index(index_name)
        logger.info(f"PineconeVectorStore initialized (index={index_name})")

    def add_vectors(
        self,
        vectors: List[List[float]],
        metadata: List[Dict],
        ids: Optional[List[str]] = None,
    ):
        """
        Add vectors to Pinecone.

        Args:
            vectors: List of embedding vectors
            metadata: List of metadata dicts
            ids: List of IDs (required for Pinecone)
        """
        if not ids:
            # Generate IDs if not provided
            import hashlib

            ids = [hashlib.md5(str(meta).encode()).hexdigest() for meta in metadata]

        # Prepare vectors for upsert
        vectors_to_upsert = [
            (id_, vector, meta) for id_, vector, meta in zip(ids, vectors, metadata)
        ]

        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i : i + batch_size]
            self.index.upsert(vectors=batch)

        logger.info(f"Added {len(vectors)} vectors to Pinecone")

    def search(
        self, query_vector: List[float], k: int = 5, filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search Pinecone index.

        Args:
            query_vector: Query embedding
            k: Number of results
            filter_dict: Metadata filters

        Returns:
            List of results
        """
        results = self.index.query(
            vector=query_vector, top_k=k, include_metadata=True, filter=filter_dict
        )

        formatted_results = []
        for match in results["matches"]:
            formatted_results.append(
                {
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match.get("metadata", {}),
                }
            )

        return formatted_results

    def save(self, path: Path):
        """Pinecone is cloud-based, no local save needed."""
        logger.info("Pinecone index is stored in the cloud")

    def load(self, path: Path):
        """Pinecone is cloud-based, no local load needed."""
        logger.info("Pinecone index loaded from cloud")
