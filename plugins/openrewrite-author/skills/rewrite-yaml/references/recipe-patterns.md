# Common OpenRewrite YAML Recipe Patterns

This reference provides complete, working examples of common YAML recipe patterns.

## Table of Contents

1. [Search Recipes](#search-recipes)
2. [Replacement Recipes](#replacement-recipes)
3. [Add Missing Key Recipes](#add-missing-key-recipes)
4. [Delete Key Recipes](#delete-key-recipes)
5. [Modify Sequence Recipes](#modify-sequence-recipes)
6. [Conditional Transformation Recipes](#conditional-transformation-recipes)

---

## Search Recipes

Find and mark elements matching specific patterns without modification.

### Basic Search Pattern

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

### Multi-Pattern Search

```java
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.runs-on");
    if (matcher.matches(getCursor()) && "runs-on".equals(entry.getKey().getValue())) {
        if (entry.getValue() instanceof Yaml.Scalar) {
            Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
            String value = scalar.getValue();
            // Check multiple deprecated patterns
            if ("ubuntu-18.04".equals(value) || "ubuntu-16.04".equals(value)) {
                return SearchResult.found(entry, "Found deprecated Ubuntu version: " + value);
            }
        }
    }
    return super.visitMappingEntry(entry, ctx);
}
```

---

## Replacement Recipes

Replace values matching specific patterns.

### Simple Value Replacement

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

### Pattern-Based Replacement (Version Bumping)

```java
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");
    if (matcher.matches(getCursor()) && "uses".equals(entry.getKey().getValue())) {
        if (entry.getValue() instanceof Yaml.Scalar) {
            Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
            String value = scalar.getValue();
            // Replace any @v2 with @v3
            if (value.contains("@v2")) {
                String newValue = value.replace("@v2", "@v3");
                return entry.withValue(scalar.withValue(newValue));
            }
        }
    }
    return super.visitMappingEntry(entry, ctx);
}
```

### Conditional Replacement Based on Context

```java
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    // Only replace runs-on if the job has specific characteristics
    if ("runs-on".equals(entry.getKey().getValue())) {
        if (entry.getValue() instanceof Yaml.Scalar) {
            Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
            // Check if parent mapping has a "container" key
            Cursor parent = getCursor().getParent(2); // Navigate to job mapping
            if (parent != null && parent.getValue() instanceof Yaml.Mapping) {
                Yaml.Mapping jobMapping = (Yaml.Mapping) parent.getValue();
                boolean hasContainer = false;
                for (Yaml.Mapping.Entry e : jobMapping.getEntries()) {
                    if ("container".equals(e.getKey().getValue())) {
                        hasContainer = true;
                        break;
                    }
                }
                // Only update if no container is specified
                if (!hasContainer && "ubuntu-latest".equals(scalar.getValue())) {
                    return entry.withValue(scalar.withValue("ubuntu-22.04"));
                }
            }
        }
    }
    return super.visitMappingEntry(entry, ctx);
}
```

---

## Add Missing Key Recipes

Add keys to mappings when they don't exist.

### Add Default Timeout to Jobs

```java
@Override
public Yaml.Mapping visitMapping(Yaml.Mapping mapping, ExecutionContext ctx) {
    JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*");
    if (matcher.matches(getCursor())) {
        // Check if timeout-minutes already exists
        boolean hasTimeout = false;
        for (Yaml.Mapping.Entry entry : mapping.getEntries()) {
            if ("timeout-minutes".equals(entry.getKey().getValue())) {
                hasTimeout = true;
                break;
            }
        }

        if (!hasTimeout) {
            // Create new entry for timeout-minutes: 30
            Yaml.Scalar timeoutValue = new Yaml.Scalar(
                Tree.randomId(),
                Space.EMPTY,
                Markers.EMPTY,
                Yaml.Scalar.Style.PLAIN,
                null,
                "30"
            );

            Yaml.Mapping.Entry timeoutEntry = new Yaml.Mapping.Entry(
                Tree.randomId(),
                Space.format("\n  "),
                Markers.EMPTY,
                new Yaml.Scalar.Key(
                    Tree.randomId(),
                    Space.EMPTY,
                    Markers.EMPTY,
                    "timeout-minutes"
                ),
                Space.format(" "),
                timeoutValue
            );

            return mapping.withEntries(
                ListUtils.concat(mapping.getEntries(), timeoutEntry)
            );
        }
    }
    return super.visitMapping(mapping, ctx);
}
```

### Add Permissions Block if Missing

```java
@Override
public Yaml.Document visitDocument(Yaml.Document document, ExecutionContext ctx) {
    if (document.getBlock() instanceof Yaml.Mapping) {
        Yaml.Mapping root = (Yaml.Mapping) document.getBlock();

        // Check if permissions key exists at root level
        boolean hasPermissions = false;
        for (Yaml.Mapping.Entry entry : root.getEntries()) {
            if ("permissions".equals(entry.getKey().getValue())) {
                hasPermissions = true;
                break;
            }
        }

        if (!hasPermissions) {
            // Create permissions: read-all
            Yaml.Scalar permValue = new Yaml.Scalar(
                Tree.randomId(),
                Space.EMPTY,
                Markers.EMPTY,
                Yaml.Scalar.Style.PLAIN,
                null,
                "read-all"
            );

            Yaml.Mapping.Entry permEntry = new Yaml.Mapping.Entry(
                Tree.randomId(),
                Space.format("\n"),
                Markers.EMPTY,
                new Yaml.Scalar.Key(
                    Tree.randomId(),
                    Space.EMPTY,
                    Markers.EMPTY,
                    "permissions"
                ),
                Space.format(" "),
                permValue
            );

            Yaml.Mapping newRoot = root.withEntries(
                ListUtils.concat(root.getEntries(), permEntry)
            );

            return document.withBlock(newRoot);
        }
    }
    return super.visitDocument(document, ctx);
}
```

---

## Delete Key Recipes

Remove keys from YAML structures.

### Delete Specific Key

```java
@Override
public Yaml.Mapping visitMapping(Yaml.Mapping mapping, ExecutionContext ctx) {
    List<Yaml.Mapping.Entry> updatedEntries = new ArrayList<>();
    boolean modified = false;

    for (Yaml.Mapping.Entry entry : mapping.getEntries()) {
        // Remove deprecated 'master' branch reference
        if ("master".equals(entry.getKey().getValue())) {
            JsonPathMatcher matcher = new JsonPathMatcher("$.on.push.branches[*]");
            if (matcher.matches(getCursor())) {
                modified = true;
                continue; // Skip this entry (delete it)
            }
        }
        updatedEntries.add(entry);
    }

    if (modified) {
        return mapping.withEntries(updatedEntries);
    }
    return super.visitMapping(mapping, ctx);
}
```

### Delete Key Conditionally

```java
@Override
public Yaml.Mapping visitMapping(Yaml.Mapping mapping, ExecutionContext ctx) {
    JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*");
    if (matcher.matches(getCursor())) {
        List<Yaml.Mapping.Entry> updatedEntries = new ArrayList<>();
        boolean modified = false;

        for (Yaml.Mapping.Entry entry : mapping.getEntries()) {
            // Delete 'continue-on-error' if it's set to false (default behavior)
            if ("continue-on-error".equals(entry.getKey().getValue())) {
                if (entry.getValue() instanceof Yaml.Scalar) {
                    Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
                    if ("false".equals(scalar.getValue())) {
                        modified = true;
                        continue; // Skip this entry
                    }
                }
            }
            updatedEntries.add(entry);
        }

        if (modified) {
            return mapping.withEntries(updatedEntries);
        }
    }
    return super.visitMapping(mapping, ctx);
}
```

---

## Modify Sequence Recipes

Transform array/list structures.

### Add Item to Sequence

```java
@Override
public Yaml.Sequence visitSequence(Yaml.Sequence sequence, ExecutionContext ctx) {
    JsonPathMatcher matcher = new JsonPathMatcher("$.on.push.branches");
    if (matcher.matches(getCursor())) {
        // Check if 'main' branch already exists
        boolean hasMain = false;
        for (Yaml.Sequence.Entry entry : sequence.getEntries()) {
            if (entry.getBlock() instanceof Yaml.Scalar) {
                Yaml.Scalar scalar = (Yaml.Scalar) entry.getBlock();
                if ("main".equals(scalar.getValue())) {
                    hasMain = true;
                    break;
                }
            }
        }

        if (!hasMain) {
            // Add 'main' branch
            Yaml.Scalar mainScalar = new Yaml.Scalar(
                Tree.randomId(),
                Space.EMPTY,
                Markers.EMPTY,
                Yaml.Scalar.Style.PLAIN,
                null,
                "main"
            );

            Yaml.Sequence.Entry mainEntry = new Yaml.Sequence.Entry(
                Tree.randomId(),
                Space.format("\n    - "),
                Markers.EMPTY,
                mainScalar,
                false
            );

            return sequence.withEntries(
                ListUtils.concat(sequence.getEntries(), mainEntry)
            );
        }
    }
    return super.visitSequence(sequence, ctx);
}
```

### Replace Items in Sequence

```java
@Override
public Yaml.Sequence.Entry visitSequenceEntry(Yaml.Sequence.Entry entry, ExecutionContext ctx) {
    JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.strategy.matrix.os[*]");
    if (matcher.matches(getCursor())) {
        if (entry.getBlock() instanceof Yaml.Scalar) {
            Yaml.Scalar scalar = (Yaml.Scalar) entry.getBlock();
            // Replace ubuntu-18.04 with ubuntu-22.04
            if ("ubuntu-18.04".equals(scalar.getValue())) {
                return entry.withBlock(scalar.withValue("ubuntu-22.04"));
            }
        }
    }
    return super.visitSequenceEntry(entry, ctx);
}
```

### Filter Sequence Items

```java
@Override
public Yaml.Sequence visitSequence(Yaml.Sequence sequence, ExecutionContext ctx) {
    JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps");
    if (matcher.matches(getCursor())) {
        List<Yaml.Sequence.Entry> filteredEntries = new ArrayList<>();
        boolean modified = false;

        for (Yaml.Sequence.Entry entry : sequence.getEntries()) {
            // Remove steps that use deprecated actions
            boolean shouldRemove = false;
            if (entry.getBlock() instanceof Yaml.Mapping) {
                Yaml.Mapping stepMapping = (Yaml.Mapping) entry.getBlock();
                for (Yaml.Mapping.Entry mapEntry : stepMapping.getEntries()) {
                    if ("uses".equals(mapEntry.getKey().getValue())) {
                        if (mapEntry.getValue() instanceof Yaml.Scalar) {
                            Yaml.Scalar scalar = (Yaml.Scalar) mapEntry.getValue();
                            if (scalar.getValue().startsWith("deprecated/")) {
                                shouldRemove = true;
                                modified = true;
                                break;
                            }
                        }
                    }
                }
            }

            if (!shouldRemove) {
                filteredEntries.add(entry);
            }
        }

        if (modified) {
            return sequence.withEntries(filteredEntries);
        }
    }
    return super.visitSequence(sequence, ctx);
}
```

---

## Conditional Transformation Recipes

Apply transformations based on complex conditions.

### Transform Based on Multiple Conditions

```java
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    // Update node version only for non-matrix jobs
    if ("node-version".equals(entry.getKey().getValue())) {
        if (entry.getValue() instanceof Yaml.Scalar) {
            Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();

            // Check if we're inside a matrix strategy
            boolean inMatrix = false;
            Cursor cursor = getCursor();
            while (cursor != null) {
                if (cursor.getValue() instanceof Yaml.Mapping) {
                    Yaml.Mapping mapping = (Yaml.Mapping) cursor.getValue();
                    for (Yaml.Mapping.Entry e : mapping.getEntries()) {
                        if ("matrix".equals(e.getKey().getValue())) {
                            inMatrix = true;
                            break;
                        }
                    }
                }
                cursor = cursor.getParent();
            }

            // Only update if not in matrix and version is old
            if (!inMatrix && "14".equals(scalar.getValue())) {
                return entry.withValue(scalar.withValue("18"));
            }
        }
    }
    return super.visitMappingEntry(entry, ctx);
}
```

### Transform Based on Sibling Values

```java
@Override
public Yaml.Mapping visitMapping(Yaml.Mapping mapping, ExecutionContext ctx) {
    JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps[*]");
    if (matcher.matches(getCursor())) {
        // Find if this step has a 'uses' that needs configuration update
        String usesValue = null;
        Yaml.Mapping.Entry withEntry = null;

        for (Yaml.Mapping.Entry entry : mapping.getEntries()) {
            if ("uses".equals(entry.getKey().getValue())) {
                if (entry.getValue() instanceof Yaml.Scalar) {
                    usesValue = ((Yaml.Scalar) entry.getValue()).getValue();
                }
            } else if ("with".equals(entry.getKey().getValue())) {
                withEntry = entry;
            }
        }

        // If using actions/cache@v3, ensure 'with' has 'key' parameter
        if ("actions/cache@v3".equals(usesValue) && withEntry != null) {
            if (withEntry.getValue() instanceof Yaml.Mapping) {
                Yaml.Mapping withMapping = (Yaml.Mapping) withEntry.getValue();
                boolean hasKey = false;
                for (Yaml.Mapping.Entry e : withMapping.getEntries()) {
                    if ("key".equals(e.getKey().getValue())) {
                        hasKey = true;
                        break;
                    }
                }

                if (!hasKey) {
                    // Add default key parameter
                    Yaml.Scalar keyValue = new Yaml.Scalar(
                        Tree.randomId(),
                        Space.EMPTY,
                        Markers.EMPTY,
                        Yaml.Scalar.Style.PLAIN,
                        null,
                        "${{ runner.os }}-cache"
                    );

                    Yaml.Mapping.Entry keyEntry = new Yaml.Mapping.Entry(
                        Tree.randomId(),
                        Space.format("\n          "),
                        Markers.EMPTY,
                        new Yaml.Scalar.Key(
                            Tree.randomId(),
                            Space.EMPTY,
                            Markers.EMPTY,
                            "key"
                        ),
                        Space.format(" "),
                        keyValue
                    );

                    Yaml.Mapping updatedWith = withMapping.withEntries(
                        ListUtils.concat(withMapping.getEntries(), keyEntry)
                    );

                    List<Yaml.Mapping.Entry> updatedEntries = ListUtils.map(
                        mapping.getEntries(),
                        e -> e == withEntry ? withEntry.withValue(updatedWith) : e
                    );

                    return mapping.withEntries(updatedEntries);
                }
            }
        }
    }
    return super.visitMapping(mapping, ctx);
}
```

### Multi-File Context Transformation

```java
@Value
@EqualsAndHashCode(callSuper = false)
public class UpdateBasedOnOtherFiles extends Recipe {

    @Override
    public String getDisplayName() {
        return "Update YAML based on other files";
    }

    @Override
    public String getDescription() {
        return "Updates YAML configuration based on context from other files in the repository";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new YamlIsoVisitor<ExecutionContext>() {
            @Override
            public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
                if ("python-version".equals(entry.getKey().getValue())) {
                    // Check if project has pyproject.toml with Python version requirement
                    // This would require scanning other files in context
                    // Store findings in ExecutionContext for cross-file analysis
                    String requiredVersion = ctx.getMessage("python.version", "3.9");

                    if (entry.getValue() instanceof Yaml.Scalar) {
                        Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
                        if (!requiredVersion.equals(scalar.getValue())) {
                            return entry.withValue(scalar.withValue(requiredVersion));
                        }
                    }
                }
                return super.visitMappingEntry(entry, ctx);
            }
        };
    }
}
```

---

## Pattern Summary

| Pattern | Use Case | Complexity |
|---------|----------|------------|
| Search | Find elements without modification | Low |
| Simple Replacement | Direct value substitution | Low |
| Pattern Replacement | String manipulation, version bumping | Medium |
| Add Missing Key | Ensure required fields exist | Medium |
| Delete Key | Remove deprecated/unnecessary fields | Medium |
| Sequence Modification | Add/remove/update list items | Medium |
| Conditional Transform | Context-aware transformations | High |
| Multi-File Context | Cross-file analysis and updates | High |

## Best Practices

1. **Always call super methods** to ensure tree traversal continues
2. **Return original object if unchanged** for performance
3. **Use JsonPathMatcher for complex path matching**
4. **Check types before casting** (use `instanceof`)
5. **Handle null cases gracefully**
6. **Preserve formatting** (LST handles this automatically with proper spacing)
7. **Test edge cases** (empty files, missing keys, null values)
8. **Use ListUtils for collection transformations**
9. **Store context in ExecutionContext** for multi-file analysis
10. **Keep recipes focused** - one responsibility per recipe
