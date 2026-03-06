---
name: cli-ux-designer
description: This skill should be used when the user asks to "design a CLI", "improve command structure", "format terminal output", "review CLI usability", "design help text", or "add flags and arguments". Automatically activates when designing new CLI tools, improving command interfaces, formatting terminal output, or reviewing CLI usability. Not for GUI/web design, backend APIs, or shell scripting.
---

# CLI Design Guide

Expert CLI design consultant specializing in creating exceptional command-line interfaces. Design, review, and improve CLI tools by applying comprehensive design principles and patterns.

## When NOT to Use This Skill

Do not use this skill for:
- GUI/web interface design
- Backend API design (unless CLI tool interacts with it)
- General UX design outside command-line contexts
- Programming language design

## Core Expertise

Core design principles to apply:

### 1. Reasonable Defaults, Easy Overrides

- Optimize for common use cases while providing customization options
- Use flags to modify default behaviors
- Consider what most users need most often

### 2. Maintain Brand Consistency

- Use platform-specific language and terminology
- Mirror web interface patterns where appropriate
- Apply consistent visual styling (colors, states, syntax)
- Use sentence case, not title case

### 3. Reduce Cognitive Load

- Include confirmation steps for risky operations
- Provide clear headers for context
- Maintain consistent command patterns
- Anticipate user mistakes and next actions
- Design for accessibility

### 4. Terminal-First with Web Integration

- Keep users in terminal when possible
- Provide easy paths to web interface when needed
- Include `--web` flags for browser actions
- Output relevant URLs after operations

## Command Structure Expertise

Ensure commands follow this consistent pattern:

| tool | `<command>` | `<subcommand>` | [value]  | [flags] | [value] |
| ---- | ----------- | -------------- | -------- | ------- | ------- |
| cli  | issue       | view           | 234      | --web   | -       |
| cli  | pr          | create         | -        | --title | "Title" |
| cli  | repo        | fork           | org/repo | --clone | false   |

**Components:**

- **Command**: The object to interact with
- **Subcommand**: The action to take on that object
- **Flag**: Modifiers with long version (`--state`) and often shorthand (`-s`)
- **Values**: IDs, owner/repo pairs, URLs, branch names, file names

**Language Guidelines:**

- Use unambiguous language that can't be confused
- Use shorter phrases when possible and appropriate
- Use flags for modifiers of actions, avoid making modifiers their own commands
- Use understood shorthands to save characters

## Decision Frameworks

Use these when making CLI design choices:

**Flag vs. Subcommand:**
- Flag: modifies HOW a command runs (`--verbose`, `--format json`, `--dry-run`)
- Subcommand: defines WHAT action to take (`issue create`, `pr merge`)
- Rule: if it changes the action, it's a subcommand. If it changes the behavior, it's a flag.

**Interactive vs. Non-interactive:**
- Default to interactive when: user is exploring, multiple choices needed, destructive action requires confirmation
- Default to non-interactive when: command is commonly scripted, output is piped, CI/CD context
- Always: provide `--yes`/`-y` to skip confirmations, `--no-input` to disable all prompts

**Output Format:**
- Human-readable (default): colors, tables, summaries when stdout is a TTY
- Machine-readable (piped): no colors, tab-delimited or JSON when stdout is not a TTY
- Explicit: `--format json|table|csv` flag to override detection

**Error Handling:**
- Exit code 0: success
- Exit code 1: general error
- Exit code 2: usage error (wrong flags/args)
- Always: error message to stderr, suggested fix when possible

## Visual Design System Knowledge

### Typography

- Assume monospace fonts
- Use **bold** for emphasis and repository names
- Create hierarchy with spacing and weight
- No italics (unreliable support)

### Color Usage

Apply the 8 basic ANSI colors:

- **Green**: Success, open states
- **Red**: Failure, closed states
- **Yellow**: Warnings, draft states
- **Blue**: Information, links
- **Cyan**: Branch names, special identifiers
- **Magenta**: Special highlights
- **Gray**: Secondary information, labels
- **White/Default**: Primary text

**Guidelines:**

- Only enhance meaning, never communicate meaning solely through color
- Consider users can customize terminal colors
- Some terminals don't support 256-color sequences reliably

For complete ANSI color codes and escape sequences, see `./references/ansi-color-reference.md`.

### Iconography

Use Unicode symbols consistently:

- `✓` Success
- `✗` Failure
- `!` Alert
- `-` Neutral
- `+` Changes requested

Consider varying Unicode font support across systems.

For a comprehensive list of CLI-friendly Unicode symbols, see `./references/unicode-symbols.md`.

## Component Pattern Expertise

### Lists

- Use tabular format with headers
- Show state through color
- Include relevant contextual information

For a complete list view example, see `./references/examples/list-view-example.txt`.

### Detail Views

- Show comprehensive information
- Indent body content
- Include URLs at bottom

### Prompts

- **Yes/No**: Default in caps, for confirmations
- **Short text**: Single-line input with autocomplete
- **Long text**: Multi-line with editor option
- **Radio select**: Choose one option
- **Multi-select**: Choose multiple options
- Always provide flag alternatives to prompts

For an interactive prompt example, see `./references/examples/interactive-prompt-example.txt`.

### Help Pages

Required sections: Usage, Core commands, Flags, Learn more, Inherited flags
Optional sections: Additional commands, Examples, Arguments, Feedback

For a complete help text example, see `./references/examples/help-text-example.txt`.

### Syntax Conventions

- `<required-args>` in angle brackets
- `[optional-args]` in square brackets
- `{mutually-exclusive}` in braces
- `repeatable...` with ellipsis
- Use dash-case for multi-word variables

## Anti-patterns

Avoid these common CLI design mistakes:

| Anti-pattern | Better Approach |
|-------------|-----------------|
| Deeply nested subcommands (`tool group sub action`) | Max 2 levels: `tool command [flags]` |
| Inconsistent flag naming (`--no-color` vs `--disable-colors`) | Pick one convention and apply everywhere |
| Interactive prompts with no flag alternatives | Every prompt must have a `--flag` equivalent |
| Cryptic error messages ("Error: 1") | Include what went wrong, why, and how to fix |
| Silent failures (exit 0 on error) | Non-zero exit codes for failures, stderr for errors |
| Missing `--help` on subcommands | Every command level should have help |
| Mixing stdout data with status messages | Data to stdout, progress/status to stderr |

## Technical Considerations

### Script Automation Support

- Provide flags for all interactive elements
- Output machine-readable formats when piped
- Use tabs as delimiters for structured data
- Remove colors/formatting in non-terminal output
- Include exact timestamps and full data

### Accessibility

- Use punctuation for screen reader pauses
- Don't rely solely on color for meaning
- Support high contrast and custom themes
- Design for cognitive accessibility

## Success Criteria

Recommendations are successful when:
- Commands follow consistent patterns across the tool
- Help text is clear with useful examples
- Visual hierarchy guides users naturally
- Both interactive and scriptable use cases work
- Accessibility requirements are met
