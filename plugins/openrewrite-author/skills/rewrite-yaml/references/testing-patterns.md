# OpenRewrite YAML Testing Patterns

Complete guide to testing OpenRewrite YAML recipes using the RewriteTest framework.

## Overview

OpenRewrite provides a comprehensive testing framework that uses before/after YAML examples to verify recipe behavior. Tests are written using JUnit 5 and the `RewriteTest` interface.

## Basic Test Structure

```java
package com.example.rewrite;

import org.junit.jupiter.api.Test;
import org.openrewrite.test.RecipeSpec;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.yaml.Assertions.yaml;

class YourRecipeTest implements RewriteTest {

    @Override
    public void defaults(RecipeSpec spec) {
        spec.recipe(new YourRecipe());
    }

    @Test
    void basicTransformation() {
        rewriteRun(
            yaml(
                """
                # Before YAML
                key: old-value
                """,
                """
                # After YAML
                key: new-value
                """
            )
        );
    }
}
```

## Test Patterns

### 1. Happy Path Test

The simplest successful transformation:

```java
@Test
void replacesTargetValue() {
    rewriteRun(
        yaml(
            """
            name: my-workflow
            on:
              push:
                branches:
                  - master
            """,
            """
            name: my-workflow
            on:
              push:
                branches:
                  - main
            """
        )
    );
}
```

### 2. No-Change Test

Verify recipe doesn't modify unrelated YAML:

```java
@Test
void doesNotChangeUnrelatedYaml() {
    rewriteRun(
        yaml(
            """
            name: my-workflow
            on:
              pull_request:
                branches:
                  - develop
            """
            // No second argument = no changes expected
        )
    );
}
```

### 3. Null Safety Test

Test handling of null or missing values:

```java
@Test
void handlesNullValues() {
    rewriteRun(
        yaml(
            """
            key:
            another: null
            third:
              nested:
            """,
            """
            key: default-value
            another: null
            third:
              nested: default-value
            """
        )
    );
}
```

### 4. Empty File Test

Ensure recipe handles empty files gracefully:

```java
@Test
void handlesEmptyFile() {
    rewriteRun(
        yaml(
            """
            """
            // Empty file should remain empty
        )
    );
}
```

### 5. Complex Nested Structure Test

Test deep nesting and multiple transformations:

```java
@Test
void transformsNestedStructures() {
    rewriteRun(
        yaml(
            """
            jobs:
              build:
                runs-on: ubuntu-18.04
                steps:
                  - uses: actions/checkout@v2
                  - name: Setup
                    uses: actions/setup-node@v2
                    with:
                      node-version: 14
              test:
                runs-on: ubuntu-18.04
                steps:
                  - uses: actions/checkout@v2
            """,
            """
            jobs:
              build:
                runs-on: ubuntu-22.04
                steps:
                  - uses: actions/checkout@v3
                  - name: Setup
                    uses: actions/setup-node@v3
                    with:
                      node-version: 18
              test:
                runs-on: ubuntu-22.04
                steps:
                  - uses: actions/checkout@v3
            """
        )
    );
}
```

### 6. Array/Sequence Tests

```java
@Test
void transformsArrayItems() {
    rewriteRun(
        yaml(
            """
            branches:
              - master
              - develop
              - feature/*
            """,
            """
            branches:
              - main
              - develop
              - feature/*
            """
        )
    );
}

@Test
void addsItemToArray() {
    rewriteRun(
        yaml(
            """
            branches:
              - develop
            """,
            """
            branches:
              - develop
              - main
            """
        )
    );
}

@Test
void removesItemFromArray() {
    rewriteRun(
        yaml(
            """
            branches:
              - master
              - develop
              - main
            """,
            """
            branches:
              - develop
              - main
            """
        )
    );
}
```

### 7. Add Missing Key Tests

```java
@Test
void addsMissingKey() {
    rewriteRun(
        yaml(
            """
            jobs:
              build:
                runs-on: ubuntu-latest
                steps:
                  - run: echo "Hello"
            """,
            """
            jobs:
              build:
                runs-on: ubuntu-latest
                timeout-minutes: 30
                steps:
                  - run: echo "Hello"
            """
        )
    );
}

@Test
void doesNotAddKeyWhenAlreadyPresent() {
    rewriteRun(
        yaml(
            """
            jobs:
              build:
                runs-on: ubuntu-latest
                timeout-minutes: 60
                steps:
                  - run: echo "Hello"
            """
        )
    );
}
```

### 8. Delete Key Tests

```java
@Test
void deletesDeprecatedKey() {
    rewriteRun(
        yaml(
            """
            jobs:
              build:
                runs-on: ubuntu-latest
                deprecated-field: value
                steps:
                  - run: echo "Hello"
            """,
            """
            jobs:
              build:
                runs-on: ubuntu-latest
                steps:
                  - run: echo "Hello"
            """
        )
    );
}
```

### 9. Conditional Transformation Tests

```java
@Test
void transformsOnlyWhenConditionMet() {
    rewriteRun(
        yaml(
            """
            jobs:
              build:
                runs-on: ubuntu-latest
                container:
                  image: node:14
                steps:
                  - run: echo "Hello"
              test:
                runs-on: ubuntu-latest
                steps:
                  - run: echo "Test"
            """,
            """
            jobs:
              build:
                runs-on: ubuntu-latest
                container:
                  image: node:14
                steps:
                  - run: echo "Hello"
              test:
                runs-on: ubuntu-22.04
                steps:
                  - run: echo "Test"
            """
        )
    );
}
```

### 10. Pattern Matching Tests

```java
@Test
void matchesGlobPatterns() {
    rewriteRun(
        yaml(
            """
            steps:
              - uses: actions/checkout@v2
              - uses: actions/setup-node@v2
              - uses: actions/cache@v2
              - uses: custom/action@v1
            """,
            """
            steps:
              - uses: actions/checkout@v3
              - uses: actions/setup-node@v3
              - uses: actions/cache@v3
              - uses: custom/action@v1
            """
        )
    );
}
```

---

## Multi-Document YAML Testing

YAML files can contain multiple documents separated by `---`:

```java
@Test
void transformsMultipleDocuments() {
    rewriteRun(
        yaml(
            """
            ---
            apiVersion: v1
            kind: ConfigMap
            metadata:
              name: config1
            data:
              key: value1
            ---
            apiVersion: v1
            kind: ConfigMap
            metadata:
              name: config2
            data:
              key: value2
            """,
            """
            ---
            apiVersion: v1
            kind: ConfigMap
            metadata:
              name: config1
            data:
              key: updated-value1
            ---
            apiVersion: v1
            kind: ConfigMap
            metadata:
              name: config2
            data:
              key: updated-value2
            """
        )
    );
}

@Test
void transformsOnlySpecificDocument() {
    rewriteRun(
        yaml(
            """
            ---
            version: 1
            config:
              setting: old
            ---
            version: 2
            config:
              setting: old
            """,
            """
            ---
            version: 1
            config:
              setting: new
            ---
            version: 2
            config:
              setting: old
            """
        )
    );
}
```

---

## Edge Cases to Test

### Comments and Formatting

```java
@Test
void preservesComments() {
    rewriteRun(
        yaml(
            """
            # This is a comment
            key: old-value  # Inline comment
            # Another comment
            nested:
              inner: value
            """,
            """
            # This is a comment
            key: new-value  # Inline comment
            # Another comment
            nested:
              inner: value
            """
        )
    );
}

@Test
void preservesFormatting() {
    rewriteRun(
        yaml(
            """
            key:    old-value


            nested:
              inner:     value
            """,
            """
            key:    new-value


            nested:
              inner:     value
            """
        )
    );
}
```

### Different YAML Styles

```java
@Test
void handlesInlineArrays() {
    rewriteRun(
        yaml(
            """
            branches: [master, develop]
            """,
            """
            branches: [main, develop]
            """
        )
    );
}

@Test
void handlesQuotedStrings() {
    rewriteRun(
        yaml(
            """
            single: 'old value'
            double: "old value"
            plain: old value
            """,
            """
            single: 'new value'
            double: "new value"
            plain: new value
            """
        )
    );
}

@Test
void handlesMultilineStrings() {
    rewriteRun(
        yaml(
            """
            literal: |
              Line 1
              Line 2
            folded: >
              This is a
              folded string
            """,
            """
            literal: |
              Line 1 updated
              Line 2
            folded: >
              This is a
              folded string
            """
        )
    );
}
```

### Special Values

```java
@Test
void handlesSpecialYamlValues() {
    rewriteRun(
        yaml(
            """
            null_value: null
            tilde_null: ~
            empty:
            boolean_true: true
            boolean_yes: yes
            boolean_on: on
            number_int: 42
            number_float: 3.14
            number_exp: 1.2e3
            """,
            """
            null_value: null
            tilde_null: ~
            empty:
            boolean_true: true
            boolean_yes: yes
            boolean_on: on
            number_int: 43
            number_float: 3.14
            number_exp: 1.2e3
            """
        )
    );
}
```

### Anchors and Aliases

```java
@Test
void handlesYamlAnchors() {
    rewriteRun(
        yaml(
            """
            defaults: &defaults
              timeout: 30
              retry: 3

            job1:
              <<: *defaults
              name: Job 1

            job2:
              <<: *defaults
              name: Job 2
            """,
            """
            defaults: &defaults
              timeout: 60
              retry: 3

            job1:
              <<: *defaults
              name: Job 1

            job2:
              <<: *defaults
              name: Job 2
            """
        )
    );
}
```

---

## Parameterized Recipe Tests

Test recipes with different parameter values:

```java
@Value
@EqualsAndHashCode(callSuper = false)
class ParameterizedRecipe extends Recipe {
    @Option(displayName = "Old value", description = "Value to replace")
    String oldValue;

    @Option(displayName = "New value", description = "Replacement value")
    String newValue;

    @Override
    public String getDisplayName() {
        return "Replace value";
    }

    @Override
    public String getDescription() {
        return "Replaces old value with new value";
    }

    // Implementation...
}

class ParameterizedRecipeTest implements RewriteTest {

    @Test
    void replacesWithParameter1() {
        rewriteRun(
            spec -> spec.recipe(new ParameterizedRecipe("old1", "new1")),
            yaml(
                """
                key: old1
                """,
                """
                key: new1
                """
            )
        );
    }

    @Test
    void replacesWithParameter2() {
        rewriteRun(
            spec -> spec.recipe(new ParameterizedRecipe("old2", "new2")),
            yaml(
                """
                key: old2
                """,
                """
                key: new2
                """
            )
        );
    }
}
```

---

## Testing Multiple Files

```java
@Test
void transformsMultipleFiles() {
    rewriteRun(
        yaml(
            """
            # File 1
            key: old
            """,
            """
            # File 1
            key: new
            """,
            spec -> spec.path("file1.yml")
        ),
        yaml(
            """
            # File 2
            key: old
            """,
            """
            # File 2
            key: new
            """,
            spec -> spec.path("file2.yml")
        )
    );
}

@Test
void transformsOnlyMatchingFiles() {
    rewriteRun(
        yaml(
            """
            # Should transform
            key: old
            """,
            """
            # Should transform
            key: new
            """,
            spec -> spec.path(".github/workflows/ci.yml")
        ),
        yaml(
            """
            # Should not transform
            key: old
            """,
            spec -> spec.path("config/settings.yml")
        )
    );
}
```

---

## Testing Search Recipes

For recipes that mark results without modifying:

```java
@Test
void findsDeprecatedPatterns() {
    rewriteRun(
        spec -> spec.recipe(new FindDeprecatedActions()),
        yaml(
            """
            jobs:
              build:
                steps:
                  - uses: actions/checkout@v2
                  - uses: actions/setup-node@v3
            """,
            """
            jobs:
              build:
                steps:
                  - uses: actions/checkout@v2
                    ~~>
                  - uses: actions/setup-node@v3
            """
        )
    );
}
```

The `~~>` marker indicates a search result.

---

## Test Organization Best Practices

### Naming Conventions

```java
@Test
void happyPath() { /* Basic successful case */ }

@Test
void handlesEdgeCase() { /* Specific edge case */ }

@Test
void doesNotChangeWhenConditionNotMet() { /* No-op test */ }

@Test
void throwsExceptionForInvalidInput() { /* Error case */ }
```

### Test Structure

```java
class RecipeTest implements RewriteTest {

    @Nested
    class HappyPath {
        @Test void basicCase() { }
        @Test void complexCase() { }
    }

    @Nested
    class EdgeCases {
        @Test void nullValues() { }
        @Test void emptyFile() { }
        @Test void missingKeys() { }
    }

    @Nested
    class NoChanges {
        @Test void unrelatedYaml() { }
        @Test void alreadyCorrect() { }
    }
}
```

---

## Debugging Failed Tests

### Use Detailed Assertions

```java
@Test
void transformsValue() {
    rewriteRun(
        yaml(
            """
            key: old
            """,
            """
            key: new
            """
        )
    );
}
```

If test fails, OpenRewrite shows:
- Expected YAML
- Actual YAML
- Diff highlighting differences

### Add Debug Output

```java
@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    System.out.println("Visiting key: " + entry.getKey().getValue());
    // Your logic...
    return super.visitMappingEntry(entry, ctx);
}
```

### Test Incrementally

Start with simplest test, then add complexity:

```java
@Test void step1_basicReplacement() { }
@Test void step2_withNesting() { }
@Test void step3_withArrays() { }
@Test void step4_withConditions() { }
```

---

## Complete Test Suite Example

```java
package com.example.rewrite;

import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.openrewrite.test.RecipeSpec;
import org.openrewrite.test.RewriteTest;

import static org.openrewrite.yaml.Assertions.yaml;

class UpdateGitHubActionsTest implements RewriteTest {

    @Override
    public void defaults(RecipeSpec spec) {
        spec.recipe(new UpdateGitHubActions());
    }

    @Nested
    class HappyPath {
        @Test
        void updatesCheckoutAction() {
            rewriteRun(
                yaml(
                    """
                    jobs:
                      build:
                        steps:
                          - uses: actions/checkout@v2
                    """,
                    """
                    jobs:
                      build:
                        steps:
                          - uses: actions/checkout@v3
                    """
                )
            );
        }

        @Test
        void updatesMultipleActions() {
            rewriteRun(
                yaml(
                    """
                    jobs:
                      build:
                        steps:
                          - uses: actions/checkout@v2
                          - uses: actions/setup-node@v2
                    """,
                    """
                    jobs:
                      build:
                        steps:
                          - uses: actions/checkout@v3
                          - uses: actions/setup-node@v3
                    """
                )
            );
        }
    }

    @Nested
    class EdgeCases {
        @Test
        void handlesEmptyWorkflow() {
            rewriteRun(yaml(""));
        }

        @Test
        void handlesWorkflowWithoutSteps() {
            rewriteRun(
                yaml(
                    """
                    jobs:
                      build:
                        runs-on: ubuntu-latest
                    """
                )
            );
        }

        @Test
        void preservesComments() {
            rewriteRun(
                yaml(
                    """
                    jobs:
                      build:
                        steps:
                          # Checkout code
                          - uses: actions/checkout@v2
                    """,
                    """
                    jobs:
                      build:
                        steps:
                          # Checkout code
                          - uses: actions/checkout@v3
                    """
                )
            );
        }
    }

    @Nested
    class NoChanges {
        @Test
        void doesNotChangeOtherActions() {
            rewriteRun(
                yaml(
                    """
                    jobs:
                      build:
                        steps:
                          - uses: custom/action@v1
                    """
                )
            );
        }

        @Test
        void doesNotChangeAlreadyUpdated() {
            rewriteRun(
                yaml(
                    """
                    jobs:
                      build:
                        steps:
                          - uses: actions/checkout@v3
                    """
                )
            );
        }
    }
}
```

---

## Testing Checklist

- [ ] Happy path test (basic successful transformation)
- [ ] No-op test (recipe doesn't change unrelated YAML)
- [ ] Null value test
- [ ] Empty file test
- [ ] Complex nested structure test
- [ ] Array manipulation tests (add/remove/modify items)
- [ ] Missing key tests
- [ ] Comment preservation test
- [ ] Formatting preservation test
- [ ] Multi-document YAML test (if applicable)
- [ ] Different YAML styles (inline arrays, quoted strings, multiline)
- [ ] Special values (null, booleans, numbers)
- [ ] Parameterized recipe variations
- [ ] Multiple file tests
- [ ] Search recipe marking (if applicable)

---

## Additional Resources

- OpenRewrite Testing Documentation: https://docs.openrewrite.org/authoring-recipes/recipe-testing
- RewriteTest API: https://docs.openrewrite.org/reference/rewrite-test
- JUnit 5 Documentation: https://junit.org/junit5/docs/current/user-guide/
