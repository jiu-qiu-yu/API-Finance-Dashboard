## MODIFIED Requirements

### Requirement: CSS selector extraction mode
The system SHALL support extracting monetary values from web pages using CSS selectors. Users SHALL be able to configure a CSS selector per site that targets the DOM element containing the desired value. The system SHALL only begin selector waiting after browser startup diagnostics confirm that the page is running in the intended site context rather than a browser warning or startup failure page.

#### Scenario: Successful CSS selector extraction
- **WHEN** system navigates to a configured site URL
- **AND** the CSS selector matches a DOM element
- **THEN** system extracts the text content and parses the monetary value

#### Scenario: CSS selector match failure
- **WHEN** the configured CSS selector matches no element on the page
- **THEN** system falls back to regex extraction mode

#### Scenario: Startup diagnostics fail before extraction
- **WHEN** browser startup diagnostics determine the page is blocked by an unsupported launch warning or startup failure
- **THEN** the system stops the scrape attempt before selector waiting
- **AND** reports a launch-related error instead of a selector timeout
