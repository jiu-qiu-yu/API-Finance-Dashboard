"""Collapsible panel widget with smooth animation and max-height scroll."""

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    Qt,
)
from PySide6.QtWidgets import (
    QFrame,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class CollapsiblePanel(QWidget):
    """A panel that can expand/collapse with smooth animation.

    Content exceeding ``max_content_height`` scrolls internally via QScrollArea.
    """

    ANIMATION_DURATION = 250  # ms

    def __init__(self, parent=None, *, max_content_height: int = 200) -> None:
        super().__init__(parent)

        self._is_expanded = False
        self._max_content_height = max_content_height

        # Outer frame animated for expand/collapse
        self._content_area = QFrame()
        self._content_area.setFrameShape(QFrame.Shape.NoFrame)
        self._content_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed,
        )
        self._content_area.setMaximumHeight(0)
        self._content_area.setMinimumHeight(0)
        self._content_area.setStyleSheet("background: transparent; border: none;")

        # Inner scroll area to handle overflow
        self._scroll_area = QScrollArea(self._content_area)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )

        self._inner_widget = QWidget()
        self._content_layout = QVBoxLayout(self._inner_widget)
        self._content_layout.setContentsMargins(0, 8, 0, 0)
        self._content_layout.setSpacing(4)
        self._scroll_area.setWidget(self._inner_widget)

        area_layout = QVBoxLayout(self._content_area)
        area_layout.setContentsMargins(0, 0, 0, 0)
        area_layout.setSpacing(0)
        area_layout.addWidget(self._scroll_area)

        self._animation = QParallelAnimationGroup(self)

        self._height_anim = QPropertyAnimation(self._content_area, b"maximumHeight")
        self._height_anim.setDuration(self.ANIMATION_DURATION)
        self._height_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.addAnimation(self._height_anim)

        self._min_anim = QPropertyAnimation(self._content_area, b"minimumHeight")
        self._min_anim.setDuration(self.ANIMATION_DURATION)
        self._min_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.addAnimation(self._min_anim)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._content_area)

    @property
    def content_layout(self) -> QVBoxLayout:
        """Access the inner layout to add content widgets."""
        return self._content_layout

    @property
    def is_expanded(self) -> bool:
        return self._is_expanded

    def toggle(self) -> None:
        """Toggle between expanded and collapsed states."""
        if self._is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self) -> None:
        if self._is_expanded:
            return
        self._is_expanded = True

        content_height = self._content_layout.sizeHint().height() + 16
        target_height = min(content_height, self._max_content_height)

        self._height_anim.setStartValue(0)
        self._height_anim.setEndValue(target_height)
        self._min_anim.setStartValue(0)
        self._min_anim.setEndValue(target_height)

        self._animation.start()

    def collapse(self) -> None:
        if not self._is_expanded:
            return
        self._is_expanded = False

        current_height = self._content_area.maximumHeight()

        self._height_anim.setStartValue(current_height)
        self._height_anim.setEndValue(0)
        self._min_anim.setStartValue(current_height)
        self._min_anim.setEndValue(0)

        self._animation.start()
