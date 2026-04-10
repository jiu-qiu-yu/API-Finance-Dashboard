### Requirement: Cookie-based session reuse
The system SHALL launch Playwright with the `user-data-dir` parameter pointing to the dedicated automation profile directory (NOT the user's daily browser profile). The system SHALL NOT require users to input any account credentials. The automation profile SHALL contain login state persisted from prior manual logins via the "Login to this site" action. Since each site uses cookies scoped to its own domain, multiple sites with different accounts coexist in the same profile without interference.

#### Scenario: Successful session reuse via automation profile
- **WHEN** system opens a panel URL using the automation profile
- **AND** the user has previously logged in to that site via "Login to this site"
- **THEN** the page loads in an authenticated state without any login prompt

#### Scenario: Expired session detection
- **WHEN** system opens a panel URL but the session cookie has expired
- **THEN** the scraping result for that site SHALL indicate failure
- **AND** the user can use "Login to this site" to re-login

#### Scenario: Site never logged in
- **WHEN** user runs test scrape or inspection for a site that was never logged in via automation browser
- **THEN** the scrape SHALL fail with an appropriate error (e.g., login page detected)
- **AND** the user can use "Login to this site" to perform the initial login

### Requirement: Browser process conflict detection
The system SHALL detect if the automation browser is currently running with the same automation profile directory. If a conflict is detected, the system SHALL notify the user to close the automation browser before proceeding. The user's daily browser running with its own profile SHALL NOT be treated as a conflict.

#### Scenario: Automation browser still running
- **WHEN** user clicks "Test Scrape" or "Start Inspection" but the automation browser is running with the automation profile
- **THEN** system displays a warning asking user to close the automation browser before proceeding

#### Scenario: Daily browser does not conflict
- **WHEN** user's daily Chrome/Edge is running with its own User Data directory
- **AND** user starts test scrape or inspection using the separate automation profile
- **THEN** system SHALL proceed without conflict since the profiles are in separate directories

### Requirement: Browser profile path configuration
The system SHALL automatically manage the automation browser profile path. Users SHALL NOT need to manually select a browser profile or User Data directory for automation. The path is determined by platform conventions and displayed as read-only in global settings.

#### Scenario: No manual profile selection needed
- **WHEN** user opens global settings
- **THEN** the automation browser section displays the path as read-only
- **AND** there is no profile dropdown selector for automation
