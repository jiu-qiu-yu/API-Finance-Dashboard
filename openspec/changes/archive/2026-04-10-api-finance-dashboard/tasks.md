## 1. Project Scaffolding & Data Layer

- [x] 1.1 Initialize Python project structure (pyproject.toml, src layout, requirements)
- [x] 1.2 Set up SQLite database module with schema (sites table, settings table)
- [x] 1.3 Implement SiteRepository with CRUD operations (create, read, update, delete)
- [x] 1.4 Implement ConfigRepository for key-value settings storage (browser path, exchange rate, currency)
- [x] 1.5 Add database initialization on first launch with migration support

## 2. Local Browser Context Engine

- [x] 2.1 Implement browser profile path validation (check Chrome/Edge user-data-dir exists)
- [x] 2.2 Implement browser process conflict detection (check if Chrome/Edge is running with same profile)
- [x] 2.3 Create BrowserEngine class that launches Playwright with user-data-dir parameter
- [x] 2.4 Implement session validity detection (detect login page / expired cookie scenarios)

## 3. Web Scraping & Parsing Engine

- [x] 3.1 Build preset rule dictionary for common panels (New API, One API CSS selectors and keywords)
- [x] 3.2 Implement CSS selector extraction mode (navigate to URL, wait for element, extract text)
- [x] 3.3 Implement regex fallback extraction mode (scan full page text for monetary values near keywords)
- [x] 3.4 Implement monetary value data cleaner (normalize $12.50, ￥88.00, 12.50 USD → Decimal + currency)
- [x] 3.5 Create ScrapingEngine class that orchestrates CSS → regex fallback pipeline per site

## 4. Finance Calculation & Alert System

- [x] 4.1 Implement exchange rate conversion logic using Decimal arithmetic
- [x] 4.2 Implement net profit calculator (main site consumption - sum of upstream consumption)
- [x] 4.3 Handle partial data scenarios (exclude failed sites, show warnings)
- [x] 4.4 Implement cross-platform Notifier interface (Windows Toast / macOS Notification Center)
- [x] 4.5 Implement post-inspection alert check (compare balances against thresholds, trigger notifications)

## 5. Inspection Service (Orchestration)

- [x] 5.1 Create InspectionService that coordinates BrowserEngine + ScrapingEngine across all configured sites
- [x] 5.2 Implement sequential site inspection with per-site error handling and status tracking
- [x] 5.3 Integrate CalculationEngine to compute net profit after all sites are scraped
- [x] 5.4 Integrate AlertService to check thresholds and send notifications post-inspection

## 6. PySide6 UI - Main Window & Dashboard

- [x] 6.1 Set up PySide6 application entry point and main window scaffold
- [x] 6.2 Build top dashboard widget (net profit display in large green font, formula hint, last inspection time)
- [x] 6.3 Build "Start Inspection" button with disabled state during inspection
- [x] 6.4 Implement QThread worker for running inspection in background without freezing UI
- [x] 6.5 Add progress indicator / loading bar during inspection

## 7. PySide6 UI - Status List & Settings

- [x] 7.1 Build upstream health status table/card list (name, consumption, balance, status with color coding)
- [x] 7.2 Implement status color logic (green 正常, red 额度告急, yellow 需核实)
- [x] 7.3 Build site management settings panel (add/edit/delete site forms)
- [x] 7.4 Implement panel type dropdown with preset auto-fill for CSS selectors
- [x] 7.5 Build global settings form (browser profile path, exchange rate, display currency)

## 8. Integration & Testing

- [x] 8.1 Wire all layers together (UI → Service → Engine → Data)
- [x] 8.2 Write unit tests for CalculationEngine (Decimal precision, multi-currency, partial data)
- [x] 8.3 Write unit tests for data cleaner (various monetary format parsing)
- [x] 8.4 Write integration test for SiteRepository CRUD operations
- [x] 8.5 Manual end-to-end test: configure a site, run inspection, verify results display
