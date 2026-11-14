---
description: Launch a devpod: review <PR url>, research <question>, or factory <task or issue url>
argument-hint: review <PR url> | research <question> | factory <task or issue url>
---

Launch a devpod for: $ARGUMENTS

The first word is the flavor: `review`, `research` or `factory`. The rest is the target. If the flavor is missing or unknown, or the target is empty, ask which one and stop.

## Steps

1. Pick the flavor's name pattern and write its prompt to `/tmp/devpod-prompts/<name>.md`. Use a short slug of letters and digits joined by single hyphens, 32 characters at most (for example `review-rr-134`, `research-ts7-peers`, `factory-i18n-keys`). If a devpod with that name exists in `devpod ls`, add a number.
2. Pick the size (see "Choosing size and disk" below) and launch it as a background task: `devpod run <name> [--size=TYPE] -- mod claude chat . --prompt @/tmp/devpod-prompts/<name>.md`. Omit `--size` only when the work needs the default; a read-only review gets `--size=t4g.large`.
3. Reply with the devpod name, flavor and size, one line each, with a few words on why you chose that size. Do not wait for it to start.
4. If a "Devpod supervisor check" cron job exists (CronList) and is not on the 5-minute rung, and `~/.local/state/devpod-supervisor/schedule.txt` has no active override, reset it to `3-58/5 * * * *` by creating the new job first and then deleting the old one.

## Choosing size and disk

Size is set only when a devpod is created: `--size` is ignored for one that exists, so a wrong size means a new devpod. Sizes: `t4g.medium`, `t4g.large`, `t4g.xlarge` (burstable, cheaper), then `m9g.xlarge`, `m9g.2xlarge` (the default, 8 vCPU and about 30 GB RAM), `m9g.4xlarge` and `m9g.8xlarge`.

Pick the smallest size that fits what the task will actually run, not the flavor's name. Start from what it does:
- **Read-only work: `t4g.large` (2 vCPU, about 8 GB).** A review that reads the diff and the source, runs `/code-review` and `/simplify`, and posts or approves, and research that clones one repo and reads it. The user's feedback is that `m9g.xlarge` was too large for a read-only review. A `t4g.large` devpod (design-system-a11y) also ran a full build, lint, type check and tests for a small component library, only slower, so it is enough for a review that needs at most a type check or lint. Its startup check warns when free memory is under 8 GiB; that warning was harmless there. `t4g.medium` (about 4 GB) has not been tried; use it only for reviews that clearly run nothing.
- **Light builds: `m9g.xlarge` (4 vCPU, about 15 GB).** A review or small change that has to build or test one repo, or a UI repo where the checks take minutes. A 4 vCPU devpod ran a large UI repo's whole vitest suite at about 320% CPU, so it is the floor for a UI repo you must test.
- **Default (`m9g.2xlarge`, 8 vCPU, about 30 GB)** for real build work: factory tasks, Gradle or Maven builds of rewrite-prethink-sized repos, `mod build` of a handful of repos, and research that runs recipes. The Python research and build devpod ran on it for hours, with `mod build --parallel=3` over 52 repos taking about 43 minutes at load 2 to 3.
- **Larger (`m9g.4xlarge`)** when a long build or test run is the bottleneck: a factory task with a large build, a big test suite that runs at full CPU for minutes (a UI repo's vitest run used 320% CPU on 4 vCPU), or a corpus run over 50 or more repos where finishing sooner matters. `m9g.8xlarge` is rarely worth it; ask the user first.
- When unsure between two sizes, take the larger one for factory work (it runs unattended for hours and waits on builds) and the smaller for review and research. Reviews and research default to `t4g.large`; a review prompt that does not need a build should say so, and say not to run the full test suite.

Disk cannot be chosen with `devpod run`. Every devpod gets 200 GiB (about 193 GB usable) and `devpod stop` keeps it. Budget for it: a 52-repo Python corpus with built LSTs, worktrees and a Gradle cache used about 54 GB. If the task needs more than about 150 GB (hundreds of repos, or many full LSTs), tell the user before launching, and tell the prompt to clone shallow (`--depth 1`), build in batches and delete clones and LSTs it no longer needs.

After launch, check what you got with `coder ssh <name> -- 'nproc; free -g; df -h ~'`. If a devpod runs at load far above its vCPU count for a long time, or runs out of memory or disk, tell the user and suggest a bigger devpod, and move the work over through git.

## When a devpod finishes

Never stop or remove a devpod that did real work (any flavor) without the user's explicit confirmation. The user may want to follow up in its chat.
- Leave it running. Save its pane and any write-up to `~/.local/state/devpod-supervisor/ledgers` and verify the results (for example with `gh`).
- Report the result and ask the user once whether to remove it. Then check on it quietly and do not ask again.
- Remove it only after the user says yes. An idle devpod stops on its own after a while, but it still exists and can be restarted. That is fine.
- Ignore greyed suggestion text in a finished chat's prompt box. It is not input from the user.

Every prompt starts with the target and says to use `gh` for GitHub access. Every prompt ends by asking for a short summary of what was done, what was posted or pushed (with links), and what could not be done.

## Flavors

### review `<PR url>`

Prompt content:
- Check out the PR branch in a clone under `~/work`.
- Run `/code-review <PR url>`. Keep the findings in the chat for now.
- Run `/simplify` on the PR's changes.
- Run `/pr-review-toolkit:review-pr tests errors types comments`, only the aspects the PR touches (test files, error handling, new types, added comments). Skip `code` and `simplify`, which repeat the two commands above. Its helper agents fail on a devpod ("Not logged in"), so if they do, review those aspects in the chat yourself. Treat its findings like `/code-review` findings: red-team them before acting.
- If simplify finds significant gains (real cuts in code, duplication or complexity, not style nits): make them on a new branch stacked on the PR branch with `gh stack`, run the tests and build first, and open the stacked PR with a short description. Never push to the PR's own branch.
- Otherwise, if critical or important issues survive the red-team, run `/workflow:post-pr-comments` for those only. Post nothing for minor findings.
- If no critical or important issues survive, approve with no body and no comment (`gh pr review N -R <repo> --approve`), then verify with gh that it shows an APPROVED review with an empty body.
- If you posted comments, keep watching: write the standing instruction to `~/followup.txt` and follow it. Poll gh at least every 10 minutes for up to 6 hours for replies, new commits and new review comments. Re-read the code at the new head. Approve with no body and no comment once every finding is sufficiently resolved and no new critical or important issue holds up. If a finding is only partly resolved, reply once on the thread with the remaining gap. Post a message to the devpod message board when you approve or stop watching.
- If a slash command or `gh stack` is missing, say so and do the closest equivalent.
- Never request changes, merge, resolve threads or push to the PR's own branch. Extra text after the PR url (for example "don't approve") overrides the approve steps.
- The user pre-confirms the posting steps above (surviving critical or important comments, the empty approval, and one thread reply). A repo `CLAUDE.md` rule about confirming PR comments is satisfied by this. Post without asking. If a confirmation menu still appears, the supervisor answers it; wait for that answer.
- Any extra text after the PR url in the arguments is added as review focus.

Supervising a review (each periodic check):
- If a review chat waits on a confirmation menu to post a comment, review or approval, read the draft. Answer "post it" only when it matches the rules above: a plain comment, an approval with no body, or one thread reply, for a finding that survived the red-team, and nothing that requests changes, merges, resolves threads or pushes. Check the draft against the PR before answering.
- Anything else, such as a draft that is wrong, off-scope, minor, or asks for changes, answer "don't post" and tell the user in one line. Escalate only real judgment calls. Report what you answered and why.

### research `<question>`

Prompt content:
- Answer the question by reading code, docs, issues and PRs. Clone repos under `~/work` only if needed.
- Read-only: no pushes, no PRs, no comments on GitHub, no issues.
- Cite sources as file paths with line numbers, or links.
- Mark each claim as confirmed (you read it) or inferred.
- Save the final write-up to `~/research/<name>.md` and print it in the chat, with the short answer first.

### factory `<goal, task or issue url>`

The devpod works on its own toward a goal, and this session is its supervisor.

Before launching, write `~/.local/state/devpod-supervisor/ledgers/<name>-GOAL.md` with the goal and a short, checkable list of done criteria (for example: tests pass, PR open, CI green). Use the issue's acceptance criteria if there are any. If the goal is too vague to check, ask the user for the done criteria first.

Prompt content:
- State the goal and the done criteria. Read the issue and its comments with `gh` if the target is an issue url.
- Clone the repo under `~/work`, branch from the default branch, and follow the repo's own conventions (CLAUDE.md, contributing docs, lint and test setup).
- Work autonomously until every done criterion is met. Write a short plan first, then loop: implement a step, verify it, commit, and move to the next. Do not stop to ask for confirmation between steps.
- Write a failing test first where the repo has tests. Run the full tests, lint and build before opening a PR, and fix failures yourself.
- Open a draft PR, watch its CI, and fix failures until it is green. Link the issue if there is one.
- Stop and say so only if you are blocked: a decision only a person can make, missing access, or the same failure three times in a row. Say what you tried and what you need.
- Do not sign commits as authored by Claude. Keep commit messages and the PR description short, with the why and the broad intent, not a line-by-line walkthrough.
- Never merge, and never push to the default branch.
- Before finishing, check each done criterion and report it as met or not met.

Supervising it (each periodic check):
- Compare the pane with the goal file. If the chat stopped with criteria unmet, send a continue message that lists the remaining criteria.
- If it loops or fails the same way repeatedly, nudge it toward a different approach. Escalate to the user only for real blockers or decisions.
- Treat it as done only when the chat reports every criterion as met and you have checked the PR yourself with `gh`. Then save the pane to `~/.local/state/devpod-supervisor/ledgers` and handle the devpod as usual.
