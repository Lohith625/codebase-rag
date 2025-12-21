"""
Code Parser using Tree-sitter.
Parse source code into Abstract Syntax Trees (AST).
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from tree_sitter_languages import get_language, get_parser
from backend.utils import get_logger

logger = get_logger(__name__)


class CodeParser:
    """Parse source code using Tree-sitter."""
    
    def __init__(self):
        """Initialize code parser with supported languages."""
        self.supported_languages = {
            'python': 'python',
            'javascript': 'javascript',
            'typescript': 'typescript',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'go': 'go',
            'rust': 'rust',
        }
        
        self.parsers = {}
        self.languages = {}
        
        # Initialize parsers for each language
        self._initialize_parsers()
        
        logger.info(f"CodeParser initialized with {len(self.parsers)} languages")
    
    def _initialize_parsers(self):
        """Initialize Tree-sitter parsers for all languages."""
        for lang_name, ts_name in self.supported_languages.items():
            try:
                self.languages[lang_name] = get_language(ts_name)
                self.parsers[lang_name] = get_parser(ts_name)
                logger.debug(f"Initialized parser for {lang_name}")
            except Exception as e:
                logger.warning(f"Could not initialize {lang_name} parser: {e}")
    
    def parse(self, code: str, language: str) -> Optional[object]:
        """
        Parse code into AST.
        
        Args:
            code: Source code as string
            language: Programming language
        
        Returns:
            Tree-sitter Tree object or None
        """
        if language not in self.parsers:
            logger.warning(f"Unsupported language: {language}")
            return None
        
        try:
            parser = self.parsers[language]
            tree = parser.parse(bytes(code, "utf8"))
            return tree
        except Exception as e:
            logger.error(f"Failed to parse {language} code: {e}")
            return None
    
    def extract_functions(self, tree: object, code: str, language: str) -> List[Dict]:
        """
        Extract function definitions from AST.
        
        Args:
            tree: Tree-sitter tree
            code: Source code
            language: Programming language
        
        Returns:
            List of function dictionaries
        """
        functions = []
        
        if not tree:
            return functions
        
        # Query patterns for different languages
        queries = {
            'python': '(function_definition name: (identifier) @func_name)',
            'javascript': '(function_declaration name: (identifier) @func_name)',
            'typescript': '(function_declaration name: (identifier) @func_name)',
            'java': '(method_declaration name: (identifier) @func_name)',
            'cpp': '(function_definition declarator: (function_declarator declarator: (identifier) @func_name))',
            'c': '(function_definition declarator: (function_declarator declarator: (identifier) @func_name))',
            'go': '(function_declaration name: (identifier) @func_name)',
            'rust': '(function_item name: (identifier) @func_name)',
        }
        
        query_string = queries.get(language)
        if not query_string:
            return functions
        
        try:
            lang = self.languages[language]
            query = lang.query(query_string)
            captures = query.captures(tree.root_node)
            
            code_bytes = bytes(code, "utf8")
            
            for node, capture_name in captures:
                if capture_name == "func_name":
                    # Get parent function node
                    func_node = node.parent
                    while func_node and not self._is_function_node(func_node, language):
                        func_node = func_node.parent
                    
                    if func_node:
                        start_byte = func_node.start_byte
                        end_byte = func_node.end_byte
                        start_point = func_node.start_point
                        end_point = func_node.end_point
                        
                        func_code = code_bytes[start_byte:end_byte].decode("utf8")
                        func_name = code_bytes[node.start_byte:node.end_byte].decode("utf8")
                        
                        functions.append({
                            'name': func_name,
                            'code': func_code,
                            'start_line': start_point[0],
                            'end_line': end_point[0],
                            'start_byte': start_byte,
                            'end_byte': end_byte,
                            'type': 'function'
                        })
            
            logger.debug(f"Extracted {len(functions)} functions")
            return functions
            
        except Exception as e:
            logger.error(f"Failed to extract functions: {e}")
            return functions
    
    def extract_classes(self, tree: object, code: str, language: str) -> List[Dict]:
        """
        Extract class definitions from AST.
        
        Args:
            tree: Tree-sitter tree
            code: Source code
            language: Programming language
        
        Returns:
            List of class dictionaries
        """
        classes = []
        
        if not tree:
            return classes
        
        queries = {
            'python': '(class_definition name: (identifier) @class_name)',
            'javascript': '(class_declaration name: (identifier) @class_name)',
            'typescript': '(class_declaration name: (identifier) @class_name)',
            'java': '(class_declaration name: (identifier) @class_name)',
            'cpp': '(class_specifier name: (type_identifier) @class_name)',
            'rust': '(struct_item name: (type_identifier) @class_name)',
        }
        
        query_string = queries.get(language)
        if not query_string:
            return classes
        
        try:
            lang = self.languages[language]
            query = lang.query(query_string)
            captures = query.captures(tree.root_node)
            
            code_bytes = bytes(code, "utf8")
            
            for node, capture_name in captures:
                if capture_name == "class_name":
                    class_node = node.parent
                    
                    if class_node:
                        start_byte = class_node.start_byte
                        end_byte = class_node.end_byte
                        start_point = class_node.start_point
                        end_point = class_node.end_point
                        
                        class_code = code_bytes[start_byte:end_byte].decode("utf8")
                        class_name = code_bytes[node.start_byte:node.end_byte].decode("utf8")
                        
                        classes.append({
                            'name': class_name,
                            'code': class_code,
                            'start_line': start_point[0],
                            'end_line': end_point[0],
                            'start_byte': start_byte,
                            'end_byte': end_byte,
                            'type': 'class'
                        })
            
            logger.debug(f"Extracted {len(classes)} classes")
            return classes
            
        except Exception as e:
            logger.error(f"Failed to extract classes: {e}")
            return classes
    
    def _is_function_node(self, node: object, language: str) -> bool:
        """Check if node is a function definition."""
        function_types = {
            'python': ['function_definition'],
            'javascript': ['function_declaration', 'arrow_function'],
            'typescript': ['function_declaration', 'arrow_function'],
            'java': ['method_declaration'],
            'cpp': ['function_definition'],
            'c': ['function_definition'],
            'go': ['function_declaration'],
            'rust': ['function_item'],
        }
        
        valid_types = function_types.get(language, [])
        return node.type in valid_types
    
    def get_node_text(self, node: object, code: str) -> str:
        """
        Get text content of a node.
        
        Args:
            node: Tree-sitter node
            code: Source code
        
        Returns:
            Text content of the node
        """
        code_bytes = bytes(code, "utf8")
        return code_bytes[node.start_byte:node.end_byte].decode("utf8")
    
    def extract_imports(self, tree: object, code: str, language: str) -> List[str]:
        """
        Extract import statements from AST.
        
        Args:
            tree: Tree-sitter tree
            code: Source code
            language: Programming language
        
        Returns:
            List of import statements
        """
        imports = []
        
        if not tree:
            return imports
        
        queries = {
            'python': '(import_statement) @import',
            'javascript': '(import_statement) @import',
            'typescript': '(import_statement) @import',
            'java': '(import_declaration) @import',
        }
        
        query_string = queries.get(language)
        if not query_string:
            return imports
        
        try:
            lang = self.languages[language]
            query = lang.query(query_string)
            captures = query.captures(tree.root_node)
            
            code_bytes = bytes(code, "utf8")
            
            for node, _ in captures:
                import_text = code_bytes[node.start_byte:node.end_byte].decode("utf8")
                imports.append(import_text.strip())
            
            return imports
            
        except Exception as e:
            logger.error(f"Failed to extract imports: {e}")
            return imports
