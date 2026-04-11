## ADDED Requirements

### Requirement: Accurate sub2api consumption selectors
The sub2api `PanelPreset` SHALL use CSS selectors and keywords that specifically target consumption/usage values and SHALL NOT match balance/remaining quota elements.

#### Scenario: Consumption selectors do not match balance elements
- **WHEN** the sub2api preset's `consumption_selectors` are applied to a page containing both consumption and balance values
- **THEN** the selectors SHALL only match elements displaying consumption/usage data, not balance/remaining data

#### Scenario: Consumption keywords are specific to usage
- **WHEN** the sub2api preset's `consumption_keywords` are used for keyword proximity extraction
- **THEN** they SHALL prioritize terms like "已用", "消费", "消耗", "Used", "Cost" and SHALL NOT include ambiguous terms that could match balance context

### Requirement: Sub2api consumption anchor rules accuracy
The sub2api preset's consumption `anchor_rules` SHALL use anchor texts that unambiguously identify consumption labels, avoiding any text that appears near balance display elements.

#### Scenario: Anchor text matches consumption label
- **WHEN** the consumption anchor rule searches for anchor text on a sub2api page
- **THEN** it SHALL find elements labeled with consumption-specific terms (e.g., "已用额度", "总消费", "消费金额") and extract the adjacent numeric value

### Requirement: Sub2api preset includes pre-scrape actions for daily filter
The sub2api `PanelPreset` SHALL include `pre_scrape_actions` that automate selecting the "today" time range on the `/usage` page before data extraction.

#### Scenario: Automatic time range selection to today
- **WHEN** the scraping engine processes a sub2api site
- **THEN** it SHALL execute pre-scrape actions that: (1) click the time range selector, (2) select "today" option, (3) wait for data to refresh

#### Scenario: Fallback when time range selector is unavailable
- **WHEN** the pre-scrape actions fail to find the time range selector on a sub2api page
- **THEN** the engine SHALL proceed with scraping the default page data (7-day total) rather than failing entirely

### Requirement: Remove ambiguous color-class selectors
The sub2api preset SHALL NOT use generic Tailwind CSS color classes (e.g., `.text-green-600`, `.text-emerald-600`) as primary selectors, as these classes are used for styling multiple unrelated data fields.

#### Scenario: No generic color class in consumption selectors
- **WHEN** the sub2api preset's `consumption_selectors` are inspected
- **THEN** they SHALL NOT contain selectors based solely on text color classes like `.text-green-600`
