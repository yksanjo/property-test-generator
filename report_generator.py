"""Report Generator - Generate detailed reports for test generation."""

import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    """Generate detailed reports for test generation and execution."""
    
    def __init__(self):
        self.timestamp = datetime.now().isoformat()
        
    def generate(
        self,
        analysis: Dict[str, Any],
        generated_tests: List[str],
        test_results: Dict[str, Any]
    ) -> str:
        """Generate a comprehensive report.
        
        Args:
            analysis: Analysis results from code analysis.
            generated_tests: List of generated test files.
            test_results: Test execution results.
            
        Returns:
            The generated report as a string.
        """
        report = []
        report.append("=" * 70)
        report.append("SMART TEST GENERATOR REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {self.timestamp}")
        report.append("")
        
        # Analysis Summary
        report.append("-" * 70)
        report.append("CODE ANALYSIS SUMMARY")
        report.append("-" * 70)
        report.append(f"Files analyzed: {len(analysis.get('files', []))}")
        report.append(f"Functions found: {len(analysis.get('functions', []))}")
        report.append(f"Classes found: {len(analysis.get('classes', []))}")
        report.append(f"Edge cases detected: {len(analysis.get('edge_cases', []))}")
        report.append(f"Failure modes detected: {len(analysis.get('failure_modes', []))}")
        report.append("")
        
        # Edge Cases
        if analysis.get('edge_cases'):
            report.append("-" * 70)
            report.append("DETECTED EDGE CASES")
            report.append("-" * 70)
            for edge_case in analysis['edge_cases'][:10]:  # Limit to first 10
                report.append(f"  • {edge_case}")
            if len(analysis['edge_cases']) > 10:
                report.append(f"  ... and {len(analysis['edge_cases']) - 10} more")
            report.append("")
        
        # Failure Modes
        if analysis.get('failure_modes'):
            report.append("-" * 70)
            report.append("DETECTED FAILURE MODES")
            report.append("-" * 70)
            for failure_mode in analysis['failure_modes'][:10]:
                report.append(f"  • {failure_mode}")
            if len(analysis['failure_modes']) > 10:
                report.append(f"  ... and {len(analysis['failure_modes']) - 10} more")
            report.append("")
        
        # Generated Tests
        report.append("-" * 70)
        report.append("GENERATED TESTS")
        report.append("-" * 70)
        report.append(f"Total tests generated: {len(generated_tests)}")
        for test_file in generated_tests:
            report.append(f"  • {test_file}")
        report.append("")
        
        # Test Results
        if test_results:
            report.append("-" * 70)
            report.append("TEST EXECUTION RESULTS")
            report.append("-" * 70)
            report.append(f"Tests passed: {test_results.get('passed', 0)}")
            report.append(f"Tests failed: {test_results.get('failed', 0)}")
            report.append(f"Tests skipped: {test_results.get('skipped', 0)}")
            
            if test_results.get('failed_tests'):
                report.append("")
                report.append("Failed Tests:")
                for failed in test_results['failed_tests']:
                    report.append(f"  ❌ {failed}")
        
        report.append("")
        report.append("=" * 70)
        report.append("END OF REPORT")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def generate_json(
        self,
        analysis: Dict[str, Any],
        generated_tests: List[str],
        test_results: Dict[str, Any]
    ) -> str:
        """Generate a JSON report.
        
        Args:
            analysis: Analysis results from code analysis.
            generated_tests: List of generated test files.
            test_results: Test execution results.
            
        Returns:
            The generated report as a JSON string.
        """
        report_data = {
            "timestamp": self.timestamp,
            "analysis": {
                "files": analysis.get('files', []),
                "function_count": len(analysis.get('functions', [])),
                "class_count": len(analysis.get('classes', [])),
                "edge_cases": analysis.get('edge_cases', []),
                "failure_modes": analysis.get('failure_modes', [])
            },
            "generated_tests": generated_tests,
            "test_results": test_results
        }
        
        return json.dumps(report_data, indent=2)
    
    def generate_html(
        self,
        analysis: Dict[str, Any],
        generated_tests: List[str],
        test_results: Dict[str, Any]
    ) -> str:
        """Generate an HTML report.
        
        Args:
            analysis: Analysis results from code analysis.
            generated_tests: List of generated test files.
            test_results: Test execution results.
            
        Returns:
            The generated report as an HTML string.
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Test Generator Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat {{
            display: inline-block;
            background: #e8f4f8;
            padding: 15px 25px;
            border-radius: 8px;
            margin: 10px 10px 10px 0;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .test-pass {{
            color: #10b981;
        }}
        .test-fail {{
            color: #ef4444;
        }}
        ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        li {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Smart Test Generator Report</h1>
        <p>Generated: {self.timestamp}</p>
    </div>
    
    <div class="section">
        <h2>📊 Analysis Summary</h2>
        <div class="stat">
            <div class="stat-value">{len(analysis.get('files', []))}</div>
            <div class="stat-label">Files Analyzed</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(analysis.get('functions', []))}</div>
            <div class="stat-label">Functions</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(analysis.get('classes', []))}</div>
            <div class="stat-label">Classes</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(analysis.get('edge_cases', []))}</div>
            <div class="stat-label">Edge Cases</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(analysis.get('failure_modes', []))}</div>
            <div class="stat-label">Failure Modes</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📝 Generated Tests</h2>
        <p>Total: {len(generated_tests)} tests</p>
        <ul>
"""
        
        for test_file in generated_tests:
            html += f'            <li>📄 {test_file}</li>\n'
        
        html += """        </ul>
    </div>
"""
        
        if test_results:
            html += f"""    <div class="section">
        <h2>🧪 Test Results</h2>
        <div class="stat">
            <div class="stat-value test-pass">{test_results.get('passed', 0)}</div>
            <div class="stat-label">Passed</div>
        </div>
        <div class="stat">
            <div class="stat-value test-fail">{test_results.get('failed', 0)}</div>
            <div class="stat-label">Failed</div>
        </div>
        <div class="stat">
            <div class="stat-value">{test_results.get('skipped', 0)}</div>
            <div class="stat-label">Skipped</div>
        </div>
    </div>
"""
        
        html += """</body>
</html>"""
        
        return html
