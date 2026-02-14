#!/usr/bin/env python3
"""
Property-Based Test Generator - Generates property-based tests using Hypothesis.

This tool creates property-based tests that verify code properties across
many random inputs.
"""

import argparse
import ast
from pathlib import Path
from typing import Any, Dict, List
from generators.property_generator import PropertyBasedTestGenerator as BaseGenerator


class PropertyTestGenerator:
    """Main class for property-based test generation."""
    
    def __init__(self):
        self.generator = BaseGenerator()
        
    def generate(self, source_path: Path, output_path: Path) -> List[str]:
        """Generate property-based tests from source code.
        
        Args:
            source_path: Path to source file or directory.
            output_path: Path to output directory for tests.
            
        Returns:
            List of generated test file paths.
        """
        # Parse source files
        if source_path.is_file():
            files = [source_path]
        else:
            files = list(source_path.rglob("*.py"))
        
        analysis = {
            "files": [],
            "functions": [],
            "classes": []
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                tree = ast.parse(source_code)
                
                # Extract functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_info = {
                            "name": node.name,
                            "args": [{"name": arg.arg, "annotation": ast.unparse(arg.annotation) if arg.annotation else ""} for arg in node.args.args],
                            "return_type": ast.unparse(node.returns) if node.returns else None
                        }
                        analysis["functions"].append(func_info)
                
                # Extract classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_info = {
                            "name": node.name,
                            "methods": []
                        }
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                class_info["methods"].append({
                                    "name": item.name
                                })
                        analysis["classes"].append(class_info)
                        
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        # Generate tests
        output_path.mkdir(parents=True, exist_ok=True)
        generated = self.generator.generate(analysis, output_path)
        
        return generated


def main():
    parser = argparse.ArgumentParser(description="Property-Based Test Generator")
    parser.add_argument("--source", required=True, help="Source code path")
    parser.add_argument("--output", default="./tests", help="Output directory")
    
    args = parser.parse_args()
    
    generator = PropertyTestGenerator()
    source = Path(args.source)
    output = Path(args.output)
    
    print(f"Generating property-based tests from: {source}")
    print(f"Output directory: {output}")
    
    generated = generator.generate(source, output)
    
    print(f"\nGenerated {len(generated)} test files:")
    for f in generated:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
