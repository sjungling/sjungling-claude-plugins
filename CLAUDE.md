# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a personal collection of Claude Code plugins. Plugins extend Claude Code's functionality through custom tools, hooks, and integrations via the Claude Code plugin system.

## Development Commands

This repository doesn't require a build step - it's a collection of markdown-based plugin definitions. Key operations:

- **Validate marketplace structure**: Ensure `.claude-plugin/marketplace.json` is valid JSON
- **Test plugin locally**: Use `/plugin marketplace add /Users/scott.jungling/Work/claude-plugins` to add this marketplace
- **Install plugin**: Use `/plugin install <plugin-name>@claude-plugins` to test installation
- **Validate agent/command syntax**: Check YAML frontmatter in markdown files is properly formatted

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

**cli-developer** (`plugins/cli-developer/`):
- Agent: `cli-ux-designer.md` - Expert CLI/TUI design consultant for command structure, visual design, accessibility, and UX patterns

**technical-writer** (`plugins/technical-writer/`):
- Agent: `technical-writer.md` - Documentation specialist for all technical writing tasks (README, API docs, guides, specs, release notes) plus Obsidian vault management via obsidian-cli

**openrewrite-author** (`plugins/openrewrite-author/`):
- Agent: `yaml-recipe-expert.md` - Expert in creating OpenRewrite recipes for YAML files using LST structure and visitor patterns (Java 8 compatible)

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
   - Minimal required fields: `name`, `source`
   - The `source` path must use relative prefix `./` (e.g., `"./plugins/swift-engineer"`)
   - Plugin metadata is stored in individual plugin directories, not in marketplace.json

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
   - No YAML frontmatter required
   - Content is the command's prompt/workflow that executes when invoked
   - Example: `swift-lint.md` contains instructions to run swift-format tools

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
