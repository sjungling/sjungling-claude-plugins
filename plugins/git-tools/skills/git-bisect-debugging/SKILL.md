---
name: git-bisect-debugging
description: Use when debugging regressions, finding which commit introduced a bug, or answering "when did this break" / "this used to work" questions. Provides systematic git bisect workflow with automated test scripts, manual verification, or hybrid approaches. Activates for performance regressions, test failures that appeared recently, or any issue known to have worked at a previous commit. Can be invoked from systematic-debugging or used standalone. Not for general debugging without a known-good commit or regression history.
---

# Git Bisect Debugging

## Overview

Systematically identify which commit introduced a bug or regression using git bisect. This skill provides a structured workflow for automated, manual, and hybrid bisect approaches.

**Core principle:** Binary search through commit history to find the exact commit that introduced the issue. Main agent orchestrates, subagents execute verification at each step.

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

## MANDATORY Requirements

These are **non-negotiable**. No exceptions for time pressure, production incidents, or "simple" cases:

1. **ANNOUNCE skill usage** at start:
   ```
   "I'm using git-bisect-debugging to find which commit introduced this issue."
   ```

2. **CREATE TodoWrite checklist** immediately (before Phase 1):
   - Copy the exact checklist from "The Process" section below
   - Update status as you progress through phases
   - Mark phases complete ONLY when finished

3. **VERIFY safety checks** (Phase 1 - no skipping):
   - Working directory MUST be clean (`git status`)
   - Good commit MUST be verified (actually good)
   - Bad commit MUST be verified (actually bad)
   - If ANY check fails -> abort and fix before proceeding

4. **USE AskUserQuestion** for strategy selection (Phase 2):
   - Present all 3 approaches (automated, manual, hybrid)
   - Don't default to automated without asking
   - User must explicitly choose

5. **LAUNCH subagents** for verification (Phase 3):
   - Main agent: orchestrates git bisect state
   - Subagents: execute verification at each commit (via Task tool)
   - NEVER run verification in main context
   - Each commit tested in isolated subagent

6. **HANDOFF to systematic-debugging** (Phase 4):
   - After finding bad commit, announce handoff
   - Use superpowers:systematic-debugging skill
   - Investigate root cause, not just WHAT changed

## Red Flags - STOP and Follow the Skill

If you catch yourself thinking ANY of these, you're about to violate the skill:

- "User is in a hurry, I'll skip safety checks" -> NO. Run all safety checks.
- "This is simple, no need for TodoWrite" -> NO. Create the checklist.
- "I'll just use automated approach" -> NO. Use AskUserQuestion.
- "I'll run the test in my context" -> NO. Launch subagent.
- "Found the commit, that's enough" -> NO. Handoff to systematic-debugging.
- "Working directory looks clean" -> NO. Run `git status` to verify.
- "I'll verify good/bad commits later" -> NO. Verify BEFORE starting bisect.

**All of these mean: STOP. Follow the 4-phase workflow exactly.**

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
   - Check we're in a git repository
   - Verify working directory is clean (`git status`)
   - If uncommitted changes exist, abort and ask user to commit or stash

2. **Identify commit range:**
   - Ask user for **good commit** (where it worked)
     - Suggestions: last release tag, last passing CI, commit from when it worked
     - Commands to help: `git log --oneline`, `git tag`, `git log --since="last week"`
   - Ask user for **bad commit** (where it's broken)
     - Usually: `HEAD` or a specific commit where issue confirmed
   - Calculate estimated steps: ~log2(commits between good and bad)

3. **Verify the range:**
   - Checkout bad commit and verify issue exists
   - Checkout good commit and verify issue doesn't exist
   - If reversed, offer to swap them
   - Return to original branch/commit

4. **Safety checks:**
   - Warn if range is >1000 commits (ask for confirmation)
   - Verify good commit is ancestor of bad commit
   - Note current branch/commit for cleanup later

**Output:** Confirmed good commit hash, bad commit hash, estimated steps

### Phase 2: Strategy Selection

**Purpose:** Choose the most efficient bisect approach.

**Assessment:** Can we write an automated test script that deterministically identifies good vs bad?

**MANDATORY: Use AskUserQuestion** to present three approaches:
1. **Automated** - test script runs automatically (best for: test failures, crashes, deterministic behavior)
2. **Manual** - user verifies each commit (best for: UI/UX changes, subjective issues)
3. **Hybrid** - script + manual confirmation (best for: mostly automated with judgment calls)

**If automated or hybrid selected:**

Write test script following this template:

```bash
#!/bin/bash
# Exit codes: 0 = good, 1 = bad, 125 = skip (can't test)

# Setup/build (required for each commit)
npm install --silent 2>/dev/null || exit 125

# Run the actual test
npm test -- path/to/specific-test.js
exit $?
```

**Script guidelines:**
- Make it **deterministic** (no random data, use fixed seeds)
- Make it **fast** (runs ~log2(N) times)
- **Exit codes:** 0 = good, 1 = bad, 125 = skip
- Include build/setup (each commit might need different deps)
- Test ONE specific thing, not entire suite
- Make it **read-only** (no data modification)

**If manual selected:**

Write specific verification steps for subagent:

**Good example:**
```
1. Run `npm start`
2. Open browser to http://localhost:3000
3. Click the "Login" button
4. Check if it redirects to /dashboard
5. Respond 'good' if redirect happens, 'bad' if it doesn't
```

**Bad example:**
```
See if the login works
```

**Output:** Selected approach, test script (if automated/hybrid), or verification steps (if manual)

### Phase 3: Execution

**Architecture:** Main agent orchestrates bisect, subagents verify each commit in isolated context.

**Main agent responsibilities:**
- Manage git bisect state (`start`, `good`, `bad`, `reset`)
- Track progress and communicate remaining steps
- Launch subagents for verification
- Handle errors and cleanup

**Subagent responsibilities:**
- Execute verification in clean context (no bleeding between commits)
- Report result: "good", "bad", or "skip"
- Provide brief reasoning for result

**Execution flow:**

1. **Main agent:** Run `git bisect start <bad> <good>`

2. **Loop until bisect completes:**

   a. Git checks out a commit to test

   b. **Main agent launches subagent** using Task tool:

   **For automated:**
   ```
   Prompt: "Run this test script and report the result:

   <script content>

   Report 'good' if exit code is 0, 'bad' if exit code is 1, 'skip' if exit code is 125.
   Include the output of the script in your response."
   ```

   **For manual:**
   ```
   Prompt: "We're testing commit <hash> (<message>).

   Follow these verification steps:
   <verification steps>

   Report 'good' if the issue doesn't exist, 'bad' if it does exist.
   Explain what you observed."
   ```

   **For hybrid:**
   ```
   Prompt: "Run this test script:

   <script content>

   If exit code is 0 or 1, report that result.
   If exit code is 125 or script is ambiguous, perform manual verification:
   <verification steps>

   Report 'good', 'bad', or 'skip' with explanation."
   ```

   c. **Subagent returns:** Result ("good", "bad", or "skip") with explanation

   d. **Main agent:** Run `git bisect good|bad|skip` based on result

   e. **Main agent:** Update progress
      - Show commit that was tested and result
      - Calculate remaining steps: `git bisect log | grep "# .*step" | tail -1`
      - Example: "Tested commit abc123 (bad). ~4 steps remaining."

   f. Repeat until git bisect identifies first bad commit

3. **Main agent:** Run `git bisect reset` to cleanup

4. **Main agent:** Return to original branch/commit

**Error handling during execution:**

- **Subagent timeout/error:** Allow user to manually mark as "skip"
- **Build failures:** Use `git bisect skip`
- **Too many skips (>5):** Suggest manual investigation, show untestable commits
- **Bisect interrupted:** Ensure `git bisect reset` runs in cleanup
- **Good/bad reversed:** If all results seem opposite, offer to restart with swapped inputs
- **No bad commit found:** Verify bad commit is actually bad, check if issue is environmental
- **Cleanup (always):** Run `git bisect reset` on success or failure, return to original branch

**Output:** First bad commit hash, bisect log showing the path taken

### Phase 4: Analysis & Handoff

**Purpose:** Present findings and analyze root cause.

**Steps:**

1. **Present the identified commit:**
   ```
   Found first bad commit: <hash>

   Author: <author>
   Date: <date>

   <commit message>

   Files changed:
   <list of files from git show --stat>
   ```

2. **Show how to view details:**
   ```
   View full diff: git show <hash>
   View file at that commit: git show <hash>:<file>
   ```

3. **Handoff to root cause analysis:**
   - Announce: "Now that we've found the breaking commit at `<hash>`, I'm using systematic-debugging to analyze why this change caused the issue."
   - Use superpowers:systematic-debugging skill to investigate
   - Focus analysis on the changes in the bad commit
   - Identify the specific line/change that caused the issue
   - Explain WHY it broke (not just WHAT changed)

**Output:** Root cause understanding of why the commit broke functionality

## Best Practices

### Optimizing Commit Range
- **Narrow the range first** if possible:
  - Issue appeared last week? Start from last week, not 6 months ago
  - Use `git log --since="2 weeks ago"` to find starting point
  - Use tags/releases as good commits when possible

### Common Patterns

| Issue Type | Recommended Approach | Script/Steps Example |
|------------|---------------------|---------------------|
| Test failure | Automated | `npm test -- failing-test.spec.js` |
| Crash/error | Automated | `node app.js 2>&1 | grep -q ERROR && exit 1 || exit 0` |
| Performance | Automated | `time npm run benchmark \| awk '{if ($1 > 5.0) exit 1}'` |
| UI/UX change | Manual | "Click X, verify Y appears" |
| Behavior change | Manual or Hybrid | Script to check, manual to confirm subjective aspects |

## Integration with Other Skills

- **Called BY systematic-debugging:** When systematic-debugging detects a regression (issue absent in older commit, present now), it invokes git-bisect-debugging to find the first bad commit, then resumes its own analysis on the breaking change.
- **Calls systematic-debugging:** In Phase 4, after finding the bad commit, this skill hands off to superpowers:systematic-debugging with context focused on the identified commit to understand WHY the change broke functionality.

## Example Workflows

### Example 1: Automated Test Failure

```
User: "The login test started failing sometime in the last 50 commits."

[Phase 1] git status -> clean. Good: v1.2.0 tag, Bad: HEAD. Verified both. 47 commits, ~6 steps.
[Phase 2] AskUserQuestion -> User selects Automated.
  Script: npm install --silent 2>/dev/null || exit 125 && npm test -- tests/login.spec.js
[Phase 3] Subagent tests at each bisect step:
  abc123 -> bad (~3 left), def456 -> good (~2 left), ghi789 -> bad (~1 left), jkl012 -> good
  Result: ghi789 is first bad commit
[Phase 4] ghi789: "feat: update authentication middleware" (src/auth/middleware.js)
  -> Handoff to systematic-debugging for root cause analysis
```

### Example 2: Manual UI Regression

```
User: "The dashboard layout looks wrong, but I'm not sure when it broke."

[Phase 1] git status -> clean. Good: 2 weeks ago, Bad: HEAD. 89 commits, ~7 steps.
[Phase 2] AskUserQuestion -> User selects Manual.
  Steps: Run `npm run dev`, check sidebar/content layout at localhost:3000/dashboard
[Phase 3] Subagent presents verification steps at each commit, user reports good/bad:
  abc123 -> good, def456 -> bad, ... narrows to mno345
  Result: mno345 is first bad commit
[Phase 4] mno345: "refactor: migrate to CSS Grid layout" (Dashboard.css)
  -> Handoff to systematic-debugging for root cause analysis
```

## Troubleshooting

- **Good and bad are reversed:** Stop bisect, verify issue description, swap good/bad commits and restart.
- **Too many skips:** Review skipped commits manually. Consider narrowing the range or switching to manual investigation.
- **Bisect is stuck/interrupted:** Run `git bisect reset`, then `git checkout main`. Restart with better range/script.
- **Subagent is taking too long:** Optimize test script or simplify verification steps. Mark commit as 'skip' if needed.

## Summary

**When to use:** Historical bugs, regressions, "when did this break" questions

**Key strengths:**
- Systematic binary search (efficient)
- Subagent isolation (clean context)
- Automated + manual + hybrid approaches
- Integrates with systematic-debugging

**Remember:**
1. Always verify good is good, bad is bad
2. Keep test scripts deterministic and fast
3. Use subagents for each verification step
4. Clean up with `git bisect reset`
5. Hand off to systematic-debugging for root cause
