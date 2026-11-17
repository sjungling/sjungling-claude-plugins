---
description: Launch a devpod: review <PR url>, research <question>, factory <task or issue url>, factory recipes <library> <URL>, or dependabot <repos>
argument-hint: review <PR url> | research <question> | factory <task or issue url> | factory recipes <library> <release or migration URL> | dependabot <repo...>
---

Launch a devpod for: $ARGUMENTS

The first word is the flavor (`review`, `research`, `factory`, `dependabot`); the rest is the target. `factory recipes` is a factory subcommand: the target starts with `recipes`. If either is missing or unknown, ask and stop. Supervision rules are in `${CLAUDE_PLUGIN_ROOT}/references/playbook.md`.

## Steps

1. Pick a name: letters, digits and single hyphens, 32 characters at most (`review-rr-134`). Add a number if it exists in `devpod ls`.
2. Write the prompt to `/tmp/devpod-prompts/<name>.md`. Every prompt starts with the target, says to use `gh` and to install the stacking extension first if `gh stack` is missing (`gh extension install github/gh-stack`), and ends by asking for a short summary: done, pushed or posted (with links), and not done.
3. Pick the size (below) and launch in the background: `devpod run <name> [--size=TYPE] -- mod claude chat . --prompt @/tmp/devpod-prompts/<name>.md`.
4. Reply with name, flavor and size, one line each, and why that size. Do not wait for startup.
5. If the "Devpod supervisor check" cron job is slowed and `schedule.txt` has no active override, reset it to `3-58/5 * * * *` (create the new job first, then delete the old).

## Size

Size is fixed at creation; the smallest that fits what the task runs.
- `t4g.large`: read-only review or research, and Dependabot sweeps (burstable is enough; use `t4g.xlarge` if a repo's failing check runs out of memory).
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

## dependabot `<repo...>`

A factory pod that sweeps the open Dependabot PRs of one or more repos (`org/repo` names or URLs). Size `t4g.large` (burstable; `t4g.xlarge` if a repo's checks need more memory). Before launching, write `~/.local/state/devpod-supervisor/ledgers/<name>-GOAL.md` with the repos and these done criteria: every open Dependabot PR handled, each with a risk and reason in the ledger, LOW and MED merged with an empty-body approval, HIGH rebased, fixed and approved but not merged, and a final summary.

Prompt content:
- Work one repo at a time and one PR at a time, oldest first (`gh pr list -R <repo> --author app/dependabot --state open`). Re-list after each merge, since merges rebase or conflict the rest. Clone each repo once under `~/work`.
- Per PR: read the description and its changelog or release notes, explore the code briefly for use of the changed APIs, then rate it:
  - LOW: patch or minor update, dev tooling, or no breaking change touching code we use.
  - MED: minor update of a runtime dependency, or notable changes near code we use, but nothing breaking.
  - HIGH: a major bump, breaking changes touching code we use, a build or runtime toolchain change, or anything you cannot rule out after a quick look.
- Append a row to `~/dependabot-ledger.md`: repo, PR, title, version change, risk, reason, action.
- If CI is red: first rebase on origin/main (`gh pr update-branch N -R <repo> --rebase`, or one `@dependabot rebase` comment if that is refused), wait for CI, and decide again. If it is still red, fix it with minimal code changes that match the existing code and the library's idioms, run only the failing check locally, and push to the PR branch. Never force-push and never push to a default branch. Re-rate after a fix; a large or uncertain fix means stop on that PR, change nothing more, and report what you found.
- Once CI is green, approve with no body (`gh pr review N -R <repo> --approve`), verify an APPROVED review with an empty body, then:
  - LOW and MED: squash-merge (`gh pr merge N -R <repo> --squash`).
  - HIGH: do everything except merge. Never merge a HIGH PR; leave it to the user.
- Do not post comments, except the single `@dependabot rebase`. Do not run full test suites.
- Post to the message board at start and finish. No Claude attribution; use `uv` for Python.
- Finish with a table: every PR with repo, number, version change, risk, reason, CI, and outcome (merged, approved and waiting for the user, or blocked), plus links.

The user pre-confirms the approvals, merges and pushes above.

## factory recipes `<library> <release notes or migration guide URL>`

A factory pod that turns a library's breaking changes into OpenRewrite recipes, then proves them on real repositories. Name `factory-<library>-recipes`. Size `m9g.2xlarge`. Write the GOAL file as for any factory, with these done criteria:
- existing recipes for the library searched across `moderneinc` and `openrewrite` `rewrite-*` repos, findings written up
- every breaking change mapped to a recipe idea or a reason to skip
- 12-24 recipes, including major and minor version declarative recipes
- recipes written in the right module with tests, `recipes.csv` regenerated
- recipes validated against a synced corpus, diffs reviewed
- draft PR open, CI green or failures explained

Prompt content, in order:
1. **Discover.** Read the URL and the pages it links to. Use `gh search code` for existing recipes, so we extend instead of duplicate. Pick the home module after the search and say why in the PR. For JS and TS libraries, `moderneinc/rewrite-nodejs` and its `library-major-upgrades.yml` are the usual home.
2. **Assess.** Map each breaking change to a recipe or a reason to skip. Keep only changes you can detect from source. Stop short of 24 instead of padding. Write the assessment to `~/research/<name>.md`.
3. **Build.** Use YAML for dependency bumps, composite upgrades and import moves (`ChangeImport`). YAML cannot match call expressions, so use TypeScript or Java for call-level rewrites. Without type information, match by name and prefer a `Find` marker recipe over a risky rewrite. Test first. If there is no lockfile, run `npm install`. Before pushing, regenerate and validate `recipes.csv` with the module's `recipeCsvGenerate` and `recipeCsvValidate` tasks; the `cgp` check fails without them.
4. **Validate.** Do this before finishing, not after:
   - Use `mod` (installed and logged in) to find and sync 10-30 varied repos that use the library. A plain `mod git sync` brings LSTs only; add `--with-sources` to get the code.
   - JS recipes need the JS runtime: `npm install @openrewrite/rewrite` where `mod` runs, and install the recipe module locally with `mod config recipes`.
   - Build the LSTs, run each recipe with `mod run`, and read every diff. Check for false positives, missed cases and unsafe edits. Run each twice and expect no second diff. Run the repos' own build or tests on a few changed repos.
   - Fix the recipes and repeat. Keep all of this local: no pushes, PRs or comments on corpus repos.
5. **Ship.** Open a draft PR with a short assessment and a validation section: repos used, what each recipe changed, problems found and fixed, what remains. Watch CI until green. Never merge.

Builds and corpus runs are slow. A pod waiting on a background monitor or `mod build` is working, not idle.
