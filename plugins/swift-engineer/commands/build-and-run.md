---
description: Build the Xcode project, fix any errors, then run the application
allowed-tools:
  - Bash
  - Read
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

Build and run the current Xcode project. Follow this workflow:

## Step 1: Identify the Project

1. Look for `.xcworkspace` files first (preferred), then `.xcodeproj` files in the current directory
2. If multiple are found, use AskUserQuestion to ask the user which one to use
3. Determine the available schemes by running: `xcodebuild -list -workspace <workspace>` or `xcodebuild -list -project <project>`
4. If multiple schemes exist, use AskUserQuestion to ask which scheme to build and run

## Step 2: Build the Project

Run the build using `xcodebuild`:

```
xcodebuild -workspace <workspace> -scheme <scheme> -destination 'platform=iOS Simulator,name=iPhone 16' build 2>&1 | tail -50
```

Adjust the destination as appropriate for the project type (iOS, macOS, etc.). For macOS apps, omit the `-destination` flag.

If using a `.xcodeproj` instead of a workspace, use `-project` instead of `-workspace`.

## Step 3: Fix Build Errors

If the build fails:

1. Read the build output to identify the errors
2. Fix each error by reading and editing the relevant source files
3. Re-run the build command
4. Repeat until the build succeeds with no errors

Do not ignore warnings, but prioritize resolving errors first. If warnings remain after a clean build, briefly note them to the user.

## Step 4: Run the Application

Once the build succeeds, run the app in the simulator or locally:

- **iOS/iPadOS**: Boot the simulator and launch the app:
  ```
  xcrun simctl boot "iPhone 16" 2>/dev/null; xcrun simctl launch --console-stdout booted <bundle-identifier>
  ```
  Determine the bundle identifier from the project's `Info.plist` or build settings.

- **macOS**: Run the built binary directly from the derived data build products directory, or use `open` on the `.app` bundle.

Report the result to the user.
