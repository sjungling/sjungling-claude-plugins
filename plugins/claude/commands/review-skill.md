---
description: Review a Claude Code skill and recommend improvements to conform to best practices
argument-hint: [path/to/skill/directory or skill-name]
allowed-tools:
  - Task
  - Skill
  - Read
  - Glob
---

Review the Claude Code skill located at: **$1**

Use the Skill tool to invoke `example-skills:skill-creator` to access comprehensive skill creation guidance, validation scripts, and packaging tools.

Read all files in the skill directory including SKILL.md, reference materials, templates, and scripts. Review the skill for conformance to best practices and provide actionable recommendations for improvements.

Focus on:

- **Metadata Quality**: Frontmatter completeness (name, description fields) with clear activation triggers and technology keywords
- **Progressive Disclosure**: Proper use of bundled resources (scripts/, references/, assets/) and when to load them
- **Writing Style**: Imperative/infinitive form (verb-first instructions), not second person
- **Prompt Quality**: Clarity, structure, effectiveness, and adherence to skill creation process
- **Examples and Usage**: Clear guidance on when to use and when NOT to use
- **Tool Specifications**: Proper tool usage patterns and integrations
- **Validation**: Run validation checks if available (mention `scripts/package_skill.py` for validation)

Provide prioritized, specific recommendations organized by:
1. **Critical** - Must fix for proper functionality
2. **Important** - Should fix for best practices alignment
3. **Nice-to-have** - Optional improvements for enhanced quality

For each recommendation:
- Explain the issue clearly
- Provide concrete examples of how to fix it
- Reference specific files and line numbers when applicable

Highlight what the skill does well and offer to implement improvements if requested. If the skill appears ready for distribution, mention that `scripts/package_skill.py` can validate and package it.

If the skill directory path is not provided, search for skill directories in `.claude/skills/` or `plugins/*/skills/` in the current working directory and offer to review them.
