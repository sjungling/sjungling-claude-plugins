# tmux-tools

TMUX session awareness and process management for Claude Code.

## Features

- **Automatic detection**: SessionStart hook detects if running in TMUX
- **Dedicated workspace**: All Claude-created panes go in a `claude-controlled` window
- **Service management**: Start, stop, and restart services in isolated panes
- **Output capture**: Read pane output and detect errors automatically
- **Named panes**: Find and interact with panes by name

## Components

### SessionStart Hook

Runs automatically when a Claude Code session starts. Detects TMUX and provides context:

```
TMUX Session Detected:
- Current: window "dev" (#2), pane 0
- Claude-controlled window: exists (#4)
- Windows: [0:main] [1:logs] [2:dev] [4:claude-controlled]
```

### tmux-aware Skill

Provides workflow guidance for:

- Starting services in new panes
- Finding existing panes by name
- Capturing and analyzing output
- Error detection after commands

## Usage

Once installed, Claude automatically becomes TMUX-aware. Examples:

- "Start the API server" → Creates pane in claude-controlled window, runs command
- "Check the redis logs" → Finds redis pane, captures recent output
- "Restart the dev server" → Finds pane, sends Ctrl+C, restarts

## Naming Convention

- **Window**: `claude-controlled` (dedicated workspace for Claude)
- **Panes**: Named after service (e.g., `api-server`, `redis`, `postgres`)

## Installation

```
/plugin install tmux-tools@sjungling-plugins
```

## Requirements

- TMUX 3.0+ (uses pane titles feature)
- Running Claude Code inside a TMUX session
