#!/usr/bin/env python3
"""
Run the FastAPI server.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from backend.utils import get_logger

logger = get_logger(__name__)


def main():
    """Run the API server."""
    logger.info("🚀 Starting Codebase RAG API Server...")
    logger.info("API will be available at: http://localhost:8000")
    logger.info("API docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )


if __name__ == "__main__":
    main()
