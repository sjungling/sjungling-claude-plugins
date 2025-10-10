# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a personal collection of Claude Code plugins. Plugins extend Claude Code's functionality through custom tools, hooks, and integrations via the Claude Code plugin system.

## Architecture

### Plugin Marketplace Structure

The repository uses a marketplace configuration (`.claude-plugin/marketplace.json`) that:
- Defines the plugin root location (`plugins/` directory at repository root)
- Lists all available plugins with metadata (version, description, keywords, category)
- Maps plugin components (agents, commands) to their file locations
- Enables plugin installation via `/plugin install <name>@claude-plugins`

### Plugin Component Types

Each plugin can contain:
- **Agents** (`agents/` subdirectory): Custom agent definitions with specialized prompts and behaviors
- **Commands** (`commands/` subdirectory): Slash command implementations that execute workflows
- Both agents and commands are defined in markdown files with YAML frontmatter

### Current Plugins

**swift-engineer** (`plugins/swift-engineer/`):
- Agent: `ios-swift-expert.md` - iOS/macOS development specialist
- Command: `swift-lint.md` - Runs swift-format for code formatting and linting

## Creating New Plugins

When adding a new plugin to the marketplace:

1. **Create plugin structure:**
   ```
   plugins/<plugin-name>/
   ├── agents/           # Optional: custom agents
   ├── commands/         # Optional: slash commands
   └── README.md         # Plugin documentation
   ```

2. **Register in marketplace:**
   - Add plugin entry to `.claude-plugin/marketplace.json` under `plugins` array
   - Required fields: `name`, `source`, `description`, `version`, `author`, `license`
   - Map component paths relative to plugin source directory

3. **Update CLAUDE.md:**
   - Add plugin description to "Current Plugins" section
   - Document any special usage instructions

4. **Agent file format** (`agents/<name>.md`):
   ```markdown
   ---
   name: agent-name
   description: Agent description with usage examples
   model: inherit
   color: green
   ---

   [Agent system prompt content]
   ```

5. **Command file format** (`commands/<name>.md`):
   ```markdown
   [Command implementation - workflow steps]
   ```

## Installing Plugins from This Marketplace

Add this marketplace to Claude Code:
```
/plugin marketplace add <path-to-this-repo>
```

Install a plugin:
```
/plugin install <plugin-name>@claude-plugins
```

## Documentation Reference

Claude Code plugin documentation: https://docs.claude.com/en/docs/claude-code
