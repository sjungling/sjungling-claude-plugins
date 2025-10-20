// OpenRewrite Recipe Template - Complete Examples

// ============================================================================
// DECLARATIVE YAML RECIPE
// ============================================================================
// File: src/main/resources/META-INF/rewrite/your-recipe.yml

---
type: specs.openrewrite.org/v1beta/recipe
name: com.example.YourComposedRecipe
displayName: Your composed recipe display name
description: |
  Detailed description of what this recipe does (supports **markdown**).

  **Before:**
  ```yaml
  old: value
  ```

  **After:**
  ```yaml
  new: value
  ```
recipeList:
  - org.openrewrite.yaml.search.FindKey:
      keyPath: $.some.path
  - org.openrewrite.yaml.ChangeValue:
      keyPath: $.some.path
      value: newValue

// ============================================================================
// IMPERATIVE JAVA RECIPE - WITHOUT PARAMETERS
// ============================================================================

package com.example.rewrite;

import org.openrewrite.*;
import org.openrewrite.yaml.YamlIsoVisitor;
import org.openrewrite.yaml.tree.Yaml;

public class SimpleYamlRecipe extends Recipe {

    @Override
    public String getDisplayName() {
        return "Simple YAML transformation";
    }

    @Override
    public String getDescription() {
        return "Transforms YAML structures (supports **markdown**).\n\n" +
               "**Example:**\n```yaml\nkey: value\n```";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new YamlIsoVisitor<ExecutionContext>() {
            @Override
            public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
                // Match specific key
                if ("targetKey".equals(entry.getKey().getValue())) {
                    // Check value type and transform
                    if (entry.getValue() instanceof Yaml.Scalar) {
                        Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
                        if ("oldValue".equals(scalar.getValue())) {
                            // Return modified entry
                            return entry.withValue(scalar.withValue("newValue"));
                        }
                    }
                }
                // Always call super to continue traversal
                return super.visitMappingEntry(entry, ctx);
            }
        };
    }
}

// ============================================================================
// IMPERATIVE JAVA RECIPE - WITH PARAMETERS
// ============================================================================

package com.example.rewrite;

import lombok.EqualsAndHashCode;
import lombok.Value;
import org.openrewrite.*;
import org.openrewrite.yaml.YamlIsoVisitor;
import org.openrewrite.yaml.tree.Yaml;

@Value
@EqualsAndHashCode(callSuper = false)
public class ParameterizedYamlRecipe extends Recipe {

    @Option(
        displayName = "Key path",
        description = "JsonPath expression to locate the key (e.g., `$.jobs.*.steps[*].uses`)",
        example = "$.jobs.*.steps[*].uses"
    )
    String keyPath;

    @Option(
        displayName = "Old value",
        description = "The value to search for and replace",
        example = "actions/checkout@v2"
    )
    String oldValue;

    @Option(
        displayName = "New value",
        description = "The replacement value",
        example = "actions/checkout@v3"
    )
    String newValue;

    @Override
    public String getDisplayName() {
        return "Replace YAML value at path";
    }

    @Override
    public String getDescription() {
        return "Replaces a specific value at a JsonPath location.\n\n" +
               "**Example:** Replace `" + oldValue + "` with `" + newValue + "`";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new YamlIsoVisitor<ExecutionContext>() {
            private final JsonPathMatcher matcher = new JsonPathMatcher(keyPath);

            @Override
            public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
                if (matcher.matches(getCursor())) {
                    if (entry.getValue() instanceof Yaml.Scalar) {
                        Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
                        if (oldValue.equals(scalar.getValue())) {
                            return entry.withValue(scalar.withValue(newValue));
                        }
                    }
                }
                return super.visitMappingEntry(entry, ctx);
            }
        };
    }
}

// ============================================================================
// SEARCH RECIPE - MARKING RESULTS WITHOUT MODIFICATION
// ============================================================================

package com.example.rewrite;

import org.openrewrite.*;
import org.openrewrite.marker.SearchResult;
import org.openrewrite.yaml.YamlIsoVisitor;
import org.openrewrite.yaml.tree.Yaml;

public class YamlSearchRecipe extends Recipe {

    @Override
    public String getDisplayName() {
        return "Find deprecated YAML patterns";
    }

    @Override
    public String getDescription() {
        return "Searches for deprecated patterns in YAML files without modifying them";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new YamlIsoVisitor<ExecutionContext>() {
            private final JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");

            @Override
            public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
                if (matcher.matches(getCursor()) && "uses".equals(entry.getKey().getValue())) {
                    if (entry.getValue() instanceof Yaml.Scalar) {
                        Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
                        if (scalar.getValue().contains("@v2")) {
                            return SearchResult.found(entry, "Found deprecated v2 action");
                        }
                    }
                }
                return super.visitMappingEntry(entry, ctx);
            }
        };
    }
}

// ============================================================================
// TEST TEMPLATE
// ============================================================================

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
    void transformsBasicCase() {
        rewriteRun(
            yaml(
                """
                # before YAML
                key: old-value
                nested:
                  inner: value
                """,
                """
                # after YAML
                key: new-value
                nested:
                  inner: value
                """
            )
        );
    }

    @Test
    void noChangeWhenNotMatching() {
        rewriteRun(
            yaml(
                """
                unrelated: value
                """
            )
        );
    }

    @Test
    void handlesEdgeCases() {
        rewriteRun(
            yaml(
                """
                # Empty value
                key:
                # Null value
                key2: null
                # Array
                array:
                  - item1
                  - item2
                """,
                """
                # Expected transformation
                key: default
                key2: null
                array:
                  - item1
                  - item2
                """
            )
        );
    }
}
