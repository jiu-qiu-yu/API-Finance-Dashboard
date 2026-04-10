## MODIFIED Requirements

### Requirement: Site configuration CRUD operations
The system SHALL support Create, Read, Update, and Delete operations for site configurations. Each site record SHALL include: id, name, type (main/upstream), url, panel_type, css_selector, regex_pattern, currency, alert_threshold, dashboard_url, created_at, updated_at. The `dashboard_url` field SHALL be optional (nullable) and is only applicable to UPSTREAM type sites.

#### Scenario: Create upstream site with dashboard URL
- **WHEN** user adds a new upstream site with url "https://example.com/log" and dashboard_url "https://example.com/dashboard"
- **THEN** system inserts a new record with both URLs stored

#### Scenario: Create main site without dashboard URL
- **WHEN** user adds a new main site with url "https://mysite.com/log"
- **THEN** system inserts a new record with dashboard_url as NULL

#### Scenario: Read all site configurations
- **WHEN** application loads or user opens the site list
- **THEN** system retrieves all site records ordered by type (main sites first) then name

#### Scenario: Update site configuration
- **WHEN** user modifies a site's URL and saves
- **THEN** system updates the record and sets updated_at to current timestamp

#### Scenario: Delete site configuration
- **WHEN** user deletes a site
- **THEN** system removes the record from the database

## ADDED Requirements

### Requirement: Database schema migration for dashboard_url
The system SHALL add a `dashboard_url TEXT` column to the `sites` table during application startup if it does not already exist. The migration SHALL preserve all existing data. The schema version SHALL be incremented.

#### Scenario: Migration on existing database
- **WHEN** application starts with a database that lacks the `dashboard_url` column
- **THEN** system executes `ALTER TABLE sites ADD COLUMN dashboard_url TEXT`
- **AND** all existing records have `dashboard_url` set to NULL
- **AND** schema version is updated

#### Scenario: Migration already applied
- **WHEN** application starts with a database that already has the `dashboard_url` column
- **THEN** system skips the migration
