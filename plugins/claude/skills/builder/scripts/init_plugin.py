#!/usr/bin/env python3
"""
Plugin Scaffold Generator for Claude Code

Creates a complete plugin directory structure with skeleton files.

Usage:
    python init_plugin.py [--name NAME] [--description DESC] [--author AUTHOR] [--output DIR]

Example:
    python init_plugin.py --name my-plugin --description "My plugin description" --author "Your Name"
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional


def create_directory_structure(
    plugin_name: str,
    description: str,
    author: str,
    output_dir: Optional[str] = None
) -> Path:
    """
    Create plugin directory structure with all necessary files.

    Args:
        plugin_name: Name of the plugin (kebab-case)
        description: Plugin description
        author: Plugin author name
        output_dir: Optional output directory (defaults to current directory)

    Returns:
        Path to created plugin directory
    """
    # Determine base directory
    base_dir = Path(output_dir) if output_dir else Path.cwd()
    plugin_dir = base_dir / plugin_name

    # Check if directory already exists
    if plugin_dir.exists():
        print(f"Error: Directory '{plugin_dir}' already exists", file=sys.stderr)
        sys.exit(1)

    # Create directory structure
    plugin_dir.mkdir(parents=True)
    (plugin_dir / ".claude-plugin").mkdir()
    (plugin_dir / "agents").mkdir()
    (plugin_dir / "commands").mkdir()
    (plugin_dir / "skills").mkdir()

    print(f"Created plugin directory: {plugin_dir}")

    # Create plugin.json
    plugin_json = {
        "name": plugin_name,
        "version": "0.1.0",
        "description": description,
        "author": author,
        "agents": [],
        "commands": [],
        "skills": []
    }

    plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
    with open(plugin_json_path, "w") as f:
        json.dump(plugin_json, f, indent=2)

    print(f"Created: {plugin_json_path}")

    # Create README.md
    readme_content = f"""# {plugin_name}

{description}

## Components

This plugin includes:

- **Agents**: [List agents here]
- **Commands**: [List commands here]
- **Skills**: [List skills here]

## Installation

Add this plugin to Claude Code:

```bash
/plugin install {plugin_name}@your-marketplace
```

## Usage

[Describe how to use the plugin components]

## Author

{author}

## Version

0.1.0
"""

    readme_path = plugin_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write(readme_content)

    print(f"Created: {readme_path}")

    # Create SKILLS.md
    skills_content = f"""# {plugin_name} Skills

This document describes the skills provided by the {plugin_name} plugin.

## Skills

### skill-name

**File**: `skills/skill-name/SKILL.md`

**Description**: [Describe what this skill does and when it activates]

**Triggers**: [List activation triggers]

**Usage**: [Provide usage examples]

---

## Reference Materials

[List any reference materials or documentation included with the skills]
"""

    skills_path = plugin_dir / "SKILLS.md"
    with open(skills_path, "w") as f:
        f.write(skills_content)

    print(f"Created: {skills_path}")

    # Create placeholder files
    agent_placeholder = plugin_dir / "agents" / ".gitkeep"
    agent_placeholder.touch()

    command_placeholder = plugin_dir / "commands" / ".gitkeep"
    command_placeholder.touch()

    skill_placeholder = plugin_dir / "skills" / ".gitkeep"
    skill_placeholder.touch()

    print(f"\nPlugin scaffold created successfully!")
    print(f"\nNext steps:")
    print(f"1. Edit {plugin_json_path} to add component references")
    print(f"2. Create agents in {plugin_dir / 'agents'}/")
    print(f"3. Create commands in {plugin_dir / 'commands'}/")
    print(f"4. Create skills in {plugin_dir / 'skills'}/")
    print(f"5. Update README.md and SKILLS.md with actual documentation")

    return plugin_dir


def validate_plugin_name(name: str) -> bool:
    """Validate plugin name follows kebab-case convention."""
    if not name:
        return False
    if not all(c.islower() or c.isdigit() or c == '-' for c in name):
        return False
    if name.startswith('-') or name.endswith('-'):
        return False
    if '--' in name:
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Create a new Claude Code plugin scaffold",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python init_plugin.py --name my-plugin --description "My awesome plugin"
  python init_plugin.py --name my-plugin --author "John Doe" --output ./plugins
        """
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Plugin name (kebab-case, e.g., 'my-plugin')"
    )

    parser.add_argument(
        "--description",
        default="A Claude Code plugin",
        help="Plugin description"
    )

    parser.add_argument(
        "--author",
        default="Unknown",
        help="Plugin author name"
    )

    parser.add_argument(
        "--output",
        help="Output directory (defaults to current directory)"
    )

    args = parser.parse_args()

    # Validate plugin name
    if not validate_plugin_name(args.name):
        print(
            f"Error: Plugin name '{args.name}' is invalid. "
            "Use kebab-case (lowercase letters, numbers, and hyphens only)",
            file=sys.stderr
        )
        sys.exit(1)

    # Create plugin scaffold
    create_directory_structure(
        plugin_name=args.name,
        description=args.description,
        author=args.author,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
