## Why

Clicking the scrape test can log into the user's account, but the page then freezes on a Chrome warning about the unsupported `--no-sandbox` flag and never proceeds. This blocks the core inspection flow and indicates the browser launch pipeline is still using unsafe or incompatible flags against the user's real profile.

## What Changes

- Remove or isolate unsupported Playwright launch flags that cause Chrome to stall after opening an authenticated profile.
- Make browser startup deterministic so scraping always uses the user's installed Chrome/Edge executable instead of silently falling back to bundled Chromium.
- Add explicit detection and reporting for launch conditions that would freeze or degrade the page, including profile conflicts and unsupported flag combinations.
- Verify the test-scrape and inspection flows both use the same corrected browser launch configuration.

## Capabilities

### New Capabilities
- `browser-launch-diagnostics`: Diagnose browser startup incompatibilities and surface actionable errors when launch flags or profile state would prevent scraping from continuing.

### Modified Capabilities
- `local-browser-context`: Tighten browser launch requirements so the system uses a supported local browser executable and avoids unsupported flag combinations with the user's profile.
- `web-scraping-engine`: Require test scrape and full inspection flows to share the same corrected launch path so authenticated pages can proceed past startup.

## Impact

- Affected code: `src/api_finance_dashboard/engine/browser_engine.py`, `src/api_finance_dashboard/ui/settings_panel.py`, `src/api_finance_dashboard/ui/inspection_worker.py`, `src/api_finance_dashboard/service/inspection_service.py`, `src/api_finance_dashboard/ui/main_window.py`
- Affected behavior: browser startup, authenticated scraping, test scrape UX, inspection stability
- Dependencies/systems: Playwright persistent context launch, local Chrome/Edge installation, Windows browser profile handling
