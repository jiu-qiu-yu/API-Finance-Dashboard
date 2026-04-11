## MODIFIED Requirements

### Requirement: Settings dialog title and naming
The settings dialog SHALL be titled "配置" instead of "设置" to accurately reflect its primary function of configuring sites.

#### Scenario: User opens configuration dialog
- **WHEN** user clicks the settings/configuration button
- **THEN** the dialog window title SHALL display "配置"

### Requirement: Add site form behavior
The system SHALL clear the edit form and reset to default values when the user clicks the "添加" button, before the user fills in new site data.

#### Scenario: Add site clears form
- **WHEN** user clicks the "添加" button
- **THEN** the form SHALL be cleared with defaults: panel type "new-api", currency "USD", alert threshold 10.00
- **AND** the site list selection SHALL be deselected

#### Scenario: Add site with panel type hint
- **WHEN** user selects a panel type in the add form
- **THEN** the URL labels and placeholders SHALL update to match the selected panel type

### Requirement: Delete site list behavior
The system SHALL automatically select an adjacent site in the list after deletion to maintain operation continuity.

#### Scenario: Delete site selects previous item
- **WHEN** user deletes a site that is not the first in the list
- **THEN** the system SHALL select the previous site in the list

#### Scenario: Delete site selects first item when first is deleted
- **WHEN** user deletes the first site in the list and other sites exist
- **THEN** the system SHALL select the new first site in the list

#### Scenario: Delete last remaining site clears form
- **WHEN** user deletes the only remaining site
- **THEN** the form SHALL be cleared to default values
