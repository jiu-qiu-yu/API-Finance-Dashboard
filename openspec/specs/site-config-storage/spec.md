## ADDED Requirements

### Requirement: SQLite-based site configuration storage
The system SHALL use a local SQLite database to persist all site configurations, scraping rules, and application settings. The database file SHALL be stored in the application's data directory.

#### Scenario: First launch database initialization
- **WHEN** application launches for the first time
- **THEN** system creates the SQLite database with required tables (sites, settings)

### Requirement: Site configuration CRUD operations
The system SHALL support Create, Read, Update, and Delete operations for site configurations. Each site record SHALL include: id, name, type (main/upstream), url, panel_type, css_selector, regex_pattern, currency, alert_threshold, created_at, updated_at.

#### Scenario: Create site configuration
- **WHEN** user adds a new site with all required fields
- **THEN** system inserts a new record in the sites table with a unique id and timestamps

#### Scenario: Read all site configurations
- **WHEN** application loads or user opens the site list
- **THEN** system retrieves all site records ordered by type (main sites first) then name

#### Scenario: Update site configuration
- **WHEN** user modifies a site's URL and saves
- **THEN** system updates the record and sets updated_at to current timestamp

#### Scenario: Delete site configuration
- **WHEN** user deletes a site
- **THEN** system removes the record from the database

### Requirement: Application settings storage
The system SHALL store global settings in the same SQLite database, including: browser profile path, exchange rate, preferred display currency. Settings SHALL be stored as key-value pairs.

#### Scenario: Save and retrieve exchange rate
- **WHEN** user sets exchange rate to 7.2
- **THEN** system stores `exchange_rate = 7.2` in settings table
- **AND** subsequent reads return `7.2`

### Requirement: Data integrity
The system SHALL use database transactions for write operations. The system SHALL handle concurrent access gracefully (single-writer model since this is a single-user desktop app).

#### Scenario: Interrupted write recovery
- **WHEN** application crashes during a write operation
- **THEN** database remains in a consistent state with no partial writes
