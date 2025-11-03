# Java LST Structure Reference

Complete reference for OpenRewrite's Java Lossless Semantic Tree (LST) structure.

## Overview

The Java LST represents Java code as a tree structure that preserves all formatting, comments, and whitespace. This allows transformations that maintain the original file's appearance.

## Type Hierarchy

```
org.openrewrite.java.tree.J
├── J.CompilationUnit (root of Java file)
├── J.ClassDeclaration (class definitions)
├── J.MethodDeclaration (method definitions)
├── J.MethodInvocation (method calls)
├── J.VariableDeclarations (variable declarations)
├── J.Block (code blocks)
├── J.If (if statements)
├── J.ForLoop (for loops)
├── J.WhileLoop (while loops)
├── J.Try (try-catch blocks)
├── J.Import (import statements)
├── J.Annotation (annotations)
├── J.Binary (binary operations: +, -, *, /, &&, ||, etc.)
├── J.Literal (primitive literals)
├── J.Identifier (variable/type names)
├── J.NewClass (object instantiation)
├── J.Return (return statements)
├── J.Assignment (assignments)
└── ... (many more)
```

## Core Types

### J.CompilationUnit

The root element of a Java source file.

```java
public interface CompilationUnit extends JavaSourceFile, J {
    List<Import> getImports();
    List<ClassDeclaration> getClasses();
    Space getEof();
    // ... other methods
}
```

**Usage:**
```java
@Override
public J.CompilationUnit visitCompilationUnit(J.CompilationUnit cu, ExecutionContext ctx) {
    // Visit entire file
    cu = super.visitCompilationUnit(cu, ctx);

    // Access package declaration
    String packageName = cu.getPackageDeclaration() != null ?
        cu.getPackageDeclaration().getExpression().printTrimmed() : null;

    // Access imports
    List<J.Import> imports = cu.getImports();

    // Access classes
    List<J.ClassDeclaration> classes = cu.getClasses();

    return cu;
}
```

---

### J.ClassDeclaration

Represents class, interface, enum, or record declarations.

```java
public interface ClassDeclaration extends Statement, TypedTree {
    List<Annotation> getLeadingAnnotations();
    List<Modifier> getModifiers();
    Kind getKind(); // Class, Interface, Enum, Record, Annotation
    Identifier getName();
    @Nullable TypeParameters getTypeParameters();
    @Nullable TypeTree getExtends();
    @Nullable Container<TypeTree> getImplements();
    Block getBody();
    JavaType.FullyQualified getType();
}
```

**Usage:**
```java
@Override
public J.ClassDeclaration visitClassDeclaration(J.ClassDeclaration classDecl, ExecutionContext ctx) {
    classDecl = super.visitClassDeclaration(classDecl, ctx);

    // Get class name
    String className = classDecl.getSimpleName();

    // Get fully qualified name
    if (classDecl.getType() != null) {
        String fqn = classDecl.getType().getFullyQualifiedName();
    }

    // Check if interface
    if (classDecl.getKind() == J.ClassDeclaration.Kind.Type.Interface) {
        // ...
    }

    // Access methods
    List<Statement> statements = classDecl.getBody().getStatements();
    for (Statement statement : statements) {
        if (statement instanceof J.MethodDeclaration) {
            J.MethodDeclaration method = (J.MethodDeclaration) statement;
            // Process method
        }
    }

    return classDecl;
}
```

---

### J.MethodDeclaration

Represents method declarations.

```java
public interface MethodDeclaration extends Statement, TypedTree {
    List<Annotation> getLeadingAnnotations();
    List<Modifier> getModifiers();
    @Nullable TypeParameters getTypeParameters();
    @Nullable TypeTree getReturnTypeExpression();
    Identifier getName();
    List<Statement> getParameters();
    @Nullable Container<NameTree> getThrows();
    @Nullable Block getBody();
    JavaType.Method getMethodType();
}
```

**Usage:**
```java
@Override
public J.MethodDeclaration visitMethodDeclaration(J.MethodDeclaration method, ExecutionContext ctx) {
    method = super.visitMethodDeclaration(method, ctx);

    // Get method name
    String methodName = method.getSimpleName();

    // Get parameters
    List<Statement> params = method.getParameters();

    // Get return type
    TypeTree returnType = method.getReturnTypeExpression();

    // Get method body
    J.Block body = method.getBody();

    // Check if method matches signature
    if (method.getMethodType() != null &&
        TypeUtils.isOfType(method.getMethodType(), "com.example.Type", "methodName")) {
        // Method matches
    }

    return method;
}
```

---

### J.MethodInvocation

Represents method calls.

```java
public interface MethodInvocation extends Expression, TypedTree, MethodCall {
    @Nullable Expression getSelect(); // Object being called on
    Identifier getName();
    List<Expression> getArguments();
    JavaType.Method getMethodType();
}
```

**Usage:**
```java
@Override
public J.MethodInvocation visitMethodInvocation(J.MethodInvocation method, ExecutionContext ctx) {
    method = super.visitMethodInvocation(method, ctx);

    // Get method name
    String methodName = method.getSimpleName();

    // Get arguments
    List<Expression> args = method.getArguments();

    // Check if calling specific method
    if (method.getMethodType() != null &&
        TypeUtils.isOfType(method.getMethodType(), "java.lang.String", "equals")) {
        // This is a String.equals() call
    }

    // Get select (object being called on)
    Expression select = method.getSelect();

    return method;
}
```

---

### J.VariableDeclarations

Represents variable declarations.

```java
public interface VariableDeclarations extends Statement, TypedTree {
    List<Annotation> getLeadingAnnotations();
    List<Modifier> getModifiers();
    @Nullable TypeTree getTypeExpression();
    List<NamedVariable> getVariables();
}
```

**Usage:**
```java
@Override
public J.VariableDeclarations visitVariableDeclarations(J.VariableDeclarations multiVariable, ExecutionContext ctx) {
    multiVariable = super.visitVariableDeclarations(multiVariable, ctx);

    // Get type
    TypeTree type = multiVariable.getTypeExpression();

    // Get all variables declared
    for (J.VariableDeclarations.NamedVariable var : multiVariable.getVariables()) {
        String varName = var.getSimpleName();
        Expression initializer = var.getInitializer();
        // Process variable
    }

    return multiVariable;
}
```

---

### J.Import

Represents import statements.

```java
public interface Import extends Statement {
    boolean isStatic();
    FieldAccess getQualid();
}
```

**Usage:**
```java
@Override
public J.Import visitImport(J.Import _import, ExecutionContext ctx) {
    _import = super.visitImport(_import, ctx);

    // Get fully qualified name
    String fqn = _import.getQualid().printTrimmed();

    // Check if static import
    if (_import.isStatic()) {
        // Static import
    }

    return _import;
}
```

---

### J.Annotation

Represents annotations.

```java
public interface Annotation extends Expression {
    NameTree getAnnotationType();
    @Nullable Container<Expression> getArguments();
}
```

**Usage:**
```java
@Override
public J.Annotation visitAnnotation(J.Annotation annotation, ExecutionContext ctx) {
    annotation = super.visitAnnotation(annotation, ctx);

    // Get annotation type
    String annotationType = annotation.getAnnotationType().printTrimmed();

    // Check specific annotation
    if ("org.junit.Test".equals(annotationType)) {
        // This is a @Test annotation
    }

    // Get arguments
    if (annotation.getArguments() != null) {
        List<Expression> args = annotation.getArguments().getElements();
    }

    return annotation;
}
```

---

## Common Patterns

### Type Checking

```java
// Check if method invocation is of specific type
if (method.getMethodType() != null &&
    TypeUtils.isOfClassType(method.getMethodType().getDeclaringType(), "com.example.Class")) {
    // Method is declared in com.example.Class
}

// Check method signature
if (TypeUtils.isOfType(method.getMethodType(), "com.example.Type", "methodName")) {
    // Method matches
}
```

### Safe Value Access

```java
// Always check for null before accessing type information
if (classDecl.getType() != null) {
    String fqn = classDecl.getType().getFullyQualifiedName();
}

// Check for null on optional elements
if (method.getBody() != null) {
    List<Statement> statements = method.getBody().getStatements();
}
```

### Modifying LST Elements

```java
// Always use .withX() methods - never mutate
classDecl = classDecl.withName(classDecl.getName().withSimpleName("NewName"));

// Use ListUtils for list operations
classDecl = classDecl.withModifiers(
    ListUtils.concat(classDecl.getModifiers(), newModifier)
);

// Remove from list
method = method.withArguments(
    ListUtils.map(method.getArguments(), (i, arg) ->
        i == indexToRemove ? null : arg
    )
);
```

### Import Management

```java
// Add import if not present
maybeAddImport("java.util.List");

// Add static import
maybeAddImport("java.util.Collections", "emptyList");

// Remove import
maybeRemoveImport("old.package.Type");
```

### Visitor Chaining

```java
// Chain another visitor after this one
doAfterVisit(new SomeOtherRecipe().getVisitor());
```

## Visit Method Reference

Common visit methods to override:

| LST Element | Visit Method | Common Use |
|-------------|--------------|------------|
| `J.CompilationUnit` | `visitCompilationUnit()` | Entire file operations |
| `J.ClassDeclaration` | `visitClassDeclaration()` | Class modifications |
| `J.MethodDeclaration` | `visitMethodDeclaration()` | Method modifications |
| `J.MethodInvocation` | `visitMethodInvocation()` | Method call changes |
| `J.VariableDeclarations` | `visitVariableDeclarations()` | Variable operations |
| `J.Block` | `visitBlock()` | Code block operations |
| `J.If` | `visitIf()` | Conditional logic |
| `J.ForLoop` | `visitForLoop()` | Loop transformations |
| `J.Import` | `visitImport()` | Import management |
| `J.Annotation` | `visitAnnotation()` | Annotation operations |
| `J.Binary` | `visitBinary()` | Binary operations |
| `J.Literal` | `visitLiteral()` | Literal values |
| `J.Assignment` | `visitAssignment()` | Assignment operations |
| `J.Return` | `visitReturn()` | Return statements |
| `J.NewClass` | `visitNewClass()` | Object instantiation |

## Best Practices

1. **Always call super** - `super.visitX()` traverses the subtree
2. **Return modified copies** - Never mutate LST elements directly
3. **Use `.withX()` methods** - For all modifications
4. **Handle null cases** - Check for null before accessing type information
5. **Preserve formatting** - LST methods maintain formatting automatically
6. **Use ListUtils** - For all list operations (never mutate directly)
7. **Check types safely** - Use TypeUtils methods with null checks

## See Also

- `references/common-patterns.md` - Code patterns for common operations
- `references/troubleshooting-guide.md` - Solutions to common issues
- `templates/template-imperative-recipe.java` - Complete recipe template
