# TMUX Command Reference

## Detection

```bash
# Check if running in TMUX (already done by SessionStart hook)
echo $TMUX
```

## Window Management

```bash
# List windows
tmux list-windows -F "#{window_index}:#{window_name}"

# Create claude-controlled window
tmux new-window -n "claude-controlled"
```

## Pane Management

```bash
# List all panes with titles
tmux list-panes -a -F "#{window_name}:#{pane_index}:#{pane_title}"

# Split pane (vertical)
tmux split-window -t claude-controlled -v

# Name a pane
tmux select-pane -t "target" -T "pane-name"
```

## Sending Commands

```bash
# Send command to pane
tmux send-keys -t "target" "command here" Enter

# Send Ctrl+C (stop process)
tmux send-keys -t "target" C-c
```

## Capturing Output

```bash
# Last 50 lines
tmux capture-pane -t "target" -p -S -50

# Last 100 lines (for more context)
tmux capture-pane -t "target" -p -S -100
```

## Target Syntax

TMUX targets use the format: `session:window.pane`

- `claude-controlled:0` -- First pane in claude-controlled window
- `claude-controlled:0.api-server` -- Pane titled "api-server" in claude-controlled
- Just the pane title works if unique: `api-server`

## Layout

```bash
# Rebalance pane layout
tmux select-layout -t claude-controlled even-vertical
```

## Cleanup

```bash
# Kill the claude-controlled window
tmux kill-window -t claude-controlled
```
