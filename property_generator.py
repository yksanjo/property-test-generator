"""Property-Based Test Generator - Generates property-based tests using Hypothesis."""

from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


class PropertyBasedTestGenerator:
    """Generates property-based tests using Hypothesis."""
    
    def __init__(self):
        self.test_count = 0
        
    def generate(self, analysis: Dict[str, Any], output_path: Path) -> List[str]:
        """Generate property-based tests based on analysis results.
        
        Args:
            analysis: Analysis results containing functions and classes.
            output_path: Path to output directory for test files.
            
        Returns:
            List of generated test file paths.
        """
        generated_files = []
        
        functions = analysis.get('functions', [])
        classes = analysis.get('classes', [])
        
        # Generate property-based tests for functions
        if functions:
            test_file = self._generate_function_property_tests(functions, output_path)
            if test_file:
                generated_files.append(test_file)
        
        # Generate property-based tests for classes
        if classes:
            test_file = self._generate_class_property_tests(classes, output_path)
            if test_file:
                generated_files.append(test_file)
        
        return generated_files
    
    def _generate_function_property_tests(
        self, 
        functions: List[Dict], 
        output_path: Path
    ) -> str:
        """Generate property-based tests for functions.
        
        Args:
            functions: List of function information.
            output_path: Path to output directory.
            
        Returns:
            Path to generated test file.
        """
        test_file = output_path / "test_property_functions.py"
        
        test_content = []
        test_content.append('"""Property-based tests for functions using Hypothesis."""')
        test_content.append('')
        test_content.append('from hypothesis import given, settings, assume')
        test_content.append('from hypothesis import strategies as st')
        test_content.append('import pytest')
        test_content.append('')
        
        for func in functions:
            # Skip private functions
            func_name = func.get('name', '')
            if func_name.startswith('_') and not func_name.startswith('__'):
                continue
            
            test_content.extend(self._generate_function_property_test(func))
            test_content.append('')
        
        # Write test file
        with open(test_file, 'w') as f:
            f.write('\n'.join(test_content))
        
        return str(test_file)
    
    def _generate_function_property_test(self, func: Dict) -> List[str]:
        """Generate property-based test for a single function.
        
        Args:
            func: Function information dictionary.
            
        Returns:
            List of test case code lines.
        """
        func_name = func.get('name', 'unknown')
        args = func.get('args', [])
        
        test_cases = []
        
        # Generate strategies for each argument
        strategies = []
        for arg in args:
            arg_name = arg.get('name', 'arg')
            arg_type = arg.get('annotation', '')
            strategy = self._get_strategy_for_type(arg_type, arg_name)
            strategies.append(strategy)
        
        # Generate property test
        test_cases.append(f'@given(')
        for i, strategy in enumerate(strategies):
            if i > 0:
                test_cases[-1] += ', '
            arg_name = args[i].get('name', f'arg{i}')
            test_cases.append(f'    {arg_name}={strategy}')
        test_cases.append(')')
        test_cases.append('@settings(max_examples=100)')
        test_cases.append(f'def test_{func_name}_propertybased({", ".join([a.get("name", f"arg{i}") for i, a in enumerate(args)])}):')
        test_cases.append(f'    """Property-based test for {func_name}."""')
        
        # Add assumptions for valid inputs
        test_cases.extend(self._generate_assumptions(func))
        
        # Call the function
        call_args = ', '.join([a.get('name', f'arg{i}') for i, a in enumerate(args)])
        test_cases.append(f'    result = {func_name}({call_args})')
        
        # Add property assertions
        test_cases.extend(self._generate_property_assertions(func))
        
        test_cases.append('')
        
        # Generate inverse property tests
        test_cases.extend(self._generate_inverse_property_test(func))
        
        # Generate consistency property tests
        test_cases.extend(self._generate_consistency_property_test(func))
        
        return test_cases
    
    def _generate_assumptions(self, func: Dict) -> List[str]:
        """Generate Hypothesis assumptions for valid inputs.
        
        Args:
            func: Function information dictionary.
            
        Returns:
            List of assumption code lines.
        """
        assumptions = []
        args = func.get('args', [])
        
        for arg in args:
            arg_type = arg.get('annotation', '')
            arg_name = arg.get('name', '')
            
            # Add assumptions based on type
            if arg_type in ['int', 'float']:
                assumptions.append(f'    assume({arg_name} is not None)')
                assumptions.append(f'    assume(not (isinstance({arg_name}, float) and ({arg_name} != {arg_name})))')  # Not NaN
            elif arg_type in ['str', 'String']:
                assumptions.append(f'    assume({arg_name} is not None)')
        
        return assumptions
    
    def _generate_property_assertions(self, func: Dict) -> List[str]:
        """Generate property assertions for a function.
        
        Args:
            func: Function information dictionary.
            
        Returns:
            List of assertion code lines.
        """
        assertions = []
        func_name = func.get('name', 'unknown')
        
        # Generic property assertions
        assertions.append(f'    # Property: Result should not be None for valid inputs')
        assertions.append(f'    # assert result is not None')
        assertions.append('')
        
        # Type-specific properties
        return_type = func.get('return_type', '')
        if return_type in ['int', 'float']:
            assertions.append(f'    # Property: Result should be a number')
            assertions.append(f'    # assert isinstance(result, (int, float))')
        elif return_type in ['str', 'String']:
            assertions.append(f'    # Property: Result should be a string')
            assertions.append(f'    # assert isinstance(result, str)')
        elif return_type in ['bool', 'Boolean']:
            assertions.append(f'    # Property: Result should be a boolean')
            assertions.append(f'    # assert isinstance(result, bool)')
        
        return assertions
    
    def _generate_inverse_property_test(self, func: Dict) -> List[str]:
        """Generate inverse property test.
        
        Args:
            func: Function information dictionary.
            
        Returns:
            List of test code lines.
        """
        func_name = func.get('name', 'unknown')
        
        # Check if function name suggests invertibility
        if any(keyword in func_name.lower() for keyword in ['encode', 'encrypt', 'serialize']):
            test = []
            test.append(f'@given(value=st.text())')
            test.append('@settings(max_examples=50)')
            test.append(f'def test_{func_name}_inverse_property(value):')
            test.append(f'    """Test inverse property: decode(encode(x)) == x."""')
            test.append(f'    # encoded = {func_name}(value)')
            test.append(f'    # decoded = decode(encoded)')
            test.append(f'    # assert decoded == value')
            test.append('')
            return test
        
        return []
    
    def _generate_consistency_property_test(self, func: Dict) -> List[str]:
        """Generate consistency property test.
        
        Args:
            func: Function information dictionary.
            
        Returns:
            List of test code lines.
        """
        func_name = func.get('name', 'unknown')
        
        test = []
        test.append(f'@given(value=st.integers(min_value=0, max_value=100))')
        test.append('@settings(max_examples=50)')
        test.append(f'def test_{func_name}_consistency(value):')
        test.append(f'    """Test consistency: Same input should give same output."""')
        test.append(f'    # result1 = {func_name}(value)')
        test.append(f'    # result2 = {func_name}(value)')
        test.append(f'    # assert result1 == result2')
        test.append('')
        
        return test
    
    def _get_strategy_for_type(self, type_hint: str, arg_name: str) -> str:
        """Get Hypothesis strategy for a given type hint.
        
        Args:
            type_hint: The type hint string.
            arg_name: Name of the argument.
            
        Returns:
            Hypothesis strategy as a string.
        """
        # Handle Optional types
        if 'Optional[' in type_hint:
            type_hint = type_hint.replace('Optional[', '').rstrip(']')
        
        # Handle Union types
        if 'Union[' in type_hint:
            return f'st.one_of({self._get_strategy_for_type("int", arg_name)}, st.none())'
        
        type_mapping = {
            'int': 'st.integers(min_value=-1000, max_value=1000)',
            'float': 'st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)',
            'str': 'st.text(min_size=0, max_size=100)',
            'bool': 'st.booleans()',
            'list': 'st.lists(st.integers(), max_size=10)',
            'List': 'st.lists(st.integers(), max_size=10)',
            'dict': 'st.dictionaries(st.text(), st.integers(), max_size=10)',
            'Dict': 'st.dictionaries(st.text(), st.integers(), max_size=10)',
            'set': 'st.sets(st.integers(), max_size=10)',
            'Set': 'st.sets(st.integers(), max_size=10)',
            'tuple': 'st.tuples(st.integers(), st.integers())',
            'Tuple': 'st.tuples(st.integers(), st.integers())',
            'bytes': 'st.binary(min_size=0, max_size=100)',
            'bytearray': 'st.binary(min_size=0, max_size=100)',
        }
        
        return type_mapping.get(type_hint, 'st.none()')
    
    def _generate_class_property_tests(
        self, 
        classes: List[Dict], 
        output_path: Path
    ) -> str:
        """Generate property-based tests for classes.
        
        Args:
            classes: List of class information.
            output_path: Path to output directory.
            
        Returns:
            Path to generated test file.
        """
        test_file = output_path / "test_property_classes.py"
        
        test_content = []
        test_content.append('"""Property-based tests for classes using Hypothesis."""')
        test_content.append('')
        test_content.append('from hypothesis import given, settings, assume')
        test_content.append('from hypothesis import strategies as st')
        test_content.append('import pytest')
        test_content.append('')
        
        for cls in classes:
            class_name = cls.get('name', '')
            if class_name.startswith('_'):
                continue
            
            test_content.extend(self._generate_class_property_test(cls))
            test_content.append('')
        
        # Write test file
        with open(test_file, 'w') as f:
            f.write('\n'.join(test_content))
        
        return str(test_file)
    
    def _generate_class_property_test(self, cls: Dict) -> List[str]:
        """Generate property-based test for a class.
        
        Args:
            cls: Class information dictionary.
            
        Returns:
            List of test case code lines.
        """
        class_name = cls.get('name', 'unknown')
        
        test_cases = []
        
        # Test initialization property
        test_cases.append('@given(data=st.data())')
        test_cases.append('@settings(max_examples=50)')
        test_cases.append(f'def test_{class_name}_initialization_property(data):')
        test_cases.append(f'    """Property-based test for {class_name} initialization."""')
        test_cases.append(f'    # Test that class can be initialized with valid inputs')
        test_cases.append(f'    # Add your initialization strategies')
        test_cases.append('')
        
        # Test method properties
        methods = cls.get('methods', [])
        for method in methods:
            method_name = method.get('name', '')
            if method_name.startswith('_') and not method_name.startswith('__'):
                continue
            if method_name == '__init__':
                continue
                
            test_cases.extend(self._generate_method_property_test(class_name, method))
        
        return test_cases
    
    def _generate_method_property_test(
        self, 
        class_name: str, 
        method: Dict
    ) -> List[str]:
        """Generate property-based test for a class method.
        
        Args:
            class_name: Name of the class.
            method: Method information dictionary.
            
        Returns:
            List of test case code lines.
        """
        method_name = method.get('name', 'unknown')
        
        test_cases = []
        
        test_cases.append(f'@given(value=st.integers())')
        test_cases.append('@settings(max_examples=50)')
        test_cases.append(f'def test_{class_name}_{method_name}_property(value):')
        test_cases.append(f'    """Property-based test for {class_name}.{method_name}."""')
        test_cases.append(f'    # instance = {class_name}()')
        test_cases.append(f'    # result = instance.{method_name}(value)')
        test_cases.append(f'    # assert result is not None  # Add property assertions')
        test_cases.append('')
        
        return test_cases
