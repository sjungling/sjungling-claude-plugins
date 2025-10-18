# Swift Engineer Plugin

A Claude Code plugin providing expert iOS and macOS development capabilities through skills and commands.

## What This Plugin Does

This plugin provides comprehensive Swift and Apple platform development expertise that automatically activates when working with iOS/macOS projects.

## Features

### Skills

#### ios-swift-expert
Elite iOS and macOS development expertise that automatically activates when working with:
- `.swift` source files
- Xcode projects (`.xcodeproj`, `.xcworkspace`)
- SwiftUI views and UIKit controllers
- iOS/macOS frameworks (Core Data, Combine, UIKit, SwiftUI, etc.)
- App architecture and design patterns
- Performance optimization and debugging

**Key Capabilities:**
- **Swift Language Mastery**: Modern Swift features, concurrency, memory management
- **SwiftUI Development**: Declarative UI, state management, animations, navigation
- **UIKit**: View controllers, Auto Layout, animations, gesture handling
- **iOS Frameworks**: Core Data, Combine, CloudKit, StoreKit, HealthKit, ARKit
- **Xcode & Build System**: Project configuration, debugging, testing, SPM
- **App Architecture**: MVVM, MVI, Clean Architecture, coordinators

### Commands

#### /swift-lint
Runs swift-format for code formatting and linting on Swift files.

**Usage:**
```
/swift-lint path/to/file.swift
```

This command:
1. Validates swift-format is installed
2. Runs swift-format with configured rules
3. Reports formatting issues or confirms code is properly formatted

## Installation

From your Claude Code marketplace:

```
/plugin install swift-engineer@claude-plugins
```

## Usage

### Automatic Skill Activation

The ios-swift-expert skill automatically activates when:
- Opening `.swift` files
- Working with Xcode projects
- Discussing iOS/macOS development topics

Example interactions:
```
Help me fix this SwiftUI layout issue
```

```
How do I implement Core Data in my iOS app?
```

```
Debug this Xcode build error
```

Claude will automatically use the iOS and macOS development expertise without explicit invocation.

### Manual Command Usage

Use the swift-lint command to format code:

```
/swift-lint Sources/MyApp/ContentView.swift
```

## Plugin Structure

```
swift-engineer/
├── .claude-plugin/
│   └── plugin.json         # Plugin metadata
├── README.md               # This file
├── agents/                 # Legacy agents (deprecated)
│   └── ios-swift-expert.md
├── commands/               # Slash commands
│   └── swift-lint.md
└── skills/                 # Skills (recommended)
    └── ios-swift-expert/
        └── SKILL.md        # Main skill definition
```

## Development Workflow

When Claude uses the ios-swift-expert skill, it will:

1. **Verify Builds**: Run `xcodebuild` with `-quiet` flag after changes
2. **Follow Standards**: Apply Swift API Design Guidelines and Human Interface Guidelines
3. **Write Testable Code**: Use dependency injection and proper architecture
4. **Ensure Quality**: Memory-safe, performant, accessible implementations
5. **Reference Documentation**: Cite Apple docs and WWDC sessions

## Examples

### SwiftUI State Management

When you ask:
```
How do I manage state in this SwiftUI view?
```

Claude will provide expert guidance using:
- @State, @Binding, @StateObject, @ObservedObject
- Proper view model patterns (MVVM)
- Memory-safe closure handling
- Complete, working code examples

### Xcode Build Issues

When you encounter:
```
My Xcode project won't build - getting linker errors
```

Claude will systematically:
- Analyze error messages
- Check build settings and configurations
- Suggest specific solutions
- Verify with `xcodebuild` commands

### Performance Optimization

When you need:
```
My app is running slowly - help optimize performance
```

Claude will:
- Profile with Instruments
- Identify bottlenecks in rendering or memory
- Suggest architectural improvements
- Provide optimized code examples

## When to Use This Plugin

**Use for:**
- Swift language questions and best practices
- SwiftUI and UIKit development
- iOS/macOS framework implementation
- Xcode project configuration and debugging
- App architecture design
- Performance optimization
- Memory management and debugging
- Accessibility and localization
- Privacy and security best practices

**Don't use for:**
- Backend server development (unless Vapor/Swift on server)
- Cross-platform mobile (React Native, Flutter)
- Web development (unless WebKit/Safari specific)
- Android development

## Migration from Agent to Skill

This plugin previously used a subagent pattern (`agents/ios-swift-expert.md`). The agent has been converted to a skill (`skills/ios-swift-expert/SKILL.md`) for automatic activation based on context.

**Advantages of the skill pattern:**
- Automatic activation when working with Swift/iOS files
- No need to manually invoke via Task tool
- Better integration with Claude's context awareness
- More natural workflow for development tasks

The legacy agent file remains for backward compatibility but should not be used for new work.

## Requirements

**For /swift-lint command:**
- swift-format must be installed
- Available via Homebrew: `brew install swift-format`
- Or build from source: https://github.com/apple/swift-format

**For ios-swift-expert skill:**
- No additional tools required
- Works with any Xcode project
- Automatically provides expertise based on context

## How It Works

This plugin follows the Claude Code plugin skills pattern:

- **skills/**: Contains the ios-swift-expert skill that activates automatically
- **SKILL.md**: Includes YAML frontmatter with triggers and comprehensive instructions
- **commands/**: Contains swift-lint command for manual code formatting
- **Progressive activation**: Skill loads when Claude detects Swift/iOS context

## References

- [Swift Language Guide](https://docs.swift.org/swift-book/)
- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)
- [Claude Code Skills](https://docs.claude.com/en/docs/claude-code/skills)
