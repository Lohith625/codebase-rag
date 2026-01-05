"""
Code Chunker
Intelligently chunk code based on AST structure.
"""

from typing import List, Dict, Optional
from backend.parsing.code_parser import CodeParser
from backend.utils import get_logger

logger = get_logger(__name__)


class CodeChunk:
    """Represents a chunk of code."""
    
    def __init__(
        self,
        content: str,
        metadata: Dict,
        chunk_id: Optional[str] = None
    ):
        """Initialize a code chunk."""
        self.content = content
        self.metadata = metadata
        self.chunk_id = chunk_id or self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique chunk ID."""
        import hashlib
        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        return f"chunk_{content_hash[:16]}"
    
    def __repr__(self) -> str:
        return f"CodeChunk(id={self.chunk_id}, type={self.metadata.get('type')}, lines={self.metadata.get('num_lines')})"


class CodeChunker:
    """Chunk code intelligently using AST."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        use_ast: bool = True
    ):
        """Initialize code chunker."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_ast = use_ast
        
        if use_ast:
            self.parser = CodeParser()
        
        logger.info(f"CodeChunker initialized (chunk_size={chunk_size}, overlap={chunk_overlap}, ast={use_ast})")
    
    def chunk_code(
        self,
        code: str,
        language: str,
        file_path: str
    ) -> List[CodeChunk]:
        """Chunk code into smaller pieces."""
        if not code or not code.strip():
            logger.debug(f"Empty code for {file_path}")
            return []
        
        if self.use_ast and language in self.parser.supported_languages:
            return self._chunk_by_ast(code, language, file_path)
        else:
            return self._chunk_by_lines(code, language, file_path)
    
    def _chunk_by_ast(
        self,
        code: str,
        language: str,
        file_path: str
    ) -> List[CodeChunk]:
        """Chunk code by AST structure."""
        chunks = []
        
        # Parse code
        tree = self.parser.parse(code, language)
        if not tree:
            logger.warning(f"Could not parse {file_path}, falling back to line-based chunking")
            return self._chunk_by_lines(code, language, file_path)
        
        # Extract functions and classes
        functions = self.parser.extract_functions(tree, code, language)
        classes = self.parser.extract_classes(tree, code, language)
        
        # Combine and sort
        elements = functions + classes
        elements.sort(key=lambda x: x['start_byte'])
        
        # Create chunks from elements
        for element in elements:
            chunk = self._create_chunk_from_element(
                element, code, language, file_path
            )
            if chunk:
                chunks.append(chunk)
        
        # If no elements found, chunk by lines
        if not chunks:
            return self._chunk_by_lines(code, language, file_path)
        
        logger.debug(f"Created {len(chunks)} AST-based chunks from {file_path}")
        return chunks
    
    def _create_chunk_from_element(
        self,
        element: Dict,
        code: str,
        language: str,
        file_path: str
    ) -> Optional[CodeChunk]:
        """Create a chunk from a function or class."""
        content = element['code']
        
        # Add context
        lines = code.split('\n')
        start_line = max(0, element['start_line'] - 2)
        end_line = min(len(lines), element['end_line'] + 3)
        
        context_before = '\n'.join(lines[start_line:element['start_line']])
        context_after = '\n'.join(lines[element['end_line']+1:end_line])
        
        full_content = f"{context_before}\n{content}\n{context_after}".strip()
        
        metadata = {
            'file_path': file_path,
            'language': language,
            'type': element['type'],
            'name': element['name'],
            'start_line': element['start_line'],
            'end_line': element['end_line'],
            'num_lines': element['end_line'] - element['start_line'] + 1,
            'num_characters': len(full_content),
            'has_context': True,
            'content': full_content  # Add content to metadata for search
        }
        
        return CodeChunk(content=full_content, metadata=metadata)
    
    def _chunk_by_lines(
        self,
        code: str,
        language: str,
        file_path: str
    ) -> List[CodeChunk]:
        """Fallback: Chunk code by lines."""
        chunks = []
        lines = code.split('\n')
        
        if not lines:
            return []
        
        # Calculate lines per chunk (with safety check)
        total_chars = len(code)
        total_lines = len(lines)
        
        if total_lines == 0 or total_chars == 0:
            return []
        
        avg_line_length = total_chars / total_lines
        
        # Avoid division by zero
        if avg_line_length == 0:
            avg_line_length = 50  # Default fallback
        
        lines_per_chunk = max(1, int(self.chunk_size / avg_line_length))
        overlap_lines = max(0, int(self.chunk_overlap / avg_line_length))
        
        i = 0
        chunk_num = 0
        
        while i < len(lines):
            end = min(i + lines_per_chunk, len(lines))
            chunk_lines = lines[i:end]
            
            if chunk_lines:  # Only create chunk if there are lines
                chunk = self._create_chunk_from_lines(
                    chunk_lines, i, language, file_path, 'line_based', chunk_num
                )
                if chunk:
                    chunks.append(chunk)
                chunk_num += 1
            
            i += max(1, lines_per_chunk - overlap_lines)
        
        logger.debug(f"Created {len(chunks)} line-based chunks from {file_path}")
        return chunks
    
    def _create_chunk_from_lines(
        self,
        lines: List[str],
        start_line: int,
        language: str,
        file_path: str,
        chunk_type: str,
        chunk_num: int = 0
    ) -> Optional[CodeChunk]:
        """Create a chunk from lines."""
        content = '\n'.join(lines).strip()
        
        if not content:
            return None
        
        metadata = {
            'file_path': file_path,
            'language': language,
            'type': chunk_type,
            'start_line': start_line,
            'end_line': start_line + len(lines) - 1,
            'num_lines': len(lines),
            'num_characters': len(content),
            'chunk_number': chunk_num,
            'content': content  # Add content to metadata
        }
        
        return CodeChunk(content=content, metadata=metadata)
