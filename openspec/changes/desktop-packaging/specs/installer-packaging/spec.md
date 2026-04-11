## ADDED Requirements

### Requirement: Inno Setup installer script
The system SHALL include an Inno Setup script (`installer.iss`) that packages the PyInstaller output into a Windows installer executable.

#### Scenario: Generate installer from Inno Setup script
- **WHEN** developer runs `iscc installer.iss` after PyInstaller build completes
- **THEN** Inno Setup SHALL produce a single `API-Finance-Dashboard-Setup-{version}.exe` installer file in the `dist/` directory

### Requirement: Installation directory and structure
The installer SHALL install the application to `{userappdata}\API Finance Dashboard` by default, with the option for users to choose a custom path.

#### Scenario: Default installation
- **WHEN** user runs the installer and accepts defaults
- **THEN** the application SHALL be installed to the user's AppData directory without requiring administrator privileges

### Requirement: Start menu and desktop shortcuts
The installer SHALL create a Start Menu entry for the application and optionally create a desktop shortcut.

#### Scenario: Shortcuts created after installation
- **WHEN** installation completes successfully
- **THEN** a Start Menu folder "API Finance Dashboard" SHALL exist containing the application shortcut
- **AND** if the user selected the desktop shortcut option, a desktop shortcut SHALL exist

### Requirement: Uninstaller
The installer SHALL register an uninstaller that cleanly removes all installed files, shortcuts, and registry entries.

#### Scenario: Complete uninstallation
- **WHEN** user runs the uninstaller from Add/Remove Programs or the Start Menu
- **THEN** all application files, shortcuts, and registry entries SHALL be removed
- **AND** user data in `~/.api-finance-dashboard/` SHALL NOT be deleted (preserved)

### Requirement: Version information embedded
The installer SHALL embed version information (product name, version number, publisher) readable from file properties.

#### Scenario: Installer file properties
- **WHEN** user right-clicks the installer .exe and views Properties
- **THEN** the file details SHALL show the correct product name, version, and publisher information
