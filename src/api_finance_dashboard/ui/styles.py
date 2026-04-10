"""Design tokens and style constants for the dashboard UI."""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect


# === Colors ===
class Colors:
    # Primary (Logo navy blue)
    PRIMARY = "#2c3e50"
    PRIMARY_HOVER = "#1a252f"
    PRIMARY_DISABLED = "#95a5a6"
    ACCENT_GOLD = "#c8a84e"

    # Semantic
    SUCCESS = "#2ecc71"
    DANGER = "#e74c3c"
    WARNING = "#f39c12"
    INFO = "#2c3e50"

    # Neutrals (macOS style)
    TEXT_PRIMARY = "#1d1d1f"
    TEXT_SECONDARY = "#86868b"
    TEXT_MUTED = "#aaaaaa"
    TEXT_WHITE = "#ffffff"

    # Backgrounds (warm gray-white)
    BG_CARD = "#ffffff"
    BG_WINDOW = "#f5f5f7"
    BG_ALERT_ROW = "#e74c3c"
    BG_ALERT_SOFT = "#ffcccc"

    # Soft semantic backgrounds
    BG_SUCCESS_SOFT = "#f0faf4"
    BG_DANGER_SOFT = "#fff2f0"
    BG_WARNING_SOFT = "#fff8e6"
    BG_DANGER_HOVER = "#ffe8e5"
    ROW_HOVER = "#f5f5f7"
    PROGRESS_BG = "#e8ecef"
    SEPARATOR = "#e5e5ea"

    # Progress bar
    PROGRESS_GREEN = "#2ecc71"
    PROGRESS_YELLOW = "#f1c40f"
    PROGRESS_RED = "#e74c3c"

    # Card (borderless macOS style)
    CARD_BORDER = "transparent"
    CARD_SHADOW = "#cccccc"

    # Badge text colors (deep semantic for modern badges)
    BADGE_SUCCESS_TEXT = "#2ecc71"
    BADGE_DANGER_TEXT = "#e74c3c"
    BADGE_WARNING_TEXT = "#f39c12"


# === Shadows (Task 1.2) ===
class Shadows:
    """Three-level shadow factory methods returning QGraphicsDropShadowEffect."""

    @staticmethod
    def create_sm(parent=None) -> QGraphicsDropShadowEffect:
        """Small shadow – blur(4) offset(0,1) alpha 6."""
        shadow = QGraphicsDropShadowEffect(parent)
        shadow.setBlurRadius(4)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(0, 0, 0, 6))
        return shadow

    @staticmethod
    def create_md(parent=None) -> QGraphicsDropShadowEffect:
        """Medium shadow – blur(24) offset(0,4) alpha 8 (macOS card float)."""
        shadow = QGraphicsDropShadowEffect(parent)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 8))
        return shadow

    @staticmethod
    def create_lg(parent=None) -> QGraphicsDropShadowEffect:
        """Large shadow – blur(40) offset(0,8) alpha 12."""
        shadow = QGraphicsDropShadowEffect(parent)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 12))
        return shadow


# === Font Weights (Task 1.3) ===
class FontWeights:
    REGULAR = 400
    MEDIUM = 500
    SEMIBOLD = 600
    BOLD = 700


# === Border Radius (macOS style) ===
class BorderRadius:
    SM = 4
    MD = 8
    LG = 12
    XL = 14       # card corners
    CAPSULE = 20  # capsule buttons
    BADGE = 12    # badge pill
    PROGRESS = 6  # progress bar


# === Font Sizes ===
class FontSizes:
    TITLE_HERO = 48  # profit display
    TITLE_LARGE = 24
    TITLE_CARD = 16
    BODY = 14
    BODY_SMALL = 12
    CAPTION = 11


# === Spacing (macOS breathing room) ===
class Spacing:
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    XXXL = 48
    WINDOW = 24      # window margins
    CARD_INNER = 24  # card inner padding


# === Stylesheet Templates (macOS visual polish) ===
CARD_STYLE = (
    "QFrame#card {"
    f"  background-color: {Colors.BG_CARD};"
    f"  border-radius: {BorderRadius.XL}px;"
    "  border: none;"
    "}"
)

PROFIT_LABEL_STYLE = (
    f"font-size: {FontSizes.TITLE_HERO}px;"
    f" font-weight: {FontWeights.BOLD};"
    f" color: {Colors.SUCCESS};"
)

PROFIT_LABEL_NEGATIVE_STYLE = (
    f"font-size: {FontSizes.TITLE_HERO}px;"
    f" font-weight: {FontWeights.BOLD};"
    f" color: {Colors.DANGER};"
)

PROFIT_LABEL_NA_STYLE = (
    f"font-size: {FontSizes.TITLE_HERO}px;"
    f" font-weight: {FontWeights.BOLD};"
    f" color: {Colors.TEXT_SECONDARY};"
)

PROFIT_LABEL_CLICKABLE_STYLE = (
    f"font-size: {FontSizes.TITLE_HERO}px;"
    f" font-weight: {FontWeights.BOLD};"
    " text-decoration: underline;"
)

INSPECT_BTN_STYLE = (
    "QPushButton {"
    f"  background-color: {Colors.PRIMARY};"
    f"  color: {Colors.TEXT_WHITE};"
    f"  font-size: {FontSizes.TITLE_CARD}px;"
    f"  padding: 12px 28px;"
    f"  border-radius: {BorderRadius.CAPSULE}px;"
    "  border: none;"
    "}"
    "QPushButton:hover {"
    f"  background-color: {Colors.PRIMARY_HOVER};"
    "}"
    "QPushButton:disabled {"
    f"  background-color: {Colors.PRIMARY_DISABLED};"
    "}"
)

SETTINGS_BTN_STYLE = (
    "QPushButton {"
    f"  padding: 12px 28px;"
    f"  font-size: {FontSizes.BODY}px;"
    f"  border: 1px solid {Colors.SEPARATOR};"
    f"  border-radius: {BorderRadius.CAPSULE}px;"
    "  background-color: transparent;"
    f"  color: {Colors.TEXT_PRIMARY};"
    "}"
    "QPushButton:hover {"
    f"  background-color: {Colors.ROW_HOVER};"
    "}"
)

DANGER_BTN_STYLE = (
    "QPushButton {"
    f"  padding: 12px 28px;"
    f"  font-size: {FontSizes.BODY}px;"
    f"  border: 1px solid {Colors.DANGER};"
    f"  border-radius: {BorderRadius.CAPSULE}px;"
    "  background-color: transparent;"
    f"  color: {Colors.DANGER};"
    "}"
    "QPushButton:hover {"
    f"  background-color: {Colors.BG_DANGER_SOFT};"
    "}"
)

FORMULA_HINT_STYLE = (
    f"font-size: {FontSizes.BODY_SMALL}px;"
    f" color: {Colors.TEXT_SECONDARY};"
)

LAST_TIME_STYLE = (
    f"font-size: {FontSizes.CAPTION}px;"
    f" color: {Colors.TEXT_MUTED};"
)

SECTION_TITLE_STYLE = (
    f"font-size: {FontSizes.TITLE_CARD}px;"
    f" font-weight: {FontWeights.SEMIBOLD};"
)

ALERT_SUMMARY_NORMAL_STYLE = (
    f"font-size: {FontSizes.BODY}px;"
    f" color: {Colors.SUCCESS};"
    f" font-weight: {FontWeights.SEMIBOLD};"
)

ALERT_SUMMARY_DANGER_STYLE = (
    f"font-size: {FontSizes.BODY}px;"
    f" color: {Colors.DANGER};"
    f" font-weight: {FontWeights.SEMIBOLD};"
)
