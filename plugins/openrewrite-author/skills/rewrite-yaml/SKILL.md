---
name: rewrite-yaml
description: Test-first development of production-quality OpenRewrite recipes for YAML manipulation using LST structure, visitor patterns, and JsonPath matching
when_to_use: when creating or modifying OpenRewrite recipes for YAML files, or when user requests YAML manipulation via OpenRewrite
version: 2.0.0
---

# Writing OpenRewrite YAML Recipes

## Overview

Create production-quality OpenRewrite recipes for YAML manipulation using test-first development.

**Core principle:** Write tests first (RED), implement minimally (GREEN), apply OpenRewrite idioms (REFACTOR).

**Announce at start:** "I've read the Writing OpenRewrite YAML Recipes skill and I'm using it to create a recipe for [purpose]."

## When to Use

- User asks to create/modify OpenRewrite recipes for YAML
- Need to manipulate YAML files (GitHub Actions, K8s manifests, CI configs, generic YAML)
- Building search or transformation recipes for YAML structures

## When NOT to Use This Skill

Do not use this skill for:
- General YAML editing (use standard Edit tools)
- Non-OpenRewrite transformation tools
- Java versions above 8 (skill specializes in Java 8 compatibility)
- Generic code refactoring outside OpenRewrite ecosystem

## Critical Constraints

**JAVA 8 COMPATIBILITY ONLY**: Use traditional if-else, switch statements, explicit casting. NO switch expressions, pattern matching, `var`, text blocks, or Java 9+ features.

**LICENSE HEADERS**: Always check for `{repository_root}/gradle/licenseHeader.txt` when creating new recipe files. If this file exists, include its contents as the license header at the top of the generated Java recipe file. Remember to substitute `${year}` with the current year (2025 or later as appropriate).

## The Workflow

### Phase 1: RED - Write Failing Tests
Write test cases with before/after YAML examples using OpenRewrite's testing framework.

### Phase 2: Architecture Decision
Choose declarative (YAML composition) vs imperative (Java Visitor) approach.

### Phase 3: GREEN - Minimal Implementation
Implement just enough to make tests pass.

### Phase 4: REFACTOR - Apply OpenRewrite Idioms
Improve recipe using traits, composition, and conventions.

### Phase 5: Documentation
Add displayName, description (with markdown), and usage examples.

## Phase 1: RED - Write Failing Tests

### Test Structure

Use OpenRewrite's testing framework with before/after YAML:

```java
@Test
void testRecipeName() {
    rewriteRun(
      spec -> spec.recipe(new YourRecipe()),
      yaml(
        """
        # before YAML
        key: old-value
        """,
        """
        # after YAML
        key: new-value
        """
      )
    );
}
```

### Checklist

- [ ] Write happy path test (simplest transformation)
- [ ] Include edge cases (empty files, missing keys, null values)
- [ ] Test no-op scenarios (recipe shouldn't change unrelated YAML)
- [ ] Consider multi-document YAML if relevant
- [ ] Include real-world examples if domain is known

### Verification

**Run tests to confirm RED state:**
- Tests must fail initially
- Verify failure reason matches expectations (e.g., "recipe not implemented")

**Key principle:** Start with simplest possible before/after. Add complexity incrementally.

## Phase 2: Architecture Decision - Declarative vs Imperative

### Decision Framework

**Start with:** Can this be done by composing existing recipes?
- **YES** → Use declarative YAML recipe
- **NO** → Need imperative Java recipe with Visitor

### Declarative Recipe (YAML Composition)

Create YAML file in `src/main/resources/META-INF/rewrite/`:

```yaml
---
type: specs.openrewrite.org/v1beta/recipe
name: com.example.MyComposedRecipe
displayName: My composed recipe
description: Composes existing recipes
recipeList:
  - org.openrewrite.yaml.search.FindKey:
      keyPath: $.some.path
  - org.openrewrite.yaml.ChangeValue:
      keyPath: $.some.path
      value: newValue
```

**When to use declarative:**
- Simple transformations using existing recipes
- Searching for patterns
- Standard modifications (change values, delete keys)
- Composing multiple existing recipes

**Common declarative recipes:**
- `org.openrewrite.yaml.search.FindKey`, `FindValue` - searching
- `org.openrewrite.yaml.ChangeKey`, `ChangeValue`, `DeleteKey` - modifications
- `org.openrewrite.yaml.MergeYaml`, `CopyValue` - additions

### Imperative Recipe (Java Visitor)

**When to use imperative:**
- Complex logic or conditional transformations
- Need to traverse YAML LST structure
- Creating new YAML structures dynamically
- Custom matching beyond JsonPath capabilities

**Key principle:** Always try declarative first. Only go imperative when you hit limitations.

## Phase 3: GREEN - Minimal Implementation

### For Declarative Recipes

1. Create YAML file in `src/main/resources/META-INF/rewrite/`
2. Compose existing `org.openrewrite.yaml.*` recipes
3. Run tests to verify GREEN state

### For Imperative Recipes (Java Visitor)

**Extend the appropriate visitor:**
- `YamlIsoVisitor<ExecutionContext>` - when not changing tree structure
- `YamlVisitor<ExecutionContext>` - when structure may change

**Override visit methods for YAML LST elements:**

```java
public class YourRecipe extends Recipe {
    @Override
    public String getDisplayName() {
        return "Your recipe name";
    }

    @Override
    public String getDescription() {
        return "Your recipe description (supports **markdown**)";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new YamlIsoVisitor<ExecutionContext>() {
            @Override
            public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
                // Your transformation logic
                return super.visitMappingEntry(entry, ctx);
            }
        };
    }
}
```

### Verification

Run tests to achieve GREEN state:
- All tests must pass
- No changes to unrelated YAML structures
- Formatting preserved

## Phase 4: REFACTOR - Apply OpenRewrite Idioms

### Checklist for Idiomatic Recipes

**1. Trait Usage**
- [ ] Can this recipe implement an existing trait?
- [ ] Should a new trait be created for reusable matching logic?
- [ ] Separate "what to find" (trait) from "what to do" (recipe)

**2. Recipe Composition**
- [ ] Can parts be extracted into smaller, composable recipes?
- [ ] Are there opportunities for configurability (parameters)?
- [ ] Could this be split into search recipe + modification recipe?

**3. OpenRewrite Conventions**
- [ ] Recipe has clear `displayName` and `description` (both support **markdown**)
- [ ] Parameters use `@Option` annotations with descriptions
- [ ] Recipe class is Java 8 compatible (no newer language features)
- [ ] Properly handles `null` values and missing elements
- [ ] Preserves formatting and comments where possible

**4. Performance Considerations**
- [ ] Minimize LST traversals (don't visit more than necessary)
- [ ] Use preconditions to skip files that won't match
- [ ] Return original object if no changes made (identity check)

### Verification

- [ ] All tests still pass after refactoring
- [ ] Recipe follows OpenRewrite naming conventions
- [ ] Code is cleaner and more maintainable

## Phase 5: Documentation

### Documentation Requirements

**Recipe metadata (supports markdown):**
- `displayName`: User-friendly name with markdown formatting
- `description`: Detailed explanation with code examples, lists, links
- `@Option` descriptions: Clear explanations with inline code examples

**Example with markdown:**

```java
@Override
public String getDisplayName() {
    return "Update GitHub Actions to `actions/checkout@v4`";
}

@Override
public String getDescription() {
    return "Updates all uses of `actions/checkout@v2` and `actions/checkout@v3` to `actions/checkout@v4`.\n\n" +
           "**Before:**\n```yaml\n- uses: actions/checkout@v2\n```\n\n" +
           "**After:**\n```yaml\n- uses: actions/checkout@v4\n```";
}
```

**Usage examples:**
- Add Javadoc with common use cases
- Show before/after transformations
- Document parameter effects

## YAML LST Structure

Understanding the YAML LST hierarchy is essential:

- **Yaml.Documents** → **Yaml.Document** → **Yaml.Mapping** → **Yaml.Mapping.Entry**
- **Yaml.Sequence** → **Yaml.Sequence.Entry**
- **Yaml.Scalar** (primitive values)
- **YamlKey.getValue()** - always safe, no casting needed

## Technical Reference

### Recipe Template

Every OpenRewrite recipe follows this structure:

```java
@Value @EqualsAndHashCode(callSuper = false)
public class MyYamlRecipe extends Recipe {
    @Option(displayName = "...", description = "...", example = "...")
    String parameter;

    @Override public String getDisplayName() { return "..."; }
    @Override public String getDescription() { return "..."; }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new YamlIsoVisitor<ExecutionContext>() {
            @Override
            public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
                // Core logic here
                return super.visitMappingEntry(entry, ctx);
            }
        };
    }
}
```

### Essential Patterns

#### Key Matching

To match a specific YAML key:

```java
if ("targetKey".equals(entry.getKey().getValue())) { /* match */ }
```

#### Safe Value Access

Always check the type before casting:

```java
String value = entry.getValue() instanceof Yaml.Scalar ?
    ((Yaml.Scalar) entry.getValue()).getValue() : null;
```

#### JsonPath Matching

For complex path matching in YAML structures:

```java
JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");
if (matcher.matches(getCursor()) && "uses".equals(entry.getKey().getValue())) {
    // Process matching element
}
```

Common JsonPath patterns:
- `$.jobs.*.steps[*].uses` - Match "uses" field in any step of any job
- `$.on.push.branches[*]` - Match branch entries in push triggers
- `$.env.*` - Match any environment variable

#### Modification

To modify a YAML element, use `withX()` methods:

```java
return entry.withValue(scalar.withValue("newValue"));
```

Important: Always return modified copies, never mutate in place.

#### Search Results

To mark elements as search results without modifying:

```java
return SearchResult.found(entry, "Reason for marking this element");
```

### Core Visitor Methods

Override these methods in your YamlIsoVisitor:

- `visitMappingEntry()` - Process key-value pairs
- `visitScalar()` - Process primitive values
- `visitSequence()` - Process arrays/lists
- `visitSequenceEntry()` - Process individual array items

### Key Utilities

**SearchResult**: Mark elements in search recipes
```java
SearchResult.found(element, "description")
```

**ListUtils**: Transform collections safely
```java
ListUtils.map(list, item -> transformedItem)
```

**StringUtils**: Pattern matching
```java
StringUtils.matchesGlob(value, "actions/*@v2")
```

**Preconditions**: File filtering
```java
new Preconditions.Not(new FindSourceFiles("**/test/**"))
```

### Recipe Development Rules

1. **Always call super methods**: `return super.visitMappingEntry(entry, ctx);`
2. **Return modified copies**: Never mutate LST elements directly
3. **Use withX() methods**: All modifications via `withValue()`, `withKey()`, etc.
4. **Handle null cases**: Use conditional expressions for safe null handling
5. **Preserve formatting**: LST methods automatically maintain formatting
6. **Java 8 only**: No modern Java features

### Common Recipe Patterns

#### Search Recipe

Find all occurrences of a specific pattern:

```java
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");
    if (matcher.matches(getCursor()) && "uses".equals(entry.getKey().getValue())) {
        if (entry.getValue() instanceof Yaml.Scalar) {
            Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
            if (StringUtils.matchesGlob(scalar.getValue(), "actions/checkout@v2")) {
                return SearchResult.found(entry, "Found deprecated checkout action");
            }
        }
    }
    return super.visitMappingEntry(entry, ctx);
}
```

#### Replacement Recipe

Replace values matching a pattern:

```java
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");
    if (matcher.matches(getCursor()) && "uses".equals(entry.getKey().getValue())) {
        if (entry.getValue() instanceof Yaml.Scalar) {
            Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
            if ("actions/checkout@v2".equals(scalar.getValue())) {
                return entry.withValue(scalar.withValue("actions/checkout@v3"));
            }
        }
    }
    return super.visitMappingEntry(entry, ctx);
}
```

#### Add Missing Key Recipe

Add a key if it doesn't exist:

```java
@Override
public Yaml.Mapping visitMapping(Yaml.Mapping mapping, ExecutionContext ctx) {
    JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*");
    if (matcher.matches(getCursor())) {
        boolean hasTimeout = false;
        for (Yaml.Mapping.Entry entry : mapping.getEntries()) {
            if ("timeout-minutes".equals(entry.getKey().getValue())) {
                hasTimeout = true;
                break;
            }
        }
        if (!hasTimeout) {
            // Add timeout-minutes: 30
            Yaml.Mapping.Entry newEntry = new Yaml.Mapping.Entry(
                /* construct new entry */
            );
            return mapping.withEntries(
                ListUtils.concat(mapping.getEntries(), newEntry)
            );
        }
    }
    return super.visitMapping(mapping, ctx);
}
```

### OpenRewrite Traits (Advanced)

For complex recipes that benefit from higher-level semantic abstractions, you can use OpenRewrite Traits. Traits wrap LST elements with domain-specific logic.

**When you need detailed information about Traits**, refer to the companion guide: `./references/openrewrite-traits-guide.md`.

**Quick Traits Overview:**
- Traits implement `Trait<T extends Tree>` interface
- Include a nested `Matcher` class extending `SimpleTraitMatcher<T>`
- Use `matcher.asVisitor()` to convert to TreeVisitor in recipes
- Provide semantic methods like `getActionRef()` instead of raw LST navigation

**Example using Traits:**
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

For complete trait implementation patterns, matcher API details, and advanced examples, consult `./references/openrewrite-traits-guide.md`.

## Final Validation

### Production-Ready Checklist

- [ ] All tests pass (GREEN state maintained)
- [ ] Recipe follows OpenRewrite naming conventions (`com.yourorg.RecipeName`)
- [ ] No hardcoded values that should be parameters
- [ ] Recipe handles edge cases gracefully (no NPEs)
- [ ] Code is Java 8 compatible
- [ ] Formatting/comments preserved in YAML output
- [ ] Documentation is clear and includes examples
- [ ] Recipe could be contributed to OpenRewrite or org recipe library
- [ ] License header included if `gradle/licenseHeader.txt` exists

### Success Criteria

Recipe is production-ready when:
- Tests comprehensively cover happy path and edge cases
- Implementation follows OpenRewrite idioms (traits, composition)
- Documentation enables users to understand and use the recipe
- Code quality meets standards for upstream contribution

## Your Approach

When helping create OpenRewrite recipes:

1. **Phase 1 (RED)** - Write failing tests with before/after YAML
2. **Phase 2 (DECIDE)** - Choose declarative vs imperative approach
3. **Phase 3 (GREEN)** - Implement minimal working solution
4. **Phase 4 (REFACTOR)** - Apply OpenRewrite idioms (traits, composition)
5. **Phase 5 (DOCUMENT)** - Add markdown documentation and examples
6. **Validate** - Confirm production readiness with checklist

Always provide complete, working recipes with proper annotations, error handling, and clear comments explaining the logic.

## Remember

- **Always start with tests (RED)**
- **Try declarative before imperative**
- **Apply idioms during REFACTOR, not GREEN**
- **Document with markdown for clarity**
- **Validate production-readiness before completion**
