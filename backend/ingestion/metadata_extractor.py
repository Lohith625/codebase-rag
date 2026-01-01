"""
Metadata Extractor
Extracts detailed metadata from code files.
"""

from pathlib import Path
from typing import Dict, List, Optional
import re
from backend.utils import get_logger

logger = get_logger(__name__)


class MetadataExtractor:
    """Extract metadata from code files."""

    def __init__(self):
        """Initialize metadata extractor."""
        self.language_patterns = {
            "python": {
                "function": r"def\s+(\w+)\s*\(",
                "class": r"class\s+(\w+)\s*[:\(]",
                "import": r"(?:from\s+[\w.]+\s+)?import\s+([\w,\s]+)",
                "comment": r"#.*$",
            },
            "javascript": {
                "function": r"function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>",
                "class": r"class\s+(\w+)",
                "import": r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
                "comment": r"//.*$|/\*[\s\S]*?\*/",
            },
            "java": {
                "function": r"(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(",
                "class": r"(?:public|private)?\s*class\s+(\w+)",
                "import": r"import\s+([\w.]+);",
                "comment": r"//.*$|/\*[\s\S]*?\*/",
            },
        }

    def extract_functions(self, content: str, language: str) -> List[str]:
        """
        Extract function names from content.

        Args:
            content: File content
            language: Programming language

        Returns:
            List of function names
        """
        if language not in self.language_patterns:
            return []

        pattern = self.language_patterns[language].get("function")
        if not pattern:
            return []

        matches = re.findall(pattern, content, re.MULTILINE)
        # Flatten matches (in case of multiple groups)
        functions = [
            m if isinstance(m, str) else next(x for x in m if x) for m in matches
        ]

        return functions

    def extract_classes(self, content: str, language: str) -> List[str]:
        """
        Extract class names from content.

        Args:
            content: File content
            language: Programming language

        Returns:
            List of class names
        """
        if language not in self.language_patterns:
            return []

        pattern = self.language_patterns[language].get("class")
        if not pattern:
            return []

        matches = re.findall(pattern, content, re.MULTILINE)
        return matches

    def extract_imports(self, content: str, language: str) -> List[str]:
        """
        Extract import statements from content.

        Args:
            content: File content
            language: Programming language

        Returns:
            List of imported modules
        """
        if language not in self.language_patterns:
            return []

        pattern = self.language_patterns[language].get("import")
        if not pattern:
            return []

        matches = re.findall(pattern, content, re.MULTILINE)
        return matches

    def calculate_complexity(self, content: str) -> Dict[str, int]:
        """
        Calculate basic code complexity metrics.

        Args:
            content: File content

        Returns:
            Dictionary of complexity metrics
        """
        metrics = {
            "total_lines": content.count("\n") + 1,
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "avg_line_length": 0,
        }

        lines = content.split("\n")
        code_lines = []

        for line in lines:
            stripped = line.strip()

            if not stripped:
                metrics["blank_lines"] += 1
            elif stripped.startswith("#") or stripped.startswith("//"):
                metrics["comment_lines"] += 1
            else:
                metrics["code_lines"] += 1
                code_lines.append(line)

        if code_lines:
            metrics["avg_line_length"] = sum(len(l) for l in code_lines) // len(
                code_lines
            )

        return metrics

    def extract_metadata(self, content: str, file_path: Path, language: str) -> Dict:
        """
        Extract all metadata from a file.

        Args:
            content: File content
            file_path: Path to file
            language: Programming language

        Returns:
            Dictionary of metadata
        """
        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "language": language,
            "functions": self.extract_functions(content, language),
            "classes": self.extract_classes(content, language),
            "imports": self.extract_imports(content, language),
            "complexity": self.calculate_complexity(content),
        }

        # Add counts
        metadata["num_functions"] = len(metadata["functions"])
        metadata["num_classes"] = len(metadata["classes"])
        metadata["num_imports"] = len(metadata["imports"])

        return metadata
