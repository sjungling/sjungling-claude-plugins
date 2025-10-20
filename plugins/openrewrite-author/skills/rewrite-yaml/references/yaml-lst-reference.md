# YAML LST Structure Reference

Complete reference for OpenRewrite's YAML Lossless Semantic Tree (LST) structure.

## Overview

The YAML LST represents YAML documents as a tree structure that preserves all formatting, comments, and whitespace. This allows transformations that maintain the original file's appearance.

## Type Hierarchy

```
org.openrewrite.yaml.tree.Yaml
├── Yaml.Documents (root container)
├── Yaml.Document (single document in multi-doc file)
├── Yaml.Mapping (key-value pairs, similar to JSON object)
│   └── Yaml.Mapping.Entry (single key-value pair)
├── Yaml.Sequence (arrays/lists)
│   └── Yaml.Sequence.Entry (single array item)
├── Yaml.Scalar (primitive values: strings, numbers, booleans)
│   └── Yaml.Scalar.Key (key in a key-value pair)
└── Yaml.Anchor (YAML anchors and aliases)
```

## Core Types

### Yaml.Documents

The root element containing one or more YAML documents.

```java
public interface Documents extends Yaml {
    List<Document> getDocuments();
    Documents withDocuments(List<Document> documents);
}
```

**Usage:**
```java
@Override
public Yaml.Documents visitDocuments(Yaml.Documents documents, ExecutionContext ctx) {
    // Process all documents in the file
    List<Yaml.Document> modified = ListUtils.map(
        documents.getDocuments(),
        doc -> (Yaml.Document) visit(doc, ctx)
    );
    return documents.withDocuments(modified);
}
```

---

### Yaml.Document

A single YAML document (files can contain multiple documents separated by `---`).

```java
public interface Document extends Yaml {
    Block getBlock();  // Root block (usually Mapping or Sequence)
    Document withBlock(Block block);
    boolean isExplicit();  // True if document starts with ---
}
```

**Usage:**
```java
@Override
public Yaml.Document visitDocument(Yaml.Document document, ExecutionContext ctx) {
    if (document.getBlock() instanceof Yaml.Mapping) {
        Yaml.Mapping root = (Yaml.Mapping) document.getBlock();
        // Process root mapping
        Yaml.Mapping modified = (Yaml.Mapping) visit(root, ctx);
        if (modified != root) {
            return document.withBlock(modified);
        }
    }
    return super.visitDocument(document, ctx);
}
```

---

### Yaml.Mapping

Represents a YAML mapping (key-value pairs), equivalent to JSON objects or Python dictionaries.

```java
public interface Mapping extends Block {
    List<Entry> getEntries();
    Mapping withEntries(List<Entry> entries);
    String getAnchor();  // YAML anchor if present
}
```

**Example YAML:**
```yaml
name: my-workflow
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
```

**Navigation:**
```java
@Override
public Yaml.Mapping visitMapping(Yaml.Mapping mapping, ExecutionContext ctx) {
    for (Yaml.Mapping.Entry entry : mapping.getEntries()) {
        String key = entry.getKey().getValue();
        Block value = entry.getValue();

        if ("jobs".equals(key) && value instanceof Yaml.Mapping) {
            Yaml.Mapping jobsMapping = (Yaml.Mapping) value;
            // Process each job
            for (Yaml.Mapping.Entry jobEntry : jobsMapping.getEntries()) {
                String jobName = jobEntry.getKey().getValue();
                // Process job...
            }
        }
    }
    return super.visitMapping(mapping, ctx);
}
```

---

### Yaml.Mapping.Entry

A single key-value pair within a mapping.

```java
public interface Entry extends Yaml {
    Yaml.Scalar.Key getKey();
    Block getValue();  // Can be Scalar, Mapping, or Sequence
    Entry withKey(Yaml.Scalar.Key key);
    Entry withValue(Block value);
}
```

**Key Methods:**
- `getKey().getValue()` - Get the key as a string (always safe, no cast needed)
- `getValue()` - Get the value (requires type check and cast)
- `withKey()` - Create new entry with different key
- `withValue()` - Create new entry with different value

**Usage:**
```java
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    String keyName = entry.getKey().getValue();  // Safe access

    // Check value type before processing
    if (entry.getValue() instanceof Yaml.Scalar) {
        Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
        String value = scalar.getValue();

        // Modify value
        if ("old-value".equals(value)) {
            return entry.withValue(scalar.withValue("new-value"));
        }
    } else if (entry.getValue() instanceof Yaml.Mapping) {
        Yaml.Mapping nested = (Yaml.Mapping) entry.getValue();
        // Process nested mapping
    } else if (entry.getValue() instanceof Yaml.Sequence) {
        Yaml.Sequence sequence = (Yaml.Sequence) entry.getValue();
        // Process sequence
    }

    return super.visitMappingEntry(entry, ctx);
}
```

---

### Yaml.Sequence

Represents a YAML sequence (array/list).

```java
public interface Sequence extends Block {
    List<Entry> getEntries();
    Sequence withEntries(List<Entry> entries);
    String getAnchor();
}
```

**Example YAML:**
```yaml
branches:
  - main
  - develop
  - feature/*

# Or inline style:
branches: [main, develop, feature/*]
```

**Navigation:**
```java
@Override
public Yaml.Sequence visitSequence(Yaml.Sequence sequence, ExecutionContext ctx) {
    List<Yaml.Sequence.Entry> entries = sequence.getEntries();

    // Iterate through sequence items
    for (Yaml.Sequence.Entry entry : entries) {
        if (entry.getBlock() instanceof Yaml.Scalar) {
            Yaml.Scalar scalar = (Yaml.Scalar) entry.getBlock();
            String value = scalar.getValue();
            // Process value...
        } else if (entry.getBlock() instanceof Yaml.Mapping) {
            Yaml.Mapping mapping = (Yaml.Mapping) entry.getBlock();
            // Process mapping item...
        }
    }

    return super.visitSequence(sequence, ctx);
}
```

**Adding Items:**
```java
@Override
public Yaml.Sequence visitSequence(Yaml.Sequence sequence, ExecutionContext ctx) {
    // Check if 'main' branch exists
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
        // Create new scalar for 'main'
        Yaml.Scalar mainScalar = new Yaml.Scalar(
            Tree.randomId(),
            Space.EMPTY,
            Markers.EMPTY,
            Yaml.Scalar.Style.PLAIN,
            null,
            "main"
        );

        // Wrap in sequence entry
        Yaml.Sequence.Entry mainEntry = new Yaml.Sequence.Entry(
            Tree.randomId(),
            Space.format("\n  - "),  // Proper indentation
            Markers.EMPTY,
            mainScalar,
            false
        );

        // Add to sequence
        return sequence.withEntries(
            ListUtils.concat(sequence.getEntries(), mainEntry)
        );
    }

    return super.visitSequence(sequence, ctx);
}
```

---

### Yaml.Sequence.Entry

A single item in a sequence.

```java
public interface Entry extends Yaml {
    Block getBlock();  // The actual value
    Entry withBlock(Block block);
    boolean isTrailingCommaPrefix();
}
```

**Usage:**
```java
@Override
public Yaml.Sequence.Entry visitSequenceEntry(Yaml.Sequence.Entry entry, ExecutionContext ctx) {
    if (entry.getBlock() instanceof Yaml.Scalar) {
        Yaml.Scalar scalar = (Yaml.Scalar) entry.getBlock();
        String value = scalar.getValue();

        // Update version references
        if (value.contains("@v2")) {
            String updated = value.replace("@v2", "@v3");
            return entry.withBlock(scalar.withValue(updated));
        }
    }

    return super.visitSequenceEntry(entry, ctx);
}
```

---

### Yaml.Scalar

Represents primitive values (strings, numbers, booleans, null).

```java
public interface Scalar extends Block {
    Style getStyle();  // PLAIN, SINGLE_QUOTED, DOUBLE_QUOTED, etc.
    String getAnchor();
    String getValue();
    Scalar withValue(String value);
    Scalar withStyle(Style style);

    enum Style {
        PLAIN,
        SINGLE_QUOTED,
        DOUBLE_QUOTED,
        LITERAL,
        FOLDED
    }
}
```

**Example YAML:**
```yaml
plain: value
single: 'value'
double: "value"
number: 42
boolean: true
null_value: null
multiline: |
  Line 1
  Line 2
```

**Usage:**
```java
// Reading scalar values
if (entry.getValue() instanceof Yaml.Scalar) {
    Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
    String value = scalar.getValue();
    Yaml.Scalar.Style style = scalar.getStyle();

    // Modify value while preserving style
    Yaml.Scalar updated = scalar.withValue("new-value");
    return entry.withValue(updated);
}

// Creating new scalars
Yaml.Scalar newScalar = new Yaml.Scalar(
    Tree.randomId(),           // Unique ID
    Space.EMPTY,               // Prefix whitespace
    Markers.EMPTY,             // Markers for search results, etc.
    Yaml.Scalar.Style.PLAIN,   // Quoting style
    null,                      // Anchor
    "value"                    // Actual value
);
```

---

### Yaml.Scalar.Key

Special scalar type used for keys in mappings.

```java
public interface Key extends Yaml {
    String getValue();
    Key withValue(String value);
}
```

**Usage:**
```java
// Keys are always accessible via entry.getKey()
String keyName = entry.getKey().getValue();  // No casting needed!

// Rename a key
if ("old-key".equals(entry.getKey().getValue())) {
    Yaml.Scalar.Key newKey = entry.getKey().withValue("new-key");
    return entry.withKey(newKey);
}
```

---

## Navigation Patterns

### Cursor Navigation

The `Cursor` provides context about the current position in the tree.

```java
// Get parent elements
Cursor parent = getCursor().getParent();
Cursor grandparent = getCursor().getParent(2);

// Check parent type
if (parent != null && parent.getValue() instanceof Yaml.Mapping) {
    Yaml.Mapping parentMapping = (Yaml.Mapping) parent.getValue();
    // Process parent...
}

// Get all ancestors of a type
Iterator<Yaml.Mapping> mappings = getCursor().getPathAsStream()
    .filter(p -> p instanceof Yaml.Mapping)
    .map(p -> (Yaml.Mapping) p)
    .iterator();
```

### Finding Siblings

```java
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    // Get parent mapping to access siblings
    Cursor parent = getCursor().getParent();
    if (parent != null && parent.getValue() instanceof Yaml.Mapping) {
        Yaml.Mapping parentMapping = (Yaml.Mapping) parent.getValue();

        // Find sibling entries
        for (Yaml.Mapping.Entry sibling : parentMapping.getEntries()) {
            if (sibling != entry) {
                String siblingKey = sibling.getKey().getValue();
                // Check sibling...
            }
        }
    }

    return super.visitMappingEntry(entry, ctx);
}
```

### Path-Based Navigation with JsonPath

```java
// Match specific paths in YAML structure
JsonPathMatcher jobMatcher = new JsonPathMatcher("$.jobs.*");
JsonPathMatcher stepMatcher = new JsonPathMatcher("$.jobs.*.steps[*]");
JsonPathMatcher usesMatcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");

@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    if (usesMatcher.matches(getCursor()) && "uses".equals(entry.getKey().getValue())) {
        // This is a 'uses' field within a step
        // Process it...
    }
    return super.visitMappingEntry(entry, ctx);
}
```

---

## Type Checking and Casting

### Safe Type Checking Pattern

```java
Block value = entry.getValue();

if (value instanceof Yaml.Scalar) {
    Yaml.Scalar scalar = (Yaml.Scalar) value;
    String stringValue = scalar.getValue();
    // Process scalar...

} else if (value instanceof Yaml.Mapping) {
    Yaml.Mapping mapping = (Yaml.Mapping) value;
    // Process mapping...

} else if (value instanceof Yaml.Sequence) {
    Yaml.Sequence sequence = (Yaml.Sequence) value;
    // Process sequence...

} else {
    // Handle other types or null
}
```

### Null Safety

```java
// Keys never need null checking (always present)
String key = entry.getKey().getValue();  // Safe

// Values might be null or unexpected types
Block value = entry.getValue();
if (value == null) {
    // Handle null value (represents 'key:' with no value)
}

// Scalar values can be null string
if (value instanceof Yaml.Scalar) {
    Yaml.Scalar scalar = (Yaml.Scalar) value;
    String stringValue = scalar.getValue();
    if (stringValue == null || "null".equals(stringValue)) {
        // Handle YAML null
    }
}
```

---

## Creating New Elements

### Creating Scalars

```java
// Plain scalar
Yaml.Scalar plain = new Yaml.Scalar(
    Tree.randomId(),
    Space.EMPTY,
    Markers.EMPTY,
    Yaml.Scalar.Style.PLAIN,
    null,
    "value"
);

// Quoted scalar
Yaml.Scalar quoted = new Yaml.Scalar(
    Tree.randomId(),
    Space.EMPTY,
    Markers.EMPTY,
    Yaml.Scalar.Style.DOUBLE_QUOTED,
    null,
    "value with spaces"
);
```

### Creating Mapping Entries

```java
// Create key
Yaml.Scalar.Key key = new Yaml.Scalar.Key(
    Tree.randomId(),
    Space.EMPTY,
    Markers.EMPTY,
    "key-name"
);

// Create value
Yaml.Scalar value = new Yaml.Scalar(
    Tree.randomId(),
    Space.EMPTY,
    Markers.EMPTY,
    Yaml.Scalar.Style.PLAIN,
    null,
    "value"
);

// Create entry
Yaml.Mapping.Entry newEntry = new Yaml.Mapping.Entry(
    Tree.randomId(),
    Space.format("\n  "),  // Indentation
    Markers.EMPTY,
    key,
    Space.format(" "),     // Space after colon
    value
);
```

### Creating Sequences

```java
// Create sequence items
List<Yaml.Sequence.Entry> entries = new ArrayList<>();

entries.add(new Yaml.Sequence.Entry(
    Tree.randomId(),
    Space.format("\n  - "),
    Markers.EMPTY,
    new Yaml.Scalar(Tree.randomId(), Space.EMPTY, Markers.EMPTY,
                    Yaml.Scalar.Style.PLAIN, null, "item1"),
    false
));

entries.add(new Yaml.Sequence.Entry(
    Tree.randomId(),
    Space.format("\n  - "),
    Markers.EMPTY,
    new Yaml.Scalar(Tree.randomId(), Space.EMPTY, Markers.EMPTY,
                    Yaml.Scalar.Style.PLAIN, null, "item2"),
    false
));

// Create sequence
Yaml.Sequence sequence = new Yaml.Sequence(
    Tree.randomId(),
    Space.EMPTY,
    Markers.EMPTY,
    null,  // anchor
    entries
);
```

---

## Common Pitfalls

### 1. Not Calling Super Methods

```java
// ❌ WRONG - tree traversal stops
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    if ("target".equals(entry.getKey().getValue())) {
        return entry.withValue(newValue);
    }
    return entry;  // ❌ Should call super
}

// ✅ CORRECT
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    if ("target".equals(entry.getKey().getValue())) {
        return entry.withValue(newValue);
    }
    return super.visitMappingEntry(entry, ctx);  // ✅
}
```

### 2. Mutating Instead of Creating New Objects

```java
// ❌ WRONG - LST is immutable
Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
scalar.setValue("new-value");  // ❌ This doesn't exist

// ✅ CORRECT
Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
Yaml.Scalar updated = scalar.withValue("new-value");
return entry.withValue(updated);
```

### 3. Forgetting Type Checks

```java
// ❌ WRONG - may throw ClassCastException
Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();

// ✅ CORRECT
if (entry.getValue() instanceof Yaml.Scalar) {
    Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
    // Process safely
}
```

### 4. Incorrect Whitespace/Indentation

```java
// ❌ WRONG - no indentation
Space.EMPTY  // Results in key:value on same line as parent

// ✅ CORRECT - proper YAML indentation
Space.format("\n  ")  // Newline + 2-space indent
```

### 5. Not Returning Original When Unchanged

```java
// ❌ WRONG - creates unnecessary tree copies
return entry.withValue(entry.getValue());

// ✅ CORRECT - return original if unchanged
if (shouldModify) {
    return entry.withValue(newValue);
}
return super.visitMappingEntry(entry, ctx);  // Returns original
```

---

## Complete Example: Multi-Level Navigation

```java
/**
 * Find all GitHub Actions steps using deprecated actions
 * and update them to newer versions
 */
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    // Match: $.jobs.*.steps[*].uses
    JsonPathMatcher usesMatcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");

    if (usesMatcher.matches(getCursor()) && "uses".equals(entry.getKey().getValue())) {
        if (entry.getValue() instanceof Yaml.Scalar) {
            Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
            String actionRef = scalar.getValue();

            // Navigate to parent step to check conditions
            Cursor stepCursor = getCursor().getParent(2);
            if (stepCursor != null && stepCursor.getValue() instanceof Yaml.Mapping) {
                Yaml.Mapping step = (Yaml.Mapping) stepCursor.getValue();

                // Check if step has 'if' condition
                boolean hasCondition = false;
                for (Yaml.Mapping.Entry stepEntry : step.getEntries()) {
                    if ("if".equals(stepEntry.getKey().getValue())) {
                        hasCondition = true;
                        break;
                    }
                }

                // Only update unconditional steps
                if (!hasCondition && actionRef.contains("@v2")) {
                    String updated = actionRef.replace("@v2", "@v3");
                    return entry.withValue(scalar.withValue(updated));
                }
            }
        }
    }

    return super.visitMappingEntry(entry, ctx);
}
```

---

## Reference Chart

| LST Type | Represents | Common Methods | Notes |
|----------|-----------|----------------|-------|
| `Documents` | File root | `getDocuments()` | Container for multiple docs |
| `Document` | Single doc | `getBlock()` | May have `---` separator |
| `Mapping` | Key-value pairs | `getEntries()` | Like JSON object |
| `Mapping.Entry` | One key-value | `getKey()`, `getValue()` | Basic building block |
| `Sequence` | Array/list | `getEntries()` | Ordered collection |
| `Sequence.Entry` | Array item | `getBlock()` | Wraps actual value |
| `Scalar` | Primitive value | `getValue()`, `getStyle()` | String, number, bool, null |
| `Scalar.Key` | Mapping key | `getValue()` | Always string, no cast needed |

## Additional Resources

- OpenRewrite YAML LST JavaDoc: https://docs.openrewrite.org/reference/yaml-lossless-semantic-trees
- YAML Specification: https://yaml.org/spec/1.2/spec.html
- OpenRewrite Visitor Pattern: https://docs.openrewrite.org/concepts-and-explanations/visitors
