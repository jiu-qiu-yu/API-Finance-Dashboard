## ADDED Requirements

### Requirement: Global exchange rate configuration
The system SHALL allow users to configure a global exchange rate (e.g., `$1 = ￥7.2`). This rate SHALL be used for all currency conversion calculations.

#### Scenario: User sets exchange rate
- **WHEN** user enters an exchange rate of `7.2` for USD to CNY
- **THEN** system persists this setting and uses it for all subsequent calculations

### Requirement: Net profit calculation
The system SHALL calculate today's net profit using the formula: `主站总消耗 - SUM(上游消耗)`. All values MUST be converted to the same currency before subtraction. The result SHALL be displayed in the user's preferred currency.

#### Scenario: Multi-currency profit calculation
- **WHEN** main site consumption is ￥100.00 (CNY)
- **AND** upstream A consumption is $5.00 (USD)
- **AND** upstream B consumption is $3.00 (USD)
- **AND** exchange rate is $1 = ￥7.2
- **THEN** net profit = ￥100.00 - (5.00 + 3.00) × 7.2 = ￥42.40

### Requirement: Decimal precision
All monetary calculations SHALL use Python `Decimal` type with precision to exactly 2 decimal places. The system SHALL NOT use floating-point arithmetic for monetary values to avoid precision errors.

#### Scenario: Precision verification
- **WHEN** system calculates 0.1 + 0.2 in monetary context
- **THEN** result is exactly `0.30`, not `0.30000000000000004`

### Requirement: Partial data handling
When some sites fail to return data, the system SHALL still calculate profit using available data and clearly indicate which sites were excluded from the calculation.

#### Scenario: Calculation with missing data
- **WHEN** 3 upstream sites are configured but 1 fails to return data
- **THEN** system calculates profit using the 2 successful results and displays a warning noting the excluded site
