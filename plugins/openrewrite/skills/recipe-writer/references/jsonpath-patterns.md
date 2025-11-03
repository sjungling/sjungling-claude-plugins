# JsonPath Patterns for YAML Recipes

Comprehensive collection of JsonPath patterns for common YAML structures including GitHub Actions, Kubernetes, CI/CD configs, and generic YAML.

## Overview

JsonPath provides a query language for navigating YAML/JSON structures. In OpenRewrite, use `JsonPathMatcher` to match specific locations in YAML files.

```java
JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");
if (matcher.matches(getCursor())) {
    // This element matches the path
}
```

## JsonPath Syntax Quick Reference

| Syntax | Meaning | Example |
|--------|---------|---------|
| `$` | Root element | `$` |
| `.` | Child element | `$.jobs` |
| `..` | Recursive descent | `$..uses` |
| `*` | Wildcard (any element) | `$.jobs.*` |
| `[*]` | Array wildcard | `$.steps[*]` |
| `[n]` | Array index | `$.steps[0]` |
| `[start:end]` | Array slice | `$.steps[0:3]` |
| `[?(@.key)]` | Filter expression | `$[?(@.name)]` |

---

## GitHub Actions Patterns

### Workflow-Level Patterns

```java
// Root workflow properties
"$.name"                      // Workflow name
"$.on"                        // Trigger configuration
"$.env"                       // Workflow-level environment variables
"$.permissions"               // Workflow-level permissions
"$.concurrency"               // Concurrency configuration
"$.defaults"                  // Default settings

// Specific triggers
"$.on.push"                   // Push trigger
"$.on.pull_request"           // Pull request trigger
"$.on.workflow_dispatch"      // Manual trigger
"$.on.schedule[*]"            // Scheduled triggers (cron)

// Trigger details
"$.on.push.branches[*]"       // Push branch filters
"$.on.push.paths[*]"          // Push path filters
"$.on.pull_request.types[*]"  // PR event types
```

### Job-Level Patterns

```java
// All jobs
"$.jobs"                      // Jobs object
"$.jobs.*"                    // Any job (wildcard)
"$.jobs.build"                // Specific job named 'build'

// Job properties
"$.jobs.*.name"               // Job display name
"$.jobs.*.runs-on"            // Runner specification
"$.jobs.*.needs"              // Job dependencies
"$.jobs.*.if"                 // Job conditions
"$.jobs.*.timeout-minutes"    // Job timeout
"$.jobs.*.strategy"           // Matrix/parallel strategy
"$.jobs.*.env"                // Job-level environment variables
"$.jobs.*.permissions"        // Job-level permissions
"$.jobs.*.container"          // Container configuration
"$.jobs.*.services"           // Service containers

// Matrix strategy
"$.jobs.*.strategy.matrix"           // Matrix configuration
"$.jobs.*.strategy.matrix.os[*]"     // OS variations
"$.jobs.*.strategy.matrix.node[*]"   // Node.js versions
"$.jobs.*.strategy.fail-fast"        // Fail-fast setting
"$.jobs.*.strategy.max-parallel"     // Parallel limit
```

### Step-Level Patterns

```java
// All steps
"$.jobs.*.steps"              // Steps array
"$.jobs.*.steps[*]"           // Any step in any job
"$.jobs.build.steps[*]"       // Steps in 'build' job
"$.jobs.*.steps[0]"           // First step of each job

// Step properties
"$.jobs.*.steps[*].name"      // Step name
"$.jobs.*.steps[*].uses"      // Action reference
"$.jobs.*.steps[*].run"       // Shell command
"$.jobs.*.steps[*].with"      // Action inputs
"$.jobs.*.steps[*].env"       // Step environment variables
"$.jobs.*.steps[*].if"        // Step condition
"$.jobs.*.steps[*].continue-on-error"  // Error handling

// Action inputs (with block)
"$.jobs.*.steps[*].with.node-version"  // Specific input
"$.jobs.*.steps[*].with.*"             // Any input
```

### Complete GitHub Actions Examples

```java
// Find all uses of actions/checkout
JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");
if (matcher.matches(getCursor()) && "uses".equals(entry.getKey().getValue())) {
    if (entry.getValue() instanceof Yaml.Scalar) {
        Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
        if (scalar.getValue().startsWith("actions/checkout@")) {
            // Found checkout action
        }
    }
}

// Find all jobs running on ubuntu-latest
JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.runs-on");
if (matcher.matches(getCursor()) && "runs-on".equals(entry.getKey().getValue())) {
    // Process runner specification
}

// Find all node-version specifications in matrix
JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.strategy.matrix.node[*]");
if (matcher.matches(getCursor())) {
    // Process node version entry
}

// Find environment variables at any level
JsonPathMatcher matcher = new JsonPathMatcher("$..env.*");
if (matcher.matches(getCursor())) {
    // Found an environment variable
}
```

---

## Kubernetes Patterns

### Pod/Deployment Patterns

```java
// Metadata
"$.metadata.name"                    // Resource name
"$.metadata.namespace"               // Namespace
"$.metadata.labels.*"                // Any label
"$.metadata.annotations.*"           // Any annotation

// Spec
"$.spec.replicas"                    // Replica count
"$.spec.selector"                    // Pod selector
"$.spec.template"                    // Pod template

// Pod template
"$.spec.template.metadata.labels.*"  // Pod labels
"$.spec.template.spec.containers[*]" // All containers
"$.spec.template.spec.initContainers[*]"  // Init containers
"$.spec.template.spec.volumes[*]"    // Volumes

// Container details
"$.spec.template.spec.containers[*].name"    // Container name
"$.spec.template.spec.containers[*].image"   // Container image
"$.spec.template.spec.containers[*].ports[*]" // Container ports
"$.spec.template.spec.containers[*].env[*]"   // Environment variables
"$.spec.template.spec.containers[*].resources"  // Resource limits
"$.spec.template.spec.containers[*].volumeMounts[*]"  // Volume mounts
```

### Service Patterns

```java
"$.spec.type"                        // Service type (ClusterIP, NodePort, LoadBalancer)
"$.spec.selector.*"                  // Service selector
"$.spec.ports[*]"                    // Service ports
"$.spec.ports[*].port"               // Port number
"$.spec.ports[*].targetPort"         // Target port
"$.spec.ports[*].protocol"           // Protocol (TCP/UDP)
```

### ConfigMap/Secret Patterns

```java
"$.data.*"                           // Any data entry
"$.data.config\\.yaml"               // Specific data key
"$.stringData.*"                     // String data entries
"$.binaryData.*"                     // Binary data entries
```

### Ingress Patterns

```java
"$.spec.rules[*]"                    // Ingress rules
"$.spec.rules[*].host"               // Host pattern
"$.spec.rules[*].http.paths[*]"      // Path rules
"$.spec.rules[*].http.paths[*].path" // Path pattern
"$.spec.rules[*].http.paths[*].backend"  // Backend service
"$.spec.tls[*]"                      // TLS configuration
```

### Complete Kubernetes Examples

```java
// Update container images for nginx
JsonPathMatcher matcher = new JsonPathMatcher("$.spec.template.spec.containers[*].image");
if (matcher.matches(getCursor()) && "image".equals(entry.getKey().getValue())) {
    if (entry.getValue() instanceof Yaml.Scalar) {
        Yaml.Scalar scalar = (Yaml.Scalar) entry.getValue();
        if (scalar.getValue().startsWith("nginx:")) {
            // Update nginx version
        }
    }
}

// Find all resource limits
JsonPathMatcher matcher = new JsonPathMatcher("$.spec.template.spec.containers[*].resources.limits.memory");
if (matcher.matches(getCursor())) {
    // Process memory limit
}

// Find all environment variables across all containers
JsonPathMatcher matcher = new JsonPathMatcher("$..containers[*].env[*].name");
if (matcher.matches(getCursor())) {
    // Process environment variable
}
```

---

## CI/CD Configuration Patterns

### GitLab CI

```java
// Job-level
"$.*.script[*]"                      // Script commands in any job
"$.*.stage"                          // Job stage
"$.*.image"                          // Docker image
"$.*.services[*]"                    // Service containers
"$.*.before_script[*]"               // Before script commands
"$.*.after_script[*]"                // After script commands
"$.*.variables.*"                    // Job variables
"$.*.cache"                          // Cache configuration
"$.*.artifacts"                      // Artifacts configuration

// Pipeline-level
"$.stages[*]"                        // Pipeline stages
"$.variables.*"                      // Global variables
"$.default"                          // Default settings
```

### CircleCI

```java
// Jobs
"$.jobs.*"                           // Any job
"$.jobs.*.docker[*]"                 // Docker images
"$.jobs.*.docker[*].image"           // Docker image
"$.jobs.*.steps[*]"                  // Job steps
"$.jobs.*.environment.*"             // Job environment

// Workflows
"$.workflows.*"                      // Any workflow
"$.workflows.*.jobs[*]"              // Workflow jobs
```

### Travis CI

```java
"$.language"                         // Language
"$.os"                              // Operating system
"$.dist"                            // Distribution
"$.script[*]"                       // Build script
"$.before_install[*]"               // Before install
"$.install[*]"                      // Install commands
"$.before_script[*]"                // Before script
"$.after_success[*]"                // After success
"$.matrix.include[*]"               // Matrix builds
```

### Jenkins (Declarative Pipeline)

```java
"$.pipeline.agent"                   // Agent specification
"$.pipeline.stages[*]"               // Pipeline stages
"$.pipeline.stages[*].stage"         // Stage name
"$.pipeline.stages[*].steps[*]"      // Stage steps
"$.pipeline.environment.*"           // Environment variables
"$.pipeline.post"                    // Post actions
```

---

## Generic YAML Patterns

### Common Structures

```java
// Root level
"$.*"                                // Any root-level property
"$.version"                          // Version field
"$.name"                            // Name field
"$.description"                     // Description field

// Nested structures
"$.config.*"                        // Any config property
"$.settings.*"                      // Any settings property
"$.metadata.*"                      // Any metadata property

// Arrays
"$.items[*]"                        // Any item in array
"$.items[0]"                        // First item
"$.items[-1]"                       // Last item (not supported in all implementations)

// Deep search
"$..name"                           // Any 'name' at any level
"$..version"                        // Any 'version' at any level
```

### Package Manager Configs

```java
// package.json (npm)
"$.scripts.*"                       // npm scripts
"$.dependencies.*"                  // Dependencies
"$.devDependencies.*"               // Dev dependencies
"$.peerDependencies.*"              // Peer dependencies

// composer.json (PHP)
"$.require.*"                       // PHP dependencies
"$.require-dev.*"                   // Dev dependencies
"$.autoload.psr-4.*"                // PSR-4 autoload

// Gemfile (Ruby) - typically not YAML but similar patterns
"$.dependencies[*]"                 // Gem dependencies
```

### Docker Compose

```java
"$.version"                         // Compose file version
"$.services.*"                      // Any service
"$.services.*.image"                // Service image
"$.services.*.build"                // Build configuration
"$.services.*.ports[*]"             // Port mappings
"$.services.*.environment.*"        // Environment variables
"$.services.*.volumes[*]"           // Volume mounts
"$.services.*.depends_on[*]"        // Dependencies
"$.networks.*"                      // Network definitions
"$.volumes.*"                       // Volume definitions
```

### Ansible Playbooks

```java
"$[*].hosts"                        // Target hosts
"$[*].tasks[*]"                     // All tasks
"$[*].tasks[*].name"                // Task names
"$[*].tasks[*].when"                // Task conditions
"$[*].vars.*"                       // Variables
"$[*].roles[*]"                     // Roles
```

---

## Advanced Patterns

### Recursive Descent

Find elements at any depth in the structure:

```java
// Find all 'version' keys anywhere in document
JsonPathMatcher matcher = new JsonPathMatcher("$..version");

// Find all 'env' objects anywhere
JsonPathMatcher matcher = new JsonPathMatcher("$..env");

// Find all arrays named 'items' anywhere
JsonPathMatcher matcher = new JsonPathMatcher("$..items[*]");
```

### Multiple Matchers

Use multiple matchers for precise targeting:

```java
// Match steps that use actions AND are in build job
JsonPathMatcher stepMatcher = new JsonPathMatcher("$.jobs.build.steps[*].uses");
JsonPathMatcher anyStepMatcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");

if (stepMatcher.matches(getCursor()) || anyStepMatcher.matches(getCursor())) {
    // Process action reference
}
```

### Combining with Key Checks

```java
// Match 'uses' key within steps
JsonPathMatcher pathMatcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");

@Override
public Yaml.Mapping.Entry visitMappingEntry(Yaml.Mapping.Entry entry, ExecutionContext ctx) {
    // Check both path AND key name
    if (pathMatcher.matches(getCursor()) && "uses".equals(entry.getKey().getValue())) {
        // This is definitely a 'uses' field in a step
    }
    return super.visitMappingEntry(entry, ctx);
}
```

---

## Pattern Selection Guide

| Use Case | Pattern Type | Example |
|----------|--------------|---------|
| Exact path | Explicit path | `$.jobs.build.steps[0]` |
| Any child | Wildcard | `$.jobs.*` |
| Any array item | Array wildcard | `$.steps[*]` |
| Any depth | Recursive descent | `$..version` |
| Conditional | With key check | `pathMatcher.matches() && "key".equals(key)` |

---

## Common Mistakes

### 1. Forgetting Key Name Check

```java
// ❌ WRONG - matches parent path, not the specific key
JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");
if (matcher.matches(getCursor())) {
    // This matches the STEP, not the 'uses' key
}

// ✅ CORRECT - check both path and key
JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");
if (matcher.matches(getCursor()) && "uses".equals(entry.getKey().getValue())) {
    // Now we're definitely at the 'uses' key
}
```

### 2. Wrong Visitor Method

```java
// ❌ WRONG - visitMapping() doesn't work for sequences
JsonPathMatcher matcher = new JsonPathMatcher("$.steps[*]");
public Yaml.Mapping visitMapping(Yaml.Mapping mapping, ExecutionContext ctx) {
    // Won't match array items
}

// ✅ CORRECT - use visitSequenceEntry()
JsonPathMatcher matcher = new JsonPathMatcher("$.steps[*]");
public Yaml.Sequence.Entry visitSequenceEntry(Yaml.Sequence.Entry entry, ExecutionContext ctx) {
    if (matcher.matches(getCursor())) {
        // Process sequence entry
    }
}
```

### 3. Overly Broad Patterns

```java
// ❌ TOO BROAD - matches 'uses' anywhere
JsonPathMatcher matcher = new JsonPathMatcher("$..uses");

// ✅ BETTER - specific to GitHub Actions steps
JsonPathMatcher matcher = new JsonPathMatcher("$.jobs.*.steps[*].uses");
```

---

## Testing JsonPath Patterns

```java
// In your test, verify the path matches
@Test
void testJsonPathMatching() {
    rewriteRun(
        spec -> spec.recipe(new YourRecipe()),
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
```

---

## Quick Reference Table

| YAML Structure | JsonPath Pattern | Visitor Method |
|----------------|------------------|----------------|
| Root property | `$.property` | `visitMappingEntry` |
| Nested property | `$.parent.child` | `visitMappingEntry` |
| Any property | `$.*` or `$.parent.*` | `visitMappingEntry` |
| Array item | `$.array[*]` | `visitSequenceEntry` |
| Nested array | `$.parent.array[*]` | `visitSequenceEntry` |
| Any depth | `$..property` | `visitMappingEntry` |
| Multiple levels | `$.a.*.b.*.c` | `visitMappingEntry` |

---

## Additional Resources

- JsonPath Specification: https://goessner.net/articles/JsonPath/
- JsonPath Evaluator (online tool): https://jsonpath.com/
- OpenRewrite JsonPathMatcher JavaDoc: https://docs.openrewrite.org/
