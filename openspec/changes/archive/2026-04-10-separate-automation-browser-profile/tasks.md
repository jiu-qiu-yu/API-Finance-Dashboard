## 1. Configuration Layer

- [x] 1.1 Add `get_default_automation_profile_dir()` in new `engine/automation_profile.py` — resolves platform-specific path (`%LOCALAPPDATA%/api-finance-dashboard/automation_profile/` on Windows, `~/Library/Application Support/api-finance-dashboard/automation_profile/` on macOS)
- [x] 1.2 Add `get_automation_profile_path()` / `set_automation_profile_path()` to `ConfigRepository` — if no value stored, auto-resolves and persists the default path
- [x] 1.3 Write unit tests for `get_default_automation_profile_dir()` and new `ConfigRepository` accessors

## 2. Automation Profile Management

- [x] 2.1 Add `ensure_automation_profile_dir(path) -> Path` in `engine/automation_profile.py` — creates directory if missing, returns resolved Path
- [x] 2.2 Add `reset_automation_profile(path)` in `engine/automation_profile.py` — deletes and re-creates the directory
- [x] 2.3 Write unit tests for `ensure_automation_profile_dir` and `reset_automation_profile`

## 3. BrowserEngine Adaptation

- [x] 3.1 Simplify `BrowserEngine.__init__` — `profile_path` now always points directly to the automation profile dir; remove `profile_dir` parameter (no longer selecting sub-profiles like "Default" / "Profile 10")
- [x] 3.2 Relax `validate_browser_profile_path()` — automation profile directories are valid even without `Default/` or `Local State` subdirectories
- [x] 3.3 Update `detect_browser_conflict()` — only check lock files in the automation profile directory; daily browser with different User Data dir is NOT a conflict
- [x] 3.4 Write unit tests for simplified BrowserEngine init, relaxed validation, updated conflict detection

## 4. Per-Site Login Flow

- [x] 4.1 Create `engine/automation_login.py` with `async def run_login_session(executable_path, automation_profile_path, target_url) -> None` — launches persistent context, navigates to target URL, waits for browser close (context disconnect)
- [x] 4.2 Create `ui/automation_login_worker.py` with `SiteLoginWorker(QThread)` — wraps `run_login_session`, emits `finished()` and `error(str)` signals
- [x] 4.3 Write unit tests for `run_login_session` (mock Playwright context lifecycle)

## 5. UI: Site Edit Form

- [x] 5.1 Add "登录此站点" button in `SiteEditForm.__init__` alongside existing "测试抓取" button
- [x] 5.2 Implement `_login_site()` slot in `SettingsPanel` — reads URL from form, validates non-empty, calls `ensure_automation_profile_dir`, launches `SiteLoginWorker` targeting that URL
- [x] 5.3 On `SiteLoginWorker.finished` → automatically trigger `_test_scrape()` to verify login success
- [x] 5.4 On `SiteLoginWorker.error` → display error message, re-enable button

## 6. UI: Global Settings Simplification

- [x] 6.1 Add "自动化浏览器" group box in `_build_global_tab()` — shows automation profile path (read-only QLabel) and a "重置自动化浏览器" button
- [x] 6.2 Implement `_reset_automation_browser()` slot — confirm dialog, calls `reset_automation_profile`, shows success message
- [x] 6.3 Demote legacy "浏览器配置" section — keep visible for backward compat but add hint label: "推荐使用上方的专用自动化浏览器，无需手动配置"
- [x] 6.4 Remove profile dropdown selector from primary flow (keep only in legacy section)

## 7. Inspection Service Adaptation

- [x] 7.1 Modify `InspectionService.__init__` — accept `automation_profile_path` and use it as `BrowserEngine` profile_path
- [x] 7.2 Modify `InspectionWorker` — read `automation_profile_path` from `ConfigRepository`, pass to `InspectionService`
- [x] 7.3 Modify `_test_scrape()` in `SettingsPanel` — use `automation_profile_path` for `BrowserEngine` instead of legacy `browser_profile_path`

## 8. Verification

- [x] 8.1 Run full test suite (`pytest`) and ensure all existing + new tests pass
- [ ] 8.2 Manually validate: add new site → click "登录此站点" → login → auto test scrape succeeds
- [ ] 8.3 Manually validate: daily Chrome stays open during test scrape / inspection (no conflict)
- [ ] 8.4 Manually validate: reset automation browser → all sites need re-login
- [ ] 8.5 Manually validate: session expired → click "登录此站点" again → re-login → test scrape succeeds
