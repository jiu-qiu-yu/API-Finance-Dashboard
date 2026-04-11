## ADDED Requirements

### Requirement: GitHub Actions workflow for release builds
The system SHALL include a GitHub Actions workflow (`.github/workflows/release.yml`) that builds and publishes the installer when a version tag is pushed.

#### Scenario: Tag push triggers build
- **WHEN** a git tag matching `v*` pattern (e.g., `v0.1.0`) is pushed to the repository
- **THEN** the GitHub Actions workflow SHALL trigger and execute the full build pipeline

#### Scenario: Build pipeline completes successfully
- **WHEN** the workflow runs on `windows-latest` runner
- **THEN** it SHALL install Python dependencies, run PyInstaller, run Inno Setup, and produce the installer artifact

### Requirement: Automatic GitHub Release creation
The workflow SHALL create a GitHub Release with the installer attached when the build succeeds.

#### Scenario: Release published with installer
- **WHEN** the build pipeline completes successfully
- **THEN** a GitHub Release SHALL be created with the tag name as the release title
- **AND** the installer `.exe` file SHALL be attached as a release asset

### Requirement: Build artifact caching
The workflow SHALL cache pip dependencies to speed up subsequent builds.

#### Scenario: Cached dependencies used
- **WHEN** the workflow runs and pip dependencies have not changed since last run
- **THEN** the workflow SHALL restore dependencies from cache instead of downloading them

### Requirement: Version consistency
The workflow SHALL extract the version from `pyproject.toml` and use it consistently across the build (PyInstaller, Inno Setup, Release name).

#### Scenario: Version matches across all outputs
- **WHEN** `pyproject.toml` specifies version `0.2.0` and tag `v0.2.0` is pushed
- **THEN** the installer filename, file properties, and GitHub Release title SHALL all reflect version `0.2.0`
