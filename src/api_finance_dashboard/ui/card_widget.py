"""Reusable card widget with rounded corners and shadow effect."""

from PySide6.QtWidgets import QFrame, QVBoxLayout

from api_finance_dashboard.ui.styles import (
    BorderRadius,
    Colors,
    FontSizes,
    FontWeights,
    Shadows,
    Spacing,
)


class CardWidget(QFrame):
    """A card container with macOS-style floating appearance."""

    def __init__(self, title: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            f"QFrame#card {{"
            f"  background-color: {Colors.BG_CARD};"
            f"  border-radius: {BorderRadius.XL}px;"
            f"  border: none;"
            f"}}"
        )

        self.setGraphicsEffect(Shadows.create_md(self))

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(
            Spacing.CARD_INNER, Spacing.CARD_INNER,
            Spacing.CARD_INNER, Spacing.CARD_INNER,
        )
        self._layout.setSpacing(Spacing.SM)

        if title:
            from PySide6.QtWidgets import QLabel

            title_label = QLabel(title)
            title_label.setStyleSheet(
                f"font-size: {FontSizes.TITLE_CARD}px;"
                f" font-weight: {FontWeights.SEMIBOLD};"
                f" color: {Colors.TEXT_PRIMARY};"
                " border: none; background: transparent;"
            )
            self._layout.addWidget(title_label)

    @property
    def card_layout(self) -> QVBoxLayout:
        """Access the inner layout to add child widgets."""
        return self._layout
