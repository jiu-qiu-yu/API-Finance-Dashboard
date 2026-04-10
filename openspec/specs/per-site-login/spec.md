### Requirement: Per-site login via automation browser
The system SHALL provide a "Login to this site" button in the site edit form, placed alongside the existing "Test Scrape" button. Clicking it SHALL launch the real Chrome/Edge browser using the dedicated automation profile, navigating to that site's URL for the user to manually log in.

#### Scenario: User logs in to a new site
- **WHEN** user clicks "Login to this site" for a site with URL `https://panel-a.com/log`
- **THEN** the system SHALL launch Chrome/Edge with `user_data_dir` set to the automation profile directory
- **AND** navigate to `https://panel-a.com/log`
- **AND** the user manually logs in as they would in a normal browser

#### Scenario: User closes browser after login
- **WHEN** user finishes logging in and closes the automation browser window
- **THEN** the system SHALL automatically execute a test scrape for that site to verify login success

#### Scenario: Auto test scrape succeeds after login
- **WHEN** the automatic test scrape after login completes successfully
- **THEN** the system SHALL display the scrape result (e.g., "Today's consumption: $12.50")

#### Scenario: Auto test scrape fails after login
- **WHEN** the automatic test scrape after login fails (e.g., session not detected)
- **THEN** the system SHALL display the failure result
- **AND** the user can click "Login to this site" again to retry

#### Scenario: Browser launch failure during login
- **WHEN** the browser fails to launch (e.g., executable not found)
- **THEN** the system SHALL display a clear error message in Chinese

### Requirement: Per-site re-login for expired sessions
The system SHALL allow users to click "Login to this site" at any time to refresh an expired login session. No prior initialization state is required.

#### Scenario: Re-login after session expiry
- **WHEN** a previously working site's test scrape now fails
- **AND** user clicks "Login to this site"
- **THEN** the system SHALL launch the browser with the existing automation profile (preserving other sites' login state)
- **AND** navigate to that site's URL for re-login

#### Scenario: Multiple sites with different accounts
- **WHEN** user has logged in to site A with account-A and site B with account-B
- **AND** site A's session expires
- **THEN** re-logging in to site A SHALL NOT affect site B's login state (cookies are domain-scoped)

### Requirement: Login URL source
The "Login to this site" action SHALL use the site's configured URL from the site edit form.

#### Scenario: URL read from form input
- **WHEN** user clicks "Login to this site"
- **THEN** the system SHALL read the URL from the site edit form's URL input field
- **AND** if the URL is empty, display a warning asking the user to fill in the URL first
