"""Failure Mode Detector - Identifies common failure patterns in code."""

from typing import Any, Dict, List


class FailureModeDetector:
    """Detects common failure modes in functions and classes."""
    
    def __init__(self):
        self.failure_patterns = {
            'null_pointer': [
                'None check missing',
                'null dereference',
                'attribute access on None'
            ],
            'index_error': [
                'index out of bounds',
                'negative index',
                'empty collection access'
            ],
            'type_error': [
                'type mismatch',
                'invalid type conversion',
                'operation on wrong type'
            ],
            'value_error': [
                'invalid argument value',
                'invalid range',
                'invalid format'
            ],
            'io_error': [
                'file not found',
                'permission denied',
                'disk full',
                'network error'
            ],
            'concurrency': [
                'race condition',
                'deadlock',
                'thread safety',
                'concurrent modification'
            ],
            'resource': [
                'memory leak',
                'connection leak',
                'file handle leak',
                'resource exhaustion'
            ],
            'validation': [
                'missing validation',
                'incomplete validation',
                'incorrect validation logic'
            ],
            'error_handling': [
                'bare except',
                'swallowed exception',
                'missing error handling',
                'incorrect error handling'
            ],
            'logic': [
                'off-by-one error',
                'incorrect boundary condition',
                'incorrect loop condition',
                'incorrect comparison'
            ]
        }
    
    def detect(self, functions: List[Dict], classes: List[Dict]) -> List[str]:
        """Detect failure modes in functions and classes.
        
        Args:
            functions: List of function information.
            classes: List of class information.
            
        Returns:
            List of detected failure modes.
        """
        failure_modes = []
        
        # Analyze each function
        for func in functions:
            failure_modes.extend(self._detect_function_failure_modes(func))
        
        # Analyze each class
        for cls in classes:
            failure_modes.extend(self._detect_class_failure_modes(cls))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_failure_modes = []
        for mode in failure_modes:
            if mode not in seen:
                seen.add(mode)
                unique_failure_modes.append(mode)
        
        return unique_failure_modes
    
    def _detect_function_failure_modes(self, func: Dict) -> List[str]:
        """Detect failure modes for a specific function.
        
        Args:
            func: Function information dictionary.
            
        Returns:
            List of failure modes.
        """
        failure_modes = []
        func_name = func.get('name', 'unknown')
        
        # Check function name for hints about potential failures
        if any(keyword in func_name.lower() for keyword in ['get', 'find', 'search']):
            failure_modes.append(f"{func_name}: may return None without indication")
            failure_modes.append(f"{func_name}: may raise exception when not found")
        
        if any(keyword in func_name.lower() for keyword in ['parse', 'load', 'read']):
            failure_modes.append(f"{func_name}: may raise parsing error on invalid input")
            failure_modes.append(f"{func_name}: may not handle malformed data")
        
        if any(keyword in func_name.lower() for keyword in ['delete', 'remove']):
            failure_modes.append(f"{func_name}: may fail silently on non-existent item")
            failure_modes.append(f"{func_name}: may raise exception when item not found")
        
        if any(keyword in func_name.lower() for keyword in ['validate', 'check']):
            failure_modes.append(f"{func_name}: may have incomplete validation")
        
        # Check arguments
        args = func.get('args', [])
        
        # Check for missing validation opportunities
        for arg in args:
            arg_name = arg.get('name', '')
            arg_type = arg.get('annotation', '')
            
            # Check for common missing validations
            if arg_type in ['list', 'List', 'dict', 'Dict', 'set', 'Set']:
                failure_modes.append(f"{func_name}: may not handle empty {arg_name}")
                failure_modes.append(f"{func_name}: may not handle None {arg_name}")
            
            if arg_type in ['int', 'float', 'str', 'bool']:
                failure_modes.append(f"{func_name}: may not validate {arg_name} type")
        
        # Check return type
        return_type = func.get('return_type')
        if return_type:
            # Functions returning Optional should be checked for None
            if 'Optional' in return_type or 'None' in return_type:
                failure_modes.append(f"{func_name}: returns Optional - caller may not check for None")
            
            # Functions returning collections
            if any(t in return_type for t in ['List', 'Dict', 'Set', 'Tuple']):
                failure_modes.append(f"{func_name}: may return empty collection")
        
        # Check for potential concurrency issues
        if func.get('is_async'):
            failure_modes.append(f"{func_name}: async function - potential race condition")
            failure_modes.append(f"{func_name}: async function - missing await points")
        
        # Check for recursion
        func_body = func.get('body', '')
        if 'recursive' in func_name.lower() or 'recursion' in str(func_body).lower():
            failure_modes.append(f"{func_name}: recursive function - stack overflow risk")
            failure_modes.append(f"{func_name}: recursive function - missing base case risk")
        
        # Check complexity for testing difficulty
        complexity = func.get('complexity', 0)
        if complexity > 15:
            failure_modes.append(f"{func_name}: high complexity ({complexity}) - hard to test all paths")
        
        # Check for varargs/kwargs
        if func.get('has_varargs'):
            failure_modes.append(f"{func_name}: *args - may not validate number of arguments")
        
        if func.get('has_kwargs'):
            failure_modes.append(f"{func_name}: **kwargs - may not validate unexpected keys")
        
        return failure_modes
    
    def _detect_class_failure_modes(self, cls: Dict) -> List[str]:
        """Detect failure modes for a specific class.
        
        Args:
            cls: Class information dictionary.
            
        Returns:
            List of failure modes.
        """
        failure_modes = []
        class_name = cls.get('name', 'unknown')
        
        # Check class initialization
        failure_modes.append(f"{class_name}: __init__ may not validate constructor arguments")
        
        # Check methods
        methods = cls.get('methods', [])
        
        for method in methods:
            method_name = method.get('name', '')
            
            # Constructor issues
            if method_name == '__init__':
                failure_modes.append(f"{class_name}: may not handle invalid initialization state")
                failure_modes.append(f"{class_name}: may not handle missing required fields")
            
            # Property access
            if method_name.startswith('__get'):
                failure_modes.append(f"{class_name}: may raise AttributeError on missing attributes")
            
            # Property setting
            if method_name.startswith('__set'):
                failure_modes.append(f"{class_name}: may not validate assigned values")
            
            # Context managers
            if method_name == '__enter__' or method_name == '__exit__':
                failure_modes.append(f"{class_name}: context manager - may not handle exceptions properly")
            
            # String representation
            if method_name in ['__str__', '__repr__']:
                failure_modes.append(f"{class_name}: may raise exception on malformed instance")
            
            # Comparison
            if method_name.startswith('__eq__') or method_name.startswith('__cmp'):
                failure_modes.append(f"{class_name}: comparison may not handle None or different types")
        
        return failure_modes
    
    def get_critical_tests(self, functions: List[Dict], classes: List[Dict]) -> List[Dict]:
        """Get critical test cases based on detected failure modes.
        
        Args:
            functions: List of function information.
            classes: List of class information.
            
        Returns:
            List of critical test cases.
        """
        tests = []
        failure_modes = self.detect(functions, classes)
        
        for mode in failure_modes:
            test = {
                'name': f"Test_{mode.replace(' ', '_').replace(':', '_')}",
                'description': mode,
                'type': 'failure_mode',
                'critical': True
            }
            tests.append(test)
        
        return tests
