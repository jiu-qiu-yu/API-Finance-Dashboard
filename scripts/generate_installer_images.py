"""Generate installer wizard images from the project logo.

Inno Setup requires:
- WizardImageFile: 164x314 BMP (left sidebar on welcome/finish pages)
- WizardSmallImageFile: 55x55 BMP (top-right corner on inner pages)
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "logo" / "logo.png"
OUT_DIR = ROOT / "installer_assets"


def generate_wizard_image():
    """Generate 164x314 sidebar image with logo centered on branded background."""
    width, height = 164, 314
    bg_color = (44, 62, 80)  # Colors.PRIMARY #2c3e50

    img = Image.new("RGB", (width, height), bg_color)

    logo = Image.open(LOGO).convert("RGBA")
    logo_size = 100
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

    # Center logo horizontally, place at ~40% from top
    x = (width - logo_size) // 2
    y = int(height * 0.35) - logo_size // 2
    img.paste(logo, (x, y), logo)

    out = OUT_DIR / "wizard_image.bmp"
    img.save(str(out), "BMP")
    print(f"  Generated: {out}")


def generate_wizard_small_image():
    """Generate 55x55 small image with logo."""
    size = 55
    bg_color = (255, 255, 255)

    img = Image.new("RGB", (size, size), bg_color)

    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.resize((48, 48), Image.LANCZOS)

    x = (size - 48) // 2
    y = (size - 48) // 2
    img.paste(logo, (x, y), logo)

    out = OUT_DIR / "wizard_small_image.bmp"
    img.save(str(out), "BMP")
    print(f"  Generated: {out}")


if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True)
    print("Generating installer images...")
    generate_wizard_image()
    generate_wizard_small_image()
    print("Done!")
