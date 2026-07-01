# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a personal collection of Claude Code plugins. Plugins extend Claude Code's functionality through custom tools, hooks, and integrations via the Claude Code plugin system.

## Development Commands

This repository doesn't require a build step - it's a collection of markdown-based plugin definitions. Key operations:

- **Validate marketplace structure**: Ensure `.claude-plugin/marketplace.json` is valid JSON
- **Test plugin locally**: Use `/plugin marketplace add /Users/scott.jungling/Work/sjungling-claude-plugins` to add this marketplace
- **Install plugin**: Use `/plugin install <plugin-name>@sjungling-plugins` to test installation
- **Validate agent/command syntax**: Check YAML frontmatter in markdown files is properly formatted
- **Bump plugin version**: Always increment `version` in `plugins/<plugin-name>/.claude-plugin/plugin.json` when making any changes to a plugin. Claude Code won't detect updates on reinstall without a version bump.

## Architecture

### Plugin Marketplace Structure

The repository uses a marketplace configuration (`.claude-plugin/marketplace.json`) that:
- Defines the plugin root location (`plugins/` directory at repository root)
- Lists all available plugins with metadata (version, description, keywords, category)
- Maps plugin components (agents, commands) to their file locations
- Enables plugin installation via `/plugin install <name>@sjungling-plugins`

### Plugin Component Types

Each plugin can contain:
- **Agents** (`agents/` subdirectory): Custom agent definitions with specialized prompts and behaviors
- **Commands** (`commands/` subdirectory): Slash command implementations that execute workflows
- **Skills** (`skills/` subdirectory): Reusable prompt templates that Claude automatically invokes based on context
- Components are defined in markdown files with YAML frontmatter (skills and agents require frontmatter, commands don't)

### Current Plugins

**swift-engineer** (`plugins/swift-engineer/`):
- Skill: `ios-swift-expert` - Elite iOS and macOS development expertise that automatically activates when working with Swift, SwiftUI, UIKit, Xcode projects, or Apple frameworks
- Command: `swift-lint.md` - Runs swift-format for code formatting and linting
- Command: `generate-docs.md` - Builds symbol graph documentation via xcodebuild docbuild, extracts .symbolgraph.json files to .build/symbol-graphs/, and updates the target project's CLAUDE.md with jq query examples for LLM-friendly API discovery
- Agent (legacy): `ios-swift-expert.md` - Original agent implementation (prefer skills for automatic activation)

**cli-developer** (`plugins/cli-developer/`):
- Agent: `cli-ux-designer.md` - Expert CLI/TUI design consultant for command structure, visual design, accessibility, and UX patterns

**technical-writer** (`plugins/technical-writer/`):
- Skill: `technical-writer` - Expert in technical documentation (README, API docs, guides, tutorials, quickstarts, specs, release notes) that automatically activates when working with .md files in docs/ directories or README files
- Skill: `pdf-generation` - Generate a PDF book from a directory of ordered markdown chapters using pandoc and weasyprint. Includes print-optimized CSS, table of contents, and inter-chapter link resolution.
- Command: `/technical-overview [output-dir]` - Create or update a comprehensive Beej's-Guide-style technical manual with parallel chapter writing via teammates, then generate a PDF
- Command: `/walkthrough [path-to-source]` - Generate a code walkthrough using showboat
- Command: `/save-to-obsidian [vault] [topic]` - Save the current spec/plan/session summary to Obsidian as a design note. Auto-discovers superpowers specs/plans or a Claude plan file (falls back to a conversation summary), resolves the target vault/folder/tag conventions from existing notes, then writes through `write-markdown-to-vault.js` (never the `Write` tool) since iCloud-synced vaults are TCC-protected against direct filesystem access.
- Agent: `technical-writer.md` - Legacy agent implementation (prefer skill for automatic activation)
- Agent: `obsidian-vault-manager.md` - Obsidian vault management specialist using obsidian-cli
- Script: `skills/obsidian-vault-manager/scripts/write-markdown-to-vault.js` - Reliable CLI-based writer for markdown notes into iCloud-synced (or any) vault: chunks payloads under the CLI's ~10KB IPC ceiling, filters banner noise, retries transient errors, verifies via read-back. Must run unsandboxed.

**git-tools** (`plugins/git-tools/`):
- Skill: `git-bisect-debugging` - Systematic workflow for using git bisect to identify which commit introduced a bug. Supports automated test scripts, manual verification, and hybrid approaches with subagent architecture for isolated execution. Integrates with superpowers:systematic-debugging for root cause analysis.

**workflow** (`plugins/workflow/`):
- Command: `/spotlight [on|off|status]` - Spotlight worktree changes into main worktree for testing (like Conductor Spotlight). Merges committed worktree changes via `git merge --no-commit` so you can test in the main worktree's environment, then cleanly abort when done.
- Command: `/review-unstaged` - Review unstaged changes for code quality, style, and potential issues
- Command: `/create-issue [file-path]` - Create a GitHub issue from session context. Auto-discovers superpowers specs/plans, Claude plan files, or generates a conversation summary. Uses `gh` CLI with `--body-file`.
- Command: `/post-pr-comments` - Post inline code review comments from conversation onto the current branch's PR. Writes a comments JSON file, then uses `gh api` to post a pull request review with targeted line comments.
- Command: `/monitor-prs` - Monitor open PRs on a recurring basis: review changes, post validated comments, resolve merge conflicts in worktrees, and surface new reviewer feedback. Designed for use with `/loop` (e.g., `/loop 5m /monitor-prs`).
- Command: `/review-and-fix [pr-number]` - Run a review-and-fix cycle on an existing PR: dispatches a code-review subagent, applies high-confidence fixes (>=80), runs build verification, asks for confirmation, then commits and pushes. Mandatory build gate before commit.
- Command: `/teleport-tmux [session-name]` - Teleport the current Claude session into a new tmux window so you can close the terminal you accidentally started Claude outside of tmux in. macOS can't move a live process's terminal, so it arms a new tmux window to `claude --resume <session-id>` the moment the old process exits (detected via the ancestor PID + `kill -0`), avoiding concurrent transcript writes. Falls back to a pre-typed manual launch if the old PID can't be detected.
- Hook: SessionStart - Emits worktree context (cwd, git toplevel, branch, worktree detection) so subagents stay in the correct working tree and don't accidentally edit the main repo.

**data-tools** (`plugins/data-tools/`):
- Skill: `structured-logging` - Use SQLite for structured data during complex workflows, debugging, and data analysis instead of temp files or stdout parsing. Automatically activates when parsing large output (>100 lines), tracking state across operations, correlating events, or analyzing structured data. Databases stored in `~/.claude-logs/<project-name>.db` persist across sessions.

**tmux-tools** (`plugins/tmux-tools/`):
- Skill: `tmux-aware` - TMUX session awareness and process management. Automatically activates when running in a TMUX session (detected by SessionStart hook). Manages services in dedicated panes within a `claude-controlled` window, captures pane output, detects errors, and finds panes by name.
- Hook: SessionStart - Detects TMUX environment and provides session context

**tailscale-notify** (`plugins/tailscale-notify/`):
- Hook: Notification - Sends Claude Code notifications to a Tailscale endpoint via HTTP POST. Configurable via `TAILSCALE_NOTIFY_URL` environment variable.

## Creating New Plugins

When adding a new plugin to the marketplace:

1. **Create plugin structure:**
   ```
   plugins/<plugin-name>/
   ├── agents/           # Optional: custom agents
   ├── commands/         # Optional: slash commands
   ├── skills/           # Optional: reusable skills (auto-discovered from skills/<name>/SKILL.md)
   └── README.md         # Plugin documentation
   ```

2. **Register in marketplace:**
   - Add plugin entry to `.claude-plugin/marketplace.json` under `plugins` array
   - Minimal required fields: `name`, `source`
   - The `source` path must use relative prefix `./` (e.g., `"./plugins/swift-engineer"`)
   - Plugin metadata is stored in individual plugin directories, not in marketplace.json

3. **Bump plugin version:**
   - Increment `version` in `plugins/<plugin-name>/.claude-plugin/plugin.json`
   - Required for Claude Code to detect new components on reinstall

4. **Update CLAUDE.md:**
   - Add plugin description to "Current Plugins" section
   - Document any special usage instructions

5. **Agent file format** (`agents/<name>.md`):
   ```markdown
   ---
   name: agent-name
   description: Agent description with usage examples
   model: inherit
   color: green
   ---

   [Agent system prompt content]
   ```

6. **Command file format** (`commands/<name>.md`):
   ```markdown
   ---
   description: Brief explanation shown in /help
   argument-hint: [expected-arguments]
   allowed-tools:
     - Tool1
     - Tool2
   ---

   [Command prompt content with $1, $2 for positional args or $ARGUMENTS for all args]
   ```
   - YAML frontmatter is optional but strongly recommended for best practices
   - Use `description` for help text, `argument-hint` for auto-completion, `allowed-tools` for explicit permissions
   - Content is the command's prompt/workflow that executes when invoked

7. **Skill file format** (`skills/<name>.md`):
   ```markdown
   ---
   name: skill-name
   description: Detailed description including when to use this skill and specific triggers
   ---

   [Skill prompt content]
   ```

8. **Skills index format** (`SKILL.md`):
   - Required if plugin contains skills
   - Documents all skills in the plugin
   - Includes usage examples and reference materials

## Installing Plugins from This Marketplace

Add this marketplace to Claude Code:
```
/plugin marketplace add <path-to-this-repo>
```

Install a plugin:
```
/plugin install <plugin-name>@sjungling-plugins
```

## Documentation Reference

Claude Code plugin documentation: https://docs.claude.com/en/docs/claude-code
