---
description: Move a moderne-saas issue to a column on GitHub project 8
argument-hint: "<issue-number> [column]"
allowed-tools:
  - Bash(gh project item-list:*)
  - Bash(gh project item-edit:*)
  - Bash(gh project item-add:*)
  - Bash(gh auth refresh:*)
---

Move a moderne-saas issue to a column on project board 8
(https://github.com/orgs/moderneinc/projects/8).

Parse `$ARGUMENTS`:
- First token = issue number (required).
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

Resolve the per-issue item ID, then set the Status field. Replace `<ISSUE>`
with the issue number and `<OPTION_ID>` with the option ID for the requested
column:

```bash
ISSUE=<ISSUE>
OPTION_ID=<OPTION_ID>

ITEM_ID=$(gh project item-list 8 --owner moderneinc --format json --limit 1000 | \
  jq -r '.items[] | select(.content.number == '"$ISSUE"') | .id')

if [ -z "$ITEM_ID" ]; then
  echo "Issue #$ISSUE is not on project 8. Add it first with:"
  echo "  gh project item-add 8 --owner moderneinc --url https://github.com/moderneinc/moderne-saas/issues/$ISSUE"
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
- If the issue isn't on the board, surface the `gh project item-add` command
  (shown above) rather than failing silently.
- Report the final column the issue landed in.
