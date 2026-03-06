# Git Bisect Troubleshooting and Common Patterns

## Troubleshooting

- **Good and bad are reversed:** Stop bisect, verify issue description, swap good/bad commits and restart.
- **Too many skips:** Review skipped commits manually. Consider narrowing the range or switching to manual investigation.
- **Bisect is stuck/interrupted:** Run `git bisect reset`, then `git checkout main`. Restart with better range/script.
- **Subagent is taking too long:** Optimize test script or simplify verification steps. Mark commit as 'skip' if needed.

## Common Patterns

| Issue Type | Recommended Approach | Script/Steps Example |
|------------|---------------------|---------------------|
| Test failure | Automated | `npm test -- failing-test.spec.js` |
| Crash/error | Automated | `node app.js 2>&1 \| grep -q ERROR && exit 1 \|\| exit 0` |
| Performance | Automated | `time npm run benchmark \| awk '{if ($1 > 5.0) exit 1}'` |
| UI/UX change | Manual | "Click X, verify Y appears" |
| Behavior change | Manual or Hybrid | Script to check, manual to confirm subjective aspects |

## Optimizing Commit Range

- **Narrow the range first** if possible:
  - Issue appeared last week? Start from last week, not 6 months ago
  - Use `git log --since="2 weeks ago"` to find starting point
  - Use tags/releases as good commits when possible

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
