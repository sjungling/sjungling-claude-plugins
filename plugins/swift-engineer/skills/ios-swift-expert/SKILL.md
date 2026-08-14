---
name: ios-swift-expert
description: This skill should be used when the user asks to "build an iOS app", "build a macOS app", "create a view controller", "create a SwiftUI view", "fix Xcode build errors", "implement Core Data", "design app architecture", or "optimize Swift performance". Automatically activates when working with .swift files, Xcode projects (.xcodeproj, .xcworkspace), UIKit or AppKit interfaces, SwiftUI views, or Apple platform frameworks (Core Data, Combine, WidgetKit, App Intents). Not for cross-platform frameworks (React Native, Flutter), non-Apple platforms, or backend server development.
---

# iOS and macOS Development Expert

## Overview

Elite-level guidance for iOS and macOS development with deep expertise in Swift, UIKit, AppKit, SwiftUI, and the entire Apple development ecosystem.

**Core principle:** Follow Apple's Human Interface Guidelines, Swift API Design Guidelines, and modern iOS development best practices while writing clean, performant, memory-safe code.

## When to Use

Automatically activates when:
- Working with `.swift` source files
- Opening or modifying Xcode projects (`.xcodeproj`, `.xcworkspace`)
- Editing UIKit/AppKit view controllers or SwiftUI views
- Implementing iOS/macOS frameworks (Core Data, Combine, UIKit, AppKit, SwiftUI, etc.)
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

Broad expertise across the Apple development ecosystem: Swift language, UIKit, AppKit, SwiftUI, all major Apple frameworks (Core Data, Combine, CloudKit, StoreKit, HealthKit, ARKit, etc.), Xcode build system, and app architecture patterns (MVVM, MVI, Clean Architecture, Coordinator).

### Decision Frameworks

**UI Framework Selection:**
- iOS/iPadOS apps: prefer UIKit as the primary UI framework
- macOS apps: prefer AppKit as the primary UI framework
- Match the existing codebase: if a project is already SwiftUI-based, stay consistent rather than mixing paradigms
- Use SwiftUI where the platform requires it (widgets, Live Activities, watchOS, App Intents UI) or for simple, self-contained views where it clearly reduces effort
- Bridge SwiftUI into UIKit/AppKit via UIHostingController/NSHostingView — host SwiftUI inside the native app shell, not the reverse

**State Management (when working in SwiftUI code):**
- @State: local value types
- @StateObject: reference types created by the view
- @EnvironmentObject: dependency injection across hierarchy
- @Observable (iOS 17+): preferred for new code

**Concurrency:**
- Use async/await, not completion handlers
- Use actors for shared mutable state
- Use MainActor for UI updates
- Use TaskGroup for parallel work

**Data Persistence:**
- SwiftData (iOS 17+): preferred for new projects
- Core Data: existing projects or compatibility needs
- Keychain: credentials and sensitive data only

**Architecture:**
- MVVM + Coordinator: default for UIKit/AppKit apps
- MVVM: default for SwiftUI code
- Clean Architecture: multi-team projects with heavy testing

## Development Workflow

### 1. Build Verification

Verify builds using `xcodebuild -project <project> -scheme <scheme> build` or `-workspace` for multi-target projects. Use the `-quiet` flag to suppress verbose output. Check exit code to confirm success.

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

**Performance Profiling:**

Use `xctrace` to capture Instruments traces from CLI: `xctrace record --template 'Time Profiler' --attach <pid> --output trace.trace --time-limit 10s`. Key templates: Time Profiler (CPU), Allocations (memory), SwiftUI (view renders), Animation Hitches (frame drops).

See `./references/debugging-strategies.md` for detailed profiling workflows and analysis patterns.

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
| Force-unwrapping optionals | Use `guard let`, `if let`, or `??` |
| Expensive work in SwiftUI `body` | Move to `.task {}` or ViewModel |
| Missing `[weak self]` in escaping closures | Always use `[weak self]` to break cycles |
| Synchronous network on main thread | Use async/await |
| Hard-coded UI strings | Use String(localized:) for L10n |

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
