#!/usr/bin/env python3
"""
Test the data ingestion pipeline.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ingestion.github_loader import GitHubLoader
from backend.ingestion.document_loader import DocumentLoader
from backend.ingestion.metadata_extractor import MetadataExtractor
from backend.utils import get_logger

logger = get_logger(__name__)


def test_github_clone():
    """Test cloning a GitHub repository."""
    logger.info("=" * 60)
    logger.info("TEST 1: GitHub Repository Cloning")
    logger.info("=" * 60)

    # Initialize loader
    loader = GitHubLoader()

    # Clone a small test repository (Flask microframework)
    repo_url = "https://github.com/pallets/flask"

    try:
        repo_path = loader.clone_repository(repo_url=repo_url, branch="main")

        logger.info(f"\n✅ Repository cloned to: {repo_path}")

        # Get repository info
        info = loader.get_repository_info(repo_path)
        logger.info(f"\nRepository Info:")
        logger.info(f"  Name: {info['name']}")
        logger.info(f"  Branch: {info['branch']}")
        logger.info(f"  Last Commit: {info['last_commit']['hash'][:8]}")
        logger.info(f"  Author: {info['last_commit']['author']}")
        logger.info(f"  Total Commits: {info['total_commits']}")

        return repo_path

    except Exception as e:
        logger.error(f"❌ Failed to clone repository: {e}")
        return None


def test_file_loading(repo_path: Path):
    """Test loading files from repository."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: File Loading")
    logger.info("=" * 60)

    # Initialize loaders
    github_loader = GitHubLoader()
    doc_loader = DocumentLoader()

    # Get Python files
    file_paths = github_loader.get_file_list(repo_path, extensions=[".py"])

    logger.info(f"\nFound {len(file_paths)} Python files")

    # Load first 5 files as test
    test_files = file_paths[:5]
    logger.info(f"Loading first {len(test_files)} files...")

    documents = doc_loader.load_files(test_files, show_progress=False)

    logger.info(f"\n✅ Loaded {len(documents)} documents")

    # Show sample document
    if documents:
        doc = documents[0]
        logger.info(f"\nSample Document:")
        logger.info(f"  ID: {doc.doc_id}")
        logger.info(f"  Filename: {doc.metadata['filename']}")
        logger.info(f"  Language: {doc.metadata['language']}")
        logger.info(f"  Size: {doc.metadata['num_characters']} chars")
        logger.info(f"  Lines: {doc.metadata['num_lines']}")
        logger.info(f"  Content Preview: {doc.content[:200]}...")

    return documents


def test_metadata_extraction(documents):
    """Test metadata extraction."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Metadata Extraction")
    logger.info("=" * 60)

    extractor = MetadataExtractor()

    # Extract metadata from first document
    if documents:
        doc = documents[0]
        metadata = extractor.extract_metadata(
            content=doc.content,
            file_path=Path(doc.metadata["filepath"]),
            language=doc.metadata["language"],
        )

        logger.info(f"\nExtracted Metadata:")
        logger.info(f"  File: {metadata['file_name']}")
        logger.info(f"  Functions Found: {metadata['num_functions']}")
        if metadata["functions"]:
            logger.info(f"  Sample Functions: {metadata['functions'][:5]}")
        logger.info(f"  Classes Found: {metadata['num_classes']}")
        if metadata["classes"]:
            logger.info(f"  Sample Classes: {metadata['classes'][:5]}")
        logger.info(f"  Imports Found: {metadata['num_imports']}")
        logger.info(f"  Complexity:")
        for key, value in metadata["complexity"].items():
            logger.info(f"    {key}: {value}")


def test_commit_history(repo_path: Path):
    """Test getting commit history."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Commit History")
    logger.info("=" * 60)

    loader = GitHubLoader()
    commits = loader.get_commit_history(repo_path, max_count=5)

    logger.info(f"\nLast {len(commits)} commits:")
    for i, commit in enumerate(commits, 1):
        logger.info(f"\n{i}. {commit['hash'][:8]} - {commit['author']}")
        logger.info(f"   Date: {commit['date']}")
        logger.info(f"   Message: {commit['message'][:80]}")
        logger.info(f"   Files Changed: {commit['files_changed']}")


def main():
    """Run all tests."""
    logger.info("🚀 Starting Data Ingestion Pipeline Tests\n")

    # Test 1: Clone repository
    repo_path = test_github_clone()
    if not repo_path:
        logger.error("Cannot proceed without repository")
        return 1

    # Test 2: Load files
    documents = test_file_loading(repo_path)
    if not documents:
        logger.error("No documents loaded")
        return 1

    # Test 3: Extract metadata
    test_metadata_extraction(documents)

    # Test 4: Get commit history
    test_commit_history(repo_path)

    logger.info("\n" + "=" * 60)
    logger.info("✅ All tests completed successfully!")
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
