## ADDED Requirements

### Requirement: PreScrapeAction data model
The system SHALL define a `PreScrapeAction` frozen dataclass with the following fields:
- `action_type`: string enum, one of `"click"`, `"select_option"`, `"wait"`
- `selector`: CSS selector string to target the element
- `value`: optional string parameter (used as option value for `select_option`, or milliseconds for `wait`)

#### Scenario: Valid click action
- **WHEN** a `PreScrapeAction` is created with `action_type="click"` and `selector=".date-picker-btn"`
- **THEN** the action object SHALL be a valid frozen dataclass instance with `value=None`

#### Scenario: Valid select_option action
- **WHEN** a `PreScrapeAction` is created with `action_type="select_option"`, `selector=".time-range select"`, and `value="today"`
- **THEN** the action object SHALL store all three fields correctly

### Requirement: PanelPreset supports pre-scrape actions
The `PanelPreset` dataclass SHALL include an optional `pre_scrape_actions` field of type `tuple[PreScrapeAction, ...]`, defaulting to an empty tuple.

#### Scenario: Preset without pre-scrape actions
- **WHEN** a `PanelPreset` is created without specifying `pre_scrape_actions`
- **THEN** `pre_scrape_actions` SHALL default to an empty tuple `()`

#### Scenario: Preset with pre-scrape actions
- **WHEN** a `PanelPreset` is created with a list of `PreScrapeAction` instances
- **THEN** `pre_scrape_actions` SHALL contain the configured actions in order

### Requirement: Execute pre-scrape actions before data extraction
The `ScrapingEngine` SHALL execute all `pre_scrape_actions` from the active preset after page load completes and before data extraction begins.

#### Scenario: Click action execution
- **WHEN** a pre-scrape action with `action_type="click"` is encountered
- **THEN** the engine SHALL click the element matching the CSS selector and wait for the page to settle (network idle or brief timeout)

#### Scenario: Select option action execution
- **WHEN** a pre-scrape action with `action_type="select_option"` is encountered
- **THEN** the engine SHALL select the option with the matching value in the element identified by the CSS selector

#### Scenario: Wait action execution
- **WHEN** a pre-scrape action with `action_type="wait"` is encountered
- **THEN** the engine SHALL wait for the specified duration in milliseconds (from the `value` field)

### Requirement: Pre-scrape action failure is non-fatal
If any pre-scrape action fails (element not found, timeout, etc.), the engine SHALL log a warning and continue with data extraction using the current page state.

#### Scenario: Action target element not found
- **WHEN** a pre-scrape action's CSS selector matches no element on the page
- **THEN** the engine SHALL skip that action, log a warning, and proceed to the next action or data extraction

#### Scenario: Action timeout
- **WHEN** a pre-scrape action exceeds a reasonable timeout (5 seconds)
- **THEN** the engine SHALL skip that action, log a warning, and continue
