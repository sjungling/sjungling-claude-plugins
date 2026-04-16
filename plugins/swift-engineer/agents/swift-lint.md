---
name: swift-lint
description: Format and lint Swift code using swift-format. Iteratively fixes lint issues until clean. Use when the /swift-lint command dispatches to this agent.
tools: Bash, Read, Edit, Glob
model: haiku
color: green
---

Format and lint Swift code for the target project. The dispatching command will provide context including the plugin root path and target path.

## Step 1: Run swift-lint.sh

Execute the helper script which handles periphery (auto-detected), formatting, and linting in a single invocation:

```
bash <plugin-root>/commands/references/swift-lint.sh [path] --periphery
```

- Pass the target path (or `.` for the full project)
- Always pass `--periphery` — the script automatically skips if periphery is not installed or the project lacks configuration
- The `<plugin-root>` path will be provided by the dispatching command

The script outputs one JSON line per step with the structure: `{"step": "...", "status": "...", "output": "..."}`.

## Step 2: Handle Results

Parse the JSON output from the script:

1. **periphery** step (if run): Note any unused code findings
2. **format** step: Note that formatting was applied in-place
3. **lint** step:
   - If `status` is `"clean"` — done
   - If `status` is `"issues"` — read the flagged files, fix each lint issue using Edit, then re-verify by running:
     ```
     bash <plugin-root>/commands/references/swift-lint.sh [path] --lint-only
     ```
   - Repeat until lint is clean

## Step 3: Report Summary

Provide a concise summary including:
- Number of files formatted
- Number of lint issues found and fixed
- Any unused code findings from periphery
- Whether lint is now clean
