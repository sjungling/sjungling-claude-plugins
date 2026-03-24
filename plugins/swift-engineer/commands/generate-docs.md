---
description: Build symbol graph documentation for the current Xcode project
argument-hint: "[scheme]"
allowed-tools:
  - Agent
---

Launch the `generate-docs` agent to build symbol graph documentation with context isolation.

Pass the following context to the agent:
- **Plugin root**: `${CLAUDE_PLUGIN_ROOT}`
- **Scheme argument**: `$ARGUMENTS` (if provided)
- **Working directory**: the current project root

When the agent completes, report its summary to the user including documented modules, counts, and what files were updated.
