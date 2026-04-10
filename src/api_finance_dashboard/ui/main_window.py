"""Main application window with modernized card-based dashboard layout.

Layout (S3 merged plan):
┌─────────────────────────────────────────────────────┐
│  [利润卡片 + 摘要行]                    (全宽, 固定)  │
├──────────────┬──────────────────────────────────────┤
│  [告警侧栏]   │  [站点健康总览 - 超级表格]             │
│  (~200px)    │  (stretch, 唯一滚动区)                │
│  (固定宽度)   │                                      │
└──────────────┴──────────────────────────────────────┘
"""

from datetime import datetime
from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QCursor, QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from api_finance_dashboard.resources import get_resource_path
from api_finance_dashboard.data.config_repository import ConfigRepository
from api_finance_dashboard.data.database import init_database
from api_finance_dashboard.data.models import (
    Currency,
    InspectionResult,
    SiteResult,
    SiteStatus,
    SiteType,
)
from api_finance_dashboard.data.site_repository import SiteRepository
from api_finance_dashboard.engine.browser_engine import (
    detect_browser_conflict,
    validate_browser_profile_path,
)
from api_finance_dashboard.engine.notifier import check_and_alert
from api_finance_dashboard.ui.card_widget import CardWidget
from api_finance_dashboard.ui.collapsible_panel import CollapsiblePanel
from api_finance_dashboard.ui.inspection_worker import InspectionWorker
from api_finance_dashboard.ui.settings_panel import SettingsPanel
from api_finance_dashboard.ui.status_list import StatusListWidget
from api_finance_dashboard.ui.styles import (
    ALERT_SUMMARY_DANGER_STYLE,
    ALERT_SUMMARY_NORMAL_STYLE,
    BorderRadius,
    Colors,
    DANGER_BTN_STYLE,
    FontSizes,
    FontWeights,
    FORMULA_HINT_STYLE,
    INSPECT_BTN_STYLE,
    LAST_TIME_STYLE,
    PROFIT_LABEL_NA_STYLE,
    Shadows,
    SETTINGS_BTN_STYLE,
    Spacing,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("API 财务仪表盘")
        self.setMinimumSize(960, 700)
        self.setStyleSheet(f"QMainWindow {{ background-color: {Colors.BG_WINDOW}; }}")

        # Brand logo as window icon (Task 3.1)
        self._set_window_icon()

        init_database()
        self._site_repo = SiteRepository()
        self._config_repo = ConfigRepository()
        self._worker: InspectionWorker | None = None
        self._last_result: InspectionResult | None = None

        self._setup_ui()

    # ================================================================
    # UI Construction
    # ================================================================

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        # Profit card <-> bottom area spacing = 28px
        main_layout.setSpacing(28)
        main_layout.setContentsMargins(
            Spacing.WINDOW, Spacing.WINDOW, Spacing.WINDOW, Spacing.WINDOW,
        )

        # === Top: Profit Card (full width) ===
        self._profit_card = CardWidget("")
        self._build_profit_card()
        main_layout.addWidget(self._profit_card)

        # === Bottom: Alert Sidebar + Super Table (Task 4.2) ===
        bottom_layout = QHBoxLayout()
        # Task 4.4: sidebar <-> table spacing = LG (16px)
        bottom_layout.setSpacing(Spacing.LG)

        # Left: Alert sidebar (~200px fixed) — Tasks 5.1-5.3
        self._alert_sidebar = CardWidget("")
        self._alert_sidebar.setFixedWidth(200)
        self._build_alert_sidebar()
        bottom_layout.addWidget(
            self._alert_sidebar,
            alignment=Qt.AlignmentFlag.AlignTop,  # Task 4.3
        )

        # Right: Super table (stretch) — Tasks 6.1-6.9
        self._status_list = StatusListWidget()
        bottom_layout.addWidget(self._status_list, stretch=1)

        main_layout.addLayout(bottom_layout, stretch=1)

    def _set_window_icon(self) -> None:
        """Set window icon from brand logo (Task 3.1)."""
        # Try .ico first (multi-size, best for taskbar/title bar)
        ico_path = get_resource_path("logo/logo.ico")
        png_path = get_resource_path("logo/logo.png")

        icon = QIcon(ico_path)
        if icon.isNull():
            icon = QIcon(png_path)
        if not icon.isNull():
            self.setWindowIcon(icon)

    def _build_profit_card(self) -> None:
        layout = self._profit_card.card_layout

        # Brand logo + title row (Task 3.2)
        title_row = QHBoxLayout()
        title_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_row.setSpacing(Spacing.SM)

        logo_path = get_resource_path("logo/logo.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            logo_label = QLabel()
            logo_label.setPixmap(
                pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation),
            )
            logo_label.setFixedSize(32, 32)
            logo_label.setStyleSheet("background: transparent; border: none;")
            title_row.addWidget(logo_label)

        profit_title = QLabel("今日盈利")
        profit_title.setStyleSheet(
            f"font-size: {FontSizes.TITLE_CARD}px;"
            f" font-weight: {FontWeights.SEMIBOLD};"
            f" color: {Colors.TEXT_PRIMARY};"
            " background: transparent; border: none;"
        )
        title_row.addWidget(profit_title)
        layout.addLayout(title_row)

        # Summary bar
        self._summary_bar = QLabel("")
        self._summary_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._summary_bar.setStyleSheet(
            f"font-size: {FontSizes.BODY_SMALL}px;"
            f" color: {Colors.TEXT_SECONDARY};"
            " background: transparent; border: none;"
        )
        layout.addWidget(self._summary_bar)
        self._update_summary_bar_initial()

        # Profit label (Task 3.2: trend arrows)
        self._profit_label = QLabel("--")
        self._profit_label.setStyleSheet(
            f"font-size: {FontSizes.TITLE_HERO}px;"
            f" font-weight: {FontWeights.BOLD};"
            f" color: {Colors.TEXT_SECONDARY};"
        )
        self._profit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._profit_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._profit_label.setToolTip("点击查看盈利明细")
        self._profit_label.mousePressEvent = lambda _: self._toggle_profit_detail()
        layout.addWidget(self._profit_label)

        # Collapsible profit detail panel (Task 3.3: max-height via CollapsiblePanel)
        self._profit_detail_panel = CollapsiblePanel(max_content_height=200)
        self._profit_detail_content = QLabel("")
        self._profit_detail_content.setWordWrap(True)
        self._profit_detail_content.setStyleSheet(
            f"font-size: 13px; color: {Colors.TEXT_PRIMARY};"
            " background: transparent; border: none;"
        )
        self._profit_detail_panel.content_layout.addWidget(self._profit_detail_content)
        layout.addWidget(self._profit_detail_panel)

        formula_hint = QLabel("净利润 = 主站消耗 - 上游总消耗")
        formula_hint.setStyleSheet(FORMULA_HINT_STYLE)
        formula_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(formula_hint)

        # Controls row (Task 3.5: button styles)
        controls = QHBoxLayout()
        self._inspect_btn = QPushButton("开始巡检")
        self._inspect_btn.setStyleSheet(INSPECT_BTN_STYLE)
        self._inspect_btn.clicked.connect(self._start_inspection)
        controls.addWidget(self._inspect_btn)

        settings_btn = QPushButton("设置")
        settings_btn.setStyleSheet(SETTINGS_BTN_STYLE)
        settings_btn.clicked.connect(self._open_settings)
        controls.addWidget(settings_btn)
        layout.addLayout(controls)

        self._last_time_label = QLabel("")
        self._last_time_label.setStyleSheet(LAST_TIME_STYLE)
        self._last_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._last_time_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setTextVisible(True)
        layout.addWidget(self._progress_bar)

    def _build_alert_sidebar(self) -> None:
        """Build the alert sidebar card — Tasks 5.1-5.3."""
        layout = self._alert_sidebar.card_layout

        self._alert_title = QLabel("告警摘要")
        self._alert_title.setStyleSheet(
            f"font-size: {FontSizes.TITLE_CARD}px;"
            f" font-weight: {FontWeights.SEMIBOLD};"
            f" color: {Colors.TEXT_PRIMARY};"
            " border: none; background: transparent;"
        )
        layout.addWidget(self._alert_title)

        self._alert_content = QLabel("暂无数据")
        self._alert_content.setStyleSheet(
            ALERT_SUMMARY_NORMAL_STYLE + " background: transparent; border: none;",
        )
        self._alert_content.setWordWrap(True)
        layout.addWidget(self._alert_content)

        # Alert list container for individual alert entries (Task 5.3)
        self._alert_list_container = QWidget()
        self._alert_list_layout = QVBoxLayout(self._alert_list_container)
        self._alert_list_layout.setContentsMargins(0, 0, 0, 0)
        self._alert_list_layout.setSpacing(Spacing.XS)
        self._alert_list_container.setVisible(False)
        layout.addWidget(self._alert_list_container)

        layout.addStretch()

    # ================================================================
    # Summary Bar
    # ================================================================

    def _update_summary_bar_initial(self) -> None:
        """Show initial summary with site count from config (Task 3.1)."""
        sites = self._site_repo.get_all()
        total = len(sites)
        self._summary_bar.setText(
            f"站点: {total} | 告警: -- | 总消耗: --",
        )

    def _update_summary_bar(
        self, total_sites: int, upstream_count: int,
        alert_count: int, total_consumption: str,
    ) -> None:
        """Update summary bar with inspection results (Task 3.1, 3.6)."""
        # Build rich text: alert count colored
        if alert_count > 0:
            alert_part = f'<span style="color:{Colors.DANGER};font-weight:{FontWeights.SEMIBOLD};">{alert_count}</span>'
        else:
            alert_part = f'<span style="color:{Colors.SUCCESS};font-weight:{FontWeights.SEMIBOLD};">0</span>'

        html = (
            f'<span style="font-size:{FontSizes.BODY_SMALL}px;color:{Colors.TEXT_SECONDARY};">'
            f'站点: <b>{total_sites}</b>'
            f' | 上游: <b>{upstream_count}</b>'
            f' | 告警: {alert_part}'
            f' | 总消耗: <b>{total_consumption}</b>'
            f'</span>'
        )
        self._summary_bar.setTextFormat(Qt.TextFormat.RichText)
        self._summary_bar.setText(html)

    # ================================================================
    # Inspection Logic
    # ================================================================

    def _start_inspection(self) -> None:
        from api_finance_dashboard.engine.automation_profile import (
            ensure_automation_profile_dir,
        )

        automation_path = self._config_repo.get_automation_profile_path()
        ensure_automation_profile_dir(automation_path)

        is_valid, msg = validate_browser_profile_path(automation_path)
        if not is_valid:
            QMessageBox.warning(self, "配置目录无效", msg)
            return

        has_conflict, msg = detect_browser_conflict(automation_path)
        if has_conflict:
            QMessageBox.critical(self, "⚠️ 自动化浏览器冲突", msg)
            return

        sites = self._site_repo.get_all()
        if not sites:
            QMessageBox.information(
                self, "无站点", "请先在设置中添加站点。",
            )
            return

        exchange_rate = Decimal(self._config_repo.get_exchange_rate())
        display_currency = Currency(self._config_repo.get_display_currency())

        self._inspect_btn.setEnabled(False)
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)

        executable_path = self._config_repo.get_browser_executable()
        self._worker = InspectionWorker(
            sites, automation_path, exchange_rate, display_currency,
            executable_path,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, current: int, total: int, site_name: str) -> None:
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(current)
        self._progress_bar.setFormat(f"正在巡检 {site_name}... ({current}/{total})")

    def _on_finished(self, result: InspectionResult) -> None:
        self._inspect_btn.setEnabled(True)
        self._progress_bar.setVisible(False)
        self._last_result = result

        # --- Task 3.2: Profit display with trend arrows ---
        self._update_profit_display(result)

        self._last_time_label.setText(
            f"上次巡检时间：{result.inspected_at.strftime('%Y-%m-%d %H:%M:%S')}",
        )

        # --- Task 3.6: Calculate and update summary bar ---
        self._update_summary_from_result(result)

        # --- Update alert sidebar (Tasks 5.1-5.3) ---
        self._update_alert_sidebar(result)

        # --- Update super table (Tasks 6.1-6.9) ---
        self._status_list.update_results(list(result.site_results))

        # --- Update profit detail (Task 3.4) ---
        self._update_profit_detail(result)

        # --- Task 8.1: Alert popup for low balance sites ---
        self._show_alert_popup(result)

        # System notification for low balance
        check_and_alert(list(result.site_results))

        # Show calculation warnings if any
        if result.warnings:
            QMessageBox.information(
                self, "巡检警告",
                "\n".join(result.warnings),
            )

    def _on_error(self, error_msg: str) -> None:
        self._inspect_btn.setEnabled(True)
        self._progress_bar.setVisible(False)
        QMessageBox.critical(self, "巡检错误", error_msg)

    def _open_settings(self) -> None:
        dialog = SettingsPanel(self._site_repo, self._config_repo, self)
        dialog.exec()

    # ================================================================
    # Dashboard Updates
    # ================================================================

    def _update_profit_display(self, result: InspectionResult) -> None:
        """Update profit label with trend arrows (Task 3.2)."""
        if result.net_profit is not None:
            symbol = "￥" if result.profit_currency == Currency.CNY else "$"
            profit_val = result.net_profit

            if profit_val >= 0:
                display_text = f"↑ {symbol}{profit_val}"
                color = Colors.SUCCESS
            else:
                display_text = f"↓ {symbol}{profit_val}"
                color = Colors.DANGER

            self._profit_label.setText(display_text)
            self._profit_label.setStyleSheet(
                f"font-size: {FontSizes.TITLE_HERO}px;"
                f" font-weight: {FontWeights.BOLD};"
                f" color: {color};"
                " text-decoration: underline;"
            )
        else:
            self._profit_label.setText("N/A")
            self._profit_label.setStyleSheet(PROFIT_LABEL_NA_STYLE)

    def _update_summary_from_result(self, result: InspectionResult) -> None:
        """Calculate summary data and update summary bar (Task 3.6)."""
        all_results = list(result.site_results)
        total_sites = len(all_results)
        upstream_results = [r for r in all_results if r.site.type == SiteType.UPSTREAM]
        upstream_count = len(upstream_results)
        alert_count = sum(
            1 for r in all_results if r.status == SiteStatus.LOW_BALANCE
        )

        # Calculate total consumption in display currency
        exchange_rate = Decimal(self._config_repo.get_exchange_rate())
        target = result.profit_currency
        total_consumption = Decimal("0")
        for r in all_results:
            cons = r.consumption if r.consumption is not None else Decimal("0")
            if r.site.currency != target:
                if r.site.currency == Currency.USD and target == Currency.CNY:
                    cons = cons * exchange_rate
                elif exchange_rate:
                    cons = cons / exchange_rate
            total_consumption += cons

        symbol = "￥" if target == Currency.CNY else "$"
        cons_text = f"{symbol}{total_consumption.quantize(Decimal('0.01'))}"

        self._update_summary_bar(total_sites, upstream_count, alert_count, cons_text)

    def _update_alert_sidebar(self, result: InspectionResult) -> None:
        """Update alert sidebar appearance — Tasks 5.1-5.3."""
        low_balance = [
            r for r in result.site_results if r.status == SiteStatus.LOW_BALANCE
        ]

        # Clear previous alert entries
        while self._alert_list_layout.count():
            item = self._alert_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not low_balance:
            # No alerts — normal white card
            self._alert_sidebar.setStyleSheet(
                f"QFrame#card {{"
                f"  background-color: {Colors.BG_CARD};"
                f"  border-radius: {BorderRadius.XL}px;"
                f"  border: none;"
                f"}}",
            )
            self._alert_content.setText("✅ 所有上游额度正常")
            self._alert_content.setStyleSheet(
                ALERT_SUMMARY_NORMAL_STYLE
                + " background: transparent; border: none;",
            )
            self._alert_list_container.setVisible(False)
        else:
            # Alert state — light red bg + left 4px red border
            self._alert_sidebar.setStyleSheet(
                f"QFrame#card {{"
                f"  background-color: {Colors.BG_DANGER_SOFT};"
                f"  border-radius: {BorderRadius.XL}px;"
                f"  border: none;"
                f"  border-left: 4px solid {Colors.DANGER};"
                f"}}",
            )
            self._alert_content.setText(
                f"⚠️ {len(low_balance)} 个上游额度告急",
            )
            self._alert_content.setStyleSheet(
                ALERT_SUMMARY_DANGER_STYLE
                + " background: transparent; border: none;",
            )

            # Task 5.3: Individual alert entries
            self._alert_list_container.setVisible(True)
            for r in low_balance:
                entry = self._build_alert_entry(r)
                self._alert_list_layout.addWidget(entry)

    @staticmethod
    def _build_alert_entry(result: SiteResult) -> QWidget:
        """Build a single alert entry for the sidebar (Task 5.3)."""
        entry = QWidget()
        layout = QHBoxLayout(entry)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(Spacing.XS)

        # Red dot marker
        dot = QLabel("●")
        dot.setStyleSheet(
            f"color: {Colors.DANGER}; font-size: 8px;"
            " background: transparent; border: none;",
        )
        dot.setFixedWidth(12)
        layout.addWidget(dot)

        # Site info
        sym = "￥" if result.site.currency.value == "CNY" else "$"
        threshold = result.site.alert_threshold or Decimal("0")
        info = QLabel(f"{result.site.name}\n{sym}{result.balance}/{sym}{threshold}")
        info.setWordWrap(True)
        info.setStyleSheet(
            f"font-size: {FontSizes.BODY_SMALL}px;"
            f" color: {Colors.BADGE_DANGER_TEXT};"
            f" font-weight: {FontWeights.MEDIUM};"
            " background: transparent; border: none;",
        )
        layout.addWidget(info, stretch=1)
        return entry

    def _show_alert_popup(self, result: InspectionResult) -> None:
        """Show alert popup for low balance sites — uses native QMessageBox."""
        low_balance_sites = [
            r for r in result.site_results
            if r.status == SiteStatus.LOW_BALANCE
        ]
        if not low_balance_sites:
            return

        alert_lines = []
        for r in low_balance_sites:
            sym = "￥" if r.site.currency.value == "CNY" else "$"
            threshold = r.site.alert_threshold or Decimal("0")
            alert_lines.append(
                f"  {r.site.name}：余额 {sym}{r.balance}，"
                f"低于阈值 {sym}{threshold}",
            )

        QMessageBox.warning(
            self,
            "额度告警",
            f"以下 {len(low_balance_sites)} 个上游额度告急：\n\n"
            + "\n".join(alert_lines),
        )

    # ================================================================
    # Profit Detail
    # ================================================================

    def _toggle_profit_detail(self) -> None:
        """Toggle the profit detail collapsible panel."""
        self._profit_detail_panel.toggle()

    def _update_profit_detail(self, result: InspectionResult) -> None:
        """Build the profit detail breakdown content (Task 3.4: table-style layout)."""
        lines = []
        exchange_rate = Decimal(self._config_repo.get_exchange_rate())
        target = result.profit_currency

        # Main site consumption
        main_results = [r for r in result.site_results if r.site.type == SiteType.MAIN]
        for r in main_results:
            sym = "￥" if r.site.currency.value == "CNY" else "$"
            cons = r.consumption if r.consumption is not None else Decimal("0")
            line = f"主站消耗 ({r.site.name})：{sym}{cons}"
            # Cross-currency annotation
            if r.site.currency != target:
                target_sym = "￥" if target == Currency.CNY else "$"
                if r.site.currency == Currency.USD and target == Currency.CNY:
                    converted = cons * exchange_rate
                else:
                    converted = cons / exchange_rate if exchange_rate else cons
                converted = converted.quantize(Decimal("0.01"))
                line += f"  (≈ {target_sym}{converted})"
            lines.append(line)

        lines.append("")
        lines.append("上游消耗明细：")

        # Upstream consumption — table-style layout (Task 3.4)
        upstream_total = Decimal("0")
        upstream_results = [
            r for r in result.site_results if r.site.type == SiteType.UPSTREAM
        ]
        for r in upstream_results:
            sym = "￥" if r.site.currency.value == "CNY" else "$"
            cons = r.consumption if r.consumption is not None else Decimal("0")
            line = f"  {r.site.name}：{sym}{cons}"
            # Cross-currency annotation
            converted_cons = cons
            if r.site.currency != target:
                target_sym = "￥" if target == Currency.CNY else "$"
                if r.site.currency == Currency.USD and target == Currency.CNY:
                    converted_cons = cons * exchange_rate
                else:
                    converted_cons = (
                        cons / exchange_rate if exchange_rate else cons
                    )
                converted_cons = converted_cons.quantize(Decimal("0.01"))
                line += f"  (≈ {target_sym}{converted_cons})"
            upstream_total += converted_cons
            lines.append(line)

        target_sym = "￥" if target == Currency.CNY else "$"
        lines.append(
            f"\n上游总消耗：{target_sym}{upstream_total.quantize(Decimal('0.01'))}",
        )

        self._profit_detail_content.setText("\n".join(lines))
