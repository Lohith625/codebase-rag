"""
Document Loader
Loads and processes different types of files from repositories.
"""

from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime
from backend.utils import get_logger

logger = get_logger(__name__)


class Document:
    """Represents a loaded document."""

    def __init__(self, content: str, metadata: Dict, doc_id: Optional[str] = None):
        """
        Initialize a document.

        Args:
            content: Document content
            metadata: Document metadata
            doc_id: Unique document identifier
        """
        self.content = content
        self.metadata = metadata
        self.doc_id = doc_id or self._generate_id()

    def _generate_id(self) -> str:
        """Generate a unique document ID."""
        import hashlib

        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        return f"doc_{content_hash[:16]}"

    def __repr__(self) -> str:
        return f"Document(id={self.doc_id}, length={len(self.content)})"


class DocumentLoader:
    """Load documents from various file types."""

    def __init__(self):
        """Initialize document loader."""
        self.supported_extensions = {
            # Code files
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            # Documentation
            ".md": "markdown",
            ".rst": "restructuredtext",
            ".txt": "text",
            # Config files
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".xml": "xml",
            ".ini": "ini",
            ".env": "env",
        }
        logger.info(
            f"DocumentLoader initialized with {len(self.supported_extensions)} supported file types"
        )

    def load_file(self, file_path: Path) -> Optional[Document]:
        """
        Load a single file.

        Args:
            file_path: Path to file

        Returns:
            Document object or None if loading fails
        """
        try:
            # Check if file type is supported
            extension = file_path.suffix.lower()
            if extension not in self.supported_extensions:
                logger.debug(f"Unsupported file type: {extension}")
                return None

            # Read file content
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with latin-1 encoding as fallback
                try:
                    with open(file_path, "r", encoding="latin-1") as f:
                        content = f.read()
                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")
                    return None

            # Get file metadata
            metadata = self._extract_metadata(file_path, content)

            # Create document
            doc = Document(content=content, metadata=metadata)

            logger.debug(f"Loaded: {file_path.name} ({len(content)} chars)")
            return doc

        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None

    def load_files(
        self, file_paths: List[Path], show_progress: bool = True
    ) -> List[Document]:
        """
        Load multiple files.

        Args:
            file_paths: List of file paths
            show_progress: Show progress during loading

        Returns:
            List of Document objects
        """
        documents = []
        total = len(file_paths)

        logger.info(f"Loading {total} files...")

        for i, file_path in enumerate(file_paths, 1):
            if show_progress and i % 10 == 0:
                logger.info(f"Progress: {i}/{total} files loaded")

            doc = self.load_file(file_path)
            if doc:
                documents.append(doc)

        logger.info(f"✅ Successfully loaded {len(documents)}/{total} files")
        return documents

    def _extract_metadata(self, file_path: Path, content: str) -> Dict:
        """
        Extract metadata from file.

        Args:
            file_path: Path to file
            content: File content

        Returns:
            Dictionary of metadata
        """
        stats = file_path.stat()
        extension = file_path.suffix.lower()

        metadata = {
            # File info
            "filename": file_path.name,
            "filepath": str(file_path),
            "extension": extension,
            "language": self.supported_extensions.get(extension, "unknown"),
            # Size info
            "size_bytes": stats.st_size,
            "num_characters": len(content),
            "num_lines": content.count("\n") + 1,
            # Timestamps
            "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            # Content analysis
            "is_empty": len(content.strip()) == 0,
            "has_docstring": self._has_docstring(content, extension),
        }

        return metadata

    def _has_docstring(self, content: str, extension: str) -> bool:
        """
        Check if file contains docstrings/comments.

        Args:
            content: File content
            extension: File extension

        Returns:
            True if docstrings found
        """
        if extension == ".py":
            return '"""' in content or "'''" in content
        elif extension in [".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c"]:
            return "/**" in content or "/*" in content
        elif extension == ".md":
            return True  # Markdown files are documentation
        return False

    def filter_by_extension(
        self, file_paths: List[Path], extensions: List[str]
    ) -> List[Path]:
        """
        Filter files by extension.

        Args:
            file_paths: List of file paths
            extensions: List of extensions to keep (e.g., ['.py', '.js'])

        Returns:
            Filtered list of file paths
        """
        filtered = [path for path in file_paths if path.suffix.lower() in extensions]
        logger.info(
            f"Filtered {len(file_paths)} files to {len(filtered)} with extensions {extensions}"
        )
        return filtered

    def filter_by_size(
        self,
        file_paths: List[Path],
        min_size: int = 0,
        max_size: int = 1_000_000,  # 1MB default
    ) -> List[Path]:
        """
        Filter files by size.

        Args:
            file_paths: List of file paths
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes

        Returns:
            Filtered list of file paths
        """
        filtered = [
            path for path in file_paths if min_size <= path.stat().st_size <= max_size
        ]
        logger.info(
            f"Filtered {len(file_paths)} files to {len(filtered)} by size ({min_size}-{max_size} bytes)"
        )
        return filtered
