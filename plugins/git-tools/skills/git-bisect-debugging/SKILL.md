---
name: git-bisect-debugging
description: This skill should be used when the user asks to "find which commit broke this", "debug a regression", "bisect to find the bug", or says "this used to work". Automatically activates for performance regressions, test failures that appeared recently, or any issue known to have worked at a previous commit. Can be invoked from systematic-debugging or used standalone. Not for general debugging without a known-good commit or regression history.
---

# Git Bisect Debugging

## Overview

Systematically identify which commit introduced a bug or regression using git bisect. Binary search through commit history to find the exact commit that introduced the issue. Main agent orchestrates, subagents execute verification at each step.

**Announce at start:** "I'm using git-bisect-debugging to find which commit introduced this issue."

## Quick Reference

| Phase | Key Activities | Output |
|-------|---------------|--------|
| **1. Setup & Verification** | Identify good/bad commits, verify clean state | Confirmed commit range |
| **2. Strategy Selection** | Choose automated/manual/hybrid approach | Test script or verification steps |
| **3. Execution** | Run bisect with subagents | First bad commit hash |
| **4. Analysis & Handoff** | Show commit details, analyze root cause | Root cause understanding |

## Limitations (By Design)

This skill focuses on straightforward scenarios. It does NOT handle:

- Complex merge commit issues (would need `--first-parent`)
- Flaky/intermittent test failures (would need statistical approaches)
- Build system failures across many commits (would need advanced skip strategies)

For these scenarios, manual git bisect with user guidance is recommended.

## Critical Rules

These are non-negotiable. No exceptions for time pressure, production incidents, or "simple" cases:

1. **ANNOUNCE** skill usage at start
2. **CREATE TodoWrite checklist** immediately (copy from "The Process" below)
3. **VERIFY safety checks** in Phase 1 -- working directory must be clean, good commit must be verified good, bad commit must be verified bad. If any check fails, abort and fix before proceeding.
4. **USE AskUserQuestion** for strategy selection in Phase 2 -- present all 3 approaches, do not default to automated without asking
5. **LAUNCH subagents** for verification in Phase 3 -- never run verification in main context; each commit tested in isolated subagent via Task tool
6. **HANDOFF to systematic-debugging** in Phase 4 -- after finding the bad commit, investigate root cause, not just what changed

**If tempted to skip any rule:** STOP. Follow the 4-phase workflow exactly. Skipping safety checks, skipping TodoWrite, defaulting to automated, running tests in main context, or stopping after finding the commit are all violations.

## The Process

Copy this checklist to track progress:

```
Git Bisect Progress:
- [ ] Phase 1: Setup & Verification (good/bad commits identified)
- [ ] Phase 2: Strategy Selection (approach chosen, script ready)
- [ ] Phase 3: Execution (first bad commit found)
- [ ] Phase 4: Analysis & Handoff (root cause investigation complete)
```

### Phase 1: Setup & Verification

**Purpose:** Ensure git bisect is appropriate and safe to run.

**Steps:**

1. **Verify prerequisites:**
   - Verify the current directory is a git repository
   - Verify working directory is clean (`git status`)
   - If uncommitted changes exist, abort and ask user to commit or stash

2. **Identify commit range:**
   - Ask user for **good commit** (where it worked)
     - Suggestions: last release tag, last passing CI, commit from when it worked
     - Commands to help: `git log --oneline`, `git tag`, `git log --since="last week"`
   - Ask user for **bad commit** (where it is broken)
     - Usually: `HEAD` or a specific commit where issue is confirmed
   - Calculate estimated steps: ~log2(commits between good and bad)

3. **Verify the range:**
   - Checkout bad commit and verify issue exists
   - Checkout good commit and verify issue does not exist
   - If reversed, offer to swap them
   - Return to original branch/commit

4. **Safety checks:**
   - Warn if range is >1000 commits (ask for confirmation)
   - Verify good commit is ancestor of bad commit
   - Note current branch/commit for cleanup later

**Output:** Confirmed good commit hash, bad commit hash, estimated steps

### Phase 2: Strategy Selection

**Purpose:** Choose the most efficient bisect approach.

**Assessment:** Determine whether an automated test script can deterministically identify good vs bad.

**MANDATORY: Use AskUserQuestion** to present three approaches:
1. **Automated** -- test script runs automatically (best for: test failures, crashes, deterministic behavior)
2. **Manual** -- user verifies each commit (best for: UI/UX changes, subjective issues)
3. **Hybrid** -- script + manual confirmation (best for: mostly automated with judgment calls)

**If automated or hybrid selected:**

Write a test script following the template at `./scripts/bisect-test-template.sh`. Key guidelines:
- Make it deterministic (no random data, use fixed seeds)
- Make it fast (runs ~log2(N) times)
- Exit codes: 0 = good, 1 = bad, 125 = skip
- Include build/setup (each commit might need different deps)
- Test ONE specific thing, not the entire suite

**If manual selected:**

Write specific verification steps for the subagent with concrete actions and expected outcomes. Avoid vague instructions like "see if it works."

**Output:** Selected approach, test script or verification steps

### Phase 3: Execution

**Architecture:** Main agent orchestrates bisect, subagents verify each commit in isolated context.

For detailed subagent prompt templates and error handling patterns, see `./references/execution-patterns.md`.

**Execution summary:**

1. Run `git bisect start <bad> <good>`
2. Loop: launch subagent via Task tool to verify current commit -> report good/bad/skip -> run `git bisect good|bad|skip` -> update progress
3. Run `git bisect reset` to cleanup
4. Return to original branch/commit

**Output:** First bad commit hash, bisect log showing the path taken

### Phase 4: Analysis & Handoff

**Purpose:** Present findings and analyze root cause.

1. **Present the identified commit:**
   ```
   Found first bad commit: <hash>
   Author: <author>
   Date: <date>
   <commit message>
   Files changed: <list from git show --stat>
   ```

2. **Show how to view details:**
   ```
   View full diff: git show <hash>
   View file at that commit: git show <hash>:<file>
   ```

3. **Handoff to root cause analysis:**
   - Announce: "Now that the breaking commit is identified at `<hash>`, using systematic-debugging to analyze why this change caused the issue."
   - Use superpowers:systematic-debugging skill to investigate
   - Focus analysis on the changes in the bad commit
   - Identify the specific line/change that caused the issue
   - Explain WHY it broke (not just WHAT changed)

**Output:** Root cause understanding of why the commit broke functionality

## Additional Resources

- **`./references/execution-patterns.md`** -- Subagent prompt templates and error handling
- **`./references/troubleshooting.md`** -- Common patterns, troubleshooting, and example workflows
- **`./scripts/bisect-test-template.sh`** -- Test script template for automated bisect
