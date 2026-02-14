"""Code Parser - Utility for parsing and analyzing source code."""

import ast
import tokenize
import io
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path


class CodeParser:
    """Utility class for parsing source code into AST and extracting information."""
    
    def __init__(self):
        self.source_code: str = ""
        self.tree: Optional[ast.AST] = None
        self.tokens: List[tokenize.TokenInfo] = []
        
    def parse(self, source_code: str) -> ast.AST:
        """Parse source code into an AST.
        
        Args:
            source_code: The source code to parse.
            
        Returns:
            The AST tree.
            
        Raises:
            SyntaxError: If the source code has syntax errors.
        """
        self.source_code = source_code
        try:
            self.tree = ast.parse(source_code)
            return self.tree
        except SyntaxError as e:
            raise SyntaxError(f"Failed to parse code: {e}")
    
    def parse_file(self, file_path: Path) -> ast.AST:
        """Parse a source file into an AST.
        
        Args:
            file_path: Path to the source file.
            
        Returns:
            The AST tree.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        return self.parse(source_code)
    
    def get_tokens(self) -> List[tokenize.TokenInfo]:
        """Get all tokens from the source code.
        
        Returns:
            List of tokens.
        """
        if not self.source_code:
            return []
        
        if not self.tokens:
            self.tokens = list(tokenize.generate_tokens(
                io.StringIO(self.source_code).readline
            ))
        
        return self.tokens
    
    def get_function_names(self) -> List[str]:
        """Get all function names in the source code.
        
        Returns:
            List of function names.
        """
        if not self.tree:
            return []
        
        functions = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(node.name)
        
        return functions
    
    def get_class_names(self) -> List[str]:
        """Get all class names in the source code.
        
        Returns:
            List of class names.
        """
        if not self.tree:
            return []
        
        classes = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return classes
    
    def get_imports(self) -> List[Dict[str, str]]:
        """Get all imports in the source code.
        
        Returns:
            List of import dictionaries with 'module' and 'name' keys.
        """
        if not self.tree:
            return []
        
        imports = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "module": alias.name,
                        "name": alias.asname or alias.name,
                        "type": "import"
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append({
                        "module": f"{module}.{alias.name}" if module else alias.name,
                        "name": alias.asname or alias.name,
                        "type": "from_import"
                    })
        
        return imports
    
    def get_docstring(self, node: ast.AST) -> Optional[str]:
        """Get the docstring from an AST node.
        
        Args:
            node: An AST node (function, class, or module).
            
        Returns:
            The docstring or None.
        """
        docstring = ast.get_docstring(node)
        return docstring
    
    def get_function_signature(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract detailed function signature information.
        
        Args:
            node: A function AST node.
            
        Returns:
            Dictionary with argument info, return type, defaults, etc.
        """
        args = node.args
        
        arguments = []
        for arg in args.args:
            arguments.append({
                "name": arg.arg,
                "annotation": self._get_annotation(arg.annotation),
                "default": None  # Will be filled below
            })
        
        # Add defaults (mapped from right to left)
        defaults = args.defaults
        for i, default in enumerate(defaults):
            arg_index = len(arguments) - len(defaults) + i
            if arg_index >= 0:
                arguments[arg_index]["default"] = self._ast_to_str(default)
        
        # Handle *args and **kwargs
        vararg = None
        if args.vararg:
            vararg = {
                "name": args.vararg.arg,
                "annotation": self._get_annotation(args.vararg.annotation)
            }
        
        kwarg = None
        if args.kwarg:
            kwarg = {
                "name": args.kwarg.arg,
                "annotation": self._get_annotation(args.kwarg.annotation)
            }
        
        # Get return annotation
        returns = self._get_annotation(node.returns)
        
        return {
            "name": node.name,
            "arguments": arguments,
            "vararg": vararg,
            "kwarg": kwarg,
            "returns": returns,
            "is_async": isinstance(node, ast.AsyncFunctionDef)
        }
    
    def get_class_methods(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Get all methods of a class.
        
        Args:
            node: A class AST node.
            
        Returns:
            List of method information dictionaries.
        """
        methods = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append({
                    "name": item.name,
                    "signature": self.get_function_signature(item),
                    "is_static": any(
                        isinstance(d, ast.StaticMethod) 
                        for d in node.decorator_list
                        if hasattr(d, 'attr') and d.attr == item.name
                    ) or self._has_decorator(item, 'staticmethod'),
                    "is_classmethod": self._has_decorator(item, 'classmethod'),
                    "docstring": self.get_docstring(item)
                })
            elif isinstance(item, ast.AsyncFunctionDef):
                methods.append({
                    "name": item.name,
                    "signature": self.get_function_signature(item),
                    "is_static": False,
                    "is_classmethod": self._has_decorator(item, 'classmethod'),
                    "docstring": self.get_docstring(item)
                })
        
        return methods
    
    def _get_annotation(self, node: Optional[ast.AST]) -> Optional[str]:
        """Convert an annotation AST node to string."""
        if node is None:
            return None
        return self._ast_to_str(node)
    
    def _ast_to_str(self, node: ast.AST) -> str:
        """Convert an AST node to its string representation."""
        return ast.unparse(node)
    
    def _has_decorator(self, node: ast.FunctionDef, decorator_name: str) -> bool:
        """Check if a function has a specific decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == decorator_name:
                return True
            if isinstance(decorator, ast.Attribute) and decorator.attr == decorator_name:
                return True
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == decorator_name:
                    return True
                if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == decorator_name:
                    return True
        return False
    
    def get_source_lines(self, node: ast.AST) -> Tuple[int, int]:
        """Get the start and end line numbers for an AST node.
        
        Args:
            node: An AST node.
            
        Returns:
            Tuple of (start_line, end_line).
        """
        return (node.lineno, node.end_lineno or node.lineno)
    
    def get_function_body(self, node: ast.FunctionDef) -> str:
        """Get the source code of a function body.
        
        Args:
            node: A function AST node.
            
        Returns:
            The source code of the function body.
        """
        start, end = self.get_source_lines(node)
        lines = self.source_code.split('\n')
        return '\n'.join(lines[start-1:end])
