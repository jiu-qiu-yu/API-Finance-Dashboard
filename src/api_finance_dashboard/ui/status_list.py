"""Unified site health table – the 'super table' replacing both quota overview and status list."""

from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from api_finance_dashboard.data.models import SiteResult, SiteStatus, SiteType
from api_finance_dashboard.ui.card_widget import CardWidget
from api_finance_dashboard.ui.styles import (
    BorderRadius,
    Colors,
    FontSizes,
    FontWeights,
    Spacing,
)

# Badge config: (label, bg_color, text_color)
_BADGE_CONFIG = {
    SiteStatus.NORMAL: ("正常", Colors.BG_SUCCESS_SOFT, Colors.BADGE_SUCCESS_TEXT),
    SiteStatus.LOW_BALANCE: ("额度告急", Colors.BG_DANGER_SOFT, Colors.BADGE_DANGER_TEXT),
    SiteStatus.NEEDS_CHECK: ("待核实", Colors.BG_WARNING_SOFT, Colors.BADGE_WARNING_TEXT),
}

# Column indices
_COL_NAME = 0
_COL_CONSUMPTION = 1
_COL_BALANCE = 2
_COL_QUOTA_RATIO = 3
_COL_STATUS = 4

_COLUMN_COUNT = 5


class StatusListWidget(QWidget):
    """Unified site health overview table with macOS minimal list style."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Wrap table in a CardWidget container (Task 5.1)
        self._card = CardWidget("")
        card_layout = self._card.card_layout
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self._table = QTableWidget()
        self._table.setColumnCount(_COLUMN_COUNT)
        self._table.setHorizontalHeaderLabels(
            ["站点名称", "今日消耗", "当前余额", "额度比", "状态"],
        )

        # Header sizing
        header = self._table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setSectionResizeMode(_COL_NAME, QHeaderView.ResizeMode.Stretch)
        header.setFixedHeight(36)
        for col, width in ((_COL_CONSUMPTION, 100), (_COL_BALANCE, 100), (_COL_QUOTA_RATIO, 150), (_COL_STATUS, 90)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self._table.setColumnWidth(col, width)

        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)

        # Alternating row colors — very subtle (Task 5.4)
        self._table.setAlternatingRowColors(True)

        # macOS minimal list style (Tasks 5.2, 5.4)
        self._table.setStyleSheet(
            f"QHeaderView::section {{"
            f"  background-color: transparent;"
            f"  color: {Colors.TEXT_SECONDARY};"
            f"  font-size: {FontSizes.BODY_SMALL}px;"
            f"  font-weight: {FontWeights.SEMIBOLD};"
            f"  border: none;"
            f"  border-bottom: 1px solid {Colors.SEPARATOR};"
            f"  padding: 6px 8px;"
            f"}}"
            f"QTableWidget {{"
            f"  background-color: {Colors.BG_CARD};"
            f"  alternate-background-color: #fafafa;"
            f"  border: none;"
            f"  gridline-color: transparent;"
            f"  selection-background-color: {Colors.ROW_HOVER};"
            f"  selection-color: {Colors.TEXT_PRIMARY};"
            f"}}"
            f"QTableWidget::item {{"
            f"  padding: 4px 8px;"
            f"  border: none;"
            f"  border-bottom: 1px solid #f0f0f0;"
            f"}}"
            f"QTableWidget::item:hover {{"
            f"  background-color: {Colors.ROW_HOVER};"
            f"}}"
        )

        card_layout.addWidget(self._table)
        layout.addWidget(self._card)

    def update_results(self, results: list[SiteResult]) -> None:
        """Populate the super table with inspection results.

        Sorting (Task 6.9): main sites first, then alert rows, then normal.
        """
        sorted_results = self._sort_results(results)

        self._table.setRowCount(len(sorted_results))
        self._table.setUpdatesEnabled(False)

        for row, result in enumerate(sorted_results):
            self._populate_row(row, result)

        self._table.setUpdatesEnabled(True)

    # --- Private helpers ---

    @staticmethod
    def _sort_results(results: list[SiteResult]) -> list[SiteResult]:
        """Sort: main sites first, then alert rows, then normal (Task 6.9)."""
        main_sites = [r for r in results if r.site.type == SiteType.MAIN]
        alert_upstream = [
            r for r in results
            if r.site.type == SiteType.UPSTREAM and r.status == SiteStatus.LOW_BALANCE
        ]
        normal_upstream = [
            r for r in results
            if r.site.type == SiteType.UPSTREAM and r.status != SiteStatus.LOW_BALANCE
        ]
        alert_upstream.sort(key=lambda r: r.site.name)
        normal_upstream.sort(key=lambda r: r.site.name)
        return main_sites + alert_upstream + normal_upstream

    def _populate_row(self, row: int, result: SiteResult) -> None:
        site = result.site
        currency_sym = "￥" if site.currency.value == "CNY" else "$"
        is_alert = result.status == SiteStatus.LOW_BALANCE
        is_main = site.type == SiteType.MAIN

        self._table.setRowHeight(row, 44)

        # Col 0: Site name (Task 6.1)
        name_text = f"[主站] {site.name}" if is_main else site.name
        name_item = QTableWidgetItem(name_text)
        name_item.setTextAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        self._table.setItem(row, _COL_NAME, name_item)

        # Col 1: Consumption – right-aligned (Task 6.7)
        cons_text = (
            f"{currency_sym}{result.consumption}"
            if result.consumption is not None
            else "--"
        )
        cons_item = QTableWidgetItem(cons_text)
        cons_item.setTextAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        self._table.setItem(row, _COL_CONSUMPTION, cons_item)

        # Col 2: Balance – right-aligned (Task 6.7)
        if site.type == SiteType.UPSTREAM:
            bal_text = (
                f"{currency_sym}{result.balance}"
                if result.balance is not None
                else "--"
            )
        else:
            bal_text = "--"
        bal_item = QTableWidgetItem(bal_text)
        bal_item.setTextAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        self._table.setItem(row, _COL_BALANCE, bal_item)

        # Col 3: Quota ratio with progress bar (Task 6.2)
        if is_main:
            ratio_item = QTableWidgetItem("--")
            ratio_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, _COL_QUOTA_RATIO, ratio_item)
        else:
            bar = self._build_progress_bar(result)
            self._table.setCellWidget(row, _COL_QUOTA_RATIO, bar)

        # Col 4: Status badge (Task 6.4)
        badge = self._build_badge(result.status)
        self._table.setCellWidget(row, _COL_STATUS, badge)

        # Alert row styling (Task 6.6) + money column font weight (Task 6.7)
        medium_font = QFont()
        medium_font.setWeight(QFont.Weight(FontWeights.MEDIUM))
        cons_item.setFont(medium_font)
        bal_item.setFont(medium_font)

        if is_alert:
            self._style_alert_row(row)

    def _style_alert_row(self, row: int) -> None:
        """Apply alert (light red) background and semibold dark-red text (Task 6.6)."""
        bg = QColor(Colors.BG_DANGER_SOFT)
        fg = QColor(Colors.BADGE_DANGER_TEXT)
        bold_font = QFont()
        bold_font.setWeight(QFont.Weight(FontWeights.SEMIBOLD))

        for col in range(_COLUMN_COUNT):
            item = self._table.item(row, col)
            if item:
                item.setBackground(bg)
                item.setForeground(fg)
                item.setFont(bold_font)

    @staticmethod
    def _build_progress_bar(result: SiteResult) -> QWidget:
        """Build a mini progress bar for the quota ratio column (Task 6.2)."""
        balance = result.balance if result.balance is not None else Decimal("0")
        threshold = result.site.alert_threshold or Decimal("1")
        ratio = (balance / threshold * 100) if threshold > 0 else 0
        ratio_int = min(int(ratio), 200)

        # Color: >100% green, 50-100% yellow, <50% red
        if ratio > 100:
            bar_color = Colors.PROGRESS_GREEN
        elif ratio >= 50:
            bar_color = Colors.PROGRESS_YELLOW
        else:
            bar_color = Colors.PROGRESS_RED

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        bar = QProgressBar()
        bar.setRange(0, 200)
        bar.setValue(ratio_int)
        bar.setTextVisible(True)
        bar.setFormat(f"{ratio_int}%")
        bar.setFixedHeight(16)
        bar.setStyleSheet(
            f"QProgressBar {{"
            f"  border: none;"
            f"  border-radius: {BorderRadius.PROGRESS}px;"
            f"  text-align: center;"
            f"  font-size: 10px;"
            f"  background-color: {Colors.PROGRESS_BG};"
            f"  color: {Colors.TEXT_PRIMARY};"
            f"}}"
            f"QProgressBar::chunk {{"
            f"  background-color: {bar_color};"
            f"  border-radius: {BorderRadius.PROGRESS - 1}px;"
            f"}}"
        )
        layout.addWidget(bar)
        return container

    @staticmethod
    def _build_badge(status: SiteStatus) -> QWidget:
        """Build a modern status badge label (Task 6.4)."""
        label_text, bg_color, text_color = _BADGE_CONFIG.get(
            status, ("未知", Colors.PROGRESS_BG, Colors.TEXT_SECONDARY),
        )

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        badge = QLabel(label_text)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"background-color: {bg_color};"
            f" color: {text_color};"
            f" font-size: {FontSizes.BODY_SMALL}px;"
            f" font-weight: {FontWeights.SEMIBOLD};"
            f" border-radius: {BorderRadius.BADGE}px;"
            f" padding: 2px 8px;"
        )
        layout.addWidget(badge)
        return container
