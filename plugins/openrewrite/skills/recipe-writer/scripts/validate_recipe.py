#!/usr/bin/env python3
"""
Validate OpenRewrite recipe structure, naming conventions, and Java compatibility.

This script checks:
1. Recipe class structure (extends Recipe, has required annotations)
2. Required methods (getDisplayName, getDescription, getVisitor)
3. Naming conventions (package, class name, display name)
4. Java compatibility (can compile with Java 8)
5. YAML recipe format (for declarative recipes)

Usage:
    python validate_recipe.py <path-to-recipe>
    python validate_recipe.py <path-to-recipe> --java-version 8
    python validate_recipe.py <path-to-recipe> --no-compile
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")


def print_error(message: str):
    print(f"{Colors.RED}✗{Colors.RESET} {message}")


def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")


def print_info(message: str):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")


def check_java_file_structure(content: str, file_path: Path) -> List[str]:
    """Validate Java recipe file structure"""
    errors = []

    # Check for Recipe class
    if not re.search(r'class\s+\w+\s+extends\s+Recipe', content):
        errors.append("Recipe class must extend Recipe")

    # Check for @Value annotation (for immutability)
    if '@Value' not in content:
        print_warning(f"Consider using @Value annotation for immutability")

    # Check for @EqualsAndHashCode
    if '@EqualsAndHashCode' not in content:
        print_warning("Consider using @EqualsAndHashCode(callSuper = false)")

    # Check for required methods
    if 'getDisplayName()' not in content:
        errors.append("Recipe must override getDisplayName()")

    if 'getDescription()' not in content:
        errors.append("Recipe must override getDescription()")

    if 'getVisitor()' not in content:
        errors.append("Recipe must override getVisitor()")

    # Check for proper return in getVisitor
    if 'getVisitor()' in content:
        visitor_match = re.search(r'public\s+TreeVisitor<\?.*?>\s+getVisitor\([^)]*\)\s*{([^}]+)}', content, re.DOTALL)
        if visitor_match:
            visitor_body = visitor_match.group(1)
            if 'new ' not in visitor_body:
                print_warning("getVisitor() should return a NEW instance (no caching)")

    # Check display name ends with period
    display_name_match = re.search(r'getDisplayName\(\)\s*{\s*return\s*"([^"]+)"', content)
    if display_name_match:
        display_name = display_name_match.group(1)
        if not display_name.endswith('.') and not display_name.endswith('!') and not display_name.endswith('?'):
            print_warning(f"Display name should end with a period: '{display_name}'")

    # Check for @Option annotations on parameters
    option_count = content.count('@Option')
    if option_count > 0:
        # Check that options have example
        for match in re.finditer(r'@Option\([^)]+\)', content):
            option = match.group(0)
            if 'example' not in option:
                print_warning("@Option should include an example parameter")

    return errors


def check_naming_conventions(content: str, file_path: Path) -> List[str]:
    """Check naming conventions"""
    errors = []

    # Extract package name
    package_match = re.search(r'package\s+([\w.]+);', content)
    if package_match:
        package = package_match.group(1)
        if package.startswith('com.yourorg') or package.startswith('com.example'):
            print_warning(f"Update placeholder package name: {package}")

    # Extract class name
    class_match = re.search(r'class\s+(\w+)\s+extends\s+Recipe', content)
    if class_match:
        class_name = class_match.group(1)

        # Check naming convention (VerbNoun pattern)
        if not re.match(r'^[A-Z][a-z]+[A-Z]', class_name):
            print_warning(f"Recipe class name should follow VerbNoun pattern: {class_name}")

        # Check file name matches class name
        expected_filename = f"{class_name}.java"
        if file_path.name != expected_filename:
            errors.append(f"File name {file_path.name} does not match class name {expected_filename}")

    return errors


def check_java8_compatibility_patterns(content: str) -> List[str]:
    """Check for Java 8 incompatible patterns"""
    warnings = []

    # Check for var keyword
    if re.search(r'\bvar\b', content):
        warnings.append("Found 'var' keyword - not available in Java 8")

    # Check for text blocks
    if '"""' in content:
        warnings.append("Found text blocks (triple quotes) - not available in Java 8")

    # Check for switch expressions
    if re.search(r'switch\s*\([^)]+\)\s*{[^}]*->', content):
        warnings.append("Found switch expression - not available in Java 8")

    # Check for pattern matching
    if re.search(r'instanceof\s+\w+\s+\w+\s+&&', content):
        warnings.append("Found pattern matching in instanceof - not available in Java 8")

    # Check for record keyword
    if re.search(r'\brecord\s+\w+', content):
        warnings.append("Found record - not available in Java 8")

    return warnings


def compile_with_javac(file_path: Path, java_version: int = 8) -> Tuple[bool, str]:
    """Try to compile the file with javac"""
    try:
        # Create a temporary directory for compilation
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                ['javac', '-source', str(java_version), '-target', str(java_version),
                 '-d', tmpdir, str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return True, ""
            else:
                return False, result.stderr

    except FileNotFoundError:
        return False, "javac not found in PATH"
    except subprocess.TimeoutExpired:
        return False, "Compilation timed out"
    except Exception as e:
        return False, str(e)


def validate_yaml_recipe(content: str, file_path: Path) -> List[str]:
    """Validate YAML recipe format"""
    errors = []

    # Check for required fields
    if 'type: specs.openrewrite.org/v1beta/recipe' not in content:
        errors.append("YAML recipe must have 'type: specs.openrewrite.org/v1beta/recipe'")

    if not re.search(r'^name:\s+[\w.]+', content, re.MULTILINE):
        errors.append("YAML recipe must have 'name' field")

    if not re.search(r'^displayName:', content, re.MULTILINE):
        errors.append("YAML recipe must have 'displayName' field")

    if not re.search(r'^description:', content, re.MULTILINE):
        errors.append("YAML recipe must have 'description' field")

    if not re.search(r'^recipeList:', content, re.MULTILINE):
        errors.append("YAML recipe must have 'recipeList' field")

    # Check naming convention
    name_match = re.search(r'^name:\s+([\w.]+)', content, re.MULTILINE)
    if name_match:
        name = name_match.group(1)
        if not re.match(r'^[\w.]+\.[\w.]+$', name):
            print_warning(f"Recipe name should be fully qualified: {name}")
        if 'yourorg' in name.lower() or 'example' in name.lower():
            print_warning(f"Update placeholder recipe name: {name}")

    return errors


def validate_recipe(file_path: Path, java_version: int = 8, skip_compile: bool = False) -> bool:
    """Validate a recipe file"""
    print(f"\n{Colors.BOLD}Validating: {file_path}{Colors.RESET}\n")

    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return False

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print_error(f"Error reading file: {e}")
        return False

    errors = []
    warnings = []

    # Determine file type
    if file_path.suffix == '.java':
        print_info("Checking Java recipe structure...")
        errors.extend(check_java_file_structure(content, file_path))

        print_info("Checking naming conventions...")
        errors.extend(check_naming_conventions(content, file_path))

        print_info(f"Checking Java {java_version} compatibility...")
        java8_warnings = check_java8_compatibility_patterns(content)
        warnings.extend(java8_warnings)

        # Try to compile if not skipped
        if not skip_compile:
            print_info("Attempting compilation...")
            success, compile_error = compile_with_javac(file_path, java_version)
            if not success:
                if "javac not found" in compile_error:
                    print_warning("javac not found - skipping compilation check")
                else:
                    errors.append(f"Compilation failed:\n{compile_error}")
            else:
                print_success("Compilation successful")

    elif file_path.suffix in ['.yml', '.yaml']:
        print_info("Checking YAML recipe format...")
        errors.extend(validate_yaml_recipe(content, file_path))

    else:
        print_error(f"Unsupported file type: {file_path.suffix}")
        return False

    # Print results
    print()
    if errors:
        print(f"{Colors.RED}{Colors.BOLD}ERRORS:{Colors.RESET}")
        for error in errors:
            print_error(error)
        print()

    if warnings:
        print(f"{Colors.YELLOW}{Colors.BOLD}WARNINGS:{Colors.RESET}")
        for warning in warnings:
            print_warning(warning)
        print()

    if not errors and not warnings:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All checks passed!{Colors.RESET}\n")
        return True
    elif not errors:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Validation passed with warnings{Colors.RESET}\n")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Validation failed{Colors.RESET}\n")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Validate OpenRewrite recipe files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Validate a Java recipe
  python validate_recipe.py src/main/java/com/example/MyRecipe.java

  # Validate with Java 11
  python validate_recipe.py MyRecipe.java --java-version 11

  # Skip compilation check
  python validate_recipe.py MyRecipe.java --no-compile

  # Validate a YAML recipe
  python validate_recipe.py src/main/resources/META-INF/rewrite/my-recipe.yml
        '''
    )

    parser.add_argument('path', type=str, help='Path to recipe file')
    parser.add_argument('--java-version', type=int, default=8,
                        help='Target Java version (default: 8)')
    parser.add_argument('--no-compile', action='store_true',
                        help='Skip compilation check')

    args = parser.parse_args()

    file_path = Path(args.path)
    success = validate_recipe(file_path, args.java_version, args.no_compile)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
