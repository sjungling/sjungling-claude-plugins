#!/usr/bin/env python3
"""
Marketplace Configuration Validator for Claude Code

Validates marketplace.json files for correctness and best practices.

Usage:
    python validate_marketplace.py [marketplace.json]

Example:
    python validate_marketplace.py .claude-plugin/marketplace.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


class ValidationError:
    """Represents a validation error or warning."""

    def __init__(self, level: str, path: str, message: str):
        self.level = level  # 'error' or 'warning'
        self.path = path
        self.message = message

    def __str__(self):
        icon = "❌" if self.level == "error" else "⚠️"
        return f"{icon} {self.level.upper()}: {self.path}: {self.message}"


class MarketplaceValidator:
    """Validates Claude Code marketplace.json files."""

    def __init__(self, marketplace_path: Path):
        self.marketplace_path = marketplace_path
        self.base_dir = marketplace_path.parent.parent
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.data: Dict[str, Any] = {}

    def validate(self) -> bool:
        """
        Perform all validation checks.

        Returns:
            True if validation passes (no errors), False otherwise
        """
        if not self._load_json():
            return False

        self._validate_structure()
        self._validate_plugins()

        return len(self.errors) == 0

    def _load_json(self) -> bool:
        """Load and parse the JSON file."""
        try:
            with open(self.marketplace_path, "r") as f:
                self.data = json.load(f)
            return True
        except FileNotFoundError:
            self.errors.append(
                ValidationError("error", str(self.marketplace_path), "File not found")
            )
            return False
        except json.JSONDecodeError as e:
            self.errors.append(
                ValidationError(
                    "error",
                    str(self.marketplace_path),
                    f"Invalid JSON: {e}"
                )
            )
            return False

    def _validate_structure(self):
        """Validate top-level marketplace structure."""
        # Check for required field
        if "plugins" not in self.data:
            self.errors.append(
                ValidationError(
                    "error",
                    "marketplace.json",
                    "Missing required field 'plugins'"
                )
            )
            return

        if not isinstance(self.data["plugins"], list):
            self.errors.append(
                ValidationError(
                    "error",
                    "marketplace.json",
                    "'plugins' must be an array"
                )
            )

        # Check for optional pluginRoot
        if "pluginRoot" in self.data:
            plugin_root = self.data["pluginRoot"]
            if not isinstance(plugin_root, str):
                self.errors.append(
                    ValidationError(
                        "error",
                        "pluginRoot",
                        "Must be a string"
                    )
                )
            elif not plugin_root.startswith("./"):
                self.warnings.append(
                    ValidationError(
                        "warning",
                        "pluginRoot",
                        "Should start with './' for relative paths"
                    )
                )

    def _validate_plugins(self):
        """Validate each plugin entry."""
        if "plugins" not in self.data or not isinstance(self.data["plugins"], list):
            return

        plugin_names = set()

        for idx, plugin in enumerate(self.data["plugins"]):
            path_prefix = f"plugins[{idx}]"

            if not isinstance(plugin, dict):
                self.errors.append(
                    ValidationError(
                        "error",
                        path_prefix,
                        "Plugin entry must be an object"
                    )
                )
                continue

            # Validate required fields
            if "name" not in plugin:
                self.errors.append(
                    ValidationError(
                        "error",
                        f"{path_prefix}",
                        "Missing required field 'name'"
                    )
                )
            else:
                name = plugin["name"]

                # Check for duplicate names
                if name in plugin_names:
                    self.errors.append(
                        ValidationError(
                            "error",
                            f"{path_prefix}.name",
                            f"Duplicate plugin name '{name}'"
                        )
                    )
                plugin_names.add(name)

                # Validate name format
                if not self._is_valid_kebab_case(name):
                    self.warnings.append(
                        ValidationError(
                            "warning",
                            f"{path_prefix}.name",
                            f"Plugin name '{name}' should use kebab-case"
                        )
                    )

            if "source" not in plugin:
                self.errors.append(
                    ValidationError(
                        "error",
                        f"{path_prefix}",
                        "Missing required field 'source'"
                    )
                )
            else:
                self._validate_source_path(plugin["source"], path_prefix)

            # Validate optional fields
            if "version" in plugin and not isinstance(plugin["version"], str):
                self.errors.append(
                    ValidationError(
                        "error",
                        f"{path_prefix}.version",
                        "Version must be a string"
                    )
                )

            if "description" in plugin and not isinstance(plugin["description"], str):
                self.errors.append(
                    ValidationError(
                        "error",
                        f"{path_prefix}.description",
                        "Description must be a string"
                    )
                )

            # Validate component arrays
            for component_type in ["agents", "commands", "skills"]:
                if component_type in plugin:
                    self._validate_component_array(
                        plugin[component_type],
                        f"{path_prefix}.{component_type}",
                        plugin.get("source", "")
                    )

    def _validate_source_path(self, source: str, path_prefix: str):
        """Validate plugin source path."""
        if not isinstance(source, str):
            self.errors.append(
                ValidationError(
                    "error",
                    f"{path_prefix}.source",
                    "Source must be a string"
                )
            )
            return

        # Check for relative path prefix
        if not source.startswith("./"):
            self.errors.append(
                ValidationError(
                    "error",
                    f"{path_prefix}.source",
                    f"Source path '{source}' must start with './'"
                )
            )

        # Check if directory exists
        source_path = self.base_dir / source.lstrip("./")
        if not source_path.exists():
            self.errors.append(
                ValidationError(
                    "error",
                    f"{path_prefix}.source",
                    f"Source directory '{source}' does not exist"
                )
            )
        elif not source_path.is_dir():
            self.errors.append(
                ValidationError(
                    "error",
                    f"{path_prefix}.source",
                    f"Source path '{source}' is not a directory"
                )
            )

    def _validate_component_array(
        self,
        components: Any,
        path_prefix: str,
        plugin_source: str
    ):
        """Validate component array (agents, commands, or skills)."""
        if not isinstance(components, list):
            self.errors.append(
                ValidationError(
                    "error",
                    path_prefix,
                    "Component array must be an array"
                )
            )
            return

        component_type = path_prefix.split(".")[-1]  # Extract 'agents', 'commands', etc.

        for idx, component in enumerate(components):
            comp_path = f"{path_prefix}[{idx}]"

            if not isinstance(component, dict):
                self.errors.append(
                    ValidationError(
                        "error",
                        comp_path,
                        "Component entry must be an object"
                    )
                )
                continue

            # Validate required 'path' field
            if "path" not in component:
                self.errors.append(
                    ValidationError(
                        "error",
                        comp_path,
                        "Missing required field 'path'"
                    )
                )
            else:
                comp_file_path = component["path"]
                if not isinstance(comp_file_path, str):
                    self.errors.append(
                        ValidationError(
                            "error",
                            f"{comp_path}.path",
                            "Path must be a string"
                        )
                    )
                else:
                    # Resolve full path
                    if plugin_source:
                        full_path = self.base_dir / plugin_source.lstrip("./") / comp_file_path
                        if not full_path.exists():
                            self.errors.append(
                                ValidationError(
                                    "error",
                                    f"{comp_path}.path",
                                    f"Component file '{comp_file_path}' does not exist at '{full_path}'"
                                )
                            )

    @staticmethod
    def _is_valid_kebab_case(name: str) -> bool:
        """Check if string follows kebab-case convention."""
        if not name:
            return False
        if not all(c.islower() or c.isdigit() or c == '-' for c in name):
            return False
        if name.startswith('-') or name.endswith('-'):
            return False
        if '--' in name:
            return False
        return True

    def print_report(self):
        """Print validation report."""
        if self.errors:
            print("\n🔴 ERRORS:")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")

        print("\n" + "=" * 60)
        if self.errors:
            print(f"❌ Validation FAILED: {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        elif self.warnings:
            print(f"✅ Validation PASSED with {len(self.warnings)} warning(s)")
        else:
            print("✅ Validation PASSED: No errors or warnings")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Validate Claude Code marketplace.json files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_marketplace.py .claude-plugin/marketplace.json
  python validate_marketplace.py /path/to/marketplace.json
        """
    )

    parser.add_argument(
        "marketplace_file",
        nargs="?",
        default=".claude-plugin/marketplace.json",
        help="Path to marketplace.json file (default: .claude-plugin/marketplace.json)"
    )

    args = parser.parse_args()

    marketplace_path = Path(args.marketplace_file)

    print(f"Validating: {marketplace_path}")
    print("=" * 60)

    validator = MarketplaceValidator(marketplace_path)
    success = validator.validate()
    validator.print_report()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
