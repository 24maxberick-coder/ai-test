#!/usr/bin/env python3
"""
Auto AI Testing Script

Continuously analyzes this repository to surface quality/performance metrics and
produce actionable improvement suggestions. Designed to be run locally, from a
Flask endpoint, and in CI (GitHub Actions).

Key capabilities:
- Discover Python files and perform lightweight static checks
- Syntax validation via compile()
- Simple code quality estimate using comment ratio and file size
- Import-time performance probing per module
- Optional pytest execution if a tests/ directory exists
- Consolidated JSON report saved to ai_test_report.json
"""

from __future__ import annotations

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any


class AutoAI:
    """Core analysis engine for repository assessment."""

    def __init__(self) -> None:
        # CWD is assumed to be the repo root in CI and app integration
        self.repo_root: Path = Path.cwd()

        # Store raw test outputs or future checks (not used yet but reserved)
        self.test_results: List[str] = []

        # Collected suggestions across checks; deduplicated later
        self.suggestions: List[str] = []

        # Aggregate metrics updated during run_full_analysis()
        self.metrics: Dict[str, Any] = {
            "tests_run": 0,            # number of individual checks performed
            "tests_passed": 0,         # number of checks passed
            "tests_failed": 0,         # number of checks failed
            "code_quality_score": 0.0, # average per-file quality score (0-100)
            "performance_score": 0.0,  # average per-file perf score (0-100)
        }

    def discover_python_files(self) -> List[Path]:
        """Discover all Python files in the repository, excluding virtual envs/cache."""
        python_files: List[Path] = []
        for file in self.repo_root.rglob("*.py"):
            p = str(file)
            if "venv" in p or "/.venv" in p or "__pycache__" in p:
                continue
            python_files.append(file)
        return python_files

    def run_syntax_check(self, file_path: Path) -> Tuple[bool, str]:
        """Check Python syntax for a file by compiling its source in memory."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            compile(source, str(file_path), "exec")
            return True, "Syntax OK"
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"
        except Exception as e:
            # Treat other IO/codec issues as failures with a message
            return False, f"Read/Compile Error: {e}"

    def analyze_code_complexity(self, file_path: Path) -> int:
        """Very simple, explainable code quality proxy based on comments and size.

        Heuristics:
        - Start at 100 and subtract points for low comment ratio and very large files
        - Encourage maintainability by nudging more comments and smaller modules
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))
            comment_lines = sum(1 for line in lines if line.strip().startswith("#"))

            complexity_score = 100
            if total_lines > 0:
                comment_ratio = comment_lines / total_lines
                if comment_ratio < 0.1:
                    complexity_score -= 20
                    self.suggestions.append(f"Add more comments to {file_path.name}")
                if code_lines > 500:
                    complexity_score -= 15
                    self.suggestions.append(f"Consider splitting {file_path.name} into smaller modules")

            return max(0, min(100, complexity_score))
        except Exception:
            # On read errors, return a conservative mid/low score
            return 50

    def run_unit_tests(self) -> Tuple[Optional[bool], str]:
        """Execute pytest if tests/ or test/ directories exist.

        Returns:
            (None, msg) when no tests are found
            (True, stdout) when tests pass
            (False, stdout_or_error) when tests fail or errors occur
        """
        test_dirs = ["tests", "test"]
        for test_dir in test_dirs:
            test_path = self.repo_root / test_dir
            if test_path.exists():
                try:
                    result = subprocess.run(
                        ["python", "-m", "pytest", str(test_path), "-v"],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=str(self.repo_root),
                    )
                    return result.returncode == 0, result.stdout
                except Exception as e:
                    return False, f"Test execution error: {e}"
        return None, "No test directory found"

    def check_performance(self, file_path: Path) -> int:
        """Basic performance proxy: time the module import in a subprocess.

        Thresholds:
        - < 1.0s: 100
        - 1.0s - 2.0s: 80
        - > 2.0s: 60 (+ suggestion)
        """
        try:
            start_time = time.time()
            subprocess.run(
                ["python", "-c", f"import {file_path.stem}"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(file_path.parent),
            )
            elapsed = time.time() - start_time

            if elapsed > 2.0:
                self.suggestions.append(f"{file_path.name} has slow import time ({elapsed:.2f}s)")
                return 60
            if elapsed > 1.0:
                return 80
            return 100
        except Exception:
            # If import fails (e.g., dependency or side-effect), return neutral-ish score
            return 75

    def generate_improvement_suggestions(self) -> List[str]:
        """Combine inline suggestions with general best practices based on metrics."""
        suggestions = list(set(self.suggestions))  # remove duplicates

        # Repository-wide checks
        python_files = self.discover_python_files()
        has_tests = any("/test" in str(f) or "/tests" in str(f) for f in python_files)
        has_requirements = (self.repo_root / "requirements.txt").exists()
        has_readme = (self.repo_root / "README.md").exists()

        if not has_tests:
            suggestions.append("Create a tests directory with unit tests")
        if not has_requirements:
            suggestions.append("Add requirements.txt for dependency management")
        if not has_readme:
            suggestions.append("Add comprehensive README.md documentation")

        # Performance nudge
        if self.metrics.get("performance_score", 0) < 70:
            suggestions.append("Optimize slow-loading modules")

        # Code quality nudges
        if self.metrics.get("code_quality_score", 0) < 75:
            suggestions.append("Improve code documentation and structure")
            suggestions.append("Consider using linting tools (pylint, flake8)")

        return suggestions

    def run_full_analysis(self) -> None:
        """Execute all checks and print a console report, then persist JSON file."""
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

            # Syntax check increments tests counters
            syntax_ok, syntax_msg = self.run_syntax_check(py_file)
            if syntax_ok:
                print("  ✓ Syntax check passed")
                self.metrics["tests_passed"] += 1
            else:
                print(f"  ✗ Syntax check failed: {syntax_msg}")
                self.metrics["tests_failed"] += 1

            # Complexity/quality
            complexity_score = self.analyze_code_complexity(py_file)
            total_quality_score += complexity_score
            print(f"  ✓ Code quality score: {complexity_score}/100")

            # Performance
            perf_score = self.check_performance(py_file)
            total_performance_score += perf_score
            print(f"  ✓ Performance score: {perf_score}/100")

            # Three checks per file
            self.metrics["tests_run"] += 3
            print()

        # Unit tests (optional)
        print("Running unit tests...")
        test_result, test_output = self.run_unit_tests()
        if test_result is None:
            print("  ⚠ No tests found")
        elif test_result:
            print("  ✓ All unit tests passed")
            self.metrics["tests_passed"] += 1
        else:
            print("  ✗ Some unit tests failed")
            self.metrics["tests_failed"] += 1

        # Calculate aggregates
        if python_files:
            self.metrics["code_quality_score"] = total_quality_score / len(python_files)
            self.metrics["performance_score"] = total_performance_score / len(python_files)

        # Generate and emit final report
        self.print_report()

    def print_report(self) -> None:
        """Print summary to stdout and persist JSON report."""
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

        # Overall
        overall_score = (
            float(self.metrics['code_quality_score']) + float(self.metrics['performance_score'])
        ) / 2.0
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

        # Suggestions
        suggestions = self.generate_improvement_suggestions()
        if suggestions:
            print(f"\nAI-Powered Improvement Suggestions ({len(suggestions)}):")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")

        print("\n" + "=" * 60)
        print(f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Persist
        self.save_report(suggestions, overall_score)

    def save_report(self, suggestions: List[str], overall_score: float) -> None:
        """Serialize the aggregated results to ai_test_report.json at repo root."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "overall_score": overall_score,
            "suggestions": suggestions,
        }

        report_file = self.repo_root / "ai_test_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\nDetailed report saved to: {report_file}")


def main() -> int:
    """Entrypoint wrapper for robust CLI/CI execution."""
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


if __name__ == "__main__":
    sys.exit(main())
