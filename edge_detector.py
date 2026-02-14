"""Edge Case Detector - Identifies edge cases in code for testing."""

from typing import Any, Dict, List


class EdgeCaseDetector:
    """Detects potential edge cases in functions and classes."""
    
    def __init__(self):
        self.edge_case_patterns = {
            'division': [
                'division by zero',
                'integer division overflow',
                'floating point precision'
            ],
            'collections': [
                'empty collection',
                'single element collection',
                'very large collection',
                'collection with duplicates'
            ],
            'strings': [
                'empty string',
                'very long string',
                'string with special characters',
                'string with unicode',
                'string with whitespace'
            ],
            'numbers': [
                'zero',
                'negative numbers',
                'maximum integer value',
                'minimum integer value',
                'very large numbers',
                'floating point edge values'
            ],
            'booleans': [
                'true',
                'false',
                'boolean coercion'
            ],
            'none': [
                'None value',
                'null value',
                'undefined'
            ],
            'types': [
                'type conversion',
                'invalid type',
                'type coercion'
            ],
            'loops': [
                'zero iterations',
                'single iteration',
                'very large iteration count',
                'infinite loop potential'
            ],
            'recursion': [
                'base case',
                'deep recursion',
                'recursive call without base case'
            ],
            'io': [
                'empty file',
                'very large file',
                'file not found',
                'permission denied',
                'network timeout'
            ]
        }
    
    def detect(self, functions: List[Dict], classes: List[Dict]) -> List[str]:
        """Detect edge cases in functions and classes.
        
        Args:
            functions: List of function information.
            classes: List of class information.
            
        Returns:
            List of detected edge cases.
        """
        edge_cases = []
        
        # Analyze each function
        for func in functions:
            edge_cases.extend(self._detect_function_edge_cases(func))
        
        # Analyze each class
        for cls in classes:
            edge_cases.extend(self._detect_class_edge_cases(cls))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_edge_cases = []
        for case in edge_cases:
            if case not in seen:
                seen.add(case)
                unique_edge_cases.append(case)
        
        return unique_edge_cases
    
    def _detect_function_edge_cases(self, func: Dict) -> List[str]:
        """Detect edge cases for a specific function.
        
        Args:
            func: Function information dictionary.
            
        Returns:
            List of edge cases.
        """
        edge_cases = []
        func_name = func.get('name', 'unknown')
        
        # Check function name for hints
        if any(keyword in func_name.lower() for keyword in ['divide', 'div', '/']):
            edge_cases.append(f"{func_name}: division by zero")
            edge_cases.append(f"{func_name}: integer overflow in division")
        
        if any(keyword in func_name.lower() for keyword in ['sort', 'order', 'unique']):
            edge_cases.append(f"{func_name}: empty collection")
            edge_cases.append(f"{func_name}: single element collection")
            edge_cases.append(f"{func_name}: collection with duplicates")
        
        if any(keyword in func_name.lower() for keyword in ['find', 'search', 'index', 'get']):
            edge_cases.append(f"{func_name}: item not found")
            edge_cases.append(f"{func_name}: empty collection")
        
        if any(keyword in func_name.lower() for keyword in ['parse', 'convert', 'encode', 'decode']):
            edge_cases.append(f"{func_name}: empty string input")
            edge_cases.append(f"{func_name}: invalid input format")
            edge_cases.append(f"{func_name}: very long input")
        
        if any(keyword in func_name.lower() for keyword in ['read', 'load', 'fetch', 'get']):
            edge_cases.append(f"{func_name}: empty file/data")
            edge_cases.append(f"{func_name}: file not found")
            edge_cases.append(f"{func_name}: permission denied")
        
        if any(keyword in func_name.lower() for keyword in ['write', 'save', 'store']):
            edge_cases.append(f"{func_name}: write to read-only location")
            edge_cases.append(f"{func_name}: disk full")
        
        # Check arguments for type hints
        args = func.get('args', [])
        for arg in args:
            arg_name = arg.get('name', '')
            arg_type = arg.get('annotation', '')
            
            # Numeric arguments
            if arg_type in ['int', 'float', 'number']:
                edge_cases.append(f"{func_name}: {arg_name} = 0")
                edge_cases.append(f"{func_name}: {arg_name} = negative")
                edge_cases.append(f"{func_name}: {arg_name} = very large")
            
            # String arguments
            if arg_type in ['str', 'string']:
                edge_cases.append(f"{func_name}: {arg_name} = empty string")
                edge_cases.append(f"{func_name}: {arg_name} = very long string")
                edge_cases.append(f"{func_name}: {arg_name} = special characters")
            
            # Collection arguments
            if arg_type in ['list', 'set', 'dict', 'List', 'Set', 'Dict', 'Collection']:
                edge_cases.append(f"{func_name}: {arg_name} = empty collection")
                edge_cases.append(f"{func_name}: {arg_name} = very large collection")
        
        # Check return type
        return_type = func.get('return_type')
        if return_type:
            if return_type in ['int', 'float']:
                edge_cases.append(f"{func_name}: return zero")
                edge_cases.append(f"{func_name}: return negative value")
        
        # Check for potential issues based on complexity
        complexity = func.get('complexity', 0)
        if complexity > 10:
            edge_cases.append(f"{func_name}: high complexity ({complexity}) - test thoroughly")
        
        # Check for varargs/kwargs
        if func.get('has_varargs'):
            edge_cases.append(f"{func_name}: zero arguments passed to *args")
            edge_cases.append(f"{func_name}: many arguments passed to *args")
        
        if func.get('has_kwargs'):
            edge_cases.append(f"{func_name}: empty kwargs")
            edge_cases.append(f"{func_name}: unexpected kwargs keys")
        
        # Check for async
        if func.get('is_async'):
            edge_cases.append(f"{func_name}: async function - test concurrent calls")
        
        return edge_cases
    
    def _detect_class_edge_cases(self, cls: Dict) -> List[str]:
        """Detect edge cases for a specific class.
        
        Args:
            cls: Class information dictionary.
            
        Returns:
            List of edge cases.
        """
        edge_cases = []
        class_name = cls.get('name', 'unknown')
        
        # Check for initialization
        edge_cases.append(f"{class_name}: initialization with invalid parameters")
        edge_cases.append(f"{class_name}: initialization with None")
        
        # Check methods
        methods = cls.get('methods', [])
        for method in methods:
            method_name = method.get('name', '')
            
            # Constructor
            if method_name == '__init__':
                edge_cases.append(f"{class_name}: create instance with no arguments")
                edge_cases.append(f"{class_name}: create instance with extra arguments")
            
            # Property access
            if method_name.startswith('__get'):
                edge_cases.append(f"{class_name}: access non-existent attribute")
            
            # String representation
            if method_name in ['__str__', '__repr__']:
                edge_cases.append(f"{class_name}: string representation of edge case instances")
        
        return edge_cases
    
    def generate_edge_case_tests(self, func: Dict) -> List[Dict]:
        """Generate test cases for detected edge cases.
        
        Args:
            func: Function information dictionary.
            
        Returns:
            List of test case dictionaries.
        """
        test_cases = []
        edge_cases = self._detect_function_edge_cases(func)
        
        for edge_case in edge_cases:
            test_case = {
                'name': edge_case,
                'description': f"Test case for {edge_case}",
                'type': 'edge_case'
            }
            test_cases.append(test_case)
        
        return test_cases
