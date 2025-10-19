# Claude Plugin

A meta-plugin that provides expert assistance in creating Claude Code components including subagents, slash commands, skills, plugins, and plugin marketplaces.

## Overview

The `claude` plugin helps you build Claude Code extensions by providing automatic skill activation that:

- References the latest official Claude Code documentation
- Follows best practices for component creation
- Guides you through proper YAML frontmatter configuration
- Suggests appropriate tool preapprovals
- Helps design effective system prompts and workflows

## Components

### Skills

**builder** - Expert in creating Claude Code components (automatic activation)

This skill automatically activates when working with Claude Code components and specializes in:
- Creating custom subagents with proper YAML frontmatter
- Writing slash commands with argument handling and tool preapprovals
- Designing plugin structures and marketplace configurations
- Following Claude Code conventions

The skill includes comprehensive reference guides for:
- [Slash Commands](https://docs.claude.com/en/docs/claude-code/slash-commands.md)
- [Subagents](https://docs.claude.com/en/docs/claude-code/sub-agents.md)
- [Plugins](https://docs.claude.com/en/docs/claude-code/plugins.md)
- [Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md)

### Agents

**builder** - Claude Code builder agent (explicit invocation)

A delegatable agent that uses the `claude:builder` skill. Use this when you want to delegate Claude Code component creation to a specialized agent using the Task tool.

## Installation

First, add the marketplace to Claude Code:

```bash
/plugin marketplace add <path-to-claude-plugins-repo>
```

Then install this plugin:

```bash
/plugin install claude@claude-plugins
```

## Usage

Once installed, the `builder` skill automatically activates when you're working on tasks like:

### Creating a New Subagent

The skill activates automatically when working with agent markdown files or discussing Claude Code components:

```
I need to create a subagent for database schema design
```

### Writing a Slash Command

```
Create a slash command that runs my test suite and generates a coverage report
```

### Building a New Plugin

```
I want to create a plugin for Go development with agents and commands
```

### Setting Up a Plugin Marketplace

```
Help me configure a plugin marketplace for my team
```

## Best Practices

The `builder` skill follows these conventions:

1. **Naming**: Uses kebab-case for all component names
2. **Documentation**: Always includes clear descriptions and usage examples
3. **Tool Preapprovals**: Suggests commonly used bash commands to preapprove
4. **System Prompts**: Crafts focused, effective prompts for subagents
5. **Structure**: Creates proper directory layouts and file organization

## Examples

### Example: Creating a Subagent for API Testing

```
You: Create a subagent that helps test REST APIs

Claude: I'm using the builder skill to help you create an API testing subagent...

[Creates a properly formatted agent file with:
- YAML frontmatter (name, description, model, color)
- System prompt focused on API testing
- References to relevant tools and workflows]
```

### Example: Slash Command with Preapprovals

```
You: Create a command that builds my Docker images and pushes to registry

Claude: I'll create a slash command with Docker CLI preapprovals...

[Creates command with:
- YAML frontmatter including allowed-tools
- Preapproved docker commands
- Clear workflow instructions]
```

## Tips

- The skill automatically activates when working with Claude Code components
- Includes comprehensive reference guides bundled within the skill
- Provides guidance on best practices for your specific use case
- Can help refactor existing components to follow conventions
- Learn Claude Code plugin development patterns through examples and references

## Contributing

This plugin is part of a personal plugin collection. If you have suggestions or improvements, feel free to adapt it for your own use.

## License

Personal use plugin - adapt as needed for your own projects.
