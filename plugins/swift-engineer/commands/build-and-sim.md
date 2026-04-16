---
description: Build the Xcode project and launch it in an available iOS simulator
argument-hint: "[scheme]"
allowed-tools:
  - Bash
  - Read
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

Build the current Xcode project and run it in an iOS/iPadOS simulator, selecting the simulator intelligently based on availability and project preferences.

**Important:** Run all `xcodebuild` commands as background tasks. Builds can take significant time (30s–5m+). Use Bash with `run_in_background: true` to avoid blocking. Poll for completion and capture output for error analysis.

## Workflow

### Step 1: Find the Project

Look for `.xcworkspace` (preferred) or `.xcodeproj` in the current directory. If multiple exist, ask the user which to use.

### Step 2: Find the Scheme

List schemes:
```bash
xcodebuild -workspace <workspace> -list -quiet
# or
xcodebuild -project <project> -list -quiet
```

If `$1` is provided, use it. Otherwise, if multiple schemes exist, ask the user.

### Step 3: Determine Preferred Simulator

Check for a simulator preference declared in the project's `CLAUDE.md` (and any imported memory files). Look for patterns like:

- "simulator: iPhone 15 Pro"
- "preferred simulator", "default simulator", "test on"
- Any explicit simulator device name (e.g., "iPad Pro 13-inch (M4)")

Capture the preferred simulator name if found.

### Step 4: Discover Available Simulators

```bash
xcrun simctl list devices available -j
```

Parse the JSON to build a list of available simulators grouped by runtime (iOS / iPadOS). Only include devices where `isAvailable` is true.

### Step 5: Select the Simulator

Apply this decision tree:

1. **Preferred simulator found in CLAUDE.md AND available** → use it.
2. **Preferred simulator found but NOT available** → use `AskUserQuestion` to prompt the user. Present 3–5 available simulators as options (prioritize devices matching the preferred family — e.g., if preference was "iPhone 15 Pro", offer other iPhones first; for iPads, offer iPads). Include the preferred name in the question context so the user knows why we're asking.
3. **No preferred simulator in CLAUDE.md** → pick a sensible default (most recent iPhone on the latest iOS runtime) and proceed. If ambiguous (e.g., iPad-only project), ask the user.
4. **No simulators available at all** → try to install one via the CLI:
   ```bash
   xcodebuild -downloadPlatform iOS
   # or list installable runtimes:
   xcrun simctl runtime list -v
   ```
   Offer the user 2–3 options from the most recent iOS/iPadOS releases (query available runtimes via `xcrun simctl list runtimes available` and `xcodebuild -downloadAllPlatforms -exportPath` hints). If CLI installation isn't possible in this environment, instruct the user to open Xcode → Settings → Platforms and install a simulator runtime manually, then re-run the command.

Use `AskUserQuestion` for any user prompts in steps 2, 3 (ambiguous), and 4.

### Step 6: Build

For iOS/iPadOS:
```bash
xcodebuild -project <project> -scheme <scheme> \
  -destination "platform=iOS Simulator,name=<SIMULATOR>" \
  -quiet build
```

Run as a background task. On failure, read error output, fix issues, and re-run until the build succeeds. Prioritize errors over warnings.

### Step 7: Launch in Simulator

```bash
# Boot the selected simulator (no-op if already booted)
xcrun simctl boot "<SIMULATOR>" 2>/dev/null

# Open the Simulator.app so the user can see it
open -a Simulator

# Get bundle identifier
BUNDLE_ID=$(xcodebuild -project <project> -scheme <scheme> -quiet -showBuildSettings \
  | grep ' PRODUCT_BUNDLE_IDENTIFIER =' | awk '{print $3}')

# Install the built app onto the simulator
BUILT_PRODUCTS_DIR=$(xcodebuild -project <project> -scheme <scheme> \
  -destination "platform=iOS Simulator,name=<SIMULATOR>" -quiet -showBuildSettings \
  | grep ' BUILT_PRODUCTS_DIR =' | awk '{print $3}')
APP_NAME=$(xcodebuild -project <project> -scheme <scheme> \
  -destination "platform=iOS Simulator,name=<SIMULATOR>" -quiet -showBuildSettings \
  | grep ' FULL_PRODUCT_NAME =' | awk '{print $3}')

xcrun simctl install booted "$BUILT_PRODUCTS_DIR/$APP_NAME"
xcrun simctl launch --terminate-running-process booted "$BUNDLE_ID"
```

Report the selected simulator, build result, and launch status to the user.

## Troubleshooting

- **Stale cache**: `rm -rf ~/Library/Developer/Xcode/DerivedData/*` and rebuild (use sparingly).
- **Simulator boot stuck**: `xcrun simctl shutdown all` then re-boot.
- **Runtime missing**: `xcrun simctl runtime list` to verify installed runtimes.
