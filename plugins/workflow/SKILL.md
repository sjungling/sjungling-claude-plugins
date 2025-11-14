# Workflow Plugin Skills

This plugin provides skills for systematic debugging and development workflows.

## Available Skills

### git-bisect-debugging

**Location:** `skills/git-bisect-debugging/SKILL.md`

**When to use:** When debugging regressions or identifying which commit introduced a bug. Provides systematic workflow for git bisect with automated test scripts, manual verification, or hybrid approaches.

**Key features:**
- 4-phase workflow: Setup → Strategy Selection → Execution → Analysis
- Subagent architecture for isolated commit verification
- Three approaches: automated (test scripts), manual (user verification), hybrid (both)
- Integrates with superpowers:systematic-debugging for root cause analysis
- Safety checks and error handling
- Progress tracking with TodoWrite

**Activation triggers:**
- User mentions "git bisect"
- Finding "which commit" introduced a bug/regression
- Debugging historical issues where tests/behavior changed
- superpowers:systematic-debugging skill invokes it for historical bugs
- User asks "when did this break" or similar temporal debugging questions

**Example usage:**
```
User: "The login test started failing sometime in the last 50 commits."
Claude: "I'm using git-bisect-debugging to find which commit introduced this issue."
[Skill executes 4-phase workflow to identify first bad commit]
```

**Integration:**
- Can be called BY superpowers:systematic-debugging when debugging historical issues
- Calls superpowers:systematic-debugging in Phase 4 for root cause analysis

## References

For more information on creating skills for Claude Code, see:
- [Claude Code Plugin Documentation](https://docs.claude.com/en/docs/claude-code)
- Design document: `docs/plans/2025-11-13-git-bisect-skill-design.md`
