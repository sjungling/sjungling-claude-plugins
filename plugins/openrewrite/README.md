# OpenRewrite Plugin

Expert system for test-first development of production-quality OpenRewrite recipes for automated code refactoring.

## Overview

This plugin combines the best of two worlds:
- **Comprehensive coverage** of all recipe types (declarative, Refaster, imperative)
- **Deep domain expertise** in both Java and YAML transformations
- **Test-driven development** workflow (RED-GREEN-REFACTOR)
- **Production-ready patterns** and best practices

## Skills

### recipe-writer

Expert in creating OpenRewrite recipes for automated code refactoring across all languages and formats.

**Automatically activates when:**
- Working with OpenRewrite recipe files
- Java/YAML files in `src/main/java/**/rewrite/**` directories
- Writing tests implementing `RewriteTest`
- User asks about recipe development, LST manipulation, JavaTemplate usage, visitor patterns, preconditions, scanning recipes, YAML recipes, GitHub Actions transformations, Kubernetes manifest updates, or code migration strategies

**Key Capabilities:**
- **All Recipe Types**: Declarative YAML, Refaster templates, Imperative Java
- **Java Refactoring**: Type changes, method migrations, framework updates
- **YAML Transformations**: GitHub Actions, Kubernetes, CI/CD configs
- **Advanced Patterns**: Traits, ScanningRecipe, preconditions
- **Test-First Development**: Comprehensive RewriteTest coverage
- **Production Quality**: 200+ item validation checklist

## Installation

### Add Marketplace

```bash
/plugin marketplace add /Users/scott.jungling/Work/claude-plugins
```

### Install Plugin

```bash
/plugin install openrewrite@claude-plugins
```

## Quick Start

### Creating a Java Recipe

```bash
# Generate boilerplate
cd your-project
/Users/scott.jungling/Work/claude-plugins/plugins/openrewrite/skills/recipe-writer/scripts/init_recipe.py MyRecipe

# This creates:
# - src/main/java/com/yourorg/MyRecipe.java
# - src/test/java/com/yourorg/MyRecipeTest.java
```

### Creating a YAML Recipe

Create a file in `src/main/resources/META-INF/rewrite/`:

```yaml
type: specs.openrewrite.org/v1beta/recipe
name: com.yourorg.MyRecipe
displayName: My recipe display name
description: Clear description
recipeList:
  - org.openrewrite.yaml.ChangeValue:
      keyPath: $.key.path
      value: newValue
```

### Validating a Recipe

```bash
# Validate structure and Java compatibility
./scripts/validate_recipe.py src/main/java/com/yourorg/MyRecipe.java

# Validate with specific Java version
./scripts/validate_recipe.py MyRecipe.java --java-version 11

# Skip compilation check
./scripts/validate_recipe.py MyRecipe.java --no-compile
```

## Recipe Development Workflow

The skill guides you through a test-first development workflow:

```
1. RED: Write failing tests
   ↓
2. DECIDE: Choose recipe type (declarative/Refaster/imperative)
   ↓
3. GREEN: Minimal implementation
   ↓
4. REFACTOR: Apply OpenRewrite idioms (traits, composition)
   ↓
5. DOCUMENT: Add metadata with markdown examples
   ↓
6. VALIDATE: Production readiness checklist
```

## Recipe Type Decision Tree

```
Start here
    ├─ Can I compose existing recipes? ────────────────┐
    │   YES → Use Declarative YAML                      │
    │   NO ↓                                             │
    ├─ Is it a simple expression/statement replacement? │
    │   YES → Use Refaster Template                     │
    │   NO ↓                                             │
    └─ Do I need custom logic or conditional changes? ──┤
        YES → Use Imperative Java Recipe                │
                                                         │
Still unsure? → Start with declarative, ───────────────┘
               fall back to imperative
```

## Resource Organization

The skill uses progressive disclosure to minimize token usage:

### Templates (500 tokens each)
Load when creating new recipes:
- `template-imperative-recipe.java` - Complete recipe class structure
- `template-declarative-recipe.yml` - YAML recipe format
- `template-refaster-template.java` - Refaster template structure
- `template-recipe-test.java` - Test class with RewriteTest
- `license-header.txt` - Standard license header

### Examples (1,000 tokens each)
Load when learning specific patterns:
- `example-say-hello-recipe.java` - Simple recipe with JavaTemplate
- `example-scanning-recipe.java` - Multi-file analysis pattern
- `example-yaml-github-actions.java` - YAML domain example
- `example-declarative-migration.yml` - Framework migration

### References (1,500-3,000 tokens each)
Load for deep dives or validation:
- `java-lst-reference.md` - Java LST structure and hierarchy
- `yaml-lst-reference.md` - YAML LST structure and hierarchy
- `jsonpath-patterns.md` - Domain-specific JsonPath patterns
- `trait-implementation-guide.md` - Advanced trait patterns
- `checklist-recipe-development.md` - 200+ validation items
- `common-patterns.md` - Copy-paste code snippets
- `testing-patterns.md` - Test patterns and edge cases
- `troubleshooting-guide.md` - Issue diagnosis and solutions

## Automation Scripts

### init_recipe.py
Generate recipe boilerplate (class, test file, optional YAML):

```bash
./scripts/init_recipe.py RecipeName
./scripts/init_recipe.py RecipeName --declarative
./scripts/init_recipe.py RecipeName --package com.example
```

### validate_recipe.py
Validate recipe structure, naming, and compatibility:

```bash
./scripts/validate_recipe.py path/to/Recipe.java
./scripts/validate_recipe.py Recipe.java --java-version 11
./scripts/validate_recipe.py Recipe.java --no-compile
```

Checks:
- Recipe class structure (extends Recipe, required annotations)
- Required methods (getDisplayName, getDescription, getVisitor)
- Naming conventions (package, class name, display name)
- Java compatibility (compiles with target version)
- YAML recipe format (for declarative recipes)

### add_license_header.sh
Add license headers from `gradle/licenseHeader.txt`:

```bash
./scripts/add_license_header.sh path/to/Recipe.java
```

## Domain Expertise

### Java Recipes
- Type changes and package migrations
- Method signature updates
- Framework modernization (JUnit 4→5, Spring Boot 2→3)
- Dependency management
- Static analysis and code cleanup

### YAML Recipes
- GitHub Actions workflow updates
- Kubernetes manifest transformations
- CI/CD configuration migrations
- Generic YAML manipulations

**Common JsonPath Patterns:**
- GitHub Actions: `$.jobs.*.steps[*].uses`, `$.on.push.branches`
- Kubernetes: `$.spec.template.spec.containers[*].image`, `$.metadata.labels`
- Generic: `$.databases.*.connection.host`, `$[?(@.enabled == true)]`

## Advanced Features

### OpenRewrite Traits
Semantic abstractions over LST elements for reusable matching logic:

```java
@Override
public TreeVisitor<?, ExecutionContext> getVisitor() {
    return new ActionStep.Matcher().asVisitor((step, ctx) -> {
        String ref = step.getActionRef();
        if (ref != null && ref.contains("@v2")) {
            return step.withActionRef(ref.replace("@v2", "@v3")).getTree();
        }
        return step.getTree();
    });
}
```

### ScanningRecipe Pattern
Multi-file analysis with accumulator pattern:

```java
@Value
@EqualsAndHashCode(callSuper = false)
public class YourScanningRecipe extends ScanningRecipe<YourAccumulator> {
    // Scan phase: collect data
    @Override
    public TreeVisitor<?, ExecutionContext> getScanner(YourAccumulator acc) {
        // ... collect data into accumulator
    }

    // Transform phase: use collected data
    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor(YourAccumulator acc) {
        // ... make changes based on accumulator
    }
}
```

### Preconditions
Performance optimization through file filtering:

```java
@Override
public TreeVisitor<?, ExecutionContext> getVisitor() {
    return Preconditions.check(
        Preconditions.and(
            new UsesType<>("com.example.Type", true),
            new UsesJavaVersion<>(17)
        ),
        new YourVisitor()
    );
}
```

## Best Practices

### Core Principles
1. **Do No Harm** - If unsure, don't change
2. **Test First** - Write tests before implementation
3. **Immutability** - Never mutate LSTs, always use `.withX()`
4. **Idempotence** - Same input → same output, always
5. **Preserve Formatting** - Comments and whitespace matter

### Naming Conventions
- Display names: Sentence case, code in backticks, end with period
- Example: "Change type from `OldType` to `NewType`."
- Recipe names: `com.yourorg.VerbNoun` (e.g., `com.yourorg.ChangePackage`)

## Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| Recipe not running on expected files | Check preconditions, verify visitor type matches file type |
| JavaTemplate parse errors | Declare imports with `.imports()`, verify classpath |
| Tests pass but recipe fails in real code | Add realistic test cases, test with external dependencies |
| Recipe not idempotent | Check referential equality, ensure `getVisitor()` returns NEW instance |
| Type information not available | Configure test classpath, check imports present |
| YAML recipe not matching elements | Verify JsonPath pattern, handle nulls safely |
| Comments/formatting not preserved | Use `.withX()` methods, never mutate directly |

## Examples

### Simple Value Replacement
```java
@Override
public Yaml.Scalar visitScalar(Yaml.Scalar scalar, ExecutionContext ctx) {
    scalar = super.visitScalar(scalar, ctx);

    if (matcher.matches(getCursor())) {
        String value = scalar.getValue();
        if ("oldValue".equals(value)) {
            return scalar.withValue("newValue");
        }
    }

    return scalar;
}
```

### GitHub Actions Update
```java
private final JsonPathMatcher matcher =
    new JsonPathMatcher("$.jobs.*.steps[*].uses");

@Override
public Yaml.Scalar visitScalar(Yaml.Scalar scalar, ExecutionContext ctx) {
    scalar = super.visitScalar(scalar, ctx);

    if (matcher.matches(getCursor())) {
        String value = scalar.getValue();
        if (value != null && value.startsWith("actions/checkout@v2")) {
            return scalar.withValue(value.replace("@v2", "@v4"));
        }
    }

    return scalar;
}
```

## Migration from openrewrite-author

The new `openrewrite` plugin supersedes `openrewrite-author` with:

✅ **Added**: Refaster template support
✅ **Added**: Java LST reference documentation
✅ **Added**: Comprehensive troubleshooting guide
✅ **Added**: 200+ item production checklist
✅ **Enhanced**: Better test-first workflow documentation
✅ **Enhanced**: Improved validation script (no Java 8-only constraint)
✅ **Enhanced**: Token budget awareness and progressive disclosure

The old `openrewrite-author` plugin is now deprecated. Please migrate to `openrewrite`.

## Resources

- **OpenRewrite Documentation**: https://docs.openrewrite.org
- **Recipe Development Guide**: https://docs.openrewrite.org/authoring-recipes
- **Recipe Testing**: https://docs.openrewrite.org/authoring-recipes/recipe-testing
- **LST Structure**: https://docs.openrewrite.org/concepts-explanations/lossless-semantic-trees

## Version History

### v1.0.0 (Current)
- Initial release combining rewrite-yaml and recipe-writer skills
- Comprehensive coverage of all recipe types
- Test-first development workflow
- Production readiness validation
- Domain expertise in Java and YAML
- Advanced features: traits, scanning, preconditions
- Complete automation scripts

## License

This plugin is part of the claude-plugins personal collection.
See individual recipe files for their license headers.
