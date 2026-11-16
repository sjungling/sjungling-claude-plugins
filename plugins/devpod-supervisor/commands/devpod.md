---
description: Launch a devpod: review <PR url>, research <question>, or factory <task or issue url>
argument-hint: review <PR url> | research <question> | factory <task or issue url>
---

Launch a devpod for: $ARGUMENTS

The first word is the flavor (`review`, `research`, `factory`); the rest is the target. If either is missing or unknown, ask and stop. Supervision rules are in `${CLAUDE_PLUGIN_ROOT}/references/playbook.md`.

## Steps

1. Pick a name: letters, digits and single hyphens, 32 characters at most (`review-rr-134`). Add a number if it exists in `devpod ls`.
2. Write the prompt to `/tmp/devpod-prompts/<name>.md`. Every prompt starts with the target, says to use `gh`, and ends by asking for a short summary: done, pushed or posted (with links), and not done.
3. Pick the size (below) and launch in the background: `devpod run <name> [--size=TYPE] -- mod claude chat . --prompt @/tmp/devpod-prompts/<name>.md`.
4. Reply with name, flavor and size, one line each, and why that size. Do not wait for startup.
5. If the "Devpod supervisor check" cron job is slowed and `schedule.txt` has no active override, reset it to `3-58/5 * * * *` (create the new job first, then delete the old).

## Size

Size is fixed at creation; the smallest that fits what the task runs.
- `t4g.large`: read-only review or research.
- `m9g.xlarge`: a review or change that must build or test one repo.
- `m9g.2xlarge` (default): factory work, Gradle/Maven builds, recipe runs.
- `m9g.4xlarge`: long builds or 50+ repo corpus runs. Ask before `m9g.8xlarge`.
- Unsure: larger for factory, smaller for review and research.

Every devpod gets a fixed 200 GiB disk; there is no flag to shrink it. Review and research need far less. If a task needs over 150 GB, tell the user first and have the prompt clone shallow, build in batches and delete what it no longer needs. After launch, check `coder ssh <name> -- 'nproc; free -g; df -h ~'`; if load or memory is far over, suggest a bigger pod and move the work through git.

## review `<PR url>`

Prompt content:
- Check out the PR branch in a clone under `~/work`.
- Run `/pr-review-toolkit:review-pr`. Its helper agents fail on a devpod ("Not logged in"); if they do, review those aspects (code, tests, errors, types, comments) in the chat yourself.
- Red-team all findings, then keep only Critical or Important ones. Drop everything minor.
- Judge by two priorities: consistency with the existing code, and idiomatic use of any framework or library involved (Material UI, Apollo GraphQL, React, and so on). Advocate minimally invasive changes: flag changes larger than the problem needs, and prefer existing patterns and helpers over new ones.
- For each surviving finding, first look for an existing PR comment that covers it (`gh api` review and issue comments). If one exists, add a threaded reply. Otherwise post a new inline comment on the relevant line. `/workflow:post-pr-comments` can post them.
- None surviving: `gh pr review N -R <repo> --approve` with no body, then verify an APPROVED review with an empty body.
- After commenting, write the standing instruction to `~/followup.txt` and follow it: poll `gh` at least every 10 minutes for up to 6 hours for replies, commits and comments; re-read the code at the new head; approve (no body) once every finding is resolved and no new one holds up; if one is partly resolved, reply once on the thread. Post to the message board on approval or when you stop.
- Never request changes, merge, resolve threads or push to the PR's branch. Extra text after the URL is review focus; "don't approve" overrides the approve steps.
- The user pre-confirms the posts above, which satisfies a repo `CLAUDE.md` confirmation rule. Post without asking; if a menu appears, the supervisor answers it.
- If a slash command is missing, say so and do the closest equivalent.

## research `<question>`

- Answer by reading code, docs, issues and PRs. Clone under `~/work` only if needed.
- Read-only: no pushes, PRs, comments or issues.
- Cite file paths with line numbers, or links. Mark each claim confirmed (read) or inferred.
- Save the write-up to `~/research/<name>.md` and print it, short answer first.

## factory `<goal, task or issue url>`

Before launching, write `~/.local/state/devpod-supervisor/ledgers/<name>-GOAL.md` with the goal and checkable done criteria (use the issue's acceptance criteria if any). If the goal is too vague to check, ask for done criteria first.

Prompt content:
- State goal and done criteria. Read the issue and comments with `gh` if given a URL.
- Clone under `~/work`, branch from the default branch, follow the repo's conventions.
- Work autonomously: short plan, then implement, verify, commit, repeat. Do not stop to confirm between steps.
- Failing test first where the repo has tests. Run full tests, lint and build before the PR and fix failures.
- Open a draft PR, watch CI, fix until green. Link the issue.
- Stop only when blocked (a human decision, missing access, or the same failure three times). Say what you tried and need.
- No Claude attribution in commits. Short commit and PR text with the why. Never merge or push to the default branch.
- Before finishing, report each done criterion as met or not met.
