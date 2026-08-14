# iOS Development Code Examples

Complete implementation examples for common iOS and macOS development patterns.

Default to UIKit for iOS/iPadOS and AppKit for macOS; reach for SwiftUI where the platform requires it or a single view is clearly simpler. The MVVM view model below is UI-framework agnostic — the SwiftUI, UIKit, and AppKit examples all bind to the same `UserProfileViewModel`.

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

## UIKit View Controller with MVVM (iOS/iPadOS — Preferred)

The same `UserProfileViewModel` above is UI-framework agnostic. A UIKit view controller observes it and drives `UIView`s directly. Use `withObservationTracking` (Observation framework) to re-render on `@Observable` changes without Combine.

```swift
import UIKit
import Observation

final class UserProfileViewController: UIViewController {
    private let viewModel: UserProfileViewModel

    private let avatarView: UIImageView = {
        let view = UIImageView()
        view.contentMode = .scaleAspectFill
        view.clipsToBounds = true
        view.layer.cornerRadius = 50
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()

    private let nameLabel: UILabel = {
        let label = UILabel()
        label.font = .preferredFont(forTextStyle: .title1)
        label.adjustsFontForContentSizeCategory = true
        label.accessibilityTraits = .header
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let spinner = UIActivityIndicatorView(style: .medium)

    init(viewModel: UserProfileViewModel = UserProfileViewModel()) {
        self.viewModel = viewModel
        super.init(nibName: nil, bundle: nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError("init(coder:) has not been implemented") }

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Profile"
        view.backgroundColor = .systemBackground
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            systemItem: .done,
            primaryAction: UIAction { [weak self] _ in self?.dismiss(animated: true) }
        )
        setUpLayout()
        observeViewModel()
    }

    override func viewIsAppearing(_ animated: Bool) {
        super.viewIsAppearing(animated)
        Task { await viewModel.loadProfile() }
    }

    private func setUpLayout() {
        [avatarView, nameLabel, spinner].forEach(view.addSubview)
        spinner.translatesAutoresizingMaskIntoConstraints = false

        NSLayoutConstraint.activate([
            avatarView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16),
            avatarView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            avatarView.widthAnchor.constraint(equalToConstant: 100),
            avatarView.heightAnchor.constraint(equalToConstant: 100),

            nameLabel.topAnchor.constraint(equalTo: avatarView.bottomAnchor, constant: 16),
            nameLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),

            spinner.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            spinner.centerYAnchor.constraint(equalTo: view.centerYAnchor),
        ])
    }

    // Re-registers on every change so subsequent mutations keep firing.
    private func observeViewModel() {
        withObservationTracking {
            render()
        } onChange: { [weak self] in
            Task { @MainActor in self?.observeViewModel() }
        }
    }

    private func render() {
        nameLabel.text = viewModel.userName
        viewModel.isLoading ? spinner.startAnimating() : spinner.stopAnimating()
        // avatarView image would be set via an async image loader keyed on viewModel.avatarURL
    }
}
```

## UIKit List with Diffable Data Source

For collection/table content, prefer `UICollectionViewDiffableDataSource` (or the table equivalent) over manual `reloadData()` — it animates changes and avoids index-math bugs.

```swift
import UIKit

final class UserListViewController: UICollectionViewController {
    enum Section { case main }

    private lazy var dataSource = makeDataSource()

    init() {
        var config = UICollectionLayoutListConfiguration(appearance: .insetGrouped)
        config.headerMode = .none
        let layout = UICollectionViewCompositionalLayout.list(using: config)
        super.init(collectionViewLayout: layout)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError("init(coder:) has not been implemented") }

    override func viewDidLoad() {
        super.viewDidLoad()
        collectionView.dataSource = dataSource
    }

    private func makeDataSource() -> UICollectionViewDiffableDataSource<Section, UserProfile.ID> {
        let registration = UICollectionView.CellRegistration<UICollectionViewListCell, UserProfile> { cell, _, user in
            var content = cell.defaultContentConfiguration()
            content.text = user.name
            cell.contentConfiguration = content
        }
        return UICollectionViewDiffableDataSource(collectionView: collectionView) { collectionView, indexPath, id in
            let user = // look up UserProfile by id from your store
            collectionView.dequeueConfiguredReusableCell(using: registration, for: indexPath, item: user)
        }
    }

    func apply(_ users: [UserProfile], animatingDifferences: Bool = true) {
        var snapshot = NSDiffableDataSourceSnapshot<Section, UserProfile.ID>()
        snapshot.appendSections([.main])
        snapshot.appendItems(users.map(\.id))
        dataSource.apply(snapshot, animatingDifferences: animatingDifferences)
    }
}
```

## AppKit View Controller with MVVM (macOS — Preferred)

The identical view model drives an `NSViewController`. AppKit uses `NSStackView` and `NSImageView`/`NSTextField` instead of their UIKit equivalents; observation works the same way.

```swift
import AppKit
import Observation

final class UserProfileViewController: NSViewController {
    private let viewModel: UserProfileViewModel

    private let avatarView: NSImageView = {
        let view = NSImageView()
        view.imageScaling = .scaleProportionallyUpOrDown
        view.wantsLayer = true
        view.layer?.cornerRadius = 50
        view.layer?.masksToBounds = true
        return view
    }()

    private let nameField: NSTextField = {
        let field = NSTextField(labelWithString: "")
        field.font = .preferredFont(forTextStyle: .title1)
        field.setAccessibilityRole(.staticText)
        return field
    }()

    private let spinner: NSProgressIndicator = {
        let indicator = NSProgressIndicator()
        indicator.style = .spinning
        indicator.isDisplayedWhenStopped = false
        return indicator
    }()

    init(viewModel: UserProfileViewModel = UserProfileViewModel()) {
        self.viewModel = viewModel
        super.init(nibName: nil, bundle: nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError("init(coder:) has not been implemented") }

    override func loadView() {
        avatarView.translatesAutoresizingMaskIntoConstraints = false
        let stack = NSStackView(views: [avatarView, nameField, spinner])
        stack.orientation = .vertical
        stack.spacing = 16
        stack.alignment = .centerX
        stack.edgeInsets = NSEdgeInsets(top: 24, left: 24, bottom: 24, right: 24)
        view = stack

        NSLayoutConstraint.activate([
            avatarView.widthAnchor.constraint(equalToConstant: 100),
            avatarView.heightAnchor.constraint(equalToConstant: 100),
        ])
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Profile"
        observeViewModel()
    }

    override func viewWillAppear() {
        super.viewWillAppear()
        Task { await viewModel.loadProfile() }
    }

    private func observeViewModel() {
        withObservationTracking {
            render()
        } onChange: { [weak self] in
            Task { @MainActor in self?.observeViewModel() }
        }
    }

    private func render() {
        nameField.stringValue = viewModel.userName
        viewModel.isLoading ? spinner.startAnimation(nil) : spinner.stopAnimation(nil)
    }
}
```

## Hosting SwiftUI Inside UIKit/AppKit

When a specific view is genuinely simpler in SwiftUI, host it inside the native shell — the app stays UIKit/AppKit-first.

```swift
import UIKit
import SwiftUI

// A small, self-contained SwiftUI view used for one screen.
struct RatingView: View {
    let stars: Int
    var body: some View {
        HStack {
            ForEach(0..<5) { index in
                Image(systemName: index < stars ? "star.fill" : "star")
            }
        }
    }
}

extension UserProfileViewController {
    func embedRating(_ stars: Int) {
        let hosting = UIHostingController(rootView: RatingView(stars: stars))
        addChild(hosting)
        hosting.view.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(hosting.view)
        hosting.didMove(toParent: self)
        // pin hosting.view with Auto Layout as needed
    }
}

// macOS equivalent: NSHostingController(rootView:) / NSHostingView(rootView:)
```

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
