package com.yourorg;

import com.google.errorprone.refaster.annotation.AfterTemplate;
import com.google.errorprone.refaster.annotation.BeforeTemplate;
import org.openrewrite.java.template.RecipeDescriptor;

/**
 * Refaster template for simple expression/statement replacements.
 *
 * Refaster templates provide a middle ground between declarative YAML and imperative Java recipes:
 * - Faster than imperative recipes
 * - Type-aware matching
 * - Concise syntax
 * - Good for API migrations
 *
 * Usage:
 * 1. Define @BeforeTemplate with the code pattern to match
 * 2. Define @AfterTemplate with the replacement code
 * 3. OpenRewrite generates a recipe that performs the transformation
 *
 * Example usage in YAML:
 * ```yaml
 * type: specs.openrewrite.org/v1beta/recipe
 * name: com.yourorg.MyRefasterRecipe
 * recipeList:
 *   - com.yourorg.TemplateRefaster
 * ```
 */
@RecipeDescriptor(
    name = "Your Refaster recipe name",
    description = "Clear description of what this Refaster template accomplishes."
)
public class TemplateRefaster {

    /**
     * Example 1: Simple method call replacement
     * Replaces StringUtils.equals() with Objects.equals()
     */
    public static class ReplaceStringUtilsEquals {
        @BeforeTemplate
        boolean before(String s1, String s2) {
            return org.apache.commons.lang3.StringUtils.equals(s1, s2);
        }

        @AfterTemplate
        boolean after(String s1, String s2) {
            return java.util.Objects.equals(s1, s2);
        }
    }

    /**
     * Example 2: Expression replacement with type awareness
     * Replaces new ArrayList<>() with List.of() for immutable lists (Java 9+)
     */
    public static class ReplaceArrayListWithListOf {
        @BeforeTemplate
        <T> java.util.List<T> before() {
            return new java.util.ArrayList<>();
        }

        @AfterTemplate
        <T> java.util.List<T> after() {
            return java.util.List.of();
        }
    }

    /**
     * Example 3: Statement replacement
     * Replaces traditional for loop with enhanced for loop
     */
    public static class ReplaceTraditionalForWithEnhanced {
        @BeforeTemplate
        void before(java.util.List<String> items) {
            for (int i = 0; i < items.size(); i++) {
                String item = items.get(i);
                System.out.println(item);
            }
        }

        @AfterTemplate
        void after(java.util.List<String> items) {
            for (String item : items) {
                System.out.println(item);
            }
        }
    }

    /**
     * Example 4: API migration with different parameters
     * Migrates from old API to new API with parameter reordering
     */
    public static class MigrateOldApiToNew {
        @BeforeTemplate
        void before(String value, int timeout) {
            com.oldapi.Client.connect(value, timeout);
        }

        @AfterTemplate
        void after(String value, int timeout) {
            com.newapi.Client.connect(timeout, value);
        }
    }

    /**
     * TODO: Add your Refaster templates here
     *
     * Tips:
     * - Keep templates simple - complex logic should use imperative recipes
     * - Use type parameters for generic matching (<T>, <S>, etc.)
     * - Method names (before/after) can be anything - only annotations matter
     * - Return types and parameters must match between before and after for type safety
     * - You can have multiple nested template classes in one file
     */

    public static class YourRefasterTemplate {
        /**
         * Define what code pattern to match
         */
        @BeforeTemplate
        void before() {
            // TODO: Add the code pattern you want to match and replace
            // Example: someOldMethod()
        }

        /**
         * Define what to replace it with
         */
        @AfterTemplate
        void after() {
            // TODO: Add the replacement code
            // Example: someNewMethod()
        }
    }
}
