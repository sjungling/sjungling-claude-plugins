---
description: Move an issue to a column on GitHub project 8
argument-hint: "<issue-number> [column] [owner/repo]"
allowed-tools:
  - Bash(gh project item-list:*)
  - Bash(gh project item-edit:*)
  - Bash(gh project item-add:*)
  - Bash(gh auth refresh:*)
---

Move an issue to a column on project board 8
(https://github.com/orgs/moderneinc/projects/8).

Project 8 spans several repos (moderne-saas, codegenomeproject, …), so an issue
number is **not** unique on the board — the same number exists in multiple repos.
Resolve by repository, never by number alone.

Parse `$ARGUMENTS`:
- First token = issue number (required).
- A token containing `/` (e.g. `moderneinc/codegenomeproject`) = repository
  (optional). A bare repo without an owner is assumed under `moderneinc`.
- Remaining tokens = target column name (optional, default `In Progress`).
  Match case-insensitively against the known columns below.

## Known IDs (stable)

These are fixed for moderneinc project 8 — no need to re-resolve them:

- `PROJECT_ID` = `PVT_kwDOBBZwVM0q6g`
- `FIELD_ID` (Status) = `PVTSSF_lADOBBZwVM0q6s4AATqk`
- Status option IDs:
  - Icebox = `6f4ce84a`
  - Refine = `e2a82074`
  - Backlog = `f75ad846`
  - In Progress = `47fc9ee4`
  - Ready to Communicate = `98236657`
  - Done = `04d30f6f`

If the requested column is not in this list, list the valid columns and stop.

## Run

Resolve the per-issue item ID **scoped to its repository**, then set the Status
field. Replace `<ISSUE>` with the issue number, `<OPTION_ID>` with the option ID
for the requested column, and `<REPO>` with `owner/repo` (empty if the caller
gave none):

```bash
ISSUE=<ISSUE>
OPTION_ID=<OPTION_ID>
REPO=<REPO>   # e.g. moderneinc/codegenomeproject; empty if not specified

ITEMS=$(gh project item-list 8 --owner moderneinc --format json --limit 1000)

if [ -n "$REPO" ]; then
  # .content.repository is "owner/repo" — the reliable disambiguator.
  # Here-strings (<<<), not `echo "$ITEMS" | …`: zsh's echo mangles the \n/\t
  # escapes inside issue titles and corrupts the JSON.
  ITEM_ID=$(jq -r --arg n "$ISSUE" --arg r "$REPO" \
    '.items[] | select(.content.number == ($n|tonumber) and .content.repository == $r) | .id' <<<"$ITEMS")
else
  MATCHES=$(jq --arg n "$ISSUE" \
    '[.items[] | select(.content.number == ($n|tonumber))]' <<<"$ITEMS")
  if [ "$(jq 'length' <<<"$MATCHES")" -gt 1 ]; then
    echo "Issue #$ISSUE is ambiguous — it exists in multiple repos on project 8:"
    jq -r '.[] | "  \(.content.repository) — \(.content.title)"' <<<"$MATCHES"
    echo "Re-run with the repo, e.g.: /workflow:issue-status $ISSUE <column> moderneinc/<repo>"
    exit 1
  fi
  ITEM_ID=$(jq -r '.[0].id // empty' <<<"$MATCHES")
fi

if [ -z "$ITEM_ID" ]; then
  TARGET="${REPO:-moderneinc/<repo>}"
  echo "Issue #$ISSUE${REPO:+ in $REPO} is not on project 8. Add it first with:"
  echo "  gh project item-add 8 --owner moderneinc --url https://github.com/$TARGET/issues/$ISSUE"
  exit 1
fi

gh project item-edit \
  --id "$ITEM_ID" \
  --project-id "PVT_kwDOBBZwVM0q6g" \
  --field-id "PVTSSF_lADOBBZwVM0q6s4AATqk" \
  --single-select-option-id "$OPTION_ID"
```

## Notes

- `gh project` commands require the `project` scope. If you hit an auth error,
  tell the user to run `gh auth refresh -s project`.
- Numbers collide across repos on project 8: without a repo, an ambiguous number
  lists its candidates and stops rather than editing the wrong (or every) item.
  Pass `owner/repo` to resolve it directly.
- If the issue isn't on the board, surface the `gh project item-add` command
  (with the resolved repo) rather than failing silently.
- Report the final column the issue landed in.
