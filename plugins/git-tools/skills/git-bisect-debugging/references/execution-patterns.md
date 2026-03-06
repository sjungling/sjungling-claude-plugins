# Git Bisect Execution Patterns

Detailed subagent prompts and error handling for Phase 3 execution.

## Subagent Prompt Templates

### Automated Verification Prompt

```
Run this test script and report the result:

<script content>

Report 'good' if exit code is 0, 'bad' if exit code is 1, 'skip' if exit code is 125.
Include the output of the script in your response.
```

### Manual Verification Prompt

```
We're testing commit <hash> (<message>).

Follow these verification steps:
<verification steps>

Report 'good' if the issue doesn't exist, 'bad' if it does exist.
Explain what you observed.
```

### Hybrid Verification Prompt

```
Run this test script:

<script content>

If exit code is 0 or 1, report that result.
If exit code is 125 or script is ambiguous, perform manual verification:
<verification steps>

Report 'good', 'bad', or 'skip' with explanation.
```

## Execution Flow

1. **Main agent:** Run `git bisect start <bad> <good>`

2. **Loop until bisect completes:**

   a. Git checks out a commit to test

   b. **Main agent launches subagent** using Task tool with the appropriate prompt template above

   c. **Subagent returns:** Result ("good", "bad", or "skip") with explanation

   d. **Main agent:** Run `git bisect good|bad|skip` based on result

   e. **Main agent:** Update progress
      - Show commit that was tested and result
      - Calculate remaining steps: `git bisect log | grep "# .*step" | tail -1`
      - Example: "Tested commit abc123 (bad). ~4 steps remaining."

   f. Repeat until git bisect identifies first bad commit

3. **Main agent:** Run `git bisect reset` to cleanup

4. **Main agent:** Return to original branch/commit

## Error Handling

- **Subagent timeout/error:** Allow user to manually mark as "skip"
- **Build failures:** Use `git bisect skip`
- **Too many skips (>5):** Suggest manual investigation, show untestable commits
- **Bisect interrupted:** Ensure `git bisect reset` runs in cleanup
- **Good/bad reversed:** If all results seem opposite, offer to restart with swapped inputs
- **No bad commit found:** Verify bad commit is actually bad, check if issue is environmental
- **Cleanup (always):** Run `git bisect reset` on success or failure, return to original branch

## Main vs Subagent Responsibilities

**Main agent:**
- Manage git bisect state (`start`, `good`, `bad`, `reset`)
- Track progress and communicate remaining steps
- Launch subagents for verification
- Handle errors and cleanup

**Subagent:**
- Execute verification in clean context (no bleeding between commits)
- Report result: "good", "bad", or "skip"
- Provide brief reasoning for result
