# Skills Creation Guide

## Overview

Skills are reusable prompt templates that Claude Code automatically invokes based on context. They provide guidance, patterns, and workflows that activate when relevant without explicit user invocation.

**Official Documentation**: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview.md

## When to Create a Skill

Create a skill when you need:
- Automatic activation based on context or keywords
- Always-available guidance for specific tasks
- Reusable patterns that apply across projects
- Reference materials bundled with prompts
- Workflows that should be followed consistently

## Directory Structure

Skills are directories containing a `SKILL.md` file and optional bundled resources:

```
skill-name/
├── SKILL.md           # Required: main skill definition
├── references/        # Optional: docs loaded into context as needed
│   ├── guide.md
│   └── examples.md
├── assets/            # Optional: files used in output (not loaded into context)
│   ├── templates/
│   │   └── component.tsx
│   └── logo.png
└── scripts/           # Optional: executable utilities
    └── helper.py
```

### Location
- Personal: `~/.claude/skills/`
- Plugin: `<plugin-root>/skills/`
- Project: `.claude/skills/`

## SKILL.md Format

Skills require YAML frontmatter followed by the skill content:

```markdown
---
name: skill-name
description: Detailed description including when to use this skill and specific triggers
---

[Skill prompt content with instructions, examples, and guidance]
```

## YAML Frontmatter Fields

**CRITICAL**: Skills support ONLY two frontmatter fields. Do not add any other fields.

### Required Fields

**`name`** (string, max 64 characters)
- Unique identifier for the skill
- Use kebab-case
- Should match directory name
- Example: `ios-swift-expert`, `test-driven-development`

**`description`** (string, max 1024 characters)
- Comprehensive description of what the skill does
- **Critical**: Must include when to use the skill and specific trigger contexts
- Should mention key technologies, frameworks, or patterns
- Used by Claude Code to determine when to activate the skill
- Example:
  ```yaml
  description: Use when working with iOS or macOS development projects, including Swift code, SwiftUI interfaces, Xcode project configuration, iOS frameworks, app architecture, debugging iOS apps, or any Apple platform development tasks.
  ```

### No Other Fields Are Supported

Unlike subagents, skills only support `name` and `description` in frontmatter. Configuration is done through the skill content itself.

**INVALID - Do Not Use:**
```yaml
---
name: my-skill
description: Valid description
version: 1.0.0        # ❌ NOT SUPPORTED
when_to_use: ...      # ❌ NOT SUPPORTED
author: ...           # ❌ NOT SUPPORTED
tags: ...             # ❌ NOT SUPPORTED
---
```

**Note**: You may encounter skills from other repositories (e.g., superpowers) that use additional fields like `version` or `when_to_use`. These are custom conventions specific to those repositories and are NOT part of the official Claude Code skill specification. Do not copy these fields into Claude Code skills.

## Description Best Practices

The description is **critical** for skill activation. It should:

1. **Use third-person voice**: Write "Expert in X. Automatically activates when..." rather than "Use when..."
2. **List specific technologies**: Mention frameworks, languages, tools
3. **Include task types**: Design, debugging, testing, refactoring, etc.
4. **Reference file patterns**: File extensions, naming patterns
5. **Specify contexts**: Project types, scenarios, workflows

**Good Examples:**

```yaml
description: Expert in iterative design refinement. Automatically activates when creating or developing anything before writing code or implementation plans - refines rough ideas into fully-formed designs through structured Socratic questioning, alternative exploration, and incremental validation
```

```yaml
description: Expert in systematic debugging. Automatically activates when encountering any bug, test failure, or unexpected behavior before proposing fixes - four-phase framework (root cause investigation, pattern analysis, hypothesis testing, implementation) that ensures understanding before attempting solutions
```

```yaml
description: Expert in iOS and macOS development. Automatically activates when working with Swift code, SwiftUI interfaces, Xcode project configuration, iOS frameworks, app architecture, debugging iOS apps, or any Apple platform development tasks
```

**Poor Examples:**

```yaml
description: Helps with Swift development
# Too vague - no trigger contexts, not third-person
```

```yaml
description: Use when building microservices
# Second-person voice instead of third-person
```

```yaml
description: A comprehensive guide to building scalable microservices architectures using cloud-native patterns
# Doesn't clearly state when to activate
```

## Writing Style

Write the entire skill using **imperative/infinitive form** (verb-first instructions), not second person. Use objective, instructional language that Claude can follow directly.

**Do** (Imperative/Infinitive):
- "To accomplish X, do Y"
- "Start with step 1"
- "Analyze the code for patterns"
- "Create a test file"
- "Avoid using global state"

**Don't** (Second Person):
- "You should do X"
- "If you need to do X"
- "You can analyze the code"
- "You will create a test file"
- "You shouldn't use global state"

This style maintains consistency and clarity for AI consumption while keeping the skill content focused on actionable instructions rather than conversational guidance.

## Skill Creation Workflow

Follow this structured process to create effective skills:

### Step 1: Understand the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood.

Clearly understand concrete examples of how the skill will be used. Gather these through:
- Direct user examples of tasks they perform repeatedly
- Generated examples that are validated with user feedback
- Real-world scenarios from past work

**Key questions to answer**:
- What functionality should the skill support?
- What specific tasks would trigger this skill?
- What would a user say or do that should activate it?
- What file types, technologies, or contexts are involved?

Avoid overwhelming with too many questions at once. Start with the most important and follow up as needed.

**Conclude when**: There is a clear sense of the functionality the skill should support.

### Step 2: Plan the Reusable Skill Contents

Analyze each concrete example to identify what bundled resources would help:

For each example, consider:
1. How to execute the task from scratch
2. What gets rewritten repeatedly (→ candidate for `scripts/`)
3. What documentation would help (→ candidate for `references/`)
4. What templates or assets would help (→ candidate for `assets/`)

**Example analysis**:
- "Help me rotate this PDF" → `scripts/rotate_pdf.py` (same code rewritten each time)
- "Build me a todo app" → `assets/frontend-template/` (same boilerplate each time)
- "Query user data from BigQuery" → `references/schema.md` (need to rediscover schemas each time)

**Output**: A list of scripts, references, and assets to include in the skill.

### Step 3: Initialize the Skill

Create the skill structure using the initialization script from the Anthropic skills repository:

```bash
uvx --from git+https://github.com/anthropics/skills init_skill.py <skill-name> --path <output-directory>
```

This script:
- Creates the skill directory at the specified path
- Generates a SKILL.md template with proper frontmatter and placeholders
- Creates example resource directories: `scripts/`, `references/`, and `assets/`
- Adds example files in each directory that can be customized or deleted

**Alternative**: Manually create the directory structure if the script is not available, but the script ensures proper formatting and structure.

### Step 4: Implement the Skill

**Start with bundled resources**:
1. Create the scripts, references, and assets identified in Step 2
2. This may require user input (e.g., brand assets, company documentation)
3. Delete any example files/directories not needed for the skill

**Update SKILL.md**:

Answer these questions in the skill content:
1. What is the purpose of the skill? (brief overview)
2. When should the skill be used? (activation contexts)
3. How should Claude use the skill in practice?

**Remember**:
- Use third-person voice in description
- Use imperative/infinitive form in skill content
- Reference all bundled resources so Claude knows how to use them
- Keep SKILL.md lean; move detailed content to references files
- Include concrete examples where helpful

### Step 5: Package and Validate the Skill

Package the skill into a distributable format using the packaging script:

```bash
uvx --from git+https://github.com/anthropics/skills package_skill.py <path/to/skill-folder> [output-directory]
```

The script will:
1. **Validate** the skill automatically:
   - YAML frontmatter format and required fields
   - Skill naming conventions and directory structure
   - Description completeness and quality
   - File organization and resource references

2. **Package** the skill if validation passes:
   - Creates a zip file named after the skill (e.g., `my-skill.zip`)
   - Includes all files with proper directory structure
   - Ready for distribution or installation

If validation fails, fix the reported errors and run again.

### Step 6: Test and Iterate

After testing the skill in real usage:

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again

**Common iterations**:
- Refining description to improve activation triggers
- Moving content between SKILL.md and references files
- Adding missing examples or patterns
- Creating additional scripts for repeated tasks

## Skill Content Structure

### Recommended Sections

1. **Quick Start** - Immediate, actionable guidance
   ```markdown
   ## Quick Start

   When [trigger context], follow these steps:
   1. [Step 1]
   2. [Step 2]
   3. [Step 3]
   ```

2. **Core Principles** - Fundamental concepts
   ```markdown
   ## Core Principles

   - Principle 1: [explanation]
   - Principle 2: [explanation]
   ```

3. **Workflows** - Step-by-step processes
   ```markdown
   ## Workflow

   ### [Specific Task]
   1. [Step with details]
   2. [Step with details]
   ```

4. **Examples** - Concrete usage scenarios
   ```markdown
   ## Examples

   <example>
   Context: [scenario]
   user: [user request]
   assistant: [correct response]
   </example>
   ```

5. **Common Pitfalls** - What to avoid
   ```markdown
   ## Common Pitfalls

   **Don't:**
   - [Pitfall 1]
   - [Pitfall 2]

   **Do:**
   - [Best practice 1]
   - [Best practice 2]
   ```

6. **References** - Links to bundled materials
   ```markdown
   ## Bundled Resources

   See `references/guide.md` for detailed patterns.
   See `assets/templates/template.txt` for starter code.
   ```

## Bundling Reference Materials

Skills can include supporting files in the skill directory. Understanding when and how to use each type is critical for effective skill design.

### Progressive Disclosure: 3-Level Loading System

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always loaded into context (~100 words)
2. **SKILL.md body** - Loaded when skill triggers (<5k words recommended)
3. **Bundled resources** - Loaded as needed by Claude (varies by type)

This design keeps the context window lean while making specialized knowledge available when needed.

### Resource Types and Context Loading

**Critical distinction**: Different resource types have different relationships with the context window.

#### Scripts (`scripts/`)

**Purpose**: Executable code (Python, Bash, etc.) for tasks requiring deterministic reliability or repeatedly rewritten code.

**Context loading**: May be executed **without loading into context window**

**When to include**:
- Same code is being rewritten repeatedly
- Deterministic reliability is needed
- Task is procedural and automatable

**Examples**:
- `scripts/rotate_pdf.py` - PDF rotation utility
- `scripts/validate_schema.sh` - Schema validation
- `scripts/generate_boilerplate.py` - Code generation

**Benefits**: Token efficient, deterministic, can execute without reading into context

**Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments

#### References (`references/`)

**Purpose**: Documentation and reference material **loaded INTO context as needed** to inform Claude's process and thinking.

**Context loading**: **YES** - Loaded into context when Claude determines it's needed

**When to include**:
- Documentation that Claude should reference while working
- Detailed information too extensive for SKILL.md
- Domain knowledge, schemas, or specifications
- Detailed workflow guides or examples

**Examples**:
- `references/database_schema.md` - Database table structures
- `references/api_docs.md` - API specifications
- `references/company_policies.md` - Company-specific guidelines
- `references/advanced_patterns.md` - Detailed implementation patterns

**Benefits**: Keeps SKILL.md lean while making detailed information discoverable and loadable on demand

**Best practice for large files**: If reference files exceed 10k words, include grep search patterns in SKILL.md to help Claude find relevant sections efficiently.

#### Assets (`assets/`)

**Purpose**: Files **NOT intended to be loaded into context**, but rather **used within the output** Claude produces.

**Context loading**: **NO** - Not loaded into context; copied, modified, or used in final output

**When to include**:
- Files that will be used in the final output
- Templates that get copied or modified
- Images, fonts, or other binary resources
- Boilerplate code or project scaffolding

**Examples**:
- `assets/templates/component-template.tsx` - React component boilerplate
- `assets/logo.png` - Brand assets
- `assets/slides-template.pptx` - PowerPoint template
- `assets/frontend-skeleton/` - Complete project starter

**Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context

### Avoid Duplication

**Important principle**: Information should live in either SKILL.md or references files, **not both**.

Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

### Runtime Environment Constraints

**Important**: Skills run in Claude Code's runtime environment:
- No network access during skill execution
- No package installation during execution
- Must be self-contained
- Can reference bundled materials
- Scripts can execute if dependencies are available in the environment

## Naming Conventions

- Use **kebab-case** for skill directory names
- Be descriptive and searchable
- Indicate domain or capability
- Match the `name` field in SKILL.md
- Examples:
  - `ios-swift-expert`
  - `test-driven-development`
  - `systematic-debugging`
  - `brainstorming`

## Skills vs Subagents vs Commands

**Use Skills when:**
- Guidance should activate automatically
- Users shouldn't need to remember to invoke it
- Pattern applies across many contexts
- You want always-available best practices
- Example: Code style guides, testing patterns

**Use Subagents when:**
- You need explicit invocation control
- Workflow is delegatable and isolated
- You need different tool restrictions
- Context isolation is important
- Example: Specialized code reviews, complex migrations

**Use Commands when:**
- Workflow is simple and linear
- You want a keyboard shortcut
- No complex decision-making needed
- Example: Format code, run tests

## Testing Your Skill

1. **Verify Activation Context**
   - Create test scenarios matching your description
   - Check if skill activates appropriately
   - Refine description triggers if needed

2. **Test Instructions**
   - Follow the skill guidance yourself
   - Ensure steps are clear and actionable
   - Verify examples are correct

3. **Validate References**
   - Ensure bundled files are accessible
   - Check file paths are correct
   - Test any included scripts

4. **YAML Validation**
   - Verify frontmatter is valid YAML
   - Check name/description lengths
   - Ensure no unsupported fields

## Plugin Integration

When including skills in plugins:

1. Create `skills/` subdirectory in plugin root
2. Place each skill in its own directory under `skills/`
3. Create `SKILLS.md` index file (required for plugin skills)
4. Register in `.claude-plugin/marketplace.json`:
   ```json
   {
     "skills": {
       "skill-name": "./skills/skill-name"
     }
   }
   ```

### SKILLS.md Index Format

The `SKILLS.md` file documents all skills in the plugin:

```markdown
# Plugin Skills

This plugin provides the following skills:

## skill-name

[Description from SKILL.md]

### When to Use
- [Trigger scenario 1]
- [Trigger scenario 2]

### What It Provides
- [Capability 1]
- [Capability 2]

### Example Usage
[Brief example]

---

## another-skill

[Description and details for next skill]
```

## Example: Complete Skill

```markdown
---
name: api-testing-patterns
description: Expert in API testing patterns. Automatically activates when writing tests for REST APIs, GraphQL endpoints, or API integration tests - provides patterns for request mocking, response validation, authentication testing, and error scenario coverage
---

# API Testing Patterns

## Quick Start

When testing API endpoints:

1. **Arrange**: Set up test data and mocks
2. **Act**: Make the API request
3. **Assert**: Validate response status, headers, and body
4. **Cleanup**: Reset state for next test

## Core Principles

- **Test contracts, not implementation**: Focus on API behavior and response formats
- **Cover happy path and edge cases**: Success, validation errors, authentication failures
- **Mock external dependencies**: Don't hit real external APIs in tests
- **Use test fixtures**: Maintain consistent test data
- **Validate schemas**: Ensure responses match expected structure

## REST API Testing Patterns

### Basic Request/Response Test

```javascript
test('GET /users/:id returns user', async () => {
  const response = await request(app)
    .get('/users/123')
    .set('Authorization', 'Bearer test-token')
    .expect(200)
    .expect('Content-Type', /json/);

  expect(response.body).toMatchObject({
    id: '123',
    name: expect.any(String),
    email: expect.any(String)
  });
});
```

### Testing Error Scenarios

```javascript
test('GET /users/:id returns 404 for missing user', async () => {
  const response = await request(app)
    .get('/users/nonexistent')
    .set('Authorization', 'Bearer test-token')
    .expect(404);

  expect(response.body).toEqual({
    error: 'User not found',
    code: 'USER_NOT_FOUND'
  });
});
```

### Testing Authentication

```javascript
test('requires valid authentication token', async () => {
  await request(app)
    .get('/users/123')
    .expect(401);

  await request(app)
    .get('/users/123')
    .set('Authorization', 'Bearer invalid-token')
    .expect(401);
});
```

## GraphQL Testing Patterns

### Query Testing

```javascript
test('users query returns list of users', async () => {
  const query = `
    query {
      users {
        id
        name
        email
      }
    }
  `;

  const response = await request(app)
    .post('/graphql')
    .send({ query })
    .expect(200);

  expect(response.body.data.users).toBeInstanceOf(Array);
  expect(response.body.errors).toBeUndefined();
});
```

### Mutation Testing

```javascript
test('createUser mutation creates user', async () => {
  const mutation = `
    mutation CreateUser($input: UserInput!) {
      createUser(input: $input) {
        id
        name
        email
      }
    }
  `;

  const variables = {
    input: {
      name: 'Test User',
      email: 'test@example.com'
    }
  };

  const response = await request(app)
    .post('/graphql')
    .send({ query: mutation, variables })
    .expect(200);

  expect(response.body.data.createUser).toMatchObject({
    id: expect.any(String),
    name: 'Test User',
    email: 'test@example.com'
  });
});
```

## Common Pitfalls

**Don't:**
- Test internal implementation details
- Make real API calls to external services
- Share state between tests
- Use hardcoded timestamps or IDs
- Skip error scenario testing

**Do:**
- Mock external dependencies
- Use test fixtures and factories
- Validate response schemas
- Test all status codes
- Clean up after each test

## Test Organization

```
tests/
├── api/
│   ├── users.test.js
│   ├── posts.test.js
│   └── auth.test.js
├── fixtures/
│   ├── users.js
│   └── posts.js
└── helpers/
    ├── setup.js
    └── mock-server.js
```

## References

- See `references/http-status-codes.md` for complete status code reference
- See `assets/templates/api-test-template.js` for test boilerplate
- See `references/examples/complete-api-test-suite.js` for comprehensive examples
```

## Advanced Patterns

### Conditional Guidance

Use examples with different contexts to show when to apply different approaches:

```markdown
<example>
Context: Simple CRUD API with few endpoints
Recommended: Use inline test data
</example>

<example>
Context: Complex API with many interdependent resources
Recommended: Use factory pattern with test fixtures
</example>
```

### Progressive Disclosure

Start with quick patterns, then link to detailed references:

```markdown
## Quick Pattern

Use this for most cases:
[Simple example]

## Advanced Scenarios

For complex cases, see `references/advanced-patterns.md`:
- Nested resource testing
- Streaming response validation
- Webhook testing
```

### Checklists

Include actionable checklists for systematic execution:

```markdown
## API Test Checklist

Before merging API changes:
- [ ] Happy path tested with valid input
- [ ] Validation errors tested with invalid input
- [ ] Authentication/authorization tested
- [ ] Rate limiting tested
- [ ] Response schema validated
- [ ] Error responses follow format
- [ ] Documentation updated
```

## Skill Discovery

Skills are automatically discovered by Claude Code when:
- Placed in recognized skill directories
- SKILL.md has valid YAML frontmatter
- Name and description fields are present
- Plugin marketplace.json correctly references the skill

Claude Code uses the description to determine when to activate each skill, so make descriptions comprehensive and trigger-focused.
