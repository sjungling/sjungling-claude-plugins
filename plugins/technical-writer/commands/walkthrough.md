---
description: Generate a code walkthrough using showboat
argument-hint: [path-to-source]
allowed-tools:
  - Agent
---

Launch the `walkthrough` agent to generate a comprehensive code walkthrough with context isolation.

Pass the following context to the agent:
- **Plugin root**: `${CLAUDE_PLUGIN_ROOT}`
- **Target path**: `$ARGUMENTS` (or the current working directory if none provided)
- **Working directory**: the current project root

When the agent completes, report its summary to the user including the output file path and what was covered.
