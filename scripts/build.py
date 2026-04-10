"""Build script for API Finance Dashboard.

Automates the full build pipeline:
1. Extract version from pyproject.toml
2. Convert logo PNG to ICO (if needed)
3. Generate installer wizard images
4. Run PyInstaller
5. Run Inno Setup (if available)

Usage:
    python scripts/build.py
    python scripts/build.py --skip-installer  # PyInstaller only
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
LOGO_PNG = ROOT / "logo" / "logo.png"
LOGO_ICO = ROOT / "logo" / "logo.ico"
SPEC_FILE = ROOT / "api-finance-dashboard.spec"
INSTALLER_ISS = ROOT / "installer.iss"


def extract_version() -> str:
    """Extract version string from pyproject.toml."""
    content = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        print("ERROR: Could not extract version from pyproject.toml")
        sys.exit(1)
    return match.group(1)


def convert_icon():
    """Convert logo.png to logo.ico if ICO is missing or outdated."""
    if LOGO_ICO.exists() and LOGO_ICO.stat().st_mtime >= LOGO_PNG.stat().st_mtime:
        print(f"  Icon up to date: {LOGO_ICO}")
        return

    try:
        from PIL import Image

        img = Image.open(LOGO_PNG)
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(str(LOGO_ICO), format="ICO", sizes=sizes)
        print(f"  Generated: {LOGO_ICO}")
    except ImportError:
        print("  WARNING: Pillow not installed, cannot convert icon.")
        print("  Install with: pip install Pillow")
        if not LOGO_ICO.exists():
            sys.exit(1)


def generate_installer_images():
    """Generate wizard sidebar and small images for Inno Setup."""
    wizard_img = ROOT / "installer_assets" / "wizard_image.bmp"
    small_img = ROOT / "installer_assets" / "wizard_small_image.bmp"

    if wizard_img.exists() and small_img.exists():
        # Regenerate only if logo is newer
        if wizard_img.stat().st_mtime >= LOGO_PNG.stat().st_mtime:
            print("  Installer images up to date")
            return

    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_installer_images.py")],
            cwd=str(ROOT),
        )
        if result.returncode != 0:
            print("  WARNING: Failed to generate installer images")
    except Exception as e:
        print(f"  WARNING: Could not generate installer images: {e}")


def run_pyinstaller():
    """Run PyInstaller with the spec file."""
    cmd = [sys.executable, "-m", "PyInstaller", str(SPEC_FILE), "--noconfirm"]
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print("ERROR: PyInstaller build failed")
        sys.exit(1)
    print("  PyInstaller build complete")


def run_inno_setup(version: str):
    """Run Inno Setup to create the installer."""
    iscc = shutil.which("iscc")
    if not iscc:
        # Check common Windows install paths
        for candidate in [
            Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
            Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        ]:
            if candidate.exists():
                iscc = str(candidate)
                break

    if not iscc:
        print("  WARNING: Inno Setup not found, skipping installer creation.")
        print("  Install from: https://jrsoftware.org/isdl.php")
        return False

    cmd = [iscc, f"/DMyAppVersion={version}", str(INSTALLER_ISS)]
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print("ERROR: Inno Setup build failed")
        sys.exit(1)
    print("  Installer created successfully")
    return True


def main():
    parser = argparse.ArgumentParser(description="Build API Finance Dashboard")
    parser.add_argument(
        "--skip-installer",
        action="store_true",
        help="Skip Inno Setup installer creation",
    )
    args = parser.parse_args()

    version = extract_version()
    print(f"Building API Finance Dashboard v{version}")
    print()

    print("[1/4] Converting icon...")
    convert_icon()
    print()

    print("[2/4] Generating installer images...")
    generate_installer_images()
    print()

    print("[3/4] Running PyInstaller...")
    run_pyinstaller()
    print()

    if args.skip_installer:
        print("[4/4] Skipping installer (--skip-installer)")
    else:
        print("[4/4] Running Inno Setup...")
        run_inno_setup(version)

    print()
    print(f"Build complete! Output in: {ROOT / 'dist'}")


if __name__ == "__main__":
    main()
