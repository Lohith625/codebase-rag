#!/usr/bin/env python3
"""
Set up Tree-sitter language parsers.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tree_sitter import Language
from backend.utils import get_logger

logger = get_logger(__name__)


def setup_languages():
    """Download and build Tree-sitter languages."""

    # This will use tree-sitter-languages package which has pre-built binaries
    try:
        from tree_sitter_languages import get_language, get_parser

        languages = ["python", "javascript", "java", "cpp", "go", "rust", "typescript"]

        logger.info("Testing Tree-sitter language support...")

        for lang in languages:
            try:
                language = get_language(lang)
                parser = get_parser(lang)
                logger.info(f"✅ {lang.capitalize()} parser ready")
            except Exception as e:
                logger.warning(f"⚠️  {lang.capitalize()} parser unavailable: {e}")

        logger.info("\n✅ Tree-sitter setup complete!")
        return True

    except ImportError:
        logger.error("tree_sitter_languages not installed. Installing...")
        import subprocess

        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "tree-sitter-languages"]
        )
        logger.info("Please run this script again.")
        return False


if __name__ == "__main__":
    success = setup_languages()
    sys.exit(0 if success else 1)
