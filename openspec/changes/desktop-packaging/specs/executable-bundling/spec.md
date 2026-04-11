## ADDED Requirements

### Requirement: PyInstaller spec file configuration
The system SHALL include a PyInstaller `.spec` file that configures the build process for the application, including entry point, hidden imports, data files, and icon.

#### Scenario: Build executable from spec file
- **WHEN** developer runs `pyinstaller api-finance-dashboard.spec`
- **THEN** PyInstaller SHALL produce a `dist/api-finance-dashboard/` directory containing the executable and all dependencies

#### Scenario: Application icon embedded
- **WHEN** the executable is built
- **THEN** the resulting `.exe` file SHALL display the project logo (`logo/logo.png` converted to `.ico`) as its icon

### Requirement: PySide6 Qt plugins bundled correctly
The system SHALL ensure all required PySide6 Qt plugins (platforms, imageformats, styles) are included in the build output.

#### Scenario: Application launches on clean Windows system
- **WHEN** a user runs the built executable on a Windows machine without Python or PySide6 installed
- **THEN** the application SHALL start and display the main window without Qt plugin errors

### Requirement: Hidden imports resolved
The system SHALL explicitly declare all hidden imports that PyInstaller cannot auto-detect (e.g., `plyer.platforms.win.notification`).

#### Scenario: All features functional after bundling
- **WHEN** the bundled application runs notification, database, and scraping features
- **THEN** all features SHALL work identically to the development environment with no `ModuleNotFoundError`

### Requirement: Playwright runtime handling
The system SHALL NOT bundle Playwright browser binaries into the executable. Instead, it SHALL check for browsers at startup and guide the user to install them if missing.

#### Scenario: First launch without Playwright browsers
- **WHEN** the user launches the application for the first time and no Playwright-compatible browser is found
- **THEN** the application SHALL display a dialog explaining the need for browser installation and offer to run `playwright install chromium` automatically

#### Scenario: First launch with system Chrome/Edge available
- **WHEN** the user launches the application and a compatible system Chrome or Edge browser is detected
- **THEN** the application SHALL use the detected browser as a fallback without requiring Playwright browser download

### Requirement: Build script for local development
The system SHALL include a `scripts/build.py` script that automates the full build process (icon conversion, PyInstaller build).

#### Scenario: Developer runs build script
- **WHEN** a developer runs `python scripts/build.py`
- **THEN** the script SHALL produce the packaged application in the `dist/` directory ready for installer creation
