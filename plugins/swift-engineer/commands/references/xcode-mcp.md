# Xcode MCP reference

Apple's Xcode MCP server (`mcp__xcode__*`, Xcode 26+) drives a **live Xcode instance**, not `xcodebuild`.

That distinction drives everything else here: there is no `-destination` flag to pass. Scheme and run
destination are *mutable state* on the open workspace. Set the state, then act on it. Every tool takes
an optional `workspaceIdentifier` (identifier such as `workspace1`, or an absolute path); omit it when a
single workspace is open, pass it whenever more than one is.

## Detecting availability

The server is available when `mcp__xcode__*` tools appear in the tool list. If their schemas are not
loaded, fetch them with `ToolSearch` using `select:mcp__xcode__BuildProject,...`. Absence of the tools —
or any call failing because Xcode is not running — means fall back to the CLI table below.

## Tools this workflow uses

| Purpose | Tool | Notes |
|---|---|---|
| Find open workspaces | `XcodeListWorkspaces` | Returns identifier + path for each. No arguments. |
| Open one | `XcodeOpenWorkspace` | `path` to `.xcworkspace`/`.xcodeproj`; returns its identifier. |
| List schemes | `XcodeListSchemes` | Active scheme first. Full list written to `fullSchemeListPath`. |
| Set scheme | `XcodeSwitchScheme` | Returns `activeDestinationDisplayTitle` — Xcode may auto-switch the destination. |
| List destinations | `XcodeListRunDestinations` | Grouped as in the Xcode picker. Incompatible ones omitted unless `includeIncompatible: true`. |
| Set destination | `XcodeSwitchRunDestination` | Takes `displayTitle`. Refuses ineligible destinations and reports why. |
| Build | `BuildProject` | Blocks until the build finishes. `buildForTesting` also builds test targets. |
| Read failures | `GetBuildLog` | Filter with `severity` (`error`/`warning`/`remark`), `pattern` (regex), `glob` (path). |
| Build + install + launch | `RunProject` | Equivalent to Cmd+R. Boots the simulator itself. `attachDebugger` for lldb. |
| Read app output | `GetConsoleOutput` | stdout/stderr + OSLog. Filter by `pattern`, `oslogSeverity`, `tailLimit`. |
| Stop the app | `StopProject` | Cmd+. — no-op if nothing is running. |
| Per-file diagnostics | `XcodeRefreshCodeIssuesInFile` | `filePath` is project-relative (`MyApp/Sources/Foo.swift`). |
| Build settings | `GetTargetBuildSettings` | Use this rather than parsing `project.pbxproj`. |

### Round-tripping destination titles

`activeDestinationDisplayTitle` is returned by `XcodeListRunDestinations`, `XcodeSwitchScheme`, and
`XcodeSwitchRunDestination` alike, and feeds straight back into `XcodeSwitchRunDestination`. Chain those
outputs instead of re-listing.

### Key behaviours worth relying on

- **`RunProject` subsumes the whole launch sequence.** It builds, installs, boots the simulator if
  needed, and launches. Do not pair it with `simctl boot`/`install`/`launch`, and do not scrape
  `BUILT_PRODUCTS_DIR`.
- **`BuildProject` blocks.** No background task or polling needed; `GetBuildLog` also reports whether a
  build is still in progress.
- **`GetBuildLog` filters server-side.** Ask for `severity: "error"` rather than reading a full log.
- **`XcodeSwitchScheme` can move the destination.** A scheme change may silently swap e.g. `My Mac` for
  `My Mac (Mac Catalyst)`. Read the returned `activeDestinationDisplayTitle` rather than assuming.

## Runtime interaction (optional, expensive)

For tapping through UI or capturing screenshots. Sessions hold real resources and affect the user's UI —
always close them.

- `DeviceInteractionStartWorkspaceSession` — bound to the workspace, so it offers only devices the active
  scheme can run on and enables install+run. Requires `sessionIdentifier` (Title Case, human-friendly).
- `DeviceInteractionStartSession` — no workspace; cannot build or install. Requires `deviceIdentifier`.
- `DeviceInteractionInstallAndRun` — builds, installs, launches on the session's device.
- `DeviceInteractionSynthesize` — one interaction command (`t 100 200` to tap, swipe, type, press), then
  returns a screenshot **and** a UI hierarchy dump. Derive coordinates from the hierarchy, never from the
  screenshot alone.
- `DeviceInteractionEndSession` — always call this when finished.

**Parameter-name gotcha:** the session key is `interactionSessionKey` on `InstallAndRun` and
`EndSession`, but `interactSessionKey` on `Synthesize`.

## Other tools available on the server

Tests (`GetTestList`, `RunAllTests`, `RunSomeTests`, `XcodeListTestPlans`, `XcodeSwitchTestPlan`),
project structure (`XcodeListTargets`, `XcodeNewProject`, `XcodeNewTarget`, `XcodeListTemplates`),
file operations within project organization (`XcodeRead`, `XcodeWrite`, `XcodeGrep`, `XcodeGlob`,
`XcodeLS`, `XcodeMV`, `XcodeRM`, `XcodeMakeDir`, `XcodeUpdate`), configuration (`AddEntitlement`,
`AddInfoPlist`, `UpdateTargetBuildSetting`, `GetFileCompilerFlags`, `UpdateFileCompilerFlags`),
debugging (`InvokeDebuggerCommand` for any lldb command), SwiftUI previews (`RenderPreview`),
scratch evaluation (`RunCodeSnippet`), docs (`DocumentationSearch`), localization
(`LocalizationPlanner`, `StringCatalogRead`/`Edit`/`Context`), and production diagnostics
(`GetTopCrashIssues`, `GetCrashIssueLogs`, `GetTopFieldPerformanceIssues`,
`GetFieldPerformanceIssueLogs`).

Prefer any of these over the equivalent shell command when the server is available.

## CLI fallback

Used only when the MCP server is unavailable. `<proj>` is `-workspace X.xcworkspace` or
`-project X.xcodeproj`.

| MCP tool | CLI equivalent |
|---|---|
| `XcodeListWorkspaces` | `ls -d *.xcworkspace *.xcodeproj` |
| `XcodeListSchemes` | `xcodebuild <proj> -list -json` |
| `XcodeListRunDestinations` | `xcodebuild <proj> -scheme S -showdestinations` |
| `BuildProject` | `xcodebuild <proj> -scheme S -destination D build` |
| `GetBuildLog` | Parse `xcodebuild` output for `error:` lines |
| `RunProject` (macOS) | `open "$BUILT_PRODUCTS_DIR/<app>.app"` |
| `RunProject` (simulator) | `xcrun simctl boot D`, `simctl install booted <app>`, `simctl launch --terminate-running-process booted <bundle-id>` |
| `GetConsoleOutput` | `xcrun simctl spawn booted log stream --level debug` |
| `GetTargetBuildSettings` | `xcodebuild <proj> -scheme S -showBuildSettings -json` |

CLI notes:

- Builds take 30s–5m+. Run `xcodebuild` with `run_in_background: true` and poll.
- Prefer `-json` output and `jq` over `grep | awk` on human-readable output.
- List simulators with `xcrun simctl list devices available -j`; filter on `isAvailable`.
- No simulator runtimes installed: `xcodebuild -downloadPlatform iOS`, or direct the user to
  Xcode → Settings → Components.

## Troubleshooting

| Symptom | Action |
|---|---|
| MCP calls fail / no workspace | Confirm Xcode is running with the project open; `XcodeOpenWorkspace` otherwise. |
| Ambiguous scheme name | Use the `disambiguatedName` from `XcodeListSchemes` (e.g. `MyScheme (MyProject)`). |
| Destination refused as ineligible | Re-list with `includeIncompatible: true` and read the stated reason. |
| Simulator boot hangs | `xcrun simctl shutdown all`, then retry. |
| Stale build artifacts | `rm -rf ~/Library/Developer/Xcode/DerivedData/*`. Last resort — it forces a full rebuild of everything. |
