# Claude-on-Claude Plugin Skills

This plugin provides expert guidance for creating and configuring Claude Code components.

## claude-code-builder

**Automatic activation** when creating or modifying Claude Code components including subagents, skills, slash commands, plugins, or plugin marketplaces.

### When to Use

This skill activates automatically when:
- Working with `.md` files in `.claude/` directories (agents, commands, skills)
- Editing YAML frontmatter in agent or skill definitions
- Configuring `plugin.json` or `marketplace.json` files
- Discussing Claude Code extensibility and customization
- Creating new Claude Code components

### What It Provides

**Quick Start Guidance**
- Component selection guide (skill vs command vs agent vs plugin)
- Best practices for each component type
- Workflow recommendations

**YAML Frontmatter Reference**
- Complete field documentation for skills, agents, and commands
- Required vs optional fields
- Validation rules and constraints

**Comprehensive Reference Guides**
- **Subagents Guide**: Creating delegatable agents with specialized expertise
- **Skills Guide**: Building auto-activating context-aware guidance
- **Slash Commands Guide**: Designing keyboard shortcuts with tool preapprovals
- **Plugins Guide**: Packaging and distributing component collections

**Best Practices**
- Description writing for skill activation triggers
- Tool preapproval patterns for commands
- System prompt design for agents
- Plugin structure and marketplace configuration

**Troubleshooting**
- Common YAML errors and fixes
- Skill activation debugging
- Plugin installation issues
- Component discovery problems

### Bundled Reference Materials

The skill includes comprehensive reference guides stored in `references/`:

1. **subagents-guide.md** (5,900+ lines)
   - Complete YAML frontmatter reference
   - System prompt best practices and patterns
   - Domain expert and workflow automation patterns
   - Testing and integration with plugins
   - Comparison with skills and commands

2. **skills-guide.md** (5,300+ lines)
   - Description writing for automatic activation
   - Content structure recommendations
   - Bundling reference materials and templates
   - SKILLS.md index format
   - Discovery and testing techniques

3. **slash-commands-guide.md** (4,800+ lines)
   - Tool preapproval syntax and patterns
   - Argument handling with placeholders
   - Common workflow patterns
   - Security considerations
   - Integration with subagents

4. **plugins-guide.md** (5,600+ lines)
   - Plugin structure and metadata
   - Marketplace configuration (marketplace.json)
   - Installation and distribution
   - Testing and versioning
   - Troubleshooting guide

### Example Usage

#### Creating a New Skill

When you start creating a skill, this skill automatically provides:
- Proper YAML frontmatter template
- Description writing guidance with activation triggers
- Directory structure recommendations
- Reference to the detailed skills-guide.md

#### Debugging YAML Frontmatter

When editing agent or skill files, this skill helps with:
- Field validation
- Common YAML syntax errors
- Required vs optional fields
- Format and naming conventions

#### Building a Plugin

When creating a plugin, this skill guides you through:
- Directory structure creation
- plugin.json configuration
- Component registration
- marketplace.json setup
- Testing the installation process

### Quick Reference

**Component Selection**:
- **Skill**: Auto-activates based on context → Best for always-available guidance
- **Command**: Manual invocation via `/command` → Best for quick shortcuts
- **Agent**: Explicit delegation via Task tool → Best for isolated workflows
- **Plugin**: Package multiple components → Best for distribution

**YAML Frontmatter Essentials**:

```yaml
# Skills (SKILL.md)
---
name: skill-name
description: Use when [triggers]. Include specific keywords.
---

# Subagents (agents/*.md)
---
name: agent-name
description: Purpose with examples
model: inherit
color: blue
tools: Read, Write, Edit
---

# Commands (commands/*.md) - Optional frontmatter
---
description: One-line description
allowed-tools:
  - Bash(npm:*)
args:
  - name: arg-name
    description: What it is
---
```

**Key Best Practices**:
1. Skills: Start description with "Use when..." and include trigger keywords
2. Commands: Preapprove tools with glob patterns for flexibility
3. Agents: Focus on specific domain expertise
4. Plugins: Use relative paths with `./` prefix in configurations

### Links to Documentation

- Subagents: https://docs.claude.com/en/docs/claude-code/sub-agents.md
- Skills: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview.md
- Slash Commands: https://docs.claude.com/en/docs/claude-code/slash-commands.md
- Plugins: https://docs.claude.com/en/docs/claude-code/plugins.md
- Plugin Marketplaces: https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md

---

## Future Skills

This plugin may expand to include additional skills focused on:
- Advanced agent design patterns
- Plugin marketplace management
- Component testing and validation
- Claude Code best practices and conventions
