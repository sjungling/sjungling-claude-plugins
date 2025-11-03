package com.example.rewrite;

import lombok.EqualsAndHashCode;
import lombok.Value;
import org.openrewrite.*;
import org.openrewrite.yaml.JsonPathMatcher;
import org.openrewrite.yaml.YamlIsoVisitor;
import org.openrewrite.yaml.tree.Yaml;

/**
 * Example recipe demonstrating YAML manipulation for GitHub Actions workflows.
 *
 * This recipe updates GitHub Actions checkout action from v2/v3 to v4.
 *
 * Before:
 * ```yaml
 * jobs:
 *   build:
 *     steps:
 *       - uses: actions/checkout@v2
 * ```
 *
 * After:
 * ```yaml
 * jobs:
 *   build:
 *     steps:
 *       - uses: actions/checkout@v4
 * ```
 *
 * Key Concepts Demonstrated:
 * 1. YamlIsoVisitor for YAML LST manipulation
 * 2. JsonPathMatcher for targeted YAML element matching
 * 3. Safe value access with type checking
 * 4. Preserving formatting and comments
 */
@Value
@EqualsAndHashCode(callSuper = false)
public class UpdateGitHubActionsCheckout extends Recipe {

    @Override
    public String getDisplayName() {
        return "Update GitHub Actions to `actions/checkout@v4`.";
    }

    @Override
    public String getDescription() {
        return "Updates all uses of `actions/checkout@v2` and `actions/checkout@v3` to `actions/checkout@v4`.\n\n" +
               "**Before:**\n```yaml\n- uses: actions/checkout@v2\n```\n\n" +
               "**After:**\n```yaml\n- uses: actions/checkout@v4\n```";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new YamlIsoVisitor<ExecutionContext>() {

            // JsonPath to match the 'uses' field in GitHub Actions steps
            private final JsonPathMatcher matcher =
                new JsonPathMatcher("$.jobs.*.steps[*].uses");

            @Override
            public Yaml.Scalar visitScalar(Yaml.Scalar scalar, ExecutionContext ctx) {
                // Always call super to traverse the tree
                scalar = super.visitScalar(scalar, ctx);

                // Check if this scalar matches our JsonPath
                if (matcher.matches(getCursor())) {
                    String value = scalar.getValue();

                    // Safe null check
                    if (value != null) {
                        // Update v2 to v4
                        if (value.startsWith("actions/checkout@v2")) {
                            return scalar.withValue(value.replace("@v2", "@v4"));
                        }
                        // Update v3 to v4
                        if (value.startsWith("actions/checkout@v3")) {
                            return scalar.withValue(value.replace("@v3", "@v4"));
                        }
                    }
                }

                return scalar;
            }
        };
    }
}

/**
 * Additional YAML recipe examples demonstrating other common patterns:
 */

/**
 * Example: Update Kubernetes container image tags
 *
 * Before:
 * ```yaml
 * spec:
 *   containers:
 *     - image: myapp:1.0.0
 * ```
 *
 * After:
 * ```yaml
 * spec:
 *   containers:
 *     - image: myapp:2.0.0
 * ```
 */
@Value
@EqualsAndHashCode(callSuper = false)
class UpdateKubernetesImageTag extends Recipe {

    String oldTag;
    String newTag;

    @Override
    public String getDisplayName() {
        return "Update Kubernetes image tag.";
    }

    @Override
    public String getDescription() {
        return "Updates Kubernetes container image tags.";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new YamlIsoVisitor<ExecutionContext>() {

            private final JsonPathMatcher matcher =
                new JsonPathMatcher("$.spec.template.spec.containers[*].image");

            @Override
            public Yaml.Scalar visitScalar(Yaml.Scalar scalar, ExecutionContext ctx) {
                scalar = super.visitScalar(scalar, ctx);

                if (matcher.matches(getCursor())) {
                    String value = scalar.getValue();
                    if (value != null && value.endsWith(":" + oldTag)) {
                        return scalar.withValue(
                            value.substring(0, value.lastIndexOf(":")) + ":" + newTag
                        );
                    }
                }

                return scalar;
            }
        };
    }
}

/**
 * Example: Change key name in YAML
 *
 * Before:
 * ```yaml
 * oldKey: value
 * ```
 *
 * After:
 * ```yaml
 * newKey: value
 * ```
 */
@Value
@EqualsAndHashCode(callSuper = false)
class ChangeYamlKey extends Recipe {

    String oldKey;
    String newKey;

    @Override
    public String getDisplayName() {
        return "Change YAML key name.";
    }

    @Override
    public String getDescription() {
        return "Renames a YAML key while preserving its value.";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new YamlIsoVisitor<ExecutionContext>() {

            @Override
            public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
                entry = super.visitMappingEntry(entry, ctx);

                // Check if this entry has the old key
                if (oldKey.equals(entry.getKey().getValue())) {
                    // Replace the key while preserving everything else
                    return entry.withKey(
                        ((Yaml.Scalar) entry.getKey()).withValue(newKey)
                    );
                }

                return entry;
            }
        };
    }
}

/**
 * Example: Update value based on key match
 *
 * Before:
 * ```yaml
 * database:
 *   host: localhost
 * ```
 *
 * After:
 * ```yaml
 * database:
 *   host: prod-db.example.com
 * ```
 */
@Value
@EqualsAndHashCode(callSuper = false)
class UpdateYamlValue extends Recipe {

    String keyPath;
    String oldValue;
    String newValue;

    @Override
    public String getDisplayName() {
        return "Update YAML value.";
    }

    @Override
    public String getDescription() {
        return "Updates a YAML value at a specific key path.";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new YamlIsoVisitor<ExecutionContext>() {

            private final JsonPathMatcher matcher = new JsonPathMatcher(keyPath);

            @Override
            public Yaml.Scalar visitScalar(Yaml.Scalar scalar, ExecutionContext ctx) {
                scalar = super.visitScalar(scalar, ctx);

                if (matcher.matches(getCursor())) {
                    String value = scalar.getValue();
                    if (oldValue.equals(value)) {
                        return scalar.withValue(newValue);
                    }
                }

                return scalar;
            }
        };
    }
}

/**
 * Common JsonPath Patterns for YAML Recipes:
 *
 * GitHub Actions:
 * - $.jobs.*.steps[*].uses           - All 'uses' in steps
 * - $.on.push.branches               - Push trigger branches
 * - $.jobs.*.runs-on                 - Runner configuration
 * - $.jobs.*.strategy.matrix         - Matrix strategy
 *
 * Kubernetes:
 * - $.spec.template.spec.containers[*].image     - Container images
 * - $.metadata.labels                            - Labels
 * - $.spec.replicas                              - Replica count
 * - $.spec.template.spec.containers[*].env[*]    - Environment variables
 *
 * Generic YAML:
 * - $.databases.*.connection.host     - Nested configuration
 * - $[?(@.enabled == true)]           - Conditional matching
 * - $..*[?(@.type == 'service')]      - Deep search with condition
 *
 * See references/jsonpath-patterns.md for comprehensive examples.
 */
