#!/usr/bin/env python3
"""
Java 8 Compatibility Validator

Checks Java source files for language features that require Java 9+.
Reports violations with line numbers to help maintain Java 8 compatibility.

Usage:
    python validate_java8.py <path-to-java-file-or-directory>
    python validate_java8.py src/main/java/

Exit codes:
    0 - No violations found
    1 - Violations found
    2 - Error occurred
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


class Java8Validator:
    """Validates Java source files for Java 8 compatibility."""

    # Patterns for Java 9+ features
    PATTERNS = {
        'var_keyword': (
            r'\bvar\s+\w+\s*=',
            'Java 10+ feature: local variable type inference (var)'
        ),
        'switch_expression': (
            r'\bswitch\s*\([^)]+\)\s*\{[^}]*->',
            'Java 14+ feature: switch expressions with arrows'
        ),
        'text_block': (
            r'"""',
            'Java 15+ feature: text blocks (triple quotes)'
        ),
        'pattern_matching_instanceof': (
            r'\binstanceof\s+\w+\s+\w+\s*[^;{]*(?:\{|;)',
            'Java 16+ feature: pattern matching for instanceof'
        ),
        'record_declaration': (
            r'\brecord\s+\w+\s*\(',
            'Java 16+ feature: record types'
        ),
        'sealed_class': (
            r'\bsealed\s+(?:class|interface)',
            'Java 17+ feature: sealed classes'
        ),
    }

    def __init__(self):
        self.violations: List[Tuple[str, int, str, str]] = []

    def validate_file(self, file_path: Path) -> None:
        """Validate a single Java file for Java 8 compatibility."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()

            for pattern_name, (pattern, message) in self.PATTERNS.items():
                for line_num, line in enumerate(lines, start=1):
                    # Skip comments
                    if line.strip().startswith('//') or line.strip().startswith('/*'):
                        continue

                    if re.search(pattern, line):
                        self.violations.append((
                            str(file_path),
                            line_num,
                            message,
                            line.strip()
                        ))

        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)

    def validate_directory(self, dir_path: Path) -> None:
        """Recursively validate all Java files in a directory."""
        for java_file in dir_path.rglob('*.java'):
            self.validate_file(java_file)

    def report(self) -> int:
        """Print validation report and return exit code."""
        if not self.violations:
            print("✓ No Java 8 compatibility violations found")
            return 0

        print(f"✗ Found {len(self.violations)} Java 8 compatibility violation(s):\n")

        for file_path, line_num, message, line in self.violations:
            print(f"{file_path}:{line_num}")
            print(f"  Issue: {message}")
            print(f"  Code:  {line}")
            print()

        print("\nRecommendations:")
        print("- Use explicit types instead of 'var'")
        print("- Use traditional switch statements instead of switch expressions")
        print("- Use String concatenation instead of text blocks")
        print("- Use explicit casting after instanceof checks")
        print("- Use regular classes instead of records")
        print("- Use regular classes/interfaces instead of sealed types")

        return 1


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    path = Path(sys.argv[1])

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(2)

    validator = Java8Validator()

    if path.is_file():
        if path.suffix == '.java':
            validator.validate_file(path)
        else:
            print(f"Error: Not a Java file: {path}", file=sys.stderr)
            sys.exit(2)
    elif path.is_dir():
        validator.validate_directory(path)
    else:
        print(f"Error: Invalid path: {path}", file=sys.stderr)
        sys.exit(2)

    sys.exit(validator.report())


if __name__ == '__main__':
    main()
