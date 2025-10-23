---
description: Review a Claude Code skill and recommend improvements to conform to best practices
args:
  - name: skill-path
    description: Path to the directory containing the skill to review
allowed-tools:
  - Task
---

Launch a subagent using the Task tool. The subagent should use the Skill tool to invoke the `claude:builder` skill.

Analyze the Claude Code skill located at: **$1**

The subagent should read all files in the skill directory including SKILL.md, reference materials, templates, and scripts. Review the skill for conformance to best practices and provide actionable recommendations for improvements.

Focus on:

- Frontmatter quality and completeness (name, description fields)
- Description with clear activation triggers and technology keywords
- Prompt clarity, structure, and effectiveness
- Proper use of bundled resources and progressive disclosure
- Examples and usage guidance (when to use and when NOT to use)
- Tool specifications and usage patterns
- Overall adherence to Claude Code skill conventions

Provide prioritized, specific recommendations (critical, important, nice-to-have) with concrete examples. Highlight what the skill does well and offer to implement improvements if requested.
