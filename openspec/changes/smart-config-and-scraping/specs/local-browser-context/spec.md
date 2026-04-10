## MODIFIED Requirements

### Requirement: Browser profile path configuration
The system SHALL allow users to configure the browser profile either by selecting a desktop browser shortcut file (primary method) or by manually entering the user data directory path (fallback method). The system SHALL persist the resolved path and detected browser type in local configuration.

#### Scenario: User configures via shortcut selection
- **WHEN** user selects a browser shortcut file from the file dialog
- **THEN** system parses the shortcut, extracts the browser type and user data directory path
- **AND** displays the detected configuration for user confirmation
- **AND** saves the confirmed path and browser type

#### Scenario: User configures via manual path input
- **WHEN** user switches to manual input mode and enters a valid browser user data directory path
- **THEN** system saves the path and displays confirmation

#### Scenario: Invalid browser shortcut
- **WHEN** user selects a file that is not a valid browser shortcut or the parsed browser is not supported
- **THEN** system displays an error message and suggests using manual input

## ADDED Requirements

### Requirement: Browser type persistence
The system SHALL store the detected browser type (chrome, edge, chromium) in the settings table alongside the browser profile path. This enables future optimizations based on browser type.

#### Scenario: Save browser type
- **WHEN** system detects Chrome from a shortcut file
- **THEN** system stores `browser_type = "chrome"` in the settings table

#### Scenario: Retrieve browser type
- **WHEN** application reads the browser configuration
- **THEN** system returns both the profile path and the browser type
