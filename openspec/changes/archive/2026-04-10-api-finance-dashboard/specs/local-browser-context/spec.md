## ADDED Requirements

### Requirement: Browser profile path configuration
The system SHALL allow users to specify the local browser (Chrome/Edge) user data directory path. The system SHALL persist this path in local configuration and reuse it for all subsequent automation tasks.

#### Scenario: User configures browser profile path
- **WHEN** user enters a valid browser user data directory path in settings
- **THEN** system saves the path and displays confirmation

#### Scenario: Invalid browser profile path
- **WHEN** user enters a non-existent or invalid path
- **THEN** system displays an error message indicating the path is invalid

### Requirement: Cookie-based session reuse
The system SHALL launch Playwright with the `user-data-dir` parameter pointing to the user's real browser profile, so that existing login cookies are automatically available. The system SHALL NOT require users to input any account credentials.

#### Scenario: Successful session reuse
- **WHEN** system opens an upstream panel URL using the configured browser profile
- **AND** the user has previously logged in via their regular browser
- **THEN** the page loads in an authenticated state without any login prompt

#### Scenario: Expired session detection
- **WHEN** system opens a panel URL but the session cookie has expired
- **THEN** the scraping result for that site is marked as "needs verification" status

### Requirement: Browser process conflict detection
The system SHALL detect if the target browser is currently running with the same user data directory. If a conflict is detected, the system SHALL notify the user to close the browser or use a separate profile.

#### Scenario: Browser already running
- **WHEN** user clicks "Start Inspection" but Chrome/Edge is running with the same profile
- **THEN** system displays a warning asking user to close the browser before proceeding
