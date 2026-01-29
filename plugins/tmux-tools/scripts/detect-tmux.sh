#!/bin/bash
# Detect TMUX session and output context for Claude

# Check if running in TMUX
if [ -z "$TMUX" ]; then
    echo "Not running in TMUX session."
    exit 0
fi

# Get current window and pane info
CURRENT_WINDOW=$(tmux display-message -p '#{window_index}:#{window_name}')
CURRENT_PANE=$(tmux display-message -p '#{pane_index}')

# Check if claude-controlled window exists
CLAUDE_WINDOW=$(tmux list-windows -F '#{window_index}:#{window_name}' 2>/dev/null | grep ':claude-controlled$' || echo "")

# List all windows
ALL_WINDOWS=$(tmux list-windows -F '[#{window_index}:#{window_name}]' 2>/dev/null | tr '\n' ' ')

# Output context
echo "TMUX Session Detected:"
echo "- Current: window \"$(echo $CURRENT_WINDOW | cut -d: -f2)\" (#$(echo $CURRENT_WINDOW | cut -d: -f1)), pane $CURRENT_PANE"

if [ -n "$CLAUDE_WINDOW" ]; then
    CLAUDE_WINDOW_IDX=$(echo "$CLAUDE_WINDOW" | cut -d: -f1)
    echo "- Claude-controlled window: exists (#$CLAUDE_WINDOW_IDX)"
else
    echo "- Claude-controlled window: not found"
fi

echo "- Windows: $ALL_WINDOWS"
