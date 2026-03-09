---
description: Generate a code walkthrough using showboat
argument-hint: [path-to-source]
model: haiku
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
  - Glob
---

Generate a comprehensive code walkthrough for the source at `$ARGUMENTS` (or the current working directory if no path is given).

## What is Showboat

Showboat is a CLI tool for creating structured, readable code walkthroughs as markdown documents. It provides two core commands:
- `showboat note "text"` -- Add commentary and narrative prose between code snippets
- `showboat exec "command"` -- Execute a shell command and capture its output inline

Install via `uvx showboat --help` to verify availability. If showboat is not installed, fall back to writing the walkthrough directly using the Write tool in standard markdown format.

For the visual workflow diagram, see `./references/walkthrough-workflow.mmd`.

## Walkthrough Structure

Produce a walkthrough that follows this structure:

1. **Introduction** -- Brief overview of what the codebase does, its purpose, and key technologies
2. **Entry point** -- Identify and explain the main entry point (e.g., `main.swift`, `index.ts`, `app.py`)
3. **Module flow** -- Walk through each major module or component in logical order, explaining how data and control flow between them
4. **Key concepts** -- Highlight important design patterns, architecture decisions, or non-obvious implementation details
5. **Configuration and dependencies** -- Explain build configuration, dependency management, and environment setup
6. **Summary** -- Recap the overall architecture and suggest where a new contributor should start

## Workflow

1. Read the source at the given path to understand the codebase structure
2. Plan a linear walkthrough that explains how the code works in a logical reading order
3. Check if showboat is available: `command -v showboat >/dev/null 2>&1 || uvx showboat --help 2>/dev/null`
4. If showboat is available:
   - Create a `walkthrough.md` file in the repo root
   - Use `showboat note` for commentary and narrative
   - Use `showboat exec` with `sed`, `grep`, `cat`, or similar tools to include relevant code snippets
5. If showboat is NOT available:
   - Write the walkthrough directly to `walkthrough.md` using the Write tool
   - Include code snippets using standard markdown fenced code blocks
   - Read relevant source files and extract key sections inline

## Output Quality Criteria

- Every code snippet must have surrounding context explaining what it does and why
- Avoid dumping entire files; extract the relevant 5-30 lines that illustrate the point
- Use consistent heading levels (h2 for major sections, h3 for subsections)
- Include file paths in code block headers so the reader knows where to find the source
- The walkthrough should be understandable to someone unfamiliar with the codebase
