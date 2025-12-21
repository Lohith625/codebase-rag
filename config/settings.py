import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    def __init__(self):
        # API Keys
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY", "")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "")
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        
        # Paths
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.vector_store_path = self.data_dir / "vector_store"
        self.repositories_path = self.data_dir / "repositories"
        
        # Model settings
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.llm_model = os.getenv("LLM_MODEL", "gemini-1.5-flash")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.1"))
        
        # Retrieval settings
        self.top_k = int(os.getenv("TOP_K", "20"))
        self.top_n = int(os.getenv("TOP_N", "5"))
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        
        # Server settings
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.vector_store_path.mkdir(exist_ok=True)
        self.repositories_path.mkdir(exist_ok=True)

# Create singleton
settings = Settings()
