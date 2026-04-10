## 1. Locate and normalize browser launch inputs

- [x] 1.1 Trace the source of `--no-sandbox` through `BrowserEngine` and all caller paths, then centralize launch-argument construction in `src/api_finance_dashboard/engine/browser_engine.py`
- [x] 1.2 Implement launch-argument sanitization so local desktop profile reuse removes or rejects unsupported flags such as `--no-sandbox`
- [x] 1.3 Preserve the installed-browser requirement by validating the resolved Chrome/Edge executable and preventing fallback to Playwright bundled Chromium

## 2. Add startup diagnostics and error handling

- [x] 2.1 Add startup diagnostics that distinguish unsupported launch warnings, early browser-process exit, and profile-conflict failures before selector waiting begins
- [x] 2.2 Map startup diagnostic failures to actionable Chinese error messages surfaced by test scrape and inspection flows
- [x] 2.3 Ensure selector waiting only starts after startup diagnostics confirm the browser is on the intended site context instead of a warning/startup page

## 3. Unify caller behavior and verify flows

- [x] 3.1 Verify `settings_panel.py`, `inspection_service.py`, `inspection_worker.py`, and `main_window.py` all use the same browser executable/profile configuration chain
- [x] 3.2 Add or update tests covering launch sanitization, installed-browser enforcement, and startup diagnostic handling
- [ ] 3.3 Manually validate both “测试抓取” and “开始巡检” against a real logged-in browser profile to confirm the freeze is gone and authenticated scraping continues
