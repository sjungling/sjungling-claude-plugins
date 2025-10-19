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

Skills are directories containing a `SKILL.md` file and optional reference materials:

```
skill-name/
├── SKILL.md           # Required: main skill definition
├── references/        # Optional: supporting documentation
│   ├── guide.md
│   └── examples.md
├── templates/         # Optional: code templates
│   └── template.txt
└── scripts/           # Optional: helper scripts
    └── helper.sh
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

### No Other Fields

Unlike subagents, skills only support `name` and `description` in frontmatter. Configuration is done through the skill content itself.

## Description Best Practices

The description is **critical** for skill activation. It should:

1. **Start with "Use when..."**: Clearly state activation triggers
2. **List specific technologies**: Mention frameworks, languages, tools
3. **Include task types**: Design, debugging, testing, refactoring, etc.
4. **Reference file patterns**: File extensions, naming patterns
5. **Specify contexts**: Project types, scenarios, workflows

**Good Examples:**

```yaml
description: Use when creating or developing anything, before writing code or implementation plans - refines rough ideas into fully-formed designs through structured Socratic questioning, alternative exploration, and incremental validation
```

```yaml
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes - four-phase framework (root cause investigation, pattern analysis, hypothesis testing, implementation) that ensures understanding before attempting solutions
```

```yaml
description: Use when working with iOS or macOS development projects, including Swift code, SwiftUI interfaces, Xcode project configuration, iOS frameworks, app architecture, debugging iOS apps, or any Apple platform development tasks
```

**Poor Examples:**

```yaml
description: Helps with Swift development
# Too vague - no trigger contexts
```

```yaml
description: A comprehensive guide to building scalable microservices architectures using cloud-native patterns
# Doesn't say "when to use"
```

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
   ## References

   See `references/guide.md` for detailed patterns.
   See `templates/template.txt` for starter code.
   ```

## Bundling Reference Materials

Skills can include supporting files in the skill directory:

### Reference Documents (`references/`)
- Detailed guides
- API documentation
- Design patterns
- Best practices
- Examples and case studies

### Templates (`templates/`)
- Code scaffolding
- Configuration files
- Boilerplate code
- Directory structures

### Scripts (`scripts/`)
- Helper utilities
- Validation scripts
- Code generators
- Setup automation

**Important**: Skills run in Claude Code's runtime environment:
- No network access during skill execution
- No package installation
- Must be self-contained
- Can reference bundled materials

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
description: Use when writing tests for REST APIs, GraphQL endpoints, or API integration tests - provides patterns for request mocking, response validation, authentication testing, and error scenario coverage
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
- See `templates/api-test-template.js` for test boilerplate
- See `examples/complete-api-test-suite.js` for comprehensive examples
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
