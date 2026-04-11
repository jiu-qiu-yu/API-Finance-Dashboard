# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

API Finance Dashboard — an RPA desktop app for automated financial monitoring across multiple API hosting platforms (new-api, sub2api, cap). Built with PySide6 (Qt GUI) + Playwright (browser automation) + SQLite (local storage). Target platform: Windows 10/11.

## Commands

```bash
# Install (editable, with dev deps)
pip install -e ".[dev]"

# Run application
api-finance-dashboard

# Run all tests
pytest

# Run single test file
pytest tests/test_presets.py -v

# Run single test
pytest tests/test_presets.py::TestPanelPresets::test_required_presets_exist -v

# Run with coverage
pytest --cov=src tests/

# Build Windows executable (PyInstaller)
python scripts/build.py --skip-installer

# Build full installer (PyInstaller + Inno Setup)
python scripts/build.py
```

## Architecture

```
ui/ (PySide6 widgets + QThread workers)
  → service/inspection_service.py (orchestrator)
    → engine/ (specialized domain logic)
      → browser_engine.py    — Playwright lifecycle, Chrome/Edge profile reuse
      → scraping_engine.py   — 4-tier extraction: CSS → anchor → keyword → regex
      → calculation_engine.py — currency conversion (USD↔CNY), net profit math
      → data_cleaner.py      — monetary value parsing & validation
      → presets.py            — panel-specific scraping configs (new-api, sub2api, cap, custom)
      → notifier.py           — OS notifications via plyer
    → data/ (persistence)
      → database.py          — SQLite with WAL mode, schema migrations (version 2)
      → models.py            — SiteConfig, SiteResult, InspectionResult, enums
      → site_repository.py   — site CRUD
      → config_repository.py — key-value settings
```

**Key data flow:** User clicks Inspect → InspectionWorker (QThread) → InspectionService → BrowserEngine launches Playwright with user's Chrome profile (cookie reuse, no password storage) → ScrapingEngine extracts consumption/balance per site → CalculationEngine computes net profit → results emitted via Qt signals to UI.

**Async bridge:** Playwright is async (`async_playwright`). Qt workers run `asyncio.run()` inside QThread to bridge sync Qt signals with async browser operations.

**Pre-scrape actions:** Some panels require DOM interaction before data is visible (click tabs, select options, wait for elements). Configured per-preset in `presets.py`.

## Database

Location: `~/.api-finance-dashboard/data.db` (SQLite). Schema version tracked in `settings` table; migrations run automatically on startup in `database.py`.

## Release Process

Tag-triggered CI (`.github/workflows/release.yml`): push a tag like `v0.2.0` → GitHub Actions builds exe + Inno Setup installer → creates GitHub Release with installer asset.

## OpenSpec Workflow

Change proposals live in `openspec/changes/`. Use `/opsx:apply <change-name>` to implement, `/opsx:archive` to finalize. Archived changes in `openspec/changes/archive/`.

## Language

Source code comments and UI strings are in Chinese (zh-CN). Keep new comments consistent with existing language in each file.
