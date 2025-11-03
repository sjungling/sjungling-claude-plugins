---
description: Review a Claude Code slash command and recommend improvements based on best practices
argument-hint: [path-to-command.md]
allowed-tools:
  - Read
  - WebFetch
  - Glob
---

Review the Claude Code slash command located at: **$1**

First, fetch the official documentation from https://docs.claude.com/en/docs/claude-code/slash-commands.md to understand current best practices.

Then read the command file and analyze it for conformance to best practices. Provide actionable recommendations for improvements.

Focus on:

- **Frontmatter Quality**:
  - Presence of `description` field (clear, concise explanation)
  - Proper use of `argument-hint` for auto-completion guidance
  - `allowed-tools` specification (explicit permissions vs. inherited)
  - `model` specification if needed for specific Claude models
  - `disable-model-invocation` if command shouldn't be auto-invoked

- **Argument Handling**:
  - Appropriate use of `$1`, `$2` positional parameters vs `$ARGUMENTS`
  - Clear documentation of expected arguments in the prompt
  - Sensible defaults for optional arguments
  - Validation logic for required arguments

- **Command Focus**:
  - Single, well-defined purpose (not trying to do too much)
  - Clear use case that's distinct from skills/agents
  - Appropriate for "simple prompt snippets used often"

- **Writing Style**:
  - Clear, actionable instructions
  - Proper use of file references with '@' prefix if needed (e.g., @path/to/file.md)
  - Proper use of bash execution with '!' prefix if needed
  - Examples provided where helpful

- **Tool Permissions**:
  - 'allowed-tools' explicitly declared in frontmatter
  - Only necessary tools included
  - Bash commands specific rather than broad if using '!' prefix

- **Documentation Quality**:
  - Description field matches actual command behavior
  - Argument expectations clearly documented
  - Usage examples provided where helpful

Provide prioritized, specific recommendations organized by:
1. **Critical** - Must fix for proper functionality or security
2. **Important** - Should fix for best practices alignment
3. **Nice-to-have** - Optional improvements for enhanced quality

For each recommendation:
- Explain the issue clearly with reference to official documentation
- Provide concrete examples of how to fix it
- Reference specific lines in the command file when applicable
- Show before/after examples for clarity

Highlight what the command does well and offer to implement improvements if requested.

If the command file path is not provided, search for `.md` files in `.claude/commands/` in the current working directory and offer to review them.
