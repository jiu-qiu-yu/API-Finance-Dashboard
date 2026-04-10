## ADDED Requirements

### Requirement: Browser shortcut file parsing
The system SHALL support parsing desktop browser shortcut files to automatically detect the browser type and user data directory path. On Windows, the system SHALL parse `.lnk` shortcut files using PowerShell COM objects. On macOS, the system SHALL parse `.app` bundles by reading `Contents/Info.plist`.

#### Scenario: Parse Windows .lnk shortcut
- **WHEN** user selects a Chrome `.lnk` shortcut file from the file dialog
- **THEN** system extracts `TargetPath` (browser executable) and `Arguments` (including `--user-data-dir` if present) from the shortcut
- **AND** identifies the browser type as Chrome, Edge, or Chromium based on the executable name

#### Scenario: Parse macOS .app bundle
- **WHEN** user selects a browser `.app` bundle from the file dialog
- **THEN** system reads `CFBundleIdentifier` from `Info.plist` to identify browser type
- **AND** infers the default user data directory path based on the browser type (e.g., `~/Library/Application Support/Google/Chrome`)

#### Scenario: Shortcut with custom profile path
- **WHEN** a Windows `.lnk` shortcut contains `--user-data-dir=C:\custom\path` in its arguments
- **THEN** system extracts and uses `C:\custom\path` as the user data directory instead of the default path

### Requirement: Browser type detection
The system SHALL identify the browser type (Chrome, Edge, Chromium) from the parsed shortcut and display it to the user for confirmation. The detected browser type SHALL determine the default user data directory path when not explicitly specified in the shortcut.

#### Scenario: Default profile path inference
- **WHEN** system detects the browser as Google Chrome on Windows and no custom `--user-data-dir` is specified
- **THEN** system infers the default path as `%LOCALAPPDATA%\Google\Chrome\User Data`

#### Scenario: Edge browser detection
- **WHEN** system detects the browser as Microsoft Edge
- **THEN** system infers the default path as `%LOCALAPPDATA%\Microsoft\Edge\User Data` on Windows or `~/Library/Application Support/Microsoft Edge` on macOS

### Requirement: File dialog filter
The system SHALL present a file selection dialog filtered to browser shortcut files. On Windows, the filter SHALL show `.lnk` files. On macOS, the filter SHALL show `.app` bundles. The default directory SHALL be the user's desktop.

#### Scenario: Windows file dialog
- **WHEN** user clicks the browser selection button on Windows
- **THEN** system opens a file dialog with filter "Browser Shortcuts (*.lnk)" starting from the Desktop directory

#### Scenario: macOS file dialog
- **WHEN** user clicks the browser selection button on macOS
- **THEN** system opens a file dialog with filter "Applications (*.app)" starting from `/Applications`

### Requirement: Manual path input fallback
The system SHALL retain the existing manual path input field as a fallback option when automatic detection is not possible or the user prefers manual entry.

#### Scenario: Switch to manual input
- **WHEN** user clicks "手动输入" (Manual Input) link below the browser selection button
- **THEN** system shows the existing path text field and browse button for manual entry
