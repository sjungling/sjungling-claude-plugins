# iOS Development Code Examples

Complete implementation examples for common iOS and macOS development patterns.

## SwiftUI View with Proper State Management

```swift
import SwiftUI

struct UserProfileView: View {
    @StateObject private var viewModel = UserProfileViewModel()
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // Profile content
                    AsyncImage(url: viewModel.avatarURL) { image in
                        image
                            .resizable()
                            .scaledToFill()
                    } placeholder: {
                        ProgressView()
                    }
                    .frame(width: 100, height: 100)
                    .clipShape(Circle())

                    Text(viewModel.userName)
                        .font(.title)
                        .accessibilityAddTraits(.isHeader)
                }
                .padding()
            }
            .navigationTitle("Profile")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .task {
                await viewModel.loadProfile()
            }
        }
    }
}
```

## MVVM ViewModel with Async/Await (ObservableObject - pre-iOS 17)

```swift
import Foundation
import Combine

@MainActor
final class UserProfileViewModel: ObservableObject {
    @Published private(set) var userName: String = ""
    @Published private(set) var avatarURL: URL?
    @Published private(set) var isLoading = false
    @Published private(set) var error: Error?

    private let userService: UserServiceProtocol

    init(userService: UserServiceProtocol = UserService()) {
        self.userService = userService
    }

    func loadProfile() async {
        isLoading = true
        error = nil

        do {
            let profile = try await userService.fetchCurrentUser()
            userName = profile.name
            avatarURL = profile.avatarURL
        } catch {
            self.error = error
        }

        isLoading = false
    }
}

// Protocol for dependency injection and testing
protocol UserServiceProtocol {
    func fetchCurrentUser() async throws -> UserProfile
}
```

## MVVM ViewModel with @Observable (iOS 17+ - Preferred)

```swift
import Foundation
import Observation

@Observable
@MainActor
final class UserProfileViewModel {
    private(set) var userName: String = ""
    private(set) var avatarURL: URL?
    private(set) var isLoading = false
    private(set) var error: Error?

    private let userService: UserServiceProtocol

    init(userService: UserServiceProtocol = UserService()) {
        self.userService = userService
    }

    func loadProfile() async {
        isLoading = true
        error = nil

        do {
            let profile = try await userService.fetchCurrentUser()
            userName = profile.name
            avatarURL = profile.avatarURL
        } catch {
            self.error = error
        }

        isLoading = false
    }
}
```

### SwiftUI View using @Observable ViewModel (iOS 17+)

```swift
import SwiftUI

struct UserProfileView: View {
    // No property wrapper needed - just a regular property
    // @Observable automatically tracks access within body
    var viewModel = UserProfileViewModel()

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    AsyncImage(url: viewModel.avatarURL) { image in
                        image
                            .resizable()
                            .scaledToFill()
                    } placeholder: {
                        ProgressView()
                    }
                    .frame(width: 100, height: 100)
                    .clipShape(Circle())

                    Text(viewModel.userName)
                        .font(.title)
                        .accessibilityAddTraits(.isHeader)
                }
                .padding()
            }
            .navigationTitle("Profile")
            .task {
                await viewModel.loadProfile()
            }
        }
    }
}
```

### Migration Notes: ObservableObject to @Observable

| Before (ObservableObject) | After (@Observable) |
|--------------------------|---------------------|
| `class VM: ObservableObject` | `@Observable class VM` |
| `@Published var name` | `var name` (tracked automatically) |
| `@StateObject private var vm = VM()` | `@State private var vm = VM()` |
| `@ObservedObject var vm` | `var vm` (or `@Bindable var vm` for bindings) |
| `@EnvironmentObject var vm` | `@Environment(VM.self) var vm` |

## Core Data Stack with Modern Concurrency

```swift
import CoreData

final class PersistenceController {
    static let shared = PersistenceController()

    let container: NSPersistentContainer

    private init() {
        container = NSPersistentContainer(name: "AppModel")
        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("Unable to load persistent stores: \(error)")
            }
        }
        container.viewContext.automaticallyMergesChangesFromParent = true
    }

    func save() async throws {
        let context = container.viewContext
        guard context.hasChanges else { return }

        try await context.perform {
            try context.save()
        }
    }

    func backgroundContext() -> NSManagedObjectContext {
        let context = container.newBackgroundContext()
        context.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        return context
    }
}
```

## Proper Memory Management with Closures

```swift
import UIKit

final class DataManager {
    private var completionHandlers: [String: (Result<Data, Error>) -> Void] = [:]

    func fetchData(forKey key: String, completion: @escaping (Result<Data, Error>) -> Void) {
        completionHandlers[key] = completion

        URLSession.shared.dataTask(with: URL(string: "https://example.com")!) { [weak self] data, response, error in
            guard let self = self else { return }

            if let error = error {
                self.completionHandlers[key]?(.failure(error))
            } else if let data = data {
                self.completionHandlers[key]?(.success(data))
            }

            self.completionHandlers[key] = nil
        }.resume()
    }
}
```
