---
description: Format and lint Swift code using swift-format
allowed-tools:
  - Task
---

To keep the codebase clean, execute the following workflow using subagents for context isolation:

**IMPORTANT**: Launch TWO separate subagents sequentially. Do NOT run them in parallel. Formatting often fixes issues that would be flagged by the linter, so linting must happen AFTER formatting is complete.

1. First, launch a general-purpose subagent to run `swift-format format --in-place --recursive` to format all Swift code. Wait for it to complete.

2. Then, launch a second general-purpose subagent to run `swift-format lint --recursive` on the project and resolve all remaining lint issues until clean.

Use the Task tool for both steps to keep swift-format output isolated from the main agent context.

Report a brief summary of results after all steps are complete.
