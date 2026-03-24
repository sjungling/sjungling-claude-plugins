---
description: Format and lint Swift code using swift-format
argument-hint: "[path]"
allowed-tools:
  - Agent
---

Launch the `swift-lint` agent to format and lint Swift code with context isolation.

Pass the following context to the agent:
- **Plugin root**: `${CLAUDE_PLUGIN_ROOT}`
- **Target path**: `$ARGUMENTS` (or `.` if none provided)
- **Working directory**: the current project root

When the agent completes, report its summary to the user. If it fixed lint issues, mention how many files were modified.
