"""Upstream quota monitoring list widget with colored progress bars."""

from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from api_finance_dashboard.data.models import SiteResult, SiteStatus, SiteType
from api_finance_dashboard.ui.styles import Colors, Spacing


class QuotaListWidget(QWidget):
    """Displays upstream quota status with colored progress bars."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._container_layout.setSpacing(Spacing.SM)
        self._container_layout.addStretch()

        scroll.setWidget(self._container)
        layout.addWidget(scroll)

    def update_results(self, results: list[SiteResult]) -> None:
        """Refresh the quota list with new inspection results."""
        # Clear existing rows
        while self._container_layout.count() > 1:
            item = self._container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Filter upstream only and sort: low balance first, then by name
        upstream = [r for r in results if r.site.type == SiteType.UPSTREAM]
        upstream.sort(
            key=lambda r: (r.status != SiteStatus.LOW_BALANCE, r.site.name),
        )

        for result in upstream:
            row = self._build_row(result)
            self._container_layout.insertWidget(
                self._container_layout.count() - 1, row,
            )

    def _build_row(self, result: SiteResult) -> QWidget:
        """Build a single upstream quota row."""
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(Spacing.SM, Spacing.XS, Spacing.SM, Spacing.XS)
        layout.setSpacing(Spacing.MD)

        sym = "￥" if result.site.currency.value == "CNY" else "$"
        threshold = result.site.alert_threshold or Decimal("1")

        # Site name
        name_label = QLabel(result.site.name)
        name_label.setFixedWidth(120)
        name_label.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {Colors.TEXT_PRIMARY};"
        )
        layout.addWidget(name_label)

        # Balance text
        balance = result.balance if result.balance is not None else Decimal("0")
        balance_label = QLabel(f"{sym}{balance}")
        balance_label.setFixedWidth(90)
        balance_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        balance_label.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(balance_label)

        # Progress bar: balance / threshold ratio
        ratio = (balance / threshold * 100) if threshold > 0 else 0
        ratio_int = min(int(ratio), 200)

        bar = QProgressBar()
        bar.setRange(0, 200)
        bar.setValue(ratio_int)
        bar.setTextVisible(True)
        bar.setFormat(f"{ratio_int}%")
        bar.setFixedHeight(20)

        # Color logic: >100% green, 50%-100% yellow, <50% red
        if ratio > 100:
            bar_color = Colors.PROGRESS_GREEN
        elif ratio >= 50:
            bar_color = Colors.PROGRESS_YELLOW
        else:
            bar_color = Colors.PROGRESS_RED

        bar.setStyleSheet(
            f"QProgressBar {{"
            f"  border: 1px solid {Colors.CARD_BORDER};"
            f"  border-radius: 4px;"
            f"  text-align: center;"
            f"  font-size: 11px;"
            f"  background-color: #ecf0f1;"
            f"}}"
            f"QProgressBar::chunk {{"
            f"  background-color: {bar_color};"
            f"  border-radius: 3px;"
            f"}}"
        )
        layout.addWidget(bar, stretch=1)

        # Threshold label
        threshold_label = QLabel(f"阈值: {sym}{threshold}")
        threshold_label.setFixedWidth(100)
        threshold_label.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(threshold_label)

        return row
