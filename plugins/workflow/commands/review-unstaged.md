---
description: Review unstaged changes for code quality, style, and potential issues
allowed-tools:
  - Bash(git:*)
  - Read
  - Grep
  - Glob
  - Task
---

Review the unstaged changes in this repository.

## Steps

1. **Get unstaged diff**:
   ```bash
   git diff
   ```

2. **Analyze the changes** for:
   - Code quality issues
   - Style inconsistencies
   - Potential bugs or logic errors
   - Missing error handling
   - Opportunities for simplification

3. **Read full context** of modified files if needed to understand the changes better

4. **Provide feedback** organized by:
   - **Issues**: Problems that should be fixed before committing
   - **Suggestions**: Improvements that would be nice to have
   - **Simplifications**: Code that could be cleaner or more concise

## Code Simplification

If the `code-simplifier:code-simplifier` agent is available, consider using it via the Task tool to get additional recommendations for simplifying complex or verbose code sections.

## Output Format

Provide a concise review with actionable feedback. Reference specific line numbers and file paths when possible.
