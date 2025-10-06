#!/usr/bin/env python3
"""
Auto AI Testing Script
Automatically tests code in the repository, analyzes results, and suggests improvements.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path


class AutoAI:
    def __init__(self):
        self.repo_root = Path.cwd()
        self.test_results = []
        self.suggestions = []
        self.metrics = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'code_quality_score': 0,
            'performance_score': 0
        }

    def discover_python_files(self):
        """Discover all Python files in the repository."""
        python_files = []
        for file in self.repo_root.rglob('*.py'):
            if 'venv' not in str(file) and '__pycache__' not in str(file):
                python_files.append(file)
        return python_files

    def run_syntax_check(self, file_path):
        """Check Python syntax for a file."""
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            return True, "Syntax OK"
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"

    def analyze_code_complexity(self, file_path):
        """Analyze code complexity metrics."""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            
            # Calculate complexity score (simple metric)
            complexity_score = 100
            if total_lines > 0:
                comment_ratio = comment_lines / total_lines
                if comment_ratio < 0.1:
                    complexity_score -= 20
                    self.suggestions.append(f"Add more comments to {file_path.name}")
                
                if code_lines > 500:
                    complexity_score -= 15
                    self.suggestions.append(f"Consider splitting {file_path.name} into smaller modules")
            
            return complexity_score
        except Exception as e:
            return 50

    def run_unit_tests(self):
        """Run unit tests if they exist."""
        test_dirs = ['tests', 'test']
        for test_dir in test_dirs:
            test_path = self.repo_root / test_dir
            if test_path.exists():
                try:
                    result = subprocess.run(
                        ['python', '-m', 'pytest', str(test_path), '-v'],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    return result.returncode == 0, result.stdout
                except Exception as e:
                    return False, f"Test execution error: {e}"
        return None, "No test directory found"

    def check_performance(self, file_path):
        """Basic performance check by timing imports."""
        try:
            start_time = time.time()
            result = subprocess.run(
                ['python', '-c', f'import {file_path.stem}'],
                capture_output=True,
                timeout=5,
                cwd=file_path.parent
            )
            elapsed = time.time() - start_time
            
            if elapsed > 2.0:
                self.suggestions.append(f"{file_path.name} has slow import time ({elapsed:.2f}s)")
                return 60
            elif elapsed > 1.0:
                return 80
            else:
                return 100
        except Exception:
            return 75

    def generate_improvement_suggestions(self):
        """Generate AI-powered improvement suggestions."""
        suggestions = list(set(self.suggestions))  # Remove duplicates
        
        # Add general best practice suggestions
        python_files = self.discover_python_files()
        
        # Check for common patterns
        has_tests = any('test' in str(f) for f in python_files)
        has_requirements = (self.repo_root / 'requirements.txt').exists()
        has_readme = (self.repo_root / 'README.md').exists()
        
        if not has_tests:
            suggestions.append("Create a tests directory with unit tests")
        if not has_requirements:
            suggestions.append("Add requirements.txt for dependency management")
        if not has_readme:
            suggestions.append("Add comprehensive README.md documentation")
        
        # Performance suggestions
        if self.metrics['performance_score'] < 70:
            suggestions.append("Optimize slow-loading modules")
        
        # Code quality suggestions
        if self.metrics['code_quality_score'] < 75:
            suggestions.append("Improve code documentation and structure")
            suggestions.append("Consider using linting tools (pylint, flake8)")
        
        return suggestions

    def run_full_analysis(self):
        """Run complete analysis of the repository."""
        print("=" * 60)
        print("AUTO AI TESTING SYSTEM")
        print("=" * 60)
        print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Repository: {self.repo_root}\n")
        
        python_files = self.discover_python_files()
        print(f"Found {len(python_files)} Python files to analyze\n")
        
        total_quality_score = 0
        total_performance_score = 0
        
        for py_file in python_files:
            print(f"Analyzing: {py_file.name}")
            
            # Syntax check
            syntax_ok, syntax_msg = self.run_syntax_check(py_file)
            if syntax_ok:
                print(f"  ✓ Syntax check passed")
                self.metrics['tests_passed'] += 1
            else:
                print(f"  ✗ Syntax check failed: {syntax_msg}")
                self.metrics['tests_failed'] += 1
            
            # Complexity analysis
            complexity_score = self.analyze_code_complexity(py_file)
            total_quality_score += complexity_score
            print(f"  ✓ Code quality score: {complexity_score}/100")
            
            # Performance check
            perf_score = self.check_performance(py_file)
            total_performance_score += perf_score
            print(f"  ✓ Performance score: {perf_score}/100")
            
            self.metrics['tests_run'] += 3
            print()
        
        # Run unit tests
        print("Running unit tests...")
        test_result, test_output = self.run_unit_tests()
        if test_result is None:
            print("  ⚠ No tests found")
        elif test_result:
            print("  ✓ All unit tests passed")
            self.metrics['tests_passed'] += 1
        else:
            print("  ✗ Some unit tests failed")
            self.metrics['tests_failed'] += 1
        
        # Calculate overall scores
        if python_files:
            self.metrics['code_quality_score'] = total_quality_score / len(python_files)
            self.metrics['performance_score'] = total_performance_score / len(python_files)
        
        # Generate report
        self.print_report()

    def print_report(self):
        """Print analysis report with suggestions."""
        print("\n" + "=" * 60)
        print("ANALYSIS REPORT")
        print("=" * 60)
        
        print(f"\nTests Summary:")
        print(f"  Total tests run: {self.metrics['tests_run']}")
        print(f"  Passed: {self.metrics['tests_passed']}")
        print(f"  Failed: {self.metrics['tests_failed']}")
        
        print(f"\nQuality Metrics:")
        print(f"  Code Quality Score: {self.metrics['code_quality_score']:.1f}/100")
        print(f"  Performance Score: {self.metrics['performance_score']:.1f}/100")
        
        # Overall rating
        overall_score = (self.metrics['code_quality_score'] + self.metrics['performance_score']) / 2
        print(f"  Overall Score: {overall_score:.1f}/100")
        
        if overall_score >= 90:
            rating = "Excellent ⭐⭐⭐⭐⭐"
        elif overall_score >= 75:
            rating = "Good ⭐⭐⭐⭐"
        elif overall_score >= 60:
            rating = "Fair ⭐⭐⭐"
        else:
            rating = "Needs Improvement ⭐⭐"
        
        print(f"  Rating: {rating}")
        
        # Improvement suggestions
        suggestions = self.generate_improvement_suggestions()
        if suggestions:
            print(f"\nAI-Powered Improvement Suggestions ({len(suggestions)}):")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        print("\n" + "=" * 60)
        print(f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Save report to file
        self.save_report(suggestions, overall_score)

    def save_report(self, suggestions, overall_score):
        """Save analysis report to JSON file."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'overall_score': overall_score,
            'suggestions': suggestions
        }
        
        report_file = self.repo_root / 'ai_test_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_file}")


def main():
    """Main entry point."""
    try:
        ai = AutoAI()
        ai.run_full_analysis()
        return 0
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nError during analysis: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
