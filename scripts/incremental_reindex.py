#!/usr/bin/env python3
"""
Incremental re-indexing.
Re-index only changed files instead of entire repository.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import git
from backend.ingestion.github_loader import GitHubLoader
from backend.ingestion.document_loader import DocumentLoader
from backend.parsing.chunker import CodeChunker
from backend.retrieval.embeddings import EmbeddingGenerator
from backend.retrieval.vector_store import FAISSVectorStore
from backend.retrieval.indexer import Indexer
from backend.utils import get_logger
from config.settings import settings

logger = get_logger(__name__)


def get_changed_files(repo_path: Path):
    """Get list of files changed in last commit."""
    try:
        repo = git.Repo(repo_path)

        # Get changed files in last commit
        changed_files = []
        if len(list(repo.iter_commits())) > 1:
            commits = list(repo.iter_commits(max_count=2))
            diff = commits[0].diff(commits[1])

            for change in diff:
                if change.a_path:
                    file_path = repo_path / change.a_path
                    if file_path.exists() and file_path.is_file():
                        changed_files.append(file_path)

        return changed_files
    except Exception as e:
        logger.error(f"Error getting changed files: {e}")
        return []


def incremental_reindex():
    """Re-index only changed files."""
    logger.info("Starting incremental re-indexing...")

    loader = GitHubLoader()
    repos_path = settings.repositories_path

    # Load existing index
    index_path = settings.vector_store_path / "main_index"

    # Initialize components
    embedding_generator = EmbeddingGenerator(provider="openai")
    vector_store = FAISSVectorStore(dimension=1536)

    try:
        vector_store.load(index_path)
        logger.info("Loaded existing index")
    except:
        logger.warning("No existing index found, will create new one")

    indexer = Indexer(embedding_generator, vector_store)

    total_files = 0
    total_chunks = 0

    # Process each repository
    for repo_dir in repos_path.iterdir():
        if repo_dir.is_dir() and (repo_dir / ".git").exists():
            logger.info(f"Checking {repo_dir.name} for changes...")

            changed_files = get_changed_files(repo_dir)

            if not changed_files:
                logger.info(f"No changes in {repo_dir.name}")
                continue

            logger.info(f"Found {len(changed_files)} changed files in {repo_dir.name}")

            # Load and chunk changed files
            doc_loader = DocumentLoader()
            documents = doc_loader.load_files(changed_files, show_progress=False)

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
            if all_chunks:
                indexed = indexer.index_chunks(all_chunks, batch_size=32)
                total_files += len(documents)
                total_chunks += indexed
                logger.info(
                    f"✅ Re-indexed {len(documents)} files ({indexed} chunks) from {repo_dir.name}"
                )

    # Save updated index
    if total_chunks > 0:
        indexer.save_index(index_path)
        logger.info(
            f"✅ Incremental re-indexing complete: {total_files} files, {total_chunks} chunks"
        )
    else:
        logger.info("No files to re-index")


if __name__ == "__main__":
    incremental_reindex()
