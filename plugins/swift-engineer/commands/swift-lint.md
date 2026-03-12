---
description: Format and lint Swift code using swift-format
argument-hint: "[path]"
model: haiku
allowed-tools:
  - Bash
  - Read
  - Edit
  - Glob
---

To keep the codebase clean, execute the following workflow. If a path is provided as `$ARGUMENTS`, scope all formatting and linting to that path; otherwise, operate on the entire project.

For the visual workflow diagram, see `./references/swift-lint-workflow.mmd`.

## Step 1: Run swift-lint.sh

Execute the helper script which handles periphery (auto-detected), formatting, and linting in a single invocation:

```
bash ${CLAUDE_PLUGIN_ROOT}/commands/references/swift-lint.sh [path] --periphery
```

- Pass the target path (or `.` for the full project)
- Always pass `--periphery` — the script automatically skips if periphery is not installed or the project lacks configuration

The script outputs one JSON line per step with the structure: `{"step": "...", "status": "...", "output": "..."}`.

## Step 3: Handle Results

Parse the JSON output from the script:

1. **periphery** step (if run): Report any unused code findings to the user
2. **format** step: Note that formatting was applied in-place
3. **lint** step:
   - If `status` is `"clean"` — report success, done
   - If `status` is `"issues"` — read the flagged files, fix each lint issue using Edit, then re-verify by running:
     ```
     bash ${CLAUDE_PLUGIN_ROOT}/commands/references/swift-lint.sh [path] --lint-only
     ```
   - Repeat until lint is clean

Report a brief summary of all results.
