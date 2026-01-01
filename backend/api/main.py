"""
FastAPI Application
Main API for codebase RAG system.
"""

import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from backend.api.models import (
    QueryRequest,
    QueryResponse,
    IngestRequest,
    IngestResponse,
    ExplainRequest,
    ExplainResponse,
    DebugRequest,
    DebugResponse,
    HealthResponse,
    SourceReference,
)
from backend.ingestion.github_loader import GitHubLoader
from backend.ingestion.document_loader import DocumentLoader
from backend.parsing.chunker import CodeChunker
from backend.retrieval.embeddings import EmbeddingGenerator
from backend.retrieval.vector_store import FAISSVectorStore
from backend.retrieval.indexer import Indexer
from backend.retrieval.search import CodeSearchEngine
from backend.llm.rag_pipeline import RAGPipeline
from backend.llm.llm_client import MockLLMClient, GeminiClient
from backend.utils import get_logger
from config.settings import settings

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Codebase RAG API",
    description="Intelligent code search and Q&A system using RAG",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for system components
vector_store: FAISSVectorStore = None
embedding_generator: EmbeddingGenerator = None
search_engine: CodeSearchEngine = None
rag_pipeline: RAGPipeline = None
indexer: Indexer = None


def initialize_system():
    """Initialize the RAG system components."""
    global vector_store, embedding_generator, search_engine, rag_pipeline, indexer

    logger.info("Initializing RAG system...")

    # Initialize embedding generator (using simple mock for now)
    # In production, use: EmbeddingGenerator(provider="openai") or provider="huggingface"
    embedding_generator = EmbeddingGenerator(
        model_name="text-embedding-ada-002",
        provider="openai",  # Change to "huggingface" if OpenAI not available
    )

    # Initialize vector store
    dimension = embedding_generator.get_dimension() or 384
    vector_store = FAISSVectorStore(dimension=dimension)

    # Try to load existing index
    index_path = settings.vector_store_path / "main_index"
    if index_path.exists():
        try:
            vector_store.load(index_path)
            logger.info(f"Loaded existing index from {index_path}")
        except Exception as e:
            logger.warning(f"Could not load index: {e}")

    # Initialize search engine
    search_engine = CodeSearchEngine(vector_store, embedding_generator)

    # Initialize LLM client (use Mock for testing, Gemini/OpenAI for production)
    try:
        llm_client = GeminiClient()
    except:
        logger.warning("Gemini not available, using Mock LLM")
        llm_client = MockLLMClient()

    # Initialize RAG pipeline
    rag_pipeline = RAGPipeline(search_engine, llm_client, top_k=5)

    # Initialize indexer
    indexer = Indexer(embedding_generator, vector_store)

    logger.info("✅ RAG system initialized")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    initialize_system()


@app.get("/", response_model=Dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Codebase RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    stats = indexer.get_stats() if indexer else {}

    return HealthResponse(status="healthy", version="1.0.0", index_stats=stats)


@app.post("/query", response_model=QueryResponse)
async def query_code(request: QueryRequest):
    """
    Query the codebase using natural language.

    Args:
        request: Query request with question and filters

    Returns:
        Answer with sources and context
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="System not initialized")

    start_time = time.time()

    try:
        # Process query through RAG pipeline
        response = rag_pipeline.query(
            user_query=request.query,
            language=request.language,
            include_context=request.include_context,
        )

        processing_time = time.time() - start_time

        # Format sources
        sources = [SourceReference(**source) for source in response["sources"]]

        return QueryResponse(
            answer=response["answer"],
            sources=sources,
            num_sources=response["num_sources"],
            query_info=response["query_info"],
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
async def ingest_repository(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Ingest a GitHub repository into the system.

    Args:
        request: Repository URL and options
        background_tasks: Background task handler

    Returns:
        Ingestion status
    """
    if not indexer:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        # Clone repository
        loader = GitHubLoader()
        repo_path = loader.clone_repository(
            repo_url=request.repo_url, branch=request.branch
        )

        repo_name = repo_path.name

        # Get file list
        extensions = request.extensions or [".py", ".js", ".java", ".cpp", ".go"]
        files = loader.get_file_list(repo_path, extensions=extensions)

        # Load documents
        doc_loader = DocumentLoader()
        documents = doc_loader.load_files(files, show_progress=False)

        # Chunk code
        chunker = CodeChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            use_ast=True,
        )

        all_chunks = []
        for doc in documents:
            chunks = chunker.chunk_code(
                code=doc.content,
                language=doc.metadata.get("language", "unknown"),
                file_path=doc.metadata.get("filepath", ""),
            )
            all_chunks.extend(chunks)

        # Index chunks
        indexed_count = indexer.index_chunks(all_chunks, batch_size=32)

        # Save index
        index_path = settings.vector_store_path / "main_index"
        indexer.save_index(index_path)

        return IngestResponse(
            status="success",
            message=f"Repository {repo_name} ingested successfully",
            repo_name=repo_name,
            files_processed=len(documents),
            chunks_created=len(all_chunks),
            chunks_indexed=indexed_count,
        )

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain", response_model=ExplainResponse)
async def explain_code(request: ExplainRequest):
    """
    Explain what a code snippet does.

    Args:
        request: Code snippet and language

    Returns:
        Code explanation
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        explanation = rag_pipeline.explain_code(
            code=request.code, language=request.language
        )

        return ExplainResponse(
            explanation=explanation,
            code_snippet=request.code,
            language=request.language,
        )

    except Exception as e:
        logger.error(f"Explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug", response_model=DebugResponse)
async def debug_help(request: DebugRequest):
    """
    Get help debugging an error.

    Args:
        request: Error message and language

    Returns:
        Debug analysis and related code
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        result = rag_pipeline.debug_help(
            error_message=request.error_message, language=request.language
        )

        sources = [SourceReference(**source) for source in result["related_code"]]

        return DebugResponse(analysis=result["analysis"], related_code=sources)

    except Exception as e:
        logger.error(f"Debug help failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    if not indexer:
        return {"error": "System not initialized"}

    stats = indexer.get_stats()
    return {
        "indexed_vectors": stats.get("total_vectors", 0),
        "dimension": stats.get("dimension", 0),
        "status": "operational",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
