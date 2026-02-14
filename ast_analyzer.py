"""AST Analyzer - Analyzes code using Abstract Syntax Trees."""

import ast
from typing import Any, Dict, List, Optional


class ASTAnalyzer:
    """Analyzes Python code using Abstract Syntax Trees."""
    
    def __init__(self):
        self.tree: Optional[ast.AST] = None
        
    def parse(self, source_code: str) -> ast.AST:
        """Parse source code into an AST.
        
        Args:
            source_code: The source code to parse.
            
        Returns:
            The AST tree.
        """
        self.tree = ast.parse(source_code)
        return self.tree
    
    def extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract all function definitions from the AST.
        
        Args:
            tree: The AST tree.
            
        Returns:
            List of function information dictionaries.
        """
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(self._extract_function_info(node))
            elif isinstance(node, ast.AsyncFunctionDef):
                func_info = self._extract_function_info(node)
                func_info['is_async'] = True
                functions.append(func_info)
        
        return functions
    
    def extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract all class definitions from the AST.
        
        Args:
            tree: The AST tree.
            
        Returns:
            List of class information dictionaries.
        """
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(self._extract_class_info(node))
        
        return classes
    
    def extract_imports(self, tree: ast.AST) -> List[Dict[str, str]]:
        """Extract all imports from the AST.
        
        Args:
            tree: The AST tree.
            
        Returns:
            List of import dictionaries.
        """
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'module': alias.name,
                        'name': alias.asname or alias.name,
                        'type': 'import'
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'module': f'{module}.{alias.name}' if module else alias.name,
                        'name': alias.asname or alias.name,
                        'type': 'from_import'
                    })
        
        return imports
    
    def _extract_function_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract detailed information about a function.
        
        Args:
            node: A function AST node.
            
        Returns:
            Dictionary with function information.
        """
        # Extract arguments
        args = []
        for arg in node.args.args:
            arg_info = {'name': arg.arg}
            if arg.annotation:
                arg_info['annotation'] = ast.unparse(arg.annotation)
            args.append(arg_info)
        
        # Extract return type annotation
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)
        
        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            decorators.append(ast.unparse(decorator))
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Calculate complexity (simple cyclomatic complexity)
        complexity = self._calculate_complexity(node)
        
        return {
            'name': node.name,
            'args': args,
            'return_type': return_type,
            'decorators': decorators,
            'docstring': docstring,
            'line_number': node.lineno,
            'complexity': complexity,
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'has_varargs': node.args.vararg is not None,
            'has_kwargs': node.args.kwarg is not None,
            'has_defaults': len(node.args.defaults) > 0
        }
    
    def _extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract detailed information about a class.
        
        Args:
            node: A class AST node.
            
        Returns:
            Dictionary with class information.
        """
        # Extract base classes
        bases = []
        for base in node.bases:
            bases.append(ast.unparse(base))
        
        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._extract_function_info(item))
            elif isinstance(item, ast.AsyncFunctionDef):
                method_info = self._extract_function_info(item)
                method_info['is_async'] = True
                methods.append(method_info)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract class-level attributes
        attributes = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    attributes.append({
                        'name': item.target.id,
                        'annotation': ast.unparse(item.annotation) if item.annotation else None
                    })
        
        return {
            'name': node.name,
            'bases': bases,
            'methods': methods,
            'attributes': attributes,
            'docstring': docstring,
            'line_number': node.lineno
        }
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function.
        
        Args:
            node: A function AST node.
            
        Returns:
            Cyclomatic complexity value.
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Count decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # and/or operations
                complexity += len(child.values) - 1
        
        return complexity
    
    def get_function_calls(self, tree: ast.AST) -> List[str]:
        """Get all function calls in the code.
        
        Args:
            tree: The AST tree.
            
        Returns:
            List of function call names.
        """
        calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
        
        return calls
    
    def get_dependencies(self, tree: ast.AST) -> List[str]:
        """Get all module dependencies.
        
        Args:
            tree: The AST tree.
            
        Returns:
            List of module names.
        """
        dependencies = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.add(node.module.split('.')[0])
        
        return list(dependencies)
