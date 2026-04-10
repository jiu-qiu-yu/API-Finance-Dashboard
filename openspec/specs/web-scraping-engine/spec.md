## ADDED Requirements

### Requirement: CSS selector extraction mode
The system SHALL support extracting monetary values from web pages using CSS selectors. Users SHALL be able to configure a CSS selector per site that targets the DOM element containing the desired value.

#### Scenario: Successful CSS selector extraction
- **WHEN** system navigates to a configured site URL
- **AND** the CSS selector matches a DOM element
- **THEN** system extracts the text content and parses the monetary value

#### Scenario: CSS selector match failure
- **WHEN** the configured CSS selector matches no element on the page
- **THEN** system falls back to regex extraction mode

### Requirement: Regex fallback extraction mode
The system SHALL support a regex fallback mode that scans the full page text for monetary values near keywords (e.g., "消耗", "Quota", "余额", "Balance"). The regex SHALL match patterns containing `$`, `￥`, or bare floating-point numbers adjacent to these keywords.

#### Scenario: Regex extraction after CSS failure
- **WHEN** CSS selector extraction fails or is not configured
- **THEN** system scans page text using regex patterns to find monetary values near relevant keywords

#### Scenario: No value found by either method
- **WHEN** both CSS selector and regex extraction fail to find a value
- **THEN** system marks the site result as "needs verification" with an appropriate error message

### Requirement: Monetary value data cleaning
The system SHALL normalize all extracted values to plain decimal numbers. Formats such as `$12.50`, `￥88.00`, `12.50 USD`, `88.00 元` SHALL all be cleaned to their numeric value (e.g., `12.50`, `88.00`), preserving the original currency indicator for calculation purposes.

#### Scenario: Various format cleaning
- **WHEN** system extracts a raw string like `$12.50` or `￥88.00` or `12.50 USD`
- **THEN** system produces a numeric value `12.50` or `88.00` with currency type `USD` or `CNY`

### Requirement: Preset rule dictionary
The system SHALL include preset scraping rules for common panels (New API, One API). Users SHALL be able to select a panel type from a dropdown to auto-fill CSS selectors and keywords.

#### Scenario: User selects preset panel type
- **WHEN** user selects "New API" from the panel type dropdown when adding a site
- **THEN** system auto-fills the CSS selector and regex patterns for that panel type
