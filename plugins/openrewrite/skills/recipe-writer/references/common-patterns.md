# OpenRewrite Recipe Common Patterns

Quick reference for frequently used code patterns in recipe development.

## Import Management

### Adding Imports
```java
maybeAddImport("java.util.List");
maybeAddImport("java.util.Collections", "emptyList"); // Static import
```

### Removing Imports
```java
maybeRemoveImport("old.package.Type");
```

## Visitor Patterns

### Chaining Visitors
```java
doAfterVisit(new OtherRecipe().getVisitor());
```

### Cursor Messaging (Intra-visitor State)
```java
// Store state
getCursor().putMessage("key", value);

// Retrieve state
Object value = getCursor().getNearestMessage("key");
```

## Type Checking

### Check Class Type
```java
if (methodInvocation.getType() != null &&
    TypeUtils.isOfClassType(methodInvocation.getType(), "com.example.Type")) {
    // Type matches
}
```

### Check Method Type
```java
if (TypeUtils.isOfType(method.getMethodType(), "com.example.Type", "methodName")) {
    // Method matches
}
```

### Check Assignability
```java
if (TypeUtils.isAssignableTo("java.util.Collection", someType)) {
    // Type is assignable to Collection
}
```

## LST Manipulation

### Modifying Lists (Never Mutate!)
```java
// WRONG - Mutates the list
method.getArguments().remove(0);

// CORRECT - Creates new list with ListUtils
method.withArguments(ListUtils.map(method.getArguments(), (i, arg) ->
    i == 0 ? null : arg  // null removes the element
));
```

### Adding to Lists
```java
// Add at end
classDecl.withModifiers(
    ListUtils.concat(classDecl.getModifiers(), newModifier)
);

// Add at beginning
classDecl.withModifiers(
    ListUtils.concat(newModifier, classDecl.getModifiers())
);
```

### Replacing in Lists
```java
classDecl.withModifiers(
    ListUtils.map(classDecl.getModifiers(), mod ->
        shouldReplace(mod) ? newModifier : mod
    )
);
```

## JavaTemplate Patterns

### Simple Template
```java
JavaTemplate template = JavaTemplate
    .builder("new Expression()")
    .build();

// Apply
expression = template.apply(getCursor(), expression.getCoordinates().replace());
```

### Template with Imports
```java
JavaTemplate template = JavaTemplate
    .builder("Collections.emptyList()")
    .imports("java.util.Collections")
    .build();
```

### Template with Parameters
```java
JavaTemplate template = JavaTemplate
    .builder("new #{any(String)}(#{})")
    .build();

// Apply with parameters
expression = template.apply(
    getCursor(),
    expression.getCoordinates().replace(),
    typeName,        // #{any(String)}
    constructorArg   // #{}
);
```

### Template with External Classpath
```java
JavaTemplate template = JavaTemplate
    .builder("new CustomType()")
    .imports("com.external.CustomType")
    .javaParser(JavaParser.fromJavaVersion()
        .classpath("external-library"))
    .build();
```

### Context-Sensitive Template
```java
// Use ONLY when referencing local variables/methods
JavaTemplate template = JavaTemplate
    .builder("localVariable.toString()")
    .contextSensitive()
    .build();
```

## Preconditions

### Single Precondition
```java
@Override
public TreeVisitor<?, ExecutionContext> getVisitor() {
    return Preconditions.check(
        new UsesType<>("com.example.Type", true),
        new YourVisitor()
    );
}
```

### Multiple Preconditions (AND)
```java
return Preconditions.check(
    Preconditions.and(
        new UsesType<>("com.example.Type", true),
        new UsesMethod<>("com.example.Type methodName(..)")
    ),
    new YourVisitor()
);
```

### Multiple Preconditions (OR)
```java
return Preconditions.check(
    Preconditions.or(
        new UsesType<>("com.example.TypeA", true),
        new UsesType<>("com.example.TypeB", true)
    ),
    new YourVisitor()
);
```

### Java Version Check
```java
return Preconditions.check(
    new UsesJavaVersion<>(17),
    new YourVisitor()
);
```

## ScanningRecipe Patterns

### Basic Accumulator Structure
```java
public static class Accumulator {
    // Use per-project tracking for multi-module support
    Map<JavaProject, Set<String>> projectData = new HashMap<>();
}
```

### Scanner (First Pass - Collect Only)
```java
@Override
public TreeVisitor<?, ExecutionContext> getScanner(Accumulator acc) {
    return new JavaIsoVisitor<>() {
        @Override
        public J.CompilationUnit visitCompilationUnit(J.CompilationUnit cu, ExecutionContext ctx) {
            // Collect data - DO NOT MODIFY LST
            JavaProject project = cu.getMarkers()
                .findFirst(JavaProject.class)
                .orElse(null);

            if (project != null) {
                acc.projectData
                    .computeIfAbsent(project, k -> new HashSet<>())
                    .add(someData);
            }

            return cu; // Return unchanged
        }
    };
}
```

### Visitor (Second Pass - Modify Using Accumulator)
```java
@Override
public TreeVisitor<?, ExecutionContext> getVisitor(Accumulator acc) {
    return new JavaIsoVisitor<>() {
        @Override
        public J.CompilationUnit visitCompilationUnit(J.CompilationUnit cu, ExecutionContext ctx) {
            JavaProject project = cu.getMarkers()
                .findFirst(JavaProject.class)
                .orElse(null);

            if (project == null) {
                return cu;
            }

            // Use accumulator data to make decisions
            Set<String> projectData = acc.projectData.get(project);
            if (projectData != null && projectData.contains(someCondition)) {
                // Make changes
            }

            return cu;
        }
    };
}
```

## Formatting Preservation

### Use Space.format()
```java
// Preserve formatting when adding elements
Space.format("\n" + indent)
```

### Copy Formatting from Existing Elements
```java
newElement = newElement.withPrefix(existingElement.getPrefix());
```

## Testing Patterns

### Multi-file Tests
```java
rewriteRun(
    java(
        """
        package com.example;
        class First { }
        """,
        """
        package com.example;
        class First { /* modified */ }
        """
    ),
    java(
        """
        package com.example;
        class Second { }
        """
        // No second arg = no change expected
    )
);
```

### Tests with Parser Configuration
```java
@Override
public void defaults(RecipeSpec spec) {
    spec.recipe(new YourRecipe())
        .parser(JavaParser.fromJavaVersion()
            .classpath("external-library"));
}
```

### Tests with Different Java Versions
```java
rewriteRun(
    spec -> spec.parser(JavaParser.fromJavaVersion().version("11")),
    java(
        // Java 11 specific code
    )
);
```

## Error Handling

### Safe Type Access
```java
// Always check for null
if (element.getType() != null) {
    // Safe to use type
}
```

### Safe Method Type Access
```java
JavaType.Method methodType = method.getMethodType();
if (methodType != null && methodType.getDeclaringType() != null) {
    // Safe to use
}
```

## Performance Optimization

### Referential Equality Check
```java
J.ClassDeclaration cd = super.visitClassDeclaration(classDecl, ctx);

if (!shouldChange(cd)) {
    return cd; // Same object = no work downstream
}
```

### Early Return Pattern
```java
// Check cheapest conditions first
if (element.getName() == null) {
    return element;
}

if (element.getType() == null) {
    return element;
}

// Then check more expensive conditions
if (!TypeUtils.isOfClassType(element.getType(), targetType)) {
    return element;
}

// Finally, make changes
return makeChanges(element);
```
