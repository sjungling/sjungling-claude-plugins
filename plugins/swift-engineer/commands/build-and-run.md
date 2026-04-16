---
description: Build the Xcode project, fix errors, then run the application
argument-hint: "[scheme]"
allowed-tools:
  - Bash
  - Read
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

Build and run the current Xcode project.

**Important:** Run all `xcodebuild` commands as background tasks. Builds can take significant time (30s–5m+ depending on project size). Use Bash with `run_in_background: true` parameter to avoid blocking. Poll build completion and capture output for error analysis.

## Workflow

### Step 1: Find the Project

Look for `.xcworkspace` (preferred) or `.xcodeproj` in current directory. If multiple exist, ask the user which to use.

### Step 2: Find the Scheme

Get available schemes with:
```bash
xcodebuild -workspace <workspace> -list -quiet
```

or 

```bash
xcodebuild -project <project> -list -quiet
```

If multiple schemes exist, ask the user which to build. If scheme is provided as `$1`, use that.

### Step 3: Build

**Run as background task** to avoid blocking.

For macOS projects, build for native architecture:
```bash
ARCH=$(uname -m)
xcodebuild -project <project> -scheme <scheme> -destination "platform=macOS,arch=$ARCH" -quiet build
```

For iOS projects, determine available simulator and build:
```bash
SIMULATOR=$(xcrun simctl list devices available -j | python3 -c "import sys,json; devs=[d for r in json.load(sys.stdin)['devices'].values() for d in r if d['isAvailable']]; iphones=[d for d in devs if 'iPhone' in d['name']]; print(iphones[-1]['name'] if iphones else '')")
xcodebuild -project <project> -scheme <scheme> -destination "platform=iOS Simulator,name=$SIMULATOR" -quiet build
```

When build completes (exit code 0 = success, non-zero = failure), proceed to Step 4 if errors, or Step 5 if successful.

### Step 4: Fix Build Errors

If build fails, read error messages and fix each issue:
1. Read the file with the error
2. Identify and fix the issue
3. Re-run build
4. Repeat until build succeeds

Prioritize errors over warnings.

### Step 5: Run the App

**For macOS:**
```bash
# Get native architecture and build output directory
ARCH=$(uname -m)
BUILT_PRODUCTS_DIR=$(xcodebuild -project <project> -scheme <scheme> -destination "platform=macOS,arch=$ARCH" -quiet -showBuildSettings | grep ' BUILT_PRODUCTS_DIR =' | awk '{print $3}')

# Kill previous instance and run
if [ -f .build.pid ]; then
  OLD_PID=$(cat .build.pid)
  kill -0 "$OLD_PID" 2>/dev/null && kill "$OLD_PID" 2>/dev/null
fi

open "$BUILT_PRODUCTS_DIR/<app-name>.app"
sleep 1
pgrep -f "$BUILT_PRODUCTS_DIR/<app-name>" > .build.pid
```

**For iOS:**
```bash
# Get bundle identifier from Info.plist or build settings
BUNDLE_ID=$(xcodebuild -project <project> -scheme <scheme> -quiet -showBuildSettings | grep ' PRODUCT_BUNDLE_IDENTIFIER =' | awk '{print $3}')

# Boot simulator and launch
xcrun simctl boot "$SIMULATOR" 2>/dev/null
xcrun simctl launch --terminate-running-process booted "$BUNDLE_ID"
```

Report success or errors to the user.

## Troubleshooting: Clean Build Cache

If build issues persist or changes aren't being picked up, clean DerivedData and rebuild:

```bash
rm -rf ~/Library/Developer/Xcode/DerivedData/*
```

Then rebuild from Step 3. This removes all cached build artifacts and forces a fresh build. Use sparingly—only when a rebuild doesn't pick up code changes or when encountering mysterious build failures.
