## ADDED Requirements

### Requirement: Launch diagnostic reporting
The system SHALL detect browser startup failures caused by unsupported launch flags, browser process exit during startup, or incompatible profile startup conditions before beginning scrape extraction.

#### Scenario: Unsupported launch flag detected before launch
- **WHEN** the browser launch configuration contains a flag known to be unsupported for local desktop profile reuse
- **THEN** the system rejects or removes that flag before starting the browser
- **AND** records a diagnostic reason describing the prevented startup issue

#### Scenario: Browser exits during startup
- **WHEN** Playwright reports that the persistent browser context or target page closed during startup
- **THEN** the system classifies the failure as a browser launch error
- **AND** returns a user-facing diagnostic message with actionable next steps

#### Scenario: Startup warning page blocks scraping
- **WHEN** the launched browser displays a warning page caused by launch arguments instead of the intended site content
- **THEN** the system marks the scrape attempt as failed due to launch diagnostics
- **AND** does not continue waiting indefinitely for extraction selectors
