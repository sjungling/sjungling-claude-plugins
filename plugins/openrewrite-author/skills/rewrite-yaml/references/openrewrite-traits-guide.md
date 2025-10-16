# OpenRewrite Traits Guide

This is a reference guide for understanding and using OpenRewrite Traits in recipe development.

## What are Traits?

Traits are semantic wrappers around LST elements that implement the `Trait<T extends Tree>` interface. They encapsulate domain-specific logic for identifying and accessing properties of tree elements, providing a higher-level abstraction over raw LST navigation.

## IMPORTANT - Deprecated Traits Utility Classes

Older OpenRewrite code used utility classes like `org.openrewrite.java.trait.Traits`, `org.openrewrite.gradle.trait.Traits`, etc. These are now deprecated. Always instantiate matchers directly:

```java
// ❌ Old (deprecated):
Traits.literal()
Traits.methodAccess("...")

// ✅ New (preferred):
new Literal.Matcher()
new MethodAccess.Matcher("...")
```

## Core Trait Interface

The Trait interface is minimal and only requires implementing `getCursor()`:

```java
public interface Trait<T extends Tree> {
    Cursor getCursor();

    default T getTree() {
        return getCursor().getValue();
    }
}
```

## Example Trait Implementation

Here's a complete trait implementation pattern (implementation details like Lombok are optional):

```java
// Using Lombok for convenience (optional - you can implement manually)
@Value
public class YamlScalar implements Trait<Yaml.Block> {
    Cursor cursor;  // Required for getCursor()

    // Optional: Additional fields for caching computed values
    @Nullable String cachedValue;

    // Domain-specific accessor methods
    public @Nullable String getValue() {
        if (cachedValue != null) {
            return cachedValue;
        }
        Yaml.Block block = getTree();
        return block instanceof Yaml.Scalar
            ? ((Yaml.Scalar) block).getValue()
            : null;
    }

    // Static utility methods for shared logic
    public static boolean isScalar(Cursor cursor) {
        return cursor.getValue() instanceof Yaml.Scalar;
    }

    // Modification methods return new trait instances
    public YamlScalar withValue(String newValue) {
        Yaml.Scalar scalar = (Yaml.Scalar) getTree();
        Yaml.Scalar updated = scalar.withValue(newValue);
        return new YamlScalar(cursor.withValue(updated), null);
    }

    // Matcher nested as static inner class
    public static class Matcher extends SimpleTraitMatcher<YamlScalar> {
        // Optional: Configuration fields for filtering
        @Nullable
        protected String requiredValue;

        @Override
        protected @Nullable YamlScalar test(Cursor cursor) {
            Object value = cursor.getValue();
            if (!(value instanceof Yaml.Block)) {
                return null;
            }

            // Complex matching logic with guards
            if (!isScalar(cursor)) {
                return null;
            }

            Yaml.Scalar scalar = (Yaml.Scalar) value;

            // Apply filters if configured
            if (requiredValue != null &&
                !requiredValue.equals(scalar.getValue())) {
                return null;
            }

            // Return trait with cached data
            return new YamlScalar(cursor, scalar.getValue());
        }

        // Configuration methods for the matcher
        public Matcher withRequiredValue(String value) {
            this.requiredValue = value;
            return this;
        }
    }
}
```

## Important Implementation Notes

1. **Required Interface**: Only `getCursor()` is required by the Trait interface
2. **Implementation Flexibility**: You can use Lombok, manual implementation, or any pattern you prefer
3. **Matcher as Inner Class**: By convention, nest the Matcher as a static inner class
4. **Additional Fields**: Traits can have fields beyond cursor to cache expensive computations
5. **Static Utilities**: Include static helper methods for validation and shared logic
6. **Matcher Fields**: Matchers can have configuration fields for filtering behavior
7. **test() Complexity**: Real `test()` methods often contain substantial validation logic, not just simple instanceof checks

## TraitMatcher API Methods

The `TraitMatcher` interface provides several powerful methods for finding traits in the LST. Understanding these methods is essential for effective trait usage. The `SimpleTraitMatcher<U>` base class implements all these methods using a single abstract `test(Cursor)` method.

### Core API Methods

```java
// Test if cursor matches and return trait instance
Optional<U> get(Cursor cursor)

// Like get() but throws NoSuchElementException if no match
U require(Cursor cursor)

// Stream of all matching traits in ancestor chain (up the tree)
Stream<U> higher(Cursor cursor)

// Stream of all matching traits in descendants (down the tree)
Stream<U> lower(Cursor cursor)

// Stream of all matching traits in entire source file
Stream<U> lower(SourceFile sourceFile)

// Convert matcher to TreeVisitor for use in recipes
<P> TreeVisitor<? extends Tree, P> asVisitor(VisitFunction2<U, P> visitor)
```

### How SimpleTraitMatcher Implements These Methods

`SimpleTraitMatcher<U>` provides default implementations of all TraitMatcher methods by calling your abstract `test(Cursor)` method:

- `get(Cursor)` - Calls `test(cursor)` and wraps result in Optional
- `require(Cursor)` - Calls `test(cursor)` and throws if null
- `higher(Cursor)` - Walks up cursor stack, calling `test()` on each ancestor
- `lower(Cursor)` - Visits all descendants, calling `test()` on each node
- `asVisitor()` - Creates a TreeVisitor that calls `test()` on every visited node

This means you only need to implement `test(Cursor)` to get all these capabilities.

## Example 1: Finding All Traits in a File

Use `lower()` to find all matching traits in a source file or subtree:

```java
// Create matcher for GitHub Actions steps
ActionStep.Matcher stepMatcher = new ActionStep.Matcher();

// In your visitor, find all ActionStep traits in the entire file
@Override
public Yaml.Documents visitDocuments(Yaml.Documents documents, ExecutionContext ctx) {
    // Get stream of all ActionStep traits in this file
    Stream<ActionStep> allSteps = stepMatcher.lower(documents);

    // Process the stream - e.g., collect all action references
    List<String> actionRefs = allSteps
        .map(step -> step.getActionRef())
        .filter(ref -> ref != null)
        .collect(Collectors.toList());

    // Log found actions
    for (String ref : actionRefs) {
        System.out.println("Found action: " + ref);
    }

    return super.visitDocuments(documents, ctx);
}
```

## Example 2: Checking Parent Context with higher()

Use `higher()` to search up the ancestor chain to check if you're within a specific context:

```java
// Trait for GitHub Actions permissions blocks
PermissionsScope.Matcher permissionsMatcher = new PermissionsScope.Matcher();

@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    // Check if we're inside a permissions block
    Optional<PermissionsScope> permissionsScope =
        permissionsMatcher.higher(getCursor()).findFirst();

    if (permissionsScope.isPresent() && "contents".equals(entry.getKey().getValue())) {
        // We found a "contents" key inside a permissions block
        if (entry.getValue() instanceof Yaml.Scalar) {
            Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
            if ("write".equals(scalar.getValue())) {
                return SearchResult.found(entry,
                    "Found write permission to contents");
            }
        }
    }

    return super.visitMappingEntry(entry, ctx);
}
```

## Example 3: Using asVisitor() in Recipes

The `asVisitor()` method is the primary way to use traits in recipes:

```java
@Override
public TreeVisitor<?, ExecutionContext> getVisitor() {
    ActionStep.Matcher matcher = new ActionStep.Matcher();

    // Convert matcher to visitor with VisitFunction2
    return matcher.asVisitor((step, ctx) -> {
        String ref = step.getActionRef();
        if (ref != null && ref.contains("@v2")) {
            return step.withActionRef(ref.replace("@v2", "@v3")).getTree();
        }
        return step.getTree();
    });
}
```

## When to Create a Trait

A trait is the best choice when:

1. **You want to provide shared functionality encapsulating several possible LST types**
   - Example: A `YamlValue` trait that works with both `Yaml.Scalar`, `Yaml.Sequence`, and `Yaml.Mapping`
   - The trait provides a unified interface regardless of the underlying concrete type
   - Allows recipes to work generically with different YAML structures

2. **You want to provide functionality specific to a subset of an individual LST type**
   - Example: An `ActionStep` trait for `Yaml.Mapping.Entry` elements that have a `uses` key
   - Not all mapping entries are action steps, only those matching specific criteria
   - The trait represents a semantic concept within a broader LST type

Additional scenarios where traits add value:
- **Semantic abstraction** over complex LST patterns (e.g., "a workflow trigger")
- **Reusable matching logic** across multiple recipes
- **Domain-specific accessors** that hide LST complexity
- **Composable filtering** with matcher chains

## When to Use Utility Interfaces Instead

Use utility interfaces for:
- **Simple helper methods** for visitors (e.g., safe scalar extraction)
- **Stateless operations** that don't need cursor context
- **Common patterns** that don't warrant full trait machinery
- **Mixins** to share functionality across visitor classes

## Domain-Specific Matcher Base Classes

For traits within a specific domain (e.g., YAML, Gradle, Maven), consider creating an intermediate matcher base class that provides shared utilities:

```java
public abstract class YamlTraitMatcher<U extends Trait<?>>
        extends SimpleTraitMatcher<U> {

    // Shared utility for all YAML trait matchers
    protected boolean withinMapping(Cursor cursor) {
        return cursor.firstEnclosing(Yaml.Mapping.class) != null;
    }

    // Common validation logic
    protected boolean isValidYamlContext(Cursor cursor) {
        SourceFile sourceFile = cursor.firstEnclosing(SourceFile.class);
        return sourceFile instanceof Yaml.Documents;
    }

    // Helper for finding parent entries
    protected @Nullable Yaml.Mapping.Entry getParentEntry(Cursor cursor) {
        return cursor.firstEnclosing(Yaml.Mapping.Entry.class);
    }
}
```

Then your specific trait matchers extend this base class:

```java
public static class Matcher extends YamlTraitMatcher<ActionStep> {
    @Override
    protected @Nullable ActionStep test(Cursor cursor) {
        // Can use withinMapping(), isValidYamlContext(), etc. here
        if (!isValidYamlContext(cursor)) {
            return null;
        }
        // ... rest of matching logic
        return null;
    }
}
```

## Trait Best Practices Summary

**Core Requirements:**
- Implement `Trait<T extends Tree>` interface with `getCursor()` method
- Nest a `Matcher` as a static inner class extending `SimpleTraitMatcher<T>`
- Override `test(Cursor)` in your matcher to implement matching logic

**Instantiation Pattern:**
```java
// ✅ Correct - Direct instantiation
YamlScalar.Matcher matcher = new YamlScalar.Matcher();

// ❌ Wrong - Using deprecated Traits utility
Traits.yamlScalar()  // Don't use - deprecated
```

**Common Patterns:**
- Use `higher()` to search ancestor chain
- Use `lower()` to search descendants
- Use `asVisitor()` in recipe `getVisitor()` methods
- Extend domain-specific matchers like `YamlTraitMatcher` for shared utilities
