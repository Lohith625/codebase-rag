"""
FastAPI Application - Production Ready with Real LLM
"""

import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from backend.api.models import (
    QueryRequest, QueryResponse, IngestRequest, IngestResponse,
    ExplainRequest, ExplainResponse, DebugRequest, DebugResponse,
    HealthResponse, SourceReference
)
from backend.ingestion.github_loader import GitHubLoader
from backend.ingestion.document_loader import DocumentLoader
from backend.parsing.chunker import CodeChunker
from backend.retrieval.embeddings import EmbeddingGenerator
from backend.retrieval.vector_store import FAISSVectorStore
from backend.retrieval.indexer import Indexer
from backend.retrieval.search import CodeSearchEngine
from backend.llm.rag_pipeline import RAGPipeline
from backend.llm.llm_client import MockLLMClient, GeminiClient, OpenAIClient
from backend.utils import get_logger
from config.settings import settings

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Codebase RAG API",
    description="Intelligent code search and Q&A system using RAG",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
vector_store: FAISSVectorStore = None
embedding_generator = None
search_engine: CodeSearchEngine = None
rag_pipeline: RAGPipeline = None
indexer: Indexer = None


class SimpleEmbeddingGenerator:
    """Simple embeddings for development."""
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        logger.info(f"SimpleEmbeddingGenerator initialized")
    
    def generate_embedding(self, text: str):
        if not text:
            return None
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        return [float(hash_bytes[i % len(hash_bytes)]) / 255.0 for i in range(self.dimension)]
    
    def generate_embeddings(self, texts, batch_size=32, show_progress=True):
        return [self.generate_embedding(t) for t in texts]
    
    def get_dimension(self):
        return self.dimension


def get_llm_client():
    """Get the best available LLM client - FIXED VERSION!"""
    
    # TRY GEMINI FIRST
    if settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here":
        try:
            logger.info("🔄 Attempting Gemini connection...")
            client = GeminiClient()
            # ✅ FIXED: Check if client has working_model instead of model
            if client.client and client.working_model:
                logger.info(f"✅ Using Gemini LLM with model: {client.working_model}!")
                return client
            else:
                logger.warning("⚠️ Gemini client or model initialization failed")
        except Exception as e:
            logger.warning(f"⚠️ Gemini failed: {e}")
    else:
        logger.info("ℹ️ No Gemini API key configured")
    
    # TRY OPENAI SECOND
    if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
        try:
            logger.info("🔄 Attempting OpenAI connection...")
            client = OpenAIClient()
            if client.client:
                logger.info("✅ Using OpenAI LLM!")
                return client
            else:
                logger.warning("⚠️ OpenAI client initialization failed")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI failed: {e}")
    else:
        logger.info("ℹ️ No OpenAI API key configured")
    
    # FALLBACK TO MOCK
    logger.warning("⚠️ No real LLM available, using Mock LLM")
    logger.info("💡 Add GEMINI_API_KEY or OPENAI_API_KEY to .env for real AI responses")
    return MockLLMClient()


def initialize_system():
    """Initialize the RAG system."""
    global vector_store, embedding_generator, search_engine, rag_pipeline, indexer
    
    logger.info("🚀 Initializing RAG system...")
    
    embedding_generator = SimpleEmbeddingGenerator(dimension=384)
    dimension = embedding_generator.get_dimension()
    vector_store = FAISSVectorStore(dimension=dimension)
    
    # Load existing index
    index_path = settings.vector_store_path / "main_index"
    if index_path.exists():
        try:
            vector_store.load(index_path)
            logger.info(f"✅ Loaded index: {vector_store.index.ntotal} vectors")
        except Exception as e:
            logger.warning(f"Could not load index: {e}")
    
    search_engine = CodeSearchEngine(vector_store, embedding_generator)
    
    # Get LLM client (will try real APIs first!)
    llm_client = get_llm_client()
    
    rag_pipeline = RAGPipeline(search_engine, llm_client, top_k=5)
    indexer = Indexer(embedding_generator, vector_store)
    
    logger.info("✅ RAG system initialized")


@app.on_event("startup")
async def startup_event():
    """Run on startup."""
    initialize_system()


@app.get("/", response_model=Dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Codebase RAG API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check."""
    stats = indexer.get_stats() if indexer else {}
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        index_stats=stats
    )


@app.post("/query", response_model=QueryResponse)
async def query_code(request: QueryRequest):
    """Query the codebase."""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    start_time = time.time()
    
    try:
        response = rag_pipeline.query(
            user_query=request.query,
            language=request.language,
            include_context=request.include_context
        )
        
        processing_time = time.time() - start_time
        sources = [SourceReference(**source) for source in response['sources']]
        
        return QueryResponse(
            answer=response['answer'],
            sources=sources,
            num_sources=response['num_sources'],
            query_info=response['query_info'],
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
async def ingest_repository(request: IngestRequest, background_tasks: BackgroundTasks):
    """Ingest a repository."""
    if not indexer:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        loader = GitHubLoader()
        repo_path = loader.clone_repository(
            repo_url=request.repo_url,
            branch=request.branch
        )
        
        repo_name = repo_path.name
        extensions = request.extensions or ['.py', '.js', '.java', '.cpp', '.go']
        files = loader.get_file_list(repo_path, extensions=extensions)
        
        doc_loader = DocumentLoader()
        documents = doc_loader.load_files(files, show_progress=False)
        
        chunker = CodeChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            use_ast=True
        )
        
        all_chunks = []
        for doc in documents:
            chunks = chunker.chunk_code(
                code=doc.content,
                language=doc.metadata.get('language', 'unknown'),
                file_path=doc.metadata.get('filepath', '')
            )
            all_chunks.extend(chunks)
        
        indexed_count = indexer.index_chunks(all_chunks, batch_size=32)
        
        index_path = settings.vector_store_path / "main_index"
        indexer.save_index(index_path)
        
        return IngestResponse(
            status="success",
            message=f"Repository {repo_name} ingested successfully",
            repo_name=repo_name,
            files_processed=len(documents),
            chunks_created=len(all_chunks),
            chunks_indexed=indexed_count
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain", response_model=ExplainResponse)
async def explain_code(request: ExplainRequest):
    """Explain code."""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        explanation = rag_pipeline.explain_code(
            code=request.code,
            language=request.language
        )
        
        return ExplainResponse(
            explanation=explanation,
            code_snippet=request.code,
            language=request.language
        )
    except Exception as e:
        logger.error(f"Explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug", response_model=DebugResponse)
async def debug_help(request: DebugRequest):
    """Debug help."""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        result = rag_pipeline.debug_help(
            error_message=request.error_message,
            language=request.language
        )
        
        sources = [SourceReference(**source) for source in result['related_code']]
        
        return DebugResponse(
            analysis=result['analysis'],
            related_code=sources
        )
    except Exception as e:
        logger.error(f"Debug help failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get stats."""
    if not indexer:
        return {"error": "System not initialized"}
    
    stats = indexer.get_stats()
    return {
        "indexed_vectors": stats.get('total_vectors', 0),
        "dimension": stats.get('dimension', 0),
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
