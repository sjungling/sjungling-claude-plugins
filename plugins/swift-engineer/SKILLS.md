# Swift Engineer Skills

This document indexes all skills provided by the swift-engineer plugin.

## Overview

The swift-engineer plugin provides automatic expertise for iOS and macOS development through context-aware skills that activate when working with Swift code, Xcode projects, and Apple platform frameworks.

## Skills

### ios-swift-expert

**Location**: `skills/ios-swift-expert/SKILL.md`

**Description**: Elite iOS and macOS development expertise that automatically activates when working with Swift, SwiftUI, UIKit, Xcode, and the entire Apple development ecosystem.

**Automatic Activation Triggers**:
- Working with `.swift` source files
- Opening or modifying Xcode projects (`.xcodeproj`, `.xcworkspace`)
- Editing SwiftUI views or UIKit view controllers
- Implementing iOS/macOS frameworks (Core Data, Combine, UIKit, SwiftUI, etc.)
- Debugging Xcode build errors or runtime issues
- Designing app architectures (MVVM, MVI, Clean Architecture)
- Optimizing performance or fixing memory leaks
- Implementing accessibility, localization, or privacy features

**Core Expertise Areas**:
- **Swift Language**: Modern Swift features, concurrency (async/await, actors), memory management (ARC, weak/unowned), error handling, type safety
- **SwiftUI**: Declarative UI, state management (@State, @Binding, @Observable), layouts, animations, navigation
- **UIKit**: View controllers, Auto Layout, table/collection views, gestures, Core Animation
- **iOS Frameworks**: Core Data, Combine, Core Location, CloudKit, StoreKit, HealthKit, ARKit, RealityKit
- **Xcode & Build System**: Project configuration, build settings, debugging tools, testing (XCTest), Swift Package Manager
- **App Architecture**: MVVM, MVI, Clean Architecture, coordinator pattern, dependency injection

**Usage Examples**:

1. **SwiftUI Layout Issues**:
   ```
   My SwiftUI view isn't displaying correctly - the text is getting cut off
   ```
   The skill automatically provides expert SwiftUI debugging guidance.

2. **Core Data Implementation**:
   ```
   I need to add data persistence to my iOS app using Core Data
   ```
   The skill guides through Core Data setup with modern concurrency patterns.

3. **Xcode Build Errors**:
   ```
   My Xcode project won't build - getting linker errors
   ```
   The skill systematically diagnoses and resolves build issues.

4. **Performance Optimization**:
   ```
   My app is running slowly - help optimize performance
   ```
   The skill profiles with Instruments and suggests architectural improvements.

**Development Workflow**:
- Always verifies builds using `xcodebuild -quiet` after changes
- Follows Swift API Design Guidelines and Human Interface Guidelines
- Ensures code is memory-safe, performant, and accessible
- Provides testable implementations with dependency injection
- References official Apple documentation and WWDC sessions

**When NOT to Use**:
- General programming unrelated to Apple platforms
- Backend server development (unless Vapor/Swift on server)
- Cross-platform mobile (React Native, Flutter)
- Web development (unless WebKit/Safari specific)
- Android development

## Integration with Commands

The ios-swift-expert skill works seamlessly with the `/swift-lint` command:

1. Skill provides Swift development expertise
2. `/swift-lint` command formats code according to Swift standards
3. Skill validates builds after formatting changes

## Quick Start

1. **Install the plugin**:
   ```
   /plugin install swift-engineer@claude-plugins
   ```

2. **Open a Swift file** - the skill activates automatically:
   ```swift
   // Claude detects .swift file and loads ios-swift-expert skill
   import SwiftUI

   struct ContentView: View {
       var body: some View {
           Text("Hello, World!")
       }
   }
   ```

3. **Ask for help** - no manual invocation needed:
   ```
   How can I add animation to this view?
   ```

## Reference Materials

The skill references these authoritative sources:
- [Swift Language Guide](https://docs.swift.org/swift-book/)
- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)
- [WWDC Videos](https://developer.apple.com/videos/)

## Success Criteria

The skill is working successfully when:
- Code builds successfully with `xcodebuild -quiet`
- Solutions follow Apple's Human Interface Guidelines
- Implementations are memory-safe and performant
- Code adheres to Swift API Design Guidelines
- Solutions are testable and maintainable
- Proper error handling is implemented
- Accessibility and localization are considered

## Version History

- **2.0.0**: Converted from agent to skill pattern for automatic activation
- **1.0.0**: Initial agent-based implementation
