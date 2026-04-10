## ADDED Requirements

### Requirement: Extended panel preset library
The system SHALL include built-in scraping presets for the following open-source API management panels: New API, One API, One Hub, Chat Nio (CoAI), Uni API, and Custom. Each preset SHALL contain CSS selectors, keywords, and anchor rules for both consumption and balance data extraction.

#### Scenario: User selects New API preset
- **WHEN** user selects "New API" from the panel type dropdown
- **THEN** system auto-fills consumption selectors, balance selectors, consumption keywords, balance keywords, and anchor rules specific to the New API panel

#### Scenario: User selects Chat Nio preset
- **WHEN** user selects "Chat Nio" from the panel type dropdown
- **THEN** system auto-fills the scraping rules optimized for Chat Nio's dashboard layout

#### Scenario: User selects Custom preset
- **WHEN** user selects "Custom" from the panel type dropdown
- **THEN** system leaves all selector fields empty for manual configuration and uses only generic keyword matching as fallback

### Requirement: Preset data structure
Each panel preset SHALL be defined as a `PanelPreset` containing: name, consumption CSS selectors (ordered list), balance CSS selectors (ordered list), consumption keywords (tuple), balance keywords (tuple), and anchor rules (list of `AnchorRule`).

#### Scenario: Preset with multiple CSS selectors
- **WHEN** a preset defines multiple consumption CSS selectors
- **THEN** system tries each selector in order and uses the first one that matches a valid monetary value

### Requirement: Panel preset display
The panel type dropdown in the site edit form SHALL display the preset name and its associated GitHub project name for identification. The dropdown SHALL be ordered with the most commonly used presets first.

#### Scenario: Dropdown display format
- **WHEN** user opens the panel type dropdown
- **THEN** each option displays in the format "Panel Name (github-org/repo)" except for Custom which shows "Custom (自定义)"
