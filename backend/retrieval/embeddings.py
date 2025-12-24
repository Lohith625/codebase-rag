"""
Embedding Generator
Generate embeddings for code chunks using various models.
"""

from typing import List, Dict, Optional
import numpy as np
from backend.utils import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text/code."""
    
    def __init__(
        self,
        model_name: str = "text-embedding-ada-002",
        provider: str = "openai"
    ):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Name of the embedding model
            provider: Provider (openai, huggingface, local)
        """
        self.model_name = model_name
        self.provider = provider
        self.model = None
        self.dimension = None
        
        self._initialize_model()
        
        logger.info(f"EmbeddingGenerator initialized with {provider}/{model_name}")
    
    def _initialize_model(self):
        """Initialize the embedding model."""
        if self.provider == "openai":
            self._initialize_openai()
        elif self.provider == "huggingface":
            self._initialize_huggingface()
        else:
            logger.warning(f"Unknown provider: {self.provider}")
    
    def _initialize_openai(self):
        """Initialize OpenAI embeddings."""
        try:
            from openai import OpenAI
            from config.settings import settings
            
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.dimension = 1536  # ada-002 dimension
            logger.info("OpenAI embeddings initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
    
    def _initialize_huggingface(self):
        """Initialize HuggingFace embeddings."""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use a code-specific model
            model_name = "microsoft/codebert-base"
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            
            logger.info(f"HuggingFace model loaded: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace: {e}")
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector or None
        """
        if not text or not text.strip():
            logger.warning("Empty text provided")
            return None
        
        try:
            if self.provider == "openai":
                return self._generate_openai_embedding(text)
            elif self.provider == "huggingface":
                return self._generate_huggingface_embedding(text)
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                return None
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI."""
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return response.data[0].embedding
    
    def _generate_huggingface_embedding(self, text: str) -> List[float]:
        """Generate embedding using HuggingFace."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            show_progress: Show progress bar
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        total = len(texts)
        
        logger.info(f"Generating {total} embeddings...")
        
        for i in range(0, total, batch_size):
            batch = texts[i:i + batch_size]
            
            if show_progress and i % (batch_size * 10) == 0:
                logger.info(f"Progress: {i}/{total} embeddings generated")
            
            if self.provider == "openai":
                batch_embeddings = self._generate_openai_batch(batch)
            elif self.provider == "huggingface":
                batch_embeddings = self._generate_huggingface_batch(batch)
            else:
                batch_embeddings = [None] * len(batch)
            
            embeddings.extend(batch_embeddings)
        
        logger.info(f"✅ Generated {len(embeddings)} embeddings")
        return embeddings
    
    def _generate_openai_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate batch of OpenAI embeddings."""
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return [None] * len(texts)
    
    def _generate_huggingface_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate batch of HuggingFace embeddings."""
        try:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return [None] * len(texts)
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension or 0
