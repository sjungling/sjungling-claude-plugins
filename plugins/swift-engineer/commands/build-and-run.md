---
description: Build the Xcode project, fix build errors, and launch it on a simulator, device, or macOS
argument-hint: "[scheme] [destination]"
allowed-tools:
  - mcp__xcode
  - Bash
  - Read
  - Edit
  - Glob
  - Grep
  - ToolSearch
  - AskUserQuestion
---

Build the current Xcode project, fix any build errors, launch it, and confirm it actually started.

Arguments are free-form hints, not positional flags. Match `$ARGUMENTS` loosely against the real scheme
and destination lists once discovered — `MyApp`, `iPhone 17 Pro`, `My Mac`, and `MyApp on iPad` are all
valid. Infer anything not supplied.

## Tooling

Prefer Apple's Xcode MCP server (`mcp__xcode__*`) over shell commands for every operation it covers. It
drives a live Xcode instance: scheme and run destination are mutable state, so **set the state, then
build** — there is no destination flag to pass.

Read `references/xcode-mcp.md` for the verified tool list, behaviours, and the CLI fallback table. Use
the CLI path only when the MCP tools are absent or Xcode is not running.

## Workflow

### 1. Resolve the workspace

`XcodeListWorkspaces` for what is already open. If nothing is open, find the `.xcworkspace` (preferred
over `.xcodeproj`) in the working directory and `XcodeOpenWorkspace` it. Ask only when several candidates
exist and the arguments do not disambiguate.

### 2. Resolve scheme and destination

List schemes and run destinations, then pick:

- **Scheme** — from `$ARGUMENTS` if given, else the already-active scheme, else the one matching the
  project name. Ask only when genuinely ambiguous. Use `disambiguatedName` when names collide.
- **Destination** — from `$ARGUMENTS` if given; otherwise a simulator preference declared in the
  project's `CLAUDE.md` (phrasings like `simulator: iPhone 17 Pro`, "preferred simulator", "test on");
  otherwise the active destination if eligible; otherwise the newest eligible device for the scheme's
  platform.

Apply the scheme first, then the destination — switching schemes can move the destination on its own.
Read back `activeDestinationDisplayTitle` rather than assuming the switch held.

Ask the user when a preference was declared but is unavailable, or when the platform is genuinely
ambiguous. Offer real entries from the destination list, prioritising the same device family. If no
simulator runtimes exist at all, offer to install one (`xcodebuild -downloadPlatform iOS`) or point at
Xcode → Settings → Components.

### 3. Build and fix

`BuildProject`, then `GetBuildLog` with `severity: "error"` on failure — do not read the full log.

Fix each error at its root cause, rebuild, and repeat. `XcodeRefreshCodeIssuesInFile` gives per-file
diagnostics while iterating.

Bounds on the fix loop:

- **Stop after 3 failed build attempts** and report what remains. Do not keep grinding.
- **Stop immediately and ask** if a fix would delete functionality, disable a test, comment out a call
  site, or loosen a type just to satisfy the compiler.
- Only touch files implicated by the errors. Build failures are not licence for unrelated refactoring.
- Fix errors before warnings, and leave pre-existing warnings alone.

### 4. Launch

`RunProject`. It builds, installs, boots the simulator if needed, and launches — one call. Do not pair it
with `simctl`, and do not scrape `BUILT_PRODUCTS_DIR`.

Pass `attachDebugger: true` only when the user wants to debug; `InvokeDebuggerCommand` then takes any
lldb command.

### 5. Confirm it is actually running

A clean build is not a working app. After launch, check `GetConsoleOutput` for startup failures —
filter on errors and faults rather than pulling everything:

```
GetConsoleOutput(pattern: "error|fatal|crash|exception|Terminating", oslogSeverity: ["error", "fault"], tailLimit: 100)
```

If it crashed on launch, treat the trace as the next bug: fix it and return to step 3, under the same
3-attempt bound.

### 6. Report

State the scheme, destination, build result, and launch state. Report what the evidence shows — if the
build succeeded but the app crashed on launch, or errors remain after 3 attempts, say so plainly with
the relevant output. Never describe an unverified launch as working.

Mention `StopProject` if the app is left running.

## Notes

- Do not run `BuildProject` and `RunProject` in sequence for a plain run — `RunProject` already builds.
  Build separately only when the goal is to check compilation without launching.
- `GetTargetBuildSettings` reads build settings; never parse `project.pbxproj`.
- Clearing DerivedData (`rm -rf ~/Library/Developer/Xcode/DerivedData/*`) is a last resort for stale
  artifacts, not a routine step — it forces a full rebuild of every project on the machine.
