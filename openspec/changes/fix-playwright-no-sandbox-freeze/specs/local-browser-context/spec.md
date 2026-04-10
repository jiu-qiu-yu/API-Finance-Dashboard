## MODIFIED Requirements

### Requirement: Cookie-based session reuse
The system SHALL launch Playwright with the `user-data-dir` parameter pointing to the user's real browser profile, so that existing login cookies are automatically available. The system SHALL use an installed local Chrome or Edge executable for persistent-context startup and MUST NOT fall back to Playwright bundled Chromium when opening the user's profile. The system SHALL NOT require users to input any account credentials.

#### Scenario: Successful session reuse
- **WHEN** system opens an upstream panel URL using the configured browser profile
- **AND** the user has previously logged in via their regular browser
- **THEN** the page loads in an authenticated state without any login prompt

#### Scenario: Expired session detection
- **WHEN** system opens a panel URL but the session cookie has expired
- **THEN** the scraping result for that site is marked as "needs verification" status

#### Scenario: Installed browser executable missing
- **WHEN** the system cannot resolve a supported local Chrome or Edge executable for persistent-context startup
- **THEN** the system aborts browser startup
- **AND** shows an error instructing the user to install or auto-detect a supported browser

### Requirement: Browser process conflict detection
The system SHALL detect if the target browser is currently running with the same user data directory. If a conflict is detected, the system SHALL notify the user to close the browser or use a separate profile. The system SHALL also prevent startup with unsupported local-desktop launch flags, including `--no-sandbox`, when reusing the user's real browser profile.

#### Scenario: Browser already running
- **WHEN** user clicks "Start Inspection" but Chrome/Edge is running with the same profile
- **THEN** system displays a warning asking user to close the browser before proceeding

#### Scenario: Unsupported sandbox flag requested
- **WHEN** startup arguments for a local desktop browser profile include `--no-sandbox`
- **THEN** the system removes or rejects that argument before launch
- **AND** avoids opening the browser in a degraded unsupported mode
