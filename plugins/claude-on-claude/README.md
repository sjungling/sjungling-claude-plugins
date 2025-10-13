# Claude-on-Claude Plugin

A meta-plugin that provides expert assistance in creating Claude Code components including subagents, slash commands, plugins, and plugin marketplaces.

## Overview

The `claude-on-claude` plugin helps you build Claude Code extensions by providing a specialized subagent that:

- References the latest official Claude Code documentation
- Follows best practices for component creation
- Guides you through proper YAML frontmatter configuration
- Suggests appropriate tool preapprovals
- Helps design effective system prompts and workflows

## Components

### Agents

**claude-code-builder** - Expert in creating Claude Code components

This agent specializes in:
- Creating custom subagents with proper YAML frontmatter
- Writing slash commands with argument handling and tool preapprovals
- Designing plugin structures and marketplace configurations
- Following Claude Code conventions

The agent automatically references these documentation sources:
- [Slash Commands](https://docs.claude.com/en/docs/claude-code/slash-commands.md)
- [Subagents](https://docs.claude.com/en/docs/claude-code/sub-agents.md)
- [Plugins](https://docs.claude.com/en/docs/claude-code/plugins.md)
- [Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md)

## Installation

First, add the marketplace to Claude Code:

```bash
/plugin marketplace add <path-to-claude-plugins-repo>
```

Then install this plugin:

```bash
/plugin install claude-on-claude@claude-plugins
```

## Usage

Once installed, you can use the `claude-code-builder` agent for tasks like:

### Creating a New Subagent

```
@claude-code-builder help me create a subagent for database schema design
```

### Writing a Slash Command

```
@claude-code-builder create a slash command that runs my test suite and generates a coverage report
```

### Building a New Plugin

```
@claude-code-builder I want to create a plugin for Go development with agents and commands
```

### Setting Up a Plugin Marketplace

```
@claude-code-builder help me configure a plugin marketplace for my team
```

## Best Practices

The `claude-code-builder` agent follows these conventions:

1. **Naming**: Uses kebab-case for all component names
2. **Documentation**: Always includes clear descriptions and usage examples
3. **Tool Preapprovals**: Suggests commonly used bash commands to preapprove
4. **System Prompts**: Crafts focused, effective prompts for subagents
5. **Structure**: Creates proper directory layouts and file organization

## Examples

### Example: Creating a Subagent for API Testing

```
You: @claude-code-builder create a subagent that helps test REST APIs

Agent: I'll help you create an API testing subagent. Let me fetch the latest documentation first...

[Agent creates a properly formatted agent file with:
- YAML frontmatter (name, description, model, color)
- System prompt focused on API testing
- References to relevant tools and workflows]
```

### Example: Slash Command with Preapprovals

```
You: @claude-code-builder create a command that builds my Docker images and pushes to registry

Agent: I'll create a slash command with Docker CLI preapprovals...

[Agent creates command with:
- YAML frontmatter including allowed-tools
- Preapproved docker commands
- Clear workflow instructions]
```

## Tips

- The agent will fetch current documentation to ensure accuracy
- Ask for guidance on best practices for your specific use case
- The agent can help refactor existing components to follow conventions
- Use it to learn Claude Code plugin development patterns

## Contributing

This plugin is part of a personal plugin collection. If you have suggestions or improvements, feel free to adapt it for your own use.

## License

Personal use plugin - adapt as needed for your own projects.
