"""
Unit tests for code chunker.
"""

import pytest
from backend.parsing.chunker import CodeChunker, CodeChunk


def test_code_chunk_creation():
    """Test CodeChunk creation."""
    chunk = CodeChunk(
        content="def hello(): pass",
        metadata={'type': 'function', 'name': 'hello'}
    )
    
    assert chunk.content == "def hello(): pass"
    assert chunk.metadata['type'] == 'function'
    assert chunk.chunk_id is not None


def test_chunker_initialization():
    """Test CodeChunker initialization."""
    chunker = CodeChunker(chunk_size=500, chunk_overlap=50, use_ast=True)
    
    assert chunker.chunk_size == 500
    assert chunker.chunk_overlap == 50
    assert chunker.use_ast == True


def test_line_based_chunking():
    """Test fallback line-based chunking."""
    chunker = CodeChunker(chunk_size=100, chunk_overlap=20, use_ast=False)
    
    code = "line1\nline2\nline3\nline4\nline5"
    chunks = chunker.chunk_code(code, 'python', 'test.py')
    
    assert len(chunks) > 0
    assert all(isinstance(c, CodeChunk) for c in chunks)


def test_chunk_metadata():
    """Test chunk metadata extraction."""
    chunker = CodeChunker(use_ast=False)
    
    code = "def test():\n    pass"
    chunks = chunker.chunk_code(code, 'python', 'test.py')
    
    assert len(chunks) > 0
    chunk = chunks[0]
    assert 'file_path' in chunk.metadata
    assert 'language' in chunk.metadata
    assert chunk.metadata['language'] == 'python'
