# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for API Finance Dashboard.

Build command:
    pyinstaller api-finance-dashboard.spec

Output: dist/api-finance-dashboard/ (onedir mode)
"""

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Collect plyer platform-specific backends
plyer_hiddenimports = collect_submodules("plyer.platforms")

# PySide6 and other hidden imports
hiddenimports = [
    # Plyer Windows notification backend
    "plyer.platforms.win.notification",
    # PySide6 plugins
    "PySide6.QtSvg",
    # Playwright (we only need the sync/async API, not the browsers)
    "playwright",
    "playwright.async_api",
    "playwright._impl",
    "playwright._impl._driver",
    # Standard library modules sometimes missed
    "sqlite3",
] + plyer_hiddenimports

# Data files to include
datas = [
    ("logo/logo.png", "logo"),
    ("logo/logo.ico", "logo"),
]

a = Analysis(
    ["src/api_finance_dashboard/main.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        "tkinter",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "PIL",  # Only needed at build time for icon conversion
        "pytest",
        "pytest_asyncio",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # onedir mode
    name="api-finance-dashboard",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="logo/logo.ico",
    version_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="api-finance-dashboard",
)
