---
description: List all available Claude Code skills in a formatted table
allowed-tools:
  - Bash
  - Read
  - Glob
---

List all available Claude Code skills and display them in a readable format optimized for terminal viewing.

**Group skills by plugin source** to keep related skills together. Use this format:

```
Available Skills:

Plugin: {plugin-source}

{skill-name}
  Description: {description}

{skill-name-2}
  Description: {description}

Plugin: {another-plugin-source}

{skill-name-3}
  Description: {description}
```

**Important formatting rules:**
- Group all skills from the same plugin/marketplace together
- Show "Plugin: {source}" header once per group
- Under each skill, show ONLY the skill name and description (don't repeat the plugin source)
- If a skill appears multiple times (e.g., "2 instances"), note that in the skill name line
- Keep full descriptions (no truncation) - natural line wrapping is fine
- Add blank lines between plugin groups for visual separation

At the end, include usage instructions:
```
Usage:
  Invoke with: Skill tool using skill name
  Example: ui-engineering:senior-ui-engineer
```
