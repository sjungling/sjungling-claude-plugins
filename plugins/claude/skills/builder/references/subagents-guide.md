# Subagent Creation Guide

## Overview

Subagents are specialized AI agents with custom system prompts and behaviors. They extend Claude Code's capabilities by providing domain expertise and focused workflows.

**Official Documentation**: https://docs.claude.com/en/docs/claude-code/sub-agents.md

## When to Create a Subagent

Create a subagent when you need:
- Specialized domain expertise (e.g., iOS development, technical writing)
- Consistent behavior patterns for specific tasks
- Delegatable workflows that run independently
- Context isolation from the main session

## File Structure

Subagents are markdown files with YAML frontmatter:

```markdown
---
name: agent-name
description: Agent description with usage examples
model: inherit
color: green
tools: Read, Write, Edit, Bash, Glob
---

[Agent system prompt content]
```

### Location
- Personal: `~/.claude/agents/`
- Plugin: `<plugin-root>/agents/`
- Project: `.claude/agents/`

## YAML Frontmatter Fields

### Required Fields

**`name`** (string, kebab-case)
- Unique identifier for the agent
- Used in Task tool invocations
- Example: `ios-swift-expert`, `technical-writer`

**`description`** (string)
- Clear explanation of what the agent does
- Should include usage examples wrapped in `<example>` tags
- Visible to users when selecting agents
- Example:
  ```yaml
  description: Expert in Python linting and code quality analysis. Use when reviewing Python code for style violations, potential bugs, or best practice violations. Examples: <example>user: "Review my Python code for linting issues" assistant: "Let me use the python-linter agent to analyze your code for quality issues" <commentary>Python linting requires knowledge of PEP 8 and common Python anti-patterns.</commentary></example>
  ```

### Optional Fields

**`model`** (string)
- Specifies which model to use
- Use `inherit` to use the same model as the parent session
- Default: `inherit`
- Other options: specific model identifiers (use sparingly)

**`color`** (string)
- Display color in the UI
- Options: `blue`, `green`, `yellow`, `red`, `purple`, `cyan`, `magenta`
- Default: system default

**`tools`** (comma-separated list)
- Pre-approve specific tools for the agent
- Common tools: `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `WebFetch`
- Restricts agent to only listed tools (improves focus and safety)
- Example: `tools: Read, Write, Edit`

## System Prompt Best Practices

### Structure

1. **Identity Statement**: Clearly state what the agent is
   ```markdown
   You are an expert in iOS and macOS development with deep knowledge of Swift, SwiftUI, UIKit, and Apple frameworks.
   ```

2. **Expertise Areas**: List specific capabilities
   ```markdown
   ## Your Expertise

   You specialize in:
   - Swift language features and best practices
   - SwiftUI declarative interface design
   - UIKit view hierarchies and lifecycle
   ```

3. **Workflow Guidance**: Provide step-by-step processes
   ```markdown
   ## Workflow

   When implementing features:
   1. Analyze requirements
   2. Design data models
   3. Create views
   4. Test functionality
   ```

4. **Reference Resources**: Link to documentation
   ```markdown
   ## Documentation References

   - Apple Developer: https://developer.apple.com/documentation/
   - Swift.org: https://swift.org/documentation/
   ```

5. **Success Criteria**: Define what good looks like
   ```markdown
   ## Success Criteria

   Your code is successful when:
   - It compiles without warnings
   - It follows Swift API design guidelines
   - It handles errors appropriately
   ```

### Writing Effective Prompts

**Do:**
- Be specific about the agent's expertise boundaries
- Include concrete examples of when to use the agent
- Provide step-by-step workflows for common tasks
- Reference authoritative documentation
- Define clear success criteria

**Don't:**
- Make the agent too general-purpose
- Include tasks better suited for skills or commands
- Duplicate main Claude Code capabilities
- Create overly complex nested workflows

## Naming Conventions

- Use **kebab-case** for agent names
- Be descriptive but concise
- Indicate domain or specialty
- Examples:
  - `ios-swift-expert`
  - `technical-writer`
  - `cli-ux-designer`
  - `yaml-recipe-expert`

## Testing Your Subagent

1. **Invoke with Task tool**:
   ```
   Use the Task tool with subagent_type="your-agent-name"
   ```

2. **Verify behavior**:
   - Does it stay focused on its domain?
   - Does it follow the workflow you defined?
   - Does it have appropriate tool access?

3. **Iterate**:
   - Refine system prompt based on actual usage
   - Adjust tool preapprovals as needed
   - Update examples in description

## Common Patterns

### Domain Expert Pattern
```markdown
---
name: domain-expert
description: Expert in specific technology or domain
model: inherit
color: blue
tools: Read, Write, Edit, Bash
---

You are an expert in [specific domain].

## Your Expertise
[List specific capabilities]

## Workflow
[Define standard processes]

## Best Practices
[Domain-specific guidelines]
```

### Workflow Automation Pattern
```markdown
---
name: workflow-automator
description: Automates specific multi-step workflows
model: inherit
color: green
tools: Read, Write, Edit, Bash, Grep, Glob
---

You automate [specific workflow].

## Workflow Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Tool Usage
[How to use preapproved tools]

## Success Criteria
[What constitutes successful completion]
```

## Integration with Plugins

When creating subagents as part of plugins:

1. Place in `agents/` subdirectory of plugin
2. Register in `.claude-plugin/marketplace.json`:
   ```json
   {
     "agents": {
       "agent-name": "./agents/agent-name.md"
     }
   }
   ```
3. Document in plugin README.md
4. Consider whether a **skill** might be more appropriate (skills auto-activate based on context)

## Subagents vs Skills vs Commands

**Use Subagents when:**
- You need context isolation
- Workflow is delegatable and self-contained
- You want explicit invocation control
- Agent requires specialized model or tools

**Use Skills when:**
- You want automatic activation based on context
- Guidance should always be available
- Users shouldn't need to remember to invoke it
- Example: Code formatting rules, design patterns

**Use Commands when:**
- Workflow is simple and linear
- You want a quick shortcut
- No complex decision-making needed
- Example: Run tests, format code

## Example: Complete Subagent

```markdown
---
name: api-designer
description: Expert API designer specializing in RESTful and GraphQL APIs. Use when designing API endpoints, defining schemas, or establishing API conventions. Examples: <example>user: "Help me design a REST API for user management" assistant: "Let me use the api-designer agent to create a well-structured API" <commentary>API design requires expertise in REST principles and best practices.</commentary></example>
model: inherit
color: cyan
tools: Read, Write, Edit
---

You are an expert API designer with deep knowledge of REST, GraphQL, OpenAPI, and API best practices.

## Your Expertise

You specialize in:
- RESTful API design following Richardson Maturity Model
- GraphQL schema design and query optimization
- OpenAPI/Swagger specification authoring
- API versioning strategies
- Authentication and authorization patterns (OAuth 2.0, JWT, API keys)
- Rate limiting and pagination patterns
- Error response design
- API documentation

## Workflow

When designing APIs:

1. **Understand Requirements**
   - Identify resources and relationships
   - Determine access patterns
   - Consider scalability needs

2. **Choose Architecture**
   - REST for resource-oriented APIs
   - GraphQL for flexible data fetching
   - Consider hybrid approaches

3. **Design Endpoints/Schema**
   - Follow naming conventions
   - Use appropriate HTTP methods
   - Design consistent response formats
   - Handle errors gracefully

4. **Document**
   - Create OpenAPI specification (REST)
   - Generate schema documentation (GraphQL)
   - Provide usage examples
   - Document authentication

## Best Practices

### REST APIs
- Use nouns for resources, not verbs
- Leverage HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Version using URL path (`/v1/users`) or headers
- Return appropriate status codes
- Use HATEOAS for discoverability (Level 3 maturity)

### GraphQL APIs
- Design schema-first
- Use meaningful type names
- Implement proper error handling
- Optimize for N+1 query problem
- Provide pagination using cursor-based approach

### Common Patterns
- Use UUIDs for public IDs
- Implement request/response logging
- Support filtering, sorting, pagination
- Include rate limit headers
- Use JSON:API or HAL for hypermedia

## Reference Documentation

- REST: https://restfulapi.net/
- GraphQL: https://graphql.org/learn/
- OpenAPI: https://swagger.io/specification/
- HTTP Status Codes: https://httpstatuses.com/

## Success Criteria

Your API design is successful when:
- It follows industry standards and conventions
- Resources and endpoints are intuitive
- Error handling is comprehensive and clear
- Documentation enables easy integration
- Design scales with usage growth
```
