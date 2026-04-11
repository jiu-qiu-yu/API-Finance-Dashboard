## MODIFIED Requirements

### Requirement: Preset rule dictionary
The system SHALL include preset scraping rules for common panels (New API, Sub2API, CAP). Each preset SHALL define panel-specific CSS selectors, anchor rules, keywords, and pre-scrape actions that match the actual DOM structure of the target panel.

#### Scenario: Sub2API preset pre-scrape actions switch to today
- **WHEN** system executes pre-scrape actions for a Sub2API site on the usage page
- **THEN** system SHALL click the `.date-picker-trigger` element to open the date picker
- **AND** system SHALL click the option containing text "今天" or "今日" or "Today" to select today's date range
- **AND** system SHALL wait for data to refresh before extracting values

#### Scenario: Sub2API consumption extraction from usage page
- **WHEN** system extracts consumption from a Sub2API usage page (`/usage`)
- **AND** the date range has been switched to today
- **THEN** system SHALL locate the "总消费" anchor text and extract the adjacent monetary value

#### Scenario: Sub2API balance extraction from dashboard page
- **WHEN** system extracts balance from a Sub2API dashboard page (`/dashboard`)
- **THEN** system SHALL locate the "余额" anchor text and extract the adjacent monetary value

#### Scenario: User selects Sub2API preset panel type
- **WHEN** user selects "Sub2API" from the panel type dropdown when adding a site
- **THEN** system auto-fills the CSS selectors, anchor rules, and pre-scrape actions for Sub2API

## ADDED Requirements

### Requirement: Text-based click pre-scrape action
The system SHALL support a `text_click` pre-scrape action type that locates an element by its visible text content and clicks it. The `selector` field SHALL contain comma-separated candidate texts to match against.

#### Scenario: Text click with exact match
- **WHEN** a `text_click` pre-scrape action is executed with selector "今天,今日,Today"
- **AND** a visible element on the page contains the text "今天"
- **THEN** system SHALL click that element

#### Scenario: Text click with no match
- **WHEN** a `text_click` pre-scrape action is executed
- **AND** no visible element matches any candidate text
- **THEN** system SHALL log a warning and continue without failing

#### Scenario: Text click tries candidates in order
- **WHEN** a `text_click` pre-scrape action has multiple candidate texts
- **THEN** system SHALL try each candidate in order and click the first matching element
