## ADDED Requirements

### Requirement: Three-tier scraping strategy
The system SHALL implement a three-tier data extraction strategy executed in order: (1) CSS selector precise matching, (2) DOM anchor text search with adjacency traversal, (3) keyword proximity with value format validation. The system SHALL proceed to the next tier only when the current tier fails to extract a valid monetary value.

#### Scenario: Tier 1 CSS selector success
- **WHEN** the configured CSS selector matches a DOM element containing a valid monetary value
- **THEN** system extracts the value and skips tiers 2 and 3

#### Scenario: Tier 1 fails, Tier 2 anchor success
- **WHEN** CSS selector fails to match or returns no valid monetary value
- **AND** a DOM element containing the anchor text (e.g., "今日消耗") is found on the page
- **THEN** system searches adjacent DOM nodes (siblings, parent's siblings, up to 3 levels) for a monetary value
- **AND** extracts the first valid monetary value found

#### Scenario: All tiers fail
- **WHEN** all three tiers fail to extract a valid value
- **THEN** system marks the site result with status NEEDS_CHECK and an error message describing which tiers were attempted

### Requirement: DOM anchor text search
The system SHALL locate a DOM element whose text content matches one of the configured anchor texts (e.g., "今日消耗", "Today Usage"). From that anchor element, the system SHALL search for monetary values in adjacent DOM nodes within a configurable maximum depth (default 3 levels).

#### Scenario: Anchor found with adjacent value
- **WHEN** a `<span>` element containing "今日消耗" is found
- **AND** a sibling `<span>` element contains "$12.50"
- **THEN** system extracts `12.50` as the consumption value with currency USD

#### Scenario: Anchor found with nested value
- **WHEN** a `<div>` element containing "余额" is found
- **AND** a child element 2 levels deep contains "¥88.00"
- **THEN** system extracts `88.00` as the balance value with currency CNY

#### Scenario: Anchor found but no adjacent value
- **WHEN** anchor text is found but no valid monetary value exists within the configured DOM depth
- **THEN** system falls through to tier 3 (keyword proximity)

### Requirement: AnchorRule data model
Each anchor rule SHALL be defined as an immutable dataclass containing: target field (consumption or balance), anchor texts tuple, optional relative CSS selector from anchor, and maximum DOM search depth (default 3).

#### Scenario: AnchorRule with relative CSS selector
- **WHEN** an anchor rule defines `value_css` as `"+ .value"` (adjacent sibling with class value)
- **THEN** system first attempts this relative selector from the anchor element before falling back to DOM traversal

### Requirement: Enhanced keyword proximity validation
The tier 3 keyword proximity extraction SHALL validate extracted values against expected format: monetary values MUST contain at most 2 decimal places, MUST be non-negative, and MUST be within a reasonable range (0 to 1,000,000). Values outside this range SHALL be discarded.

#### Scenario: Value format validation passes
- **WHEN** keyword proximity finds "12.50" near the keyword "今日消耗"
- **AND** the value is non-negative and within the valid range
- **THEN** system accepts the value as valid

#### Scenario: Value format validation fails
- **WHEN** keyword proximity finds "1234567890.00" near a keyword
- **THEN** system discards this value as out of reasonable range and continues searching

### Requirement: Scraping result metadata
Each successful extraction SHALL record which tier was used (css_selector, anchor_text, or keyword_proximity) in the result metadata, enabling debugging and confidence assessment.

#### Scenario: Result includes extraction method
- **WHEN** system successfully extracts a consumption value using anchor text search (tier 2)
- **THEN** the extraction result includes `method: "anchor_text"` metadata
