#!/bin/bash
# Opens plan files in Obsidian when Claude writes to ~/.claude/plans/
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if [[ -n "$file_path" && "$file_path" == *"/.claude/plans/"* ]]; then
  open "obsidian://open?path=${file_path}" 2>/dev/null
fi
