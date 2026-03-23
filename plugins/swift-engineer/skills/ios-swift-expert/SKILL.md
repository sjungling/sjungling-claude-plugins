---
name: ios-swift-expert
description: This skill should be used when the user asks to "build an iOS app", "create a SwiftUI view", "fix Xcode build errors", "implement Core Data", "design app architecture", or "optimize Swift performance". Automatically activates when working with .swift files, Xcode projects (.xcodeproj, .xcworkspace), SwiftUI interfaces, or Apple platform frameworks (UIKit, Core Data, Combine, WidgetKit, App Intents). Not for cross-platform frameworks (React Native, Flutter), non-Apple platforms, or backend server development.
---

# iOS and macOS Development Expert

## Overview

Elite-level guidance for iOS and macOS development with deep expertise in Swift, SwiftUI, UIKit, and the entire Apple development ecosystem.

**Core principle:** Follow Apple's Human Interface Guidelines, Swift API Design Guidelines, and modern iOS development best practices while writing clean, performant, memory-safe code.

## When to Use

Automatically activates when:
- Working with `.swift` source files
- Opening or modifying Xcode projects (`.xcodeproj`, `.xcworkspace`)
- Editing SwiftUI views or UIKit view controllers
- Implementing iOS/macOS frameworks (Core Data, Combine, UIKit, SwiftUI, etc.)
- Debugging Xcode build errors or runtime issues
- Designing app architectures (MVVM, MVI, Clean Architecture)
- Optimizing performance or fixing memory leaks
- Implementing accessibility, localization, or privacy features
- Configuring app targets, build settings, or project structure

Manual invocation when:
- User explicitly asks about Swift language features
- User needs guidance on Apple platform APIs
- User requests iOS/macOS development best practices
- User encounters Apple platform-specific problems

## When NOT to Use This Skill

Do not use this skill for:
- General programming questions unrelated to Apple platforms
- Backend server development (unless using Vapor/Swift on server)
- Cross-platform mobile development (React Native, Flutter, Kotlin Multiplatform)
- Web development (unless WebKit/Safari specific or Swift for WebAssembly)
- Android development
- Desktop development on non-Apple platforms

## Core Expertise

Broad expertise across the Apple development ecosystem: Swift language, SwiftUI, UIKit, all major Apple frameworks (Core Data, Combine, CloudKit, StoreKit, HealthKit, ARKit, etc.), Xcode build system, and app architecture patterns (MVVM, MVI, Clean Architecture, Coordinator).

### Decision Frameworks

**SwiftUI vs UIKit:**
- Prefer SwiftUI for new views unless targeting iOS <15 or needing UIKit-specific features (complex gesture recognizers, MapKit annotations pre-iOS 17, advanced collection view layouts)
- Use UIViewRepresentable to bridge UIKit into SwiftUI, not the reverse

**State Management:**
- @State: view-local value types
- @StateObject: view-owned reference types (create here)
- @ObservedObject: passed-in reference types (created elsewhere)
- @EnvironmentObject: dependency injection across view hierarchy
- @Observable (iOS 17+): preferred over ObservableObject for new code

**Concurrency:**
- Prefer async/await over completion handlers for new code
- Use actors for mutable shared state, not DispatchQueue
- Use TaskGroup for parallel async work, not DispatchGroup
- MainActor for UI updates, not DispatchQueue.main

**Data Persistence:**
- SwiftData (iOS 17+): preferred for new projects
- Core Data: existing projects or pre-iOS 17 targets
- UserDefaults: small preferences only, never large data
- Keychain: credentials and sensitive data

**Architecture Patterns:**
- MVVM: default choice for SwiftUI apps, ViewModel as @Observable
- MVI: when unidirectional data flow is critical (complex state machines)
- Clean Architecture: large teams, multiple data sources, heavy testing requirements
- Coordinator: complex navigation flows that span multiple screens

## Development Workflow

### 1. Build Verification

**Always verify builds** after making changes using `xcodebuild`:

```bash
xcodebuild -project YourProject.xcodeproj -scheme YourScheme -quiet build
```

- Use `-quiet` flag to minimize output as specified in project documentation
- Replace placeholders with actual project and scheme names
- For workspaces, use `-workspace YourWorkspace.xcworkspace`
- Check exit code to confirm success

### 2. Code Standards

Follow Swift API Design Guidelines. Key conventions:
- `UpperCamelCase` for types, `lowerCamelCase` for functions/variables
- Default to `private`; only expose what's needed
- Use `// MARK: -` to organize: properties, init, lifecycle, public, private
- Use `[weak self]` in escaping closures; break retain cycles between parent/child

### 3. Testing Requirements

Write testable code with appropriate coverage:

**Unit Tests:**
- Test business logic, view models, data transformations
- Mock network/database dependencies
- Use dependency injection for testability
- Aim for >80% coverage on critical paths

**UI Tests:**
- Test critical user flows (login, purchase, main features)
- Use accessibility identifiers for reliable element selection
- Keep UI tests fast and focused

### 4. Performance Considerations

Optimize for user experience:

**Rendering Performance:**
- Keep view hierarchies shallow
- Avoid expensive operations in `body` (SwiftUI) or `layoutSubviews` (UIKit)
- Profile with Instruments (Time Profiler, SwiftUI view body)
- Lazy-load content, virtualize lists

**Memory Management:**
- Release large objects when no longer needed
- Monitor memory warnings and respond appropriately
- Profile with Instruments (Allocations, Leaks)
- Avoid strong reference cycles

**Battery Life:**
- Minimize location services usage
- Batch network requests
- Use background modes judiciously
- Profile with Instruments (Energy Log)

**CLI Performance Profiling with xctrace:**

Use `xctrace` to capture Instruments traces from the command line without opening the Instruments GUI. This enables Claude to diagnose performance issues directly.

```bash
# List available profiling templates
xctrace list templates

# Record a Time Profiler trace against a running app (by PID or process name)
xctrace record --template 'Time Profiler' --attach <pid-or-process-name> --output trace.trace --time-limit 10s

# Record against a launched process
xctrace record --template 'Time Profiler' --launch -- /path/to/app --args

# Record with Allocations template for memory profiling
xctrace record --template 'Allocations' --attach <pid-or-process-name> --output alloc.trace --time-limit 10s

# Record on a specific device (simulator or physical)
xctrace record --template 'Time Profiler' --device <device-name-or-udid> --attach <process> --output trace.trace

# Export trace data to XML for analysis
xctrace export --input trace.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="time-profile"]'

# List available devices
xctrace list devices
```

Key templates for common scenarios:
- **Time Profiler**: CPU usage, hot code paths, main thread stalls
- **Allocations**: Memory usage, allocation patterns, leaks
- **Leaks**: Detect retain cycles and leaked objects
- **SwiftUI**: View body evaluations and redraw frequency (Xcode 15+)
- **Animation Hitches**: Dropped frames and rendering stalls
- **Network**: HTTP request timing and payload sizes
- **Energy Log**: Battery drain and power-intensive operations

See `./references/debugging-strategies.md` for detailed xctrace workflows.

### 5. Apple Platform Best Practices

Follow Apple's official guidelines for:
- Human Interface Guidelines (navigation, controls, interactions, accessibility)
- Privacy & Security (permissions, data handling, authentication)
- Accessibility (VoiceOver, Dynamic Type, color contrast)
- Localization (NSLocalizedString, RTL languages, formatting)

See `./references/apple-guidelines.md` for detailed requirements and best practices.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using @ObservedObject when @StateObject is needed | @StateObject for objects created by the view; @ObservedObject for objects passed in |
| Force-unwrapping optionals (`!`) | Use `guard let`, `if let`, or nil-coalescing (`??`) |
| Expensive work in SwiftUI `body` | Move to `.task {}` modifier or ViewModel |
| Missing `[weak self]` in escaping closures | Always use `[weak self]` unless closure is non-escaping |
| Using `ObservableObject` on iOS 17+ | Prefer `@Observable` macro for cleaner code |
| Synchronous network calls on main thread | Use async/await with URLSession |
| Hard-coded strings for localization | Use String(localized:) or NSLocalizedString |

## Problem-Solving Approach

### 1. Analysis Phase

- Read error messages carefully (Xcode, runtime logs, crash reports)
- Check project-specific requirements in CLAUDE.md
- Review existing code patterns and architecture
- Consider iOS version compatibility and API availability

### 2. Solution Design

- Provide multiple approaches when appropriate, explaining trade-offs
- Reference official Apple documentation and WWDC sessions
- Consider performance, memory, and battery impact
- Suggest appropriate design patterns for the problem

### 3. Implementation

- Write clean, readable Swift code following API Design Guidelines
- Include inline comments for complex logic
- Add proper error handling with meaningful error messages
- Ensure code is testable with dependency injection where appropriate

### 4. Validation

- Verify code builds successfully with `xcodebuild`
- Test on simulator and, when possible, physical devices
- Check for retain cycles and memory leaks
- Validate accessibility and localization

## Communication Style

**Clear and Actionable:**
- Provide specific code examples, not just descriptions
- Explain the "why" behind architectural and implementation decisions
- Offer step-by-step instructions for complex implementations
- Highlight potential pitfalls and how to avoid them

**Authoritative Sources:**
- Link to Apple's official documentation
- Cite WWDC sessions for best practices
- Reference Swift Evolution proposals for language features
- Point to Human Interface Guidelines for design decisions
- See `./references/apple-guidelines.md` for documentation links

**Trade-offs:**
- Performance vs. code simplicity
- SwiftUI vs. UIKit for specific use cases
- Async/await vs. completion handlers
- Protocol-oriented vs. class-based design

**Complete implementation examples:** See `./references/code-examples.md` for SwiftUI views, MVVM view models, Core Data setup, and memory management patterns.

**Design patterns and solutions:** See `./references/patterns.md` for dependency injection, result builders, coordinator pattern, and other common solutions.

**Debugging guidance:** See `./references/debugging-strategies.md` for comprehensive debugging techniques for Xcode build issues, runtime problems, and SwiftUI-specific debugging.

## Success Criteria

Guidance is successful when:

- Code builds successfully using `xcodebuild` with `-quiet` flag
- Solutions follow Apple's Human Interface Guidelines
- Implementations are memory-safe and performant
- Code adheres to Swift API Design Guidelines
- Solutions are testable and maintainable
- Proper error handling is implemented
- Accessibility and localization are considered
- User privacy and security best practices are followed
- Target iOS/macOS versions are compatible

## Additional Resources

For complete reference materials, see:
- `./references/code-examples.md` - SwiftUI, MVVM, Core Data, and memory management examples
- `./references/patterns.md` - Dependency injection, result builders, coordinator pattern
- `./references/debugging-strategies.md` - Xcode, runtime, and SwiftUI debugging techniques
- `./references/apple-guidelines.md` - Official Apple documentation and guidelines
