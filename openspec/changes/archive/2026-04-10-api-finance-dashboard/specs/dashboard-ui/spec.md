## ADDED Requirements

### Requirement: Top dashboard with net profit display
The system SHALL display today's net profit in large green font at the top of the main window, formatted as `￥ / $ XXX.XX`. Below the profit, a small hint SHALL show the formula: (主站总消耗 - 上游总消耗). The dashboard SHALL include a prominent "Start Inspection" button and text showing the last inspection timestamp.

#### Scenario: Dashboard after successful inspection
- **WHEN** inspection completes with calculated net profit of ￥42.40
- **THEN** dashboard displays "￥42.40" in large green font
- **AND** shows last inspection time
- **AND** "Start Inspection" button returns to enabled state

### Requirement: Upstream health status list
The system SHALL display a table or card list of all configured upstream sites with columns: Site Name | Today's Consumption | Current Balance | Status. Status indicators SHALL follow color coding rules.

#### Scenario: Healthy upstream display
- **WHEN** upstream balance ($10.00) is above threshold ($5.00)
- **THEN** status column shows green "正常" badge

#### Scenario: Low balance upstream display
- **WHEN** upstream balance ($3.00) is at or below threshold ($5.00)
- **THEN** entire row has red background and status shows "额度告急"

#### Scenario: Failed scraping display
- **WHEN** scraping fails for an upstream site (page unreachable or login required)
- **THEN** status shows yellow "需核实" badge

### Requirement: Inspection progress feedback
During inspection, the UI SHALL display a loading indicator or progress bar. The UI main thread SHALL NOT freeze during the inspection process.

#### Scenario: Inspection in progress
- **WHEN** user clicks "Start Inspection"
- **THEN** button becomes disabled, a progress indicator appears
- **AND** UI remains responsive to user interaction (e.g., scrolling, window resize)

#### Scenario: Inspection completes
- **WHEN** all sites have been inspected
- **THEN** progress indicator disappears, results are displayed, and summary report is highlighted

### Requirement: Site management settings panel
The system SHALL provide a settings panel (sidebar or modal) for managing site configurations. Users SHALL be able to add, edit, and delete sites. Each site form SHALL include: site type (main/upstream), URL, panel type (dropdown with presets or custom), CSS selector, regex pattern, and alert threshold (for upstream sites only).

#### Scenario: Add new upstream site
- **WHEN** user fills in site name, URL, selects panel type "New API", sets threshold to $5.00
- **THEN** system saves the configuration and the site appears in the health status list

#### Scenario: Edit existing site
- **WHEN** user modifies the URL of an existing site and saves
- **THEN** system updates the configuration and uses the new URL on next inspection

#### Scenario: Delete site
- **WHEN** user deletes a site from the settings
- **THEN** system removes it from configuration and it no longer appears in the health list
