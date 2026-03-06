---
name: tmux-aware
description: This skill should be used when the user asks to "start a service in tmux", "check tmux pane output", "manage background processes", or "run a server in a pane". Automatically activates when running in a TMUX session (detected by SessionStart hook). Not for one-off commands that do not need a persistent pane.
---

# TMUX-Aware Process Management

## Overview

When running inside a TMUX session, manage services in dedicated panes without cluttering the current view. All Claude-created panes go in a dedicated "claude-controlled" window.

## Key Principles

1. **Never clutter the current window** - Always create panes in the "claude-controlled" window
2. **Find panes by name** - Search for existing panes/windows by title, not by process
3. **Verify commands worked** - Capture output after sending commands to detect errors
4. **Ask when uncertain** - If a pane can't be found by name, list options and ask the user

## Starting a Service

When the user asks to start a service (e.g., "start the API server"):

### Step 1: Check for claude-controlled window

```bash
# List windows, look for claude-controlled
tmux list-windows -F '#{window_index}:#{window_name}' | grep ':claude-controlled$'
```

### Step 2: Create window if needed

```bash
# Create the claude-controlled window
tmux new-window -n "claude-controlled"
```

### Step 3: Create a named pane for the service

```bash
# If claude-controlled window already has panes, split it
tmux split-window -t claude-controlled -v

# Name the pane after the service
tmux select-pane -t claude-controlled -T "api-server"
```

### Step 4: Send the start command

```bash
tmux send-keys -t "claude-controlled:0.api-server" "npm run dev" Enter
```

### Step 5: Verify it started (capture output after brief delay)

```bash
sleep 2
tmux capture-pane -t "claude-controlled:0.api-server" -p -S -20
```

Check the output for errors. Report success or detected issues.

## Naming Convention

- **Window:** `claude-controlled` (all Claude-created panes go here)
- **Pane titles:** Lowercase, hyphenated, match the service (e.g., `api-server`, `redis`, `vite-dev`, `postgres`)

## Finding Existing Panes

When the user asks to interact with a process (e.g., "check the redis logs"):

### Step 1: List panes with names

```bash
tmux list-panes -a -F '#{window_name}:#{pane_index}:#{pane_title}'
```

### Step 2: Search for match

Look for exact or partial match (e.g., "redis" matches pane titled "redis" or "redis-server").

### Step 3: If found

Interact with it:

```bash
# Capture output
tmux capture-pane -t "window:pane" -p -S -50

# Send command (e.g., restart)
tmux send-keys -t "window:pane" C-c  # Stop first
tmux send-keys -t "window:pane" "redis-server" Enter  # Restart
```

### Step 4: If not found

List available panes and ask:

> I couldn't find a pane named 'redis'. Here's what I see:
> - [0:main] pane 0: "zsh"
> - [1:dev] pane 0: "vim"
> - [2:claude-controlled] pane 0: "api-server"
>
> Which one should I use, or should I create a new one?

## Capturing Output

Use `capture-pane` to read recent output:

```bash
# Last 50 lines
tmux capture-pane -t "pane-target" -p -S -50

# Last 100 lines (for more context)
tmux capture-pane -t "pane-target" -p -S -100
```

## Error Detection

After sending commands, capture output and look for common error patterns:

- `Error:`, `ERROR`, `error:`
- `Exception`, `exception`
- `Failed`, `FAILED`, `failed`
- `Cannot`, `cannot`
- Exit codes in prompts
- Stack traces

Report issues proactively: "Started the server but detected an error: [snippet]"

## Stopping a Service

```bash
# Send Ctrl+C to stop
tmux send-keys -t "pane-target" C-c

# Verify it stopped
sleep 1
tmux capture-pane -t "pane-target" -p -S -10
```

## Multiple Services

When running multiple services:
- Split panes vertically (`-v`) for side-by-side logs
- Name each pane after its service for easy targeting
- Use `tmux select-layout -t claude-controlled even-vertical` to rebalance
- If more than 3 services, consider separate windows instead of more pane splits

For the full command reference (window/pane management, sending commands, capturing output, target syntax), see `./references/commands.md`.

## Example Workflow

User: "Start a Redis server"

1. Check for claude-controlled window (exists)
2. Create new pane: `tmux split-window -t claude-controlled -v`
3. Name it: `tmux select-pane -T "redis"`
4. Start Redis: `tmux send-keys -t "claude-controlled:redis" "redis-server" Enter`
5. Wait and capture: `sleep 2 && tmux capture-pane -t "claude-controlled:redis" -p -S -20`
6. Report: "Started Redis server in pane 'redis' (claude-controlled window). Server is ready on port 6379."

User: "Check if Redis is still running"

1. List panes, find "redis"
2. Capture output: `tmux capture-pane -t "claude-controlled:redis" -p -S -30`
3. Report status based on output

## When NOT to Use

- **One-off commands** that don't need a persistent pane (e.g., `git status`, `ls`)
- **User's existing layout** - don't create panes in the user's current window
- **Non-tmux environments** - if tmux detection fails, fall back to standard Bash
- **Quick checks** where capturing output with Bash tool is sufficient

## Cleanup

When the user's task is complete:

- **Don't auto-kill panes** - the user may want to keep services running
- **Offer cleanup** if asked: `tmux kill-window -t claude-controlled`
- **Report what's running**: List active panes so the user can decide
- If you started a service and the task failed, mention the pane is still running
