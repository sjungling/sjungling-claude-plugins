---
name: claude-code-builder
description: Use when creating or modifying Claude Code components including subagents, skills, slash commands, plugins, or plugin marketplaces. Activates when working with .md files in .claude/ directories, agent/command/skill frontmatter, marketplace.json, or when discussing Claude Code extensibility.
---

# Claude Code Builder

Expert guidance for creating Claude Code subagents, skills, slash commands, plugins, and plugin marketplaces.

## When to Use This Skill

This skill activates when you're:
- Creating or editing agent markdown files with YAML frontmatter
- Writing slash command definitions
- Developing skills with SKILL.md files
- Configuring plugin.json or marketplace.json
- Working with files in `.claude/` directories
- Discussing Claude Code extensibility and customization

## Quick Start

### Creating a New Component

**Before starting**, determine which component type fits your need:

- **Skill**: Automatic activation based on context (preferred for most use cases)
- **Slash Command**: Quick keyboard shortcuts for common tasks
- **Subagent**: Delegatable workflows needing context isolation
- **Plugin**: Package multiple components for distribution

### Component Selection Guide

| Need | Use | Example |
|------|-----|---------|
| Always-available guidance | Skill | Code style patterns, debugging workflows |
| Keyboard shortcut | Command | `/format-code`, `/run-tests` |
| Delegatable workflow | Subagent | Code reviews, complex migrations |
| Package for distribution | Plugin | Collection of related components |

## Core Workflows

### 1. Creating a Skill

Skills provide automatic, context-aware guidance.

**Steps**:
1. Create directory: `skills/skill-name/`
2. Create `SKILL.md` with frontmatter
3. Write comprehensive description with trigger keywords
4. Add skill content with examples and patterns
5. Bundle reference materials in subdirectories
6. Test activation contexts

**See**: `references/skills-guide.md` for complete best practices

### 2. Creating a Slash Command

Commands provide quick shortcuts for common tasks.

**Steps**:
1. Create file: `commands/command-name.md`
2. Add optional YAML frontmatter (description, allowed-tools, args)
3. Write command prompt with argument placeholders
4. Preapprove necessary tools
5. Test command execution

**See**: `references/slash-commands-guide.md` for complete best practices

### 3. Creating a Subagent

Subagents provide specialized expertise and delegatable workflows.

**Steps**:
1. Create file: `agents/agent-name.md`
2. Add required YAML frontmatter (name, description, model, color, tools)
3. Write focused system prompt
4. Define workflows and success criteria
5. Test with Task tool

**See**: `references/subagents-guide.md` for complete best practices

### 4. Creating a Plugin

Plugins package components for distribution.

**Steps**:
1. Create plugin directory structure
2. Create `.claude-plugin/plugin.json` with metadata
3. Add components (agents, commands, skills)
4. Create README.md and SKILLS.md
5. Register in marketplace.json
6. Test installation

**See**: `references/plugins-guide.md` for complete best practices

## YAML Frontmatter Quick Reference

### Skills (SKILL.md)

```yaml
---
name: skill-name
description: Use when [triggers]. Detailed description with keywords.
---
```

**Key points**:
- Description must include "Use when..." with specific triggers
- Max 64 chars for name, 1024 for description
- Only name and description supported

### Subagents (agents/*.md)

```yaml
---
name: agent-name
description: Agent purpose with usage examples
model: inherit
color: blue
tools: Read, Write, Edit, Bash
---
```

**Key points**:
- Use kebab-case for names
- Include usage examples in description
- Colors: blue, green, yellow, red, purple, cyan, magenta
- List specific tools to restrict agent capabilities

### Slash Commands (commands/*.md)

```yaml
---
description: One-line command description
allowed-tools:
  - Bash(npm:*)
  - Bash(git:*)
args:
  - name: argument-name
    description: What this argument is
---
```

**Key points**:
- Frontmatter is optional
- Preapprove tools to reduce user friction
- Use glob patterns for flexible tool matching
- Document args for user reference

## Best Practices

### Skill Development

**Do**:
- Write descriptions with specific activation triggers
- Include technology names and file patterns
- Bundle reference materials in skill directory
- Test in multiple contexts to verify activation
- Start with "Use when..." in description

**Don't**:
- Make descriptions too generic
- Forget to mention specific technologies
- Include network-dependent resources
- Use skills for simple linear workflows (use commands instead)

### Command Development

**Do**:
- Use clear, descriptive command names
- Preapprove necessary tools
- Document arguments
- Include error handling guidance
- Support argument substitution

**Don't**:
- Preapprove dangerous commands unnecessarily
- Create commands for complex decision-making (use agents/skills)
- Forget to test with different argument combinations

### Subagent Development

**Do**:
- Focus on specific domain expertise
- Provide step-by-step workflows
- Reference authoritative documentation
- Define clear success criteria
- Restrict tools appropriately

**Don't**:
- Make agents too general-purpose
- Duplicate main Claude capabilities
- Create overly complex nested workflows
- Skip examples in description

### Plugin Development

**Do**:
- Focus on specific use case or domain
- Provide comprehensive documentation
- Test all components before publishing
- Use semantic versioning
- Include usage examples

**Don't**:
- Create unfocused plugins
- Use absolute paths in configuration
- Skip testing installation process
- Forget to document all components

## Common Patterns

### Skill with References

```
skill-name/
├── SKILL.md
├── references/
│   ├── guide.md
│   └── patterns.md
└── templates/
    └── template.txt
```

### Multi-Component Plugin

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── expert.md
├── commands/
│   └── quick-action.md
├── skills/
│   └── auto-guidance/
│       └── SKILL.md
├── SKILLS.md
└── README.md
```

### Command with Subagent

```markdown
---
description: Complex workflow delegated to expert
allowed-tools:
  - Task
---

Use the domain-expert agent to [accomplish task].

Provide the agent with:
- [Context 1]
- [Context 2]

Expected deliverables:
- [Output 1]
- [Output 2]
```

## Troubleshooting

### Skill Not Activating

**Problem**: Skill doesn't trigger in expected contexts

**Solutions**:
- Add more specific keywords to description
- Include technology/framework names
- Mention file patterns (.swift, .tsx, etc.)
- Start description with "Use when..."
- Test with `description` variations

### Invalid YAML Frontmatter

**Problem**: Component fails to load

**Solutions**:
- Validate YAML syntax (indentation, colons, dashes)
- Check field names match requirements
- Verify string values are quoted if they contain special chars
- Ensure name fields use kebab-case

### Command Tools Not Preapproved

**Problem**: Command prompts for approval repeatedly

**Solutions**:
- Add tools to `allowed-tools` array
- Use glob patterns for flexibility: `Bash(npm:*)`
- Include all commands the workflow needs
- Test command to identify missing approvals

### Plugin Not Installing

**Problem**: Plugin installation fails

**Solutions**:
- Verify `source` path uses `./` prefix
- Check all component paths are relative
- Validate marketplace.json is valid JSON
- Ensure files exist at specified paths
- Test with: `cat marketplace.json | python -m json.tool`

## Reference Materials

This skill includes comprehensive guides for each component type:

- **Subagents Guide**: `references/subagents-guide.md`
  - Complete frontmatter reference
  - System prompt best practices
  - Testing and integration patterns
  - Common agent patterns

- **Skills Guide**: `references/skills-guide.md`
  - Description writing for activation
  - Content structure recommendations
  - Bundling reference materials
  - Discovery and testing

- **Slash Commands Guide**: `references/slash-commands-guide.md`
  - Tool preapproval syntax
  - Argument handling
  - Workflow patterns
  - Security considerations

- **Plugins Guide**: `references/plugins-guide.md`
  - Plugin structure and metadata
  - Marketplace configuration
  - Installation and distribution
  - Testing and versioning

## Examples

### Example: Creating a Testing Skill

```yaml
---
name: api-testing-patterns
description: Use when writing tests for REST APIs, GraphQL endpoints, or API integration tests - provides patterns for request mocking, response validation, authentication testing, and error scenario coverage
---

# API Testing Patterns

## Quick Start

When testing API endpoints:
1. Arrange: Set up test data and mocks
2. Act: Make the API request
3. Assert: Validate response
4. Cleanup: Reset state

[Additional content with patterns and examples]
```

### Example: Creating a Deployment Command

```markdown
---
description: Deploy application to specified environment
allowed-tools:
  - Bash(git:*)
  - Bash(npm run deploy:*)
  - Bash(gh:*)
args:
  - name: environment
    description: Target environment (dev, staging, prod)
---

Deploy to $1 environment:

1. Verify git status is clean
2. Run deployment script for $1
3. Monitor deployment status
4. Create deployment record

Use: /deploy staging
```

### Example: Creating a Code Review Agent

```yaml
---
name: code-reviewer
description: Expert code reviewer analyzing code quality, best practices, security, and maintainability. Use for comprehensive code reviews before merging.
model: inherit
color: purple
tools: Read, Grep, Glob
---

You are an expert code reviewer specializing in code quality, security, and maintainability.

## Review Process

1. Analyze changed files for:
   - Code quality and readability
   - Security vulnerabilities
   - Performance implications
   - Test coverage

2. Provide feedback on:
   - Best practices adherence
   - Design patterns
   - Error handling
   - Documentation

3. Suggest improvements with examples

[Additional review guidelines]
```

## Documentation Links

**Official Claude Code Documentation**:
- Subagents: https://docs.claude.com/en/docs/claude-code/sub-agents.md
- Skills: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview.md
- Slash Commands: https://docs.claude.com/en/docs/claude-code/slash-commands.md
- Plugins: https://docs.claude.com/en/docs/claude-code/plugins.md
- Plugin Marketplaces: https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md

## Success Criteria

Your Claude Code components are successful when:

**Skills**:
- Activate automatically in appropriate contexts
- Provide clear, actionable guidance
- Include comprehensive examples
- Bundle useful reference materials

**Commands**:
- Execute workflows efficiently
- Handle arguments correctly
- Have necessary tools preapproved
- Provide clear feedback

**Subagents**:
- Stay focused on their domain
- Follow defined workflows
- Have appropriate tool access
- Deliver expected results

**Plugins**:
- Install without errors
- All components work as documented
- Clear documentation provided
- Properly versioned and maintained
