#!/usr/bin/env python3
"""
Markdown Documentation Validator

Validates markdown documentation files for common issues:
- Proper heading hierarchy (no skipped levels)
- Code block formatting (language tags, closing backticks)
- Link syntax validation
- Basic structure checks

Usage:
    python validate_markdown.py <file_path>
    python validate_markdown.py <directory_path>
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


class ValidationError:
    """Represents a validation error with line number and description."""

    def __init__(self, line_num: int, error_type: str, message: str):
        self.line_num = line_num
        self.error_type = error_type
        self.message = message

    def __str__(self):
        return f"Line {self.line_num}: [{self.error_type}] {self.message}"


class MarkdownValidator:
    """Validates markdown documentation files."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.errors: List[ValidationError] = []
        self.lines: List[str] = []
        self.heading_levels: List[int] = []

    def validate(self) -> List[ValidationError]:
        """Run all validation checks and return list of errors."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.lines = f.readlines()
        except Exception as e:
            return [ValidationError(0, "FILE_ERROR", f"Cannot read file: {e}")]

        self._check_heading_hierarchy()
        self._check_code_blocks()
        self._check_links()
        self._check_basic_structure()

        return sorted(self.errors, key=lambda e: e.line_num)

    def _check_heading_hierarchy(self):
        """Check that heading levels don't skip (e.g., h1 -> h3)."""
        prev_level = 0

        for i, line in enumerate(self.lines, 1):
            # Match ATX-style headings (# Heading)
            match = re.match(r'^(#{1,6})\s+(.+)', line)
            if match:
                level = len(match.group(1))
                self.heading_levels.append(level)

                # Check for skipped levels
                if level > prev_level + 1:
                    self.errors.append(ValidationError(
                        i,
                        "HEADING_SKIP",
                        f"Heading level skipped (h{prev_level} -> h{level}). Use h{prev_level + 1} instead."
                    ))

                # Check for title case (common mistake)
                title = match.group(2).strip()
                if self._is_title_case(title) and level <= 3:
                    self.errors.append(ValidationError(
                        i,
                        "TITLE_CASE",
                        f"Heading appears to use title case. Use sentence case instead: '{title}'"
                    ))

                prev_level = level

    def _is_title_case(self, text: str) -> bool:
        """Check if text appears to be in title case."""
        # Skip if too short or starts with code
        if len(text.split()) < 3 or text.startswith('`'):
            return False

        words = text.split()
        # Articles and short words that should be lowercase in sentence case
        small_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by', 'with'}

        capitalized_count = sum(1 for word in words[1:] if word and word[0].isupper() and word.lower() not in small_words)

        # If more than 50% of non-first words are capitalized, likely title case
        return capitalized_count > len(words[1:]) * 0.5

    def _check_code_blocks(self):
        """Check code block formatting."""
        in_code_block = False
        code_block_start = 0

        for i, line in enumerate(self.lines, 1):
            # Check for code block fences
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Starting a code block
                    in_code_block = True
                    code_block_start = i

                    # Check for language tag
                    fence_content = line.strip()[3:].strip()
                    if not fence_content:
                        self.errors.append(ValidationError(
                            i,
                            "CODE_BLOCK_LANG",
                            "Code block missing language identifier (e.g., ```python, ```bash, ```markdown)"
                        ))
                else:
                    # Ending a code block
                    in_code_block = False

        # Check for unclosed code block
        if in_code_block:
            self.errors.append(ValidationError(
                code_block_start,
                "CODE_BLOCK_UNCLOSED",
                "Code block opened but never closed"
            ))

    def _check_links(self):
        """Check link syntax."""
        for i, line in enumerate(self.lines, 1):
            # Find all markdown links [text](url)
            links = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line)

            for match in links:
                link_text = match.group(1)
                link_url = match.group(2)

                # Check for "click here" anti-pattern
                if link_text.lower() in ['click here', 'here', 'read more', 'more']:
                    self.errors.append(ValidationError(
                        i,
                        "LINK_TEXT",
                        f"Non-descriptive link text: '{link_text}'. Use descriptive text that tells where the link goes."
                    ))

                # Check for empty link text
                if not link_text.strip():
                    self.errors.append(ValidationError(
                        i,
                        "LINK_EMPTY",
                        "Link has empty text"
                    ))

                # Check for empty URL
                if not link_url.strip():
                    self.errors.append(ValidationError(
                        i,
                        "LINK_EMPTY_URL",
                        f"Link '{link_text}' has empty URL"
                    ))

    def _check_basic_structure(self):
        """Check basic document structure."""
        # Check for at least one H1
        if not any(line.startswith('# ') for line in self.lines):
            self.errors.append(ValidationError(
                1,
                "NO_H1",
                "Document should have at least one top-level heading (# Title)"
            ))

        # Check for multiple H1s (often unintended)
        h1_count = sum(1 for line in self.lines if line.startswith('# '))
        if h1_count > 1:
            self.errors.append(ValidationError(
                1,
                "MULTIPLE_H1",
                f"Document has {h1_count} top-level headings. Consider using only one H1 as the document title."
            ))


def validate_file(file_path: Path) -> Tuple[Path, List[ValidationError]]:
    """Validate a single markdown file."""
    validator = MarkdownValidator(file_path)
    errors = validator.validate()
    return file_path, errors


def validate_directory(dir_path: Path) -> List[Tuple[Path, List[ValidationError]]]:
    """Validate all markdown files in a directory."""
    results = []

    for md_file in dir_path.rglob('*.md'):
        file_path, errors = validate_file(md_file)
        if errors:
            results.append((file_path, errors))

    return results


def print_results(results: List[Tuple[Path, List[ValidationError]]]):
    """Print validation results."""
    if not results:
        print("✓ No validation errors found!")
        return

    total_errors = sum(len(errors) for _, errors in results)

    print(f"\n{'='*70}")
    print(f"Found {total_errors} validation error(s) in {len(results)} file(s)")
    print(f"{'='*70}\n")

    for file_path, errors in results:
        print(f"\n{file_path}:")
        print("-" * 70)
        for error in errors:
            print(f"  {error}")

    print(f"\n{'='*70}")
    print(f"Total: {total_errors} error(s)")
    print(f"{'='*70}\n")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python validate_markdown.py <file_or_directory>")
        sys.exit(1)

    path = Path(sys.argv[1])

    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)

    results = []

    if path.is_file():
        if path.suffix == '.md':
            file_path, errors = validate_file(path)
            if errors:
                results.append((file_path, errors))
        else:
            print(f"Error: Not a markdown file: {path}")
            sys.exit(1)
    elif path.is_dir():
        results = validate_directory(path)
    else:
        print(f"Error: Invalid path: {path}")
        sys.exit(1)

    print_results(results)

    # Exit with error code if validation errors found
    sys.exit(1 if results else 0)


if __name__ == '__main__':
    main()
