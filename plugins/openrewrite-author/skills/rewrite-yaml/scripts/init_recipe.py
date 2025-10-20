#!/usr/bin/env python3
"""
OpenRewrite Recipe Initialization Script

Generates boilerplate code for new OpenRewrite YAML recipes including:
- Recipe class file
- Test file
- Optional declarative YAML recipe

Usage:
    python init_recipe.py --name MyRecipe --package com.example.rewrite --description "Recipe description"
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path


def read_license_header():
    """Read license header from gradle/licenseHeader.txt if it exists."""
    license_path = Path.cwd()
    while license_path != license_path.parent:
        license_file = license_path / "gradle" / "licenseHeader.txt"
        if license_file.exists():
            with open(license_file, 'r') as f:
                content = f.read()
                # Substitute ${year} with current year
                content = content.replace("${year}", str(datetime.now().year))
                return content + "\n"
        license_path = license_path.parent
    return ""


def to_snake_case(name):
    """Convert PascalCase to snake_case."""
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append('_')
        result.append(char.lower())
    return ''.join(result)


def generate_recipe_class(name, package, description, license_header):
    """Generate the recipe class file content."""
    return f"""{license_header}package {package};

import org.openrewrite.*;
import org.openrewrite.yaml.YamlIsoVisitor;
import org.openrewrite.yaml.tree.Yaml;

public class {name} extends Recipe {{

    @Override
    public String getDisplayName() {{
        return "{name}";
    }}

    @Override
    public String getDescription() {{
        return "{description}";
    }}

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {{
        return new YamlIsoVisitor<ExecutionContext>() {{
            @Override
            public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {{
                // TODO: Implement recipe logic
                return super.visitMappingEntry(entry, ctx);
            }}
        }};
    }}
}}
"""


def generate_parameterized_recipe_class(name, package, description, license_header):
    """Generate a parameterized recipe class file content."""
    return f"""{license_header}package {package};

import lombok.EqualsAndHashCode;
import lombok.Value;
import org.openrewrite.*;
import org.openrewrite.yaml.YamlIsoVisitor;
import org.openrewrite.yaml.tree.Yaml;

@Value
@EqualsAndHashCode(callSuper = false)
public class {name} extends Recipe {{

    @Option(
        displayName = "Parameter name",
        description = "Description of the parameter",
        example = "example-value"
    )
    String parameterName;

    @Override
    public String getDisplayName() {{
        return "{name}";
    }}

    @Override
    public String getDescription() {{
        return "{description}";
    }}

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {{
        return new YamlIsoVisitor<ExecutionContext>() {{
            @Override
            public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {{
                // TODO: Implement recipe logic using parameterName
                return super.visitMappingEntry(entry, ctx);
            }}
        }};
    }}
}}
"""


def generate_test_class(name, package, license_header):
    """Generate the test class file content."""
    return f"""{license_header}package {package};

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RecipeSpec;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.yaml.Assertions.yaml;

class {name}Test implements RewriteTest {{

    @Override
    public void defaults(RecipeSpec spec) {{
        spec.recipe(new {name}());
    }}

    @Test
    void basicTransformation() {{
        rewriteRun(
            yaml(
                \"\"\"
                # Before YAML
                key: old-value
                \"\"\",
                \"\"\"
                # After YAML
                key: new-value
                \"\"\"
            )
        );
    }}

    @Test
    void doesNotChangeUnrelatedYaml() {{
        rewriteRun(
            yaml(
                \"\"\"
                unrelated: value
                \"\"\"
            )
        );
    }}

    @Test
    void handlesEdgeCases() {{
        rewriteRun(
            yaml(
                \"\"\"
                # Empty value
                key:
                # Null value
                key2: null
                \"\"\"
            )
        );
    }}
}}
"""


def generate_declarative_recipe(name, package, description):
    """Generate declarative YAML recipe content."""
    return f"""---
type: specs.openrewrite.org/v1beta/recipe
name: {package}.{name}
displayName: {name}
description: {description}
recipeList:
  - org.openrewrite.yaml.search.FindKey:
      keyPath: $.some.path
  - org.openrewrite.yaml.ChangeValue:
      keyPath: $.some.path
      value: newValue
"""


def create_file(path, content):
    """Create a file with the given content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new OpenRewrite YAML recipe with boilerplate code"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Recipe class name (PascalCase, e.g., UpdateGitHubActions)"
    )
    parser.add_argument(
        "--package",
        required=True,
        help="Package name (e.g., com.example.rewrite)"
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Recipe description"
    )
    parser.add_argument(
        "--parameterized",
        action="store_true",
        help="Generate parameterized recipe with @Option annotation"
    )
    parser.add_argument(
        "--declarative",
        action="store_true",
        help="Also generate declarative YAML recipe template"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory (default: current directory)"
    )

    args = parser.parse_args()

    # Validate recipe name
    if not args.name[0].isupper():
        print("Error: Recipe name must start with uppercase letter (PascalCase)")
        sys.exit(1)

    # Read license header
    license_header = read_license_header()
    if license_header:
        print(f"Found license header (will use year {datetime.now().year})")

    # Convert package to path
    package_path = args.package.replace('.', '/')
    base_path = Path(args.output_dir)

    # Generate file paths
    recipe_path = base_path / "src" / "main" / "java" / package_path / f"{args.name}.java"
    test_path = base_path / "src" / "test" / "java" / package_path / f"{args.name}Test.java"

    # Generate recipe class
    if args.parameterized:
        recipe_content = generate_parameterized_recipe_class(
            args.name, args.package, args.description, license_header
        )
    else:
        recipe_content = generate_recipe_class(
            args.name, args.package, args.description, license_header
        )

    # Generate test class
    test_content = generate_test_class(args.name, args.package, license_header)

    # Create files
    create_file(recipe_path, recipe_content)
    create_file(test_path, test_content)

    # Generate declarative recipe if requested
    if args.declarative:
        yaml_name = to_snake_case(args.name)
        yaml_path = base_path / "src" / "main" / "resources" / "META-INF" / "rewrite" / f"{yaml_name}.yml"
        yaml_content = generate_declarative_recipe(args.name, args.package, args.description)
        create_file(yaml_path, yaml_content)

    print("\n✓ Recipe initialization complete!")
    print("\nNext steps:")
    print("1. Write failing tests in the test file")
    print("2. Implement the recipe logic")
    print("3. Run tests to verify: ./gradlew test")
    if args.declarative:
        print("4. Choose between imperative (Java) or declarative (YAML) approach")


if __name__ == "__main__":
    main()
