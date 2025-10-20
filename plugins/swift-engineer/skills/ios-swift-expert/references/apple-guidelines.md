# Apple Guidelines & Resources

Authoritative sources for iOS and macOS development best practices.

## Official Documentation

- **Apple Developer Documentation**: https://developer.apple.com/documentation/
- **Swift Language Guide**: https://docs.swift.org/swift-book/
- **Human Interface Guidelines**: https://developer.apple.com/design/human-interface-guidelines/
- **Swift API Design Guidelines**: https://www.swift.org/documentation/api-design-guidelines/
- **WWDC Videos**: https://developer.apple.com/videos/

## Human Interface Guidelines

Follow platform conventions for:
- Navigation patterns and controls
- Interactions and gestures
- Dynamic Type for accessibility
- Privacy preferences handling
- Multitasking and background modes

## Swift API Design Guidelines

Key principles:
- Clarity at the point of use
- Naming that makes code read like prose
- Prefer methods and properties over free functions
- Omit needless words
- Compensate for weak type information

## Privacy & Security

Best practices:
- Request permissions with clear purpose strings
- Handle user data securely (Keychain for credentials)
- Use App Transport Security (HTTPS by default)
- Implement Face ID/Touch ID for sensitive operations
- Follow privacy manifests requirements (iOS 17+)

## Accessibility

Requirements:
- Add accessibility labels and hints
- Support VoiceOver navigation
- Test with Accessibility Inspector
- Support Dynamic Type and larger text sizes
- Ensure sufficient color contrast

## Localization

Guidelines:
- Use `NSLocalizedString` for user-facing text
- Support right-to-left languages
- Externalize date/number formatting
- Test with pseudo-localization
