## ADDED Requirements

### Requirement: Balance threshold configuration
The system SHALL allow users to set a low-balance alert threshold per upstream site (e.g., balance < $5). This threshold SHALL be configurable in the site settings.

#### Scenario: User sets alert threshold
- **WHEN** user configures upstream site with alert threshold of $5.00
- **THEN** system saves the threshold and uses it for post-inspection evaluation

### Requirement: OS native notification on low balance
After each inspection completes, the system SHALL check all upstream balances against their thresholds. If any upstream balance is at or below its threshold, the system SHALL send an OS native notification (Windows Toast / macOS Notification Center) with an audible alert sound.

#### Scenario: Low balance triggers notification
- **WHEN** inspection completes and upstream "ProviderX" has balance $3.00 with threshold $5.00
- **THEN** system sends an OS notification: "额度告急: ProviderX 余额 $3.00，低于阈值 $5.00"
- **AND** notification includes an alert sound

#### Scenario: All balances healthy
- **WHEN** inspection completes and all upstream balances are above their thresholds
- **THEN** system does NOT send any alert notification

### Requirement: Cross-platform notification abstraction
The system SHALL provide a unified notification interface that works on both Windows (Toast notifications) and macOS (Notification Center). Platform differences SHALL be abstracted behind a common Notifier interface.

#### Scenario: Notification on Windows
- **WHEN** alert is triggered on a Windows system
- **THEN** a Windows Toast notification is displayed with title, message, and sound

#### Scenario: Notification on macOS
- **WHEN** alert is triggered on a macOS system
- **THEN** a macOS Notification Center notification is displayed with title, message, and sound
