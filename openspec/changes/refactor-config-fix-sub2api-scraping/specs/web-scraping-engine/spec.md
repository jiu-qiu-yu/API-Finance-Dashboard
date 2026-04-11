## MODIFIED Requirements

### Requirement: Monetary value validation
The system SHALL validate extracted monetary values as non-negative, within range (≤ 1,000,000), and with no more than 6 decimal places. Values with up to 6 decimal places SHALL be accepted to support API billing precision (e.g., $0.0015, $0.000123).

#### Scenario: Value with 4 decimal places is valid
- **WHEN** the scraping engine extracts a value of $0.0015
- **THEN** the system SHALL accept it as a valid monetary value

#### Scenario: Value with 6 decimal places is valid
- **WHEN** the scraping engine extracts a value of $0.000123
- **THEN** the system SHALL accept it as a valid monetary value

#### Scenario: Value with 7+ decimal places is rejected
- **WHEN** the scraping engine extracts a value with more than 6 decimal places
- **THEN** the system SHALL reject it as invalid

#### Scenario: Value with 2 decimal places is valid
- **WHEN** the scraping engine extracts a value of $1.67
- **THEN** the system SHALL accept it as a valid monetary value

### Requirement: Preset rule dictionary
The system SHALL include preset scraping rules for common panels (New API, Sub2API, CAP). Each preset SHALL define panel-specific CSS selectors, anchor rules, keywords, and pre-scrape actions that match the actual DOM structure of the target panel.

#### Scenario: Sub2API consumption extraction from dashboard
- **WHEN** system extracts consumption from a Sub2API dashboard page (`/dashboard`)
- **THEN** system SHALL locate the "今日消费" anchor text and extract the adjacent monetary value from the purple card
- **AND** the CSS selector SHALL target `p.text-xl span.text-purple-600[title]` to match only the today's actual cost (not the total or standard cost)

#### Scenario: Sub2API balance extraction from dashboard
- **WHEN** system extracts balance from a Sub2API dashboard page (`/dashboard`)
- **THEN** system SHALL locate the "余额" anchor text and extract the adjacent monetary value from the emerald card
- **AND** the CSS selector SHALL target `p.text-emerald-600.text-xl` to match the balance value

#### Scenario: Sub2API single-page extraction
- **WHEN** user configures a Sub2API site with dashboard URL as the main URL and no separate dashboard_url
- **THEN** system SHALL extract both consumption and balance from the same dashboard page without any pre-scrape actions
