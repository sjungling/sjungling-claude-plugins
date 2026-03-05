# sjungling-plugins

A personal collection of [Claude Code](https://docs.claude.com/en/docs/claude-code) plugins — skills, commands, agents, and hooks that extend what Claude Code can do out of the box.

Covers iOS/Swift development, technical writing and PDF generation, CLI design, git workflows, tmux session management, structured data handling, and push notifications over Tailscale.

## Getting started

Add this marketplace to Claude Code, then install any plugin you want:

```bash
# add the marketplace
/plugin marketplace add https://github.com/sjungling/sjungling-claude-plugins

# install a plugin
/plugin install technical-writer@sjungling-plugins
```

Browse the available plugins in the [`plugins/`](plugins/) directory. Each plugin has its own `plugin.json` describing what it provides.

## Plugin anatomy

Each plugin lives under `plugins/` and can contain any combination of:

```
plugins/<name>/
├── .claude-plugin/plugin.json   # name, version, description
├── skills/                      # auto-activated context and workflows
├── commands/                    # slash commands
├── agents/                      # specialized subagents
└── hooks/                       # event-driven automation
```

See the [Claude Code plugin docs](https://docs.claude.com/en/docs/claude-code) for details on the plugin system.
