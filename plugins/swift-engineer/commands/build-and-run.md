---
description: Build the Xcode project, fix any errors, then run the application
argument-hint: "[scheme]"
model: sonnet
allowed-tools:
  - Bash
  - Read
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - ToolSearch
---

Build and run the current Xcode project. If a scheme is provided as `$1`, use that scheme; otherwise, discover available schemes and prompt if multiple exist. Follow this workflow:

For the visual workflow diagram, see `./references/build-and-run-workflow.mmd`.

## Step 0: Check for Xcode MCP

Use ToolSearch with query "xcode build" to check if Xcode MCP tools are available (e.g., `BuildProject`, `GetBuildLog`, `XcodeListWindows`). If found, follow the **MCP Path**. Otherwise, follow the **CLI Fallback Path**.

---

## MCP Path (preferred — requires Xcode MCP configured via `claude mcp add xcode`)

### Step 1: Identify the Project

1. Call `XcodeListWindows` to discover open Xcode windows and their `tabIdentifier` values
2. If no windows are open, tell the user to open their project in Xcode first
3. If multiple windows are open, use AskUserQuestion to ask which one to use
4. Note the `tabIdentifier` — it is required for most subsequent MCP tool calls

### Step 2: Build the Project

1. Call `BuildProject` with the `tabIdentifier` to trigger an incremental build
2. Call `GetBuildLog` to retrieve the build output

### Step 3: Fix Build Errors

If the build fails:

1. Call `XcodeListNavigatorIssues` to get structured diagnostics (errors and warnings)
2. Use `XcodeRead` to read the files with errors
3. Use `XcodeUpdate` (str_replace-style patches) to fix each error
4. Re-run `BuildProject` and check `GetBuildLog` again
5. Repeat until the build succeeds

Prioritize errors over warnings. If warnings remain after a clean build, briefly note them to the user.

### Step 4: Run the Application

Once the build succeeds, run the app using Bash:

- **iOS/iPadOS**: Determine the best available simulator dynamically, then boot and launch:
  ```
  SIMULATOR=$(xcrun simctl list devices available -j | python3 -c "import sys,json; devs=[d for r in json.load(sys.stdin)['devices'].values() for d in r if d['isAvailable']]; iphones=[d for d in devs if 'iPhone' in d['name']]; print(iphones[-1]['name'] if iphones else devs[0]['name'] if devs else '')")
  xcrun simctl boot "$SIMULATOR" 2>/dev/null; xcrun simctl launch --terminate-running-process --console-stdout booted <bundle-identifier>
  ```
  Determine the bundle identifier from the project's build settings or `Info.plist`.

- **macOS**: First kill any running instance of the app (`pkill -x <app-name>`), then remove the old `.app` bundle from `DerivedData/.../Build/Products/Debug/` before building. After the build succeeds, open the fresh `.app` bundle. This avoids launching a stale cached binary.

Report the result to the user.

---

## CLI Fallback Path (no Xcode MCP available)

### Step 1: Identify the Project

1. Look for `.xcworkspace` files first (preferred), then `.xcodeproj` files in the current directory
2. If multiple are found, use AskUserQuestion to ask the user which one to use
3. Determine the available schemes by running: `xcodebuild -list -workspace <workspace>` or `xcodebuild -list -project <project>`
4. If multiple schemes exist, use AskUserQuestion to ask which scheme to build and run

### Step 2: Resolve the Build Products Directory

Before building, determine the exact output path using `-showBuildSettings`. This avoids launching a stale binary from a different DerivedData directory:

```bash
# For macOS:
BUILT_PRODUCTS_DIR=$(xcodebuild -project <project> -scheme <scheme> -configuration Debug -showBuildSettings -skipMacroValidation -destination 'platform=macOS' 2>/dev/null | grep ' BUILT_PRODUCTS_DIR =' | awk '{print $3}')

# For iOS:
BUILT_PRODUCTS_DIR=$(xcodebuild -project <project> -scheme <scheme> -configuration Debug -showBuildSettings -skipMacroValidation -destination "platform=iOS Simulator,name=$SIMULATOR" 2>/dev/null | grep ' BUILT_PRODUCTS_DIR =' | awk '{print $3}')
```

Save this path — you will use it in Step 4 to launch the correct binary.

### Step 3: Build the Project

Run the build using `xcodebuild`. For iOS, determine the simulator first:

```
SIMULATOR=$(xcrun simctl list devices available -j | python3 -c "import sys,json; devs=[d for r in json.load(sys.stdin)['devices'].values() for d in r if d['isAvailable']]; iphones=[d for d in devs if 'iPhone' in d['name']]; print(iphones[-1]['name'] if iphones else devs[0]['name'] if devs else '')")
xcodebuild -workspace <workspace> -scheme <scheme> -destination "platform=iOS Simulator,name=$SIMULATOR" build 2>&1 | tail -50
```

Adjust the destination as appropriate for the project type (iOS, macOS, etc.). For macOS apps, use `-destination 'platform=macOS'`.

If using a `.xcodeproj` instead of a workspace, use `-project` instead of `-workspace`.

### Step 4: Fix Build Errors

If the build fails:

1. Read the build output to identify the errors
2. Fix each error by reading and editing the relevant source files
3. Re-run the build command
4. Repeat until the build succeeds with no errors

Prioritize errors over warnings. If warnings remain after a clean build, briefly note them to the user.

### Step 5: Run the Application

Once the build succeeds, use the `BUILT_PRODUCTS_DIR` from Step 2 to launch the exact binary that was just built:

- **iOS/iPadOS**: Boot the simulator and launch:
  ```
  xcrun simctl boot "$SIMULATOR" 2>/dev/null; xcrun simctl launch --terminate-running-process --console-stdout booted <bundle-identifier>
  ```
  Determine the bundle identifier from the project's `Info.plist` or build settings.

- **macOS**: First kill any running instance of the app (`pkill -x <app-name>`), then open the `.app` from the resolved build products directory:
  ```bash
  pkill -x <app-name> 2>/dev/null; sleep 1
  open "$BUILT_PRODUCTS_DIR/<app-name>.app"
  ```

Report the result to the user.
