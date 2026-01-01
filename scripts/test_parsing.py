#!/usr/bin/env python3
"""
Test code parsing and chunking.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.parsing.code_parser import CodeParser
from backend.parsing.chunker import CodeChunker
from backend.utils import get_logger

logger = get_logger(__name__)


def test_parser():
    """Test code parser."""
    logger.info("=" * 60)
    logger.info("TEST 1: Code Parser")
    logger.info("=" * 60)

    # Sample Python code
    python_code = '''
import os
from pathlib import Path

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.result = 0
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b

def main():
    """Main function."""
    calc = Calculator()
    print(calc.add(5, 3))

if __name__ == "__main__":
    main()
'''

    parser = CodeParser()

    # Parse code
    tree = parser.parse(python_code, "python")
    logger.info(f"✅ Code parsed successfully")

    # Extract functions
    functions = parser.extract_functions(tree, python_code, "python")
    logger.info(f"\nExtracted {len(functions)} functions:")
    for func in functions:
        logger.info(
            f"  - {func['name']} (lines {func['start_line']}-{func['end_line']})"
        )

    # Extract classes
    classes = parser.extract_classes(tree, python_code, "python")
    logger.info(f"\nExtracted {len(classes)} classes:")
    for cls in classes:
        logger.info(f"  - {cls['name']} (lines {cls['start_line']}-{cls['end_line']})")

    # Extract imports
    imports = parser.extract_imports(tree, python_code, "python")
    logger.info(f"\nExtracted {len(imports)} imports:")
    for imp in imports[:5]:
        logger.info(f"  - {imp}")

    return python_code


def test_chunker(code: str):
    """Test code chunker."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Code Chunker")
    logger.info("=" * 60)

    chunker = CodeChunker(chunk_size=500, chunk_overlap=50, use_ast=True)

    # Chunk the code
    chunks = chunker.chunk_code(code, "python", "test.py")

    logger.info(f"\n✅ Created {len(chunks)} chunks")

    for i, chunk in enumerate(chunks, 1):
        logger.info(f"\nChunk {i}:")
        logger.info(f"  ID: {chunk.chunk_id}")
        logger.info(f"  Type: {chunk.metadata['type']}")
        logger.info(f"  Name: {chunk.metadata.get('name', 'N/A')}")
        logger.info(
            f"  Lines: {chunk.metadata['start_line']}-{chunk.metadata['end_line']}"
        )
        logger.info(f"  Size: {chunk.metadata['num_characters']} chars")
        logger.info(f"  Preview: {chunk.content[:100]}...")


def test_with_real_file():
    """Test with a real file from the project."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Real File Parsing")
    logger.info("=" * 60)

    # Use our own github_loader.py as test
    test_file = (
        Path(__file__).parent.parent / "backend" / "ingestion" / "github_loader.py"
    )

    if not test_file.exists():
        logger.warning(f"Test file not found: {test_file}")
        return

    with open(test_file, "r") as f:
        code = f.read()

    logger.info(f"Testing with: {test_file.name}")
    logger.info(f"File size: {len(code)} characters, {len(code.split(chr(10)))} lines")

    # Parse
    parser = CodeParser()
    tree = parser.parse(code, "python")

    functions = parser.extract_functions(tree, code, "python")
    classes = parser.extract_classes(tree, code, "python")

    logger.info(f"\nFound:")
    logger.info(f"  Functions: {len(functions)}")
    logger.info(f"  Classes: {len(classes)}")

    # Chunk
    chunker = CodeChunker(chunk_size=1000, chunk_overlap=200, use_ast=True)
    chunks = chunker.chunk_code(code, "python", str(test_file))

    logger.info(f"\nCreated {len(chunks)} chunks:")
    for chunk in chunks[:5]:
        logger.info(
            f"  - {chunk.metadata['type']}: {chunk.metadata.get('name', 'N/A')} ({chunk.metadata['num_lines']} lines)"
        )


def main():
    """Run all tests."""
    logger.info("🚀 Starting Code Parsing & Chunking Tests\n")

    # Test 1: Parser
    code = test_parser()

    # Test 2: Chunker
    test_chunker(code)

    # Test 3: Real file
    test_with_real_file()

    logger.info("\n" + "=" * 60)
    logger.info("✅ All parsing tests completed!")
    logger.info("=" * 60)


if __name__ == "__main__":
    sys.exit(main())
