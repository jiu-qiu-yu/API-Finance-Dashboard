## ADDED Requirements

### Requirement: Automation profile directory management
The system SHALL maintain a dedicated browser profile directory exclusively for automation purposes, located at `<app_data>/automation_profile/` following platform conventions. The directory SHALL be separate from the user's daily browser User Data directory.

#### Scenario: Automation profile auto-created on first use
- **WHEN** a user triggers "Login to this site" or "Test Scrape" and the automation profile directory does not exist
- **THEN** the system SHALL automatically create the directory before launching the browser

#### Scenario: Automation profile reset
- **WHEN** user clicks "Reset Automation Browser" in global settings
- **AND** confirms the reset action
- **THEN** the system SHALL delete the existing automation profile directory and re-create an empty one

### Requirement: Automation profile path configuration
The system SHALL persist the automation profile directory path in the configuration store via `automation_profile_path`. The path SHALL be automatically determined based on platform conventions and displayed as read-only in global settings.

#### Scenario: Path displayed in global settings
- **WHEN** user opens global settings
- **THEN** the automation browser section displays the current automation profile path as read-only text

#### Scenario: Path auto-resolved on first access
- **WHEN** `automation_profile_path` is not yet stored in configuration
- **THEN** the system SHALL resolve and persist the platform-specific default path
