## MODIFIED Requirements

### Requirement: CSS selector extraction mode
The system SHALL support extracting monetary values from web pages using CSS selectors. Each preset MAY define multiple CSS selectors in priority order. The system SHALL try each selector in order and use the first one that returns a valid monetary value.

#### Scenario: First selector succeeds
- **WHEN** system tries the first CSS selector in the list and it matches a valid monetary value
- **THEN** system uses that value and skips remaining selectors

#### Scenario: First selector fails, second succeeds
- **WHEN** the first CSS selector fails but the second matches a valid monetary value
- **THEN** system uses the value from the second selector

#### Scenario: All CSS selectors fail
- **WHEN** no CSS selector in the list matches a valid monetary value
- **THEN** system falls back to anchor text search (tier 2)

### Requirement: Regex fallback extraction mode
The system SHALL support a regex fallback mode (tier 3) that scans the full page text for monetary values near keywords. The extracted values SHALL be validated against format constraints: non-negative, at most 2 decimal places, and within range 0 to 1,000,000.

#### Scenario: Regex extraction with validation
- **WHEN** anchor text search (tier 2) fails
- **THEN** system scans page text using regex patterns near relevant keywords
- **AND** validates each candidate value against format constraints before accepting

#### Scenario: No value found by any method
- **WHEN** all three tiers fail to find a valid value
- **THEN** system marks the site result as NEEDS_CHECK with an error message listing attempted methods

### Requirement: Preset rule dictionary
The system SHALL include preset scraping rules for common panels including New API, One API, One Hub, Chat Nio, and Uni API. Users SHALL be able to select a panel type from a dropdown to auto-fill CSS selectors, keywords, and anchor rules.

#### Scenario: User selects preset panel type
- **WHEN** user selects "New API" from the panel type dropdown when adding a site
- **THEN** system auto-fills the CSS selectors, regex patterns, and anchor rules for that panel type

## ADDED Requirements

### Requirement: Dual URL scraping for upstream sites
The system SHALL scrape UPSTREAM sites using two separate page visits: the usage log URL (`url` field) for today's consumption, and the dashboard URL (`dashboard_url` field) for remaining balance. If `dashboard_url` is not configured, the system SHALL attempt to extract both values from the usage log URL.

#### Scenario: Upstream with both URLs configured
- **WHEN** system scrapes an UPSTREAM site with both `url` and `dashboard_url` set
- **THEN** system visits `url` to extract consumption value
- **AND** visits `dashboard_url` to extract balance value

#### Scenario: Upstream with only usage log URL
- **WHEN** system scrapes an UPSTREAM site where `dashboard_url` is NULL
- **THEN** system visits `url` and attempts to extract both consumption and balance from the same page

### Requirement: Test scraping preview
The system SHALL provide a "test scrape" function accessible from the site edit form. This function SHALL execute the full scraping pipeline against the configured URL(s) and display the extracted values, extraction method used (tier), and any errors to the user before saving.

#### Scenario: Successful test scrape
- **WHEN** user clicks "测试抓取" (Test Scrape) button after configuring a site's URL and panel type
- **AND** browser profile is configured
- **THEN** system opens the URL, runs the three-tier extraction, and displays the result in a dialog showing: extracted value(s), which tier matched, and the raw text around the match

#### Scenario: Test scrape with unconfigured browser
- **WHEN** user clicks "测试抓取" but no browser profile is configured
- **THEN** system shows a warning message: "请先配置浏览器" (Please configure browser first)

#### Scenario: Test scrape failure
- **WHEN** test scrape executes but all extraction tiers fail
- **THEN** system displays the failure details with suggestions (check URL, check if page requires login, try different panel type)
