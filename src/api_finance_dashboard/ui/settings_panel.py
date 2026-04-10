"""Settings panel for site management and global configuration."""

import asyncio
from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from api_finance_dashboard.data.config_repository import ConfigRepository
from api_finance_dashboard.data.models import Currency, SiteType
from api_finance_dashboard.data.site_repository import SiteRepository
from api_finance_dashboard.engine.browser_detector import scan_installed_browsers
from api_finance_dashboard.engine.presets import PANEL_PRESETS
from api_finance_dashboard.ui.styles import (
    BorderRadius,
    Colors,
    DANGER_BTN_STYLE,
    FontSizes,
    FontWeights,
    Shadows,
    Spacing,
)


class _TestScrapeWorker(QThread):
    """Background worker for test scraping."""

    finished = Signal(dict)
    error = Signal(str)

    def __init__(
        self, automation_profile_path: str, url: str, panel_type: str,
        css_selector: str | None,
        executable_path: str | None = None,
        dashboard_url: str | None = None,
    ) -> None:
        super().__init__()
        self._automation_profile_path = automation_profile_path
        self._url = url
        self._panel_type = panel_type
        self._css_selector = css_selector
        self._executable_path = executable_path
        self._dashboard_url = dashboard_url

    def run(self) -> None:
        try:
            from api_finance_dashboard.engine.browser_engine import BrowserEngine
            from api_finance_dashboard.engine.scraping_engine import ScrapingEngine

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self._run_scrape())
                self.finished.emit(result)
            finally:
                loop.close()
        except Exception as e:
            self.error.emit(str(e))

    async def _run_scrape(self) -> dict:
        from api_finance_dashboard.engine.browser_engine import BrowserEngine
        from api_finance_dashboard.engine.scraping_engine import ScrapingEngine

        engine = BrowserEngine(
            self._automation_profile_path,
            executable_path=self._executable_path,
        )
        await engine.start()
        try:
            scraper = ScrapingEngine(engine)
            return await scraper.test_scrape(
                self._url, self._panel_type, self._css_selector,
                dashboard_url=self._dashboard_url,
            )
        finally:
            await engine.stop()  # stop() never raises


class SiteEditForm(QWidget):
    """Form for adding/editing a site configuration."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        form = QFormLayout(self)

        self.name_input = QLineEdit()
        form.addRow("站点名称：", self.name_input)

        self.type_combo = QComboBox()
        self.type_combo.addItem("主站", "main")
        self.type_combo.addItem("上游", "upstream")
        form.addRow("类型：", self.type_combo)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://panel.example.com/log")
        form.addRow("使用日志地址：", self.url_input)

        self.dashboard_url_input = QLineEdit()
        self.dashboard_url_input.setPlaceholderText("https://panel.example.com/dashboard（仅上游需要）")
        self._dashboard_url_label = QLabel("数据看板地址：")
        form.addRow(self._dashboard_url_label, self.dashboard_url_input)

        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        self._on_type_changed()

        self.panel_combo = QComboBox()
        for key, preset in PANEL_PRESETS.items():
            if preset.github_repo:
                label = f"{preset.name} ({preset.github_repo})"
            else:
                label = f"{preset.name} (自定义)"
            self.panel_combo.addItem(label, key)
        self.panel_combo.currentIndexChanged.connect(self._on_panel_changed)
        form.addRow("面板类型：", self.panel_combo)

        self.css_input = QLineEdit()
        self.css_input.setPlaceholderText("CSS 选择器（可选）")
        form.addRow("CSS 选择器：", self.css_input)

        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("正则表达式（可选）")
        form.addRow("正则表达式：", self.regex_input)

        self.currency_combo = QComboBox()
        self.currency_combo.addItem("USD ($)", "USD")
        self.currency_combo.addItem("CNY (￥)", "CNY")
        form.addRow("货币：", self.currency_combo)

        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setRange(0, 999999)
        self.threshold_input.setDecimals(2)
        self.threshold_input.setValue(10.00)
        self.threshold_input.setPrefix("$ ")
        self.threshold_input.setToolTip("当余额低于此值时将触发告警（标红 + 弹窗 + 系统通知）")
        form.addRow("告警阈值：", self.threshold_input)

        threshold_hint = QLabel("提示：余额低于阈值将触发标红、弹窗和系统通知")
        threshold_hint.setStyleSheet("font-size: 11px; color: #888;")
        form.addRow("", threshold_hint)

        btn_row = QHBoxLayout()
        self.login_site_btn = QPushButton("登录此站点")
        self.login_site_btn.setToolTip("打开自动化浏览器登录此站点，登录后关闭浏览器即可")
        self.login_site_btn.setStyleSheet(
            "QPushButton { padding: 6px 16px; font-size: 13px; }"
        )
        self.login_site_btn.setMinimumHeight(32)
        btn_row.addWidget(self.login_site_btn)

        self.test_scrape_btn = QPushButton("测试抓取")
        self.test_scrape_btn.setToolTip("使用当前配置执行一次测试抓取，预览匹配结果")
        self.test_scrape_btn.setStyleSheet(
            "QPushButton { padding: 6px 16px; font-size: 13px; }"
        )
        self.test_scrape_btn.setMinimumHeight(32)
        btn_row.addWidget(self.test_scrape_btn)
        form.addRow(btn_row)

    def _on_type_changed(self, _index: int = 0) -> None:
        is_upstream = self.type_combo.currentData() == "upstream"
        self.dashboard_url_input.setVisible(is_upstream)
        self._dashboard_url_label.setVisible(is_upstream)

    def _on_panel_changed(self, _index: int) -> None:
        key = self.panel_combo.currentData()
        preset = PANEL_PRESETS.get(key)
        if preset and key != "custom" and preset.consumption_selectors:
            self.css_input.setText(", ".join(preset.consumption_selectors))

    def get_data(self) -> dict | None:
        name = self.name_input.text().strip()
        url = self.url_input.text().strip()
        if not name or not url:
            QMessageBox.warning(self, "验证失败", "站点名称和面板地址为必填项。")
            return None
        dashboard_url = self.dashboard_url_input.text().strip() or None
        return {
            "name": name,
            "site_type": SiteType(self.type_combo.currentData()),
            "url": url,
            "panel_type": self.panel_combo.currentData(),
            "css_selector": self.css_input.text().strip() or None,
            "regex_pattern": self.regex_input.text().strip() or None,
            "currency": Currency(self.currency_combo.currentData()),
            "alert_threshold": Decimal(str(self.threshold_input.value())),
            "dashboard_url": dashboard_url,
        }


class SettingsPanel(QDialog):
    """Settings dialog with tabs for site management and global settings."""

    def __init__(
        self,
        site_repo: SiteRepository,
        config_repo: ConfigRepository,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumSize(700, 500)
        self._site_repo = site_repo
        self._config_repo = config_repo

        # Dialog styling — macOS visual polish
        self.setStyleSheet(
            f"QDialog {{"
            f"  border-radius: {BorderRadius.XL}px;"
            f"  background-color: {Colors.BG_CARD};"
            f"}}"
            # Input styling with navy-blue focus highlight (Task 6.3)
            f"QLineEdit, QDoubleSpinBox, QComboBox {{"
            f"  border: 1px solid #d9d9d9;"
            f"  border-radius: {BorderRadius.SM}px;"
            f"  padding: 6px 8px;"
            f"  font-size: {FontSizes.BODY}px;"
            f"  background-color: #ffffff;"
            f"}}"
            f"QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {{"
            f"  border: 1px solid {Colors.PRIMARY};"
            f"  outline: none;"
            f"}}"
            # Default button — capsule style
            f"QPushButton {{"
            f"  padding: 8px 16px;"
            f"  font-size: {FontSizes.BODY}px;"
            f"  border-radius: {BorderRadius.CAPSULE}px;"
            f"  border: 1px solid {Colors.SEPARATOR};"
            f"  background-color: transparent;"
            f"  color: {Colors.TEXT_PRIMARY};"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {Colors.ROW_HOVER};"
            f"}}"
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.LG)
        tabs = QTabWidget()

        tabs.addTab(self._build_sites_tab(), "站点管理")
        tabs.addTab(self._build_global_tab(), "全局设置")

        layout.addWidget(tabs)

    def _build_sites_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Left: site list
        left = QVBoxLayout()
        self._site_list = QListWidget()
        self._site_list.currentRowChanged.connect(self._on_site_selected)
        left.addWidget(QLabel("站点列表："))
        left.addWidget(self._site_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("添加")
        add_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {Colors.PRIMARY};"
            f"  color: {Colors.TEXT_WHITE};"
            f"  border: none;"
            f"  border-radius: {BorderRadius.CAPSULE}px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {Colors.PRIMARY_HOVER};"
            f"}}"
        )
        add_btn.clicked.connect(self._add_site)
        del_btn = QPushButton("删除")
        del_btn.setStyleSheet(DANGER_BTN_STYLE)
        del_btn.clicked.connect(self._delete_site)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        left.addLayout(btn_row)
        layout.addLayout(left, stretch=1)

        # Right: edit form
        right = QVBoxLayout()
        self._form = SiteEditForm()
        self._form.test_scrape_btn.clicked.connect(self._test_scrape)
        self._form.login_site_btn.clicked.connect(self._login_site)
        right.addWidget(self._form)

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {Colors.PRIMARY};"
            f"  color: {Colors.TEXT_WHITE};"
            f"  padding: 12px 28px;"
            f"  font-size: {FontSizes.BODY}px;"
            f"  border-radius: {BorderRadius.CAPSULE}px;"
            f"  border: none;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {Colors.PRIMARY_HOVER};"
            f"}}"
        )
        save_btn.clicked.connect(self._save_site)
        right.addWidget(save_btn)
        layout.addLayout(right, stretch=2)

        self._refresh_site_list()
        return widget

    def _build_global_tab(self) -> QWidget:
        widget = QWidget()
        outer = QVBoxLayout(widget)

        # --- Automation browser group (primary) ---
        auto_group = QGroupBox("自动化浏览器")
        auto_form = QFormLayout(auto_group)

        automation_path = self._config_repo.get_automation_profile_path()
        self._automation_path_label = QLabel(automation_path)
        self._automation_path_label.setWordWrap(True)
        self._automation_path_label.setStyleSheet("font-size: 11px; color: #555;")
        auto_form.addRow("配置目录：", self._automation_path_label)

        reset_btn = QPushButton("重置自动化浏览器")
        reset_btn.setToolTip("清空自动化浏览器数据，所有站点需要重新登录")
        reset_btn.setStyleSheet(DANGER_BTN_STYLE)
        reset_btn.clicked.connect(self._reset_automation_browser)
        auto_form.addRow("", reset_btn)

        # Browser executable detection
        detect_row = QHBoxLayout()
        self._browser_type_label = QLabel(
            self._config_repo.get_browser_type() or "未检测"
        )
        detect_btn = QPushButton("自动检测浏览器")
        detect_btn.clicked.connect(self._detect_browser)
        detect_row.addWidget(self._browser_type_label)
        detect_row.addWidget(detect_btn)
        auto_form.addRow("浏览器：", detect_row)

        auto_hint = QLabel("提示：自动化浏览器使用独立配置，与您的日常浏览器互不干扰。巡检时无需关闭日常浏览器。")
        auto_hint.setStyleSheet("font-size: 11px; color: #27ae60;")
        auto_hint.setWordWrap(True)
        auto_form.addRow("", auto_hint)
        outer.addWidget(auto_group)

        # Currency group
        currency_group = QGroupBox("货币与汇率")
        currency_form = QFormLayout(currency_group)
        self._rate_input = QLineEdit(self._config_repo.get_exchange_rate())
        self._rate_input.setToolTip("用于将 USD 消耗转换为 CNY 显示")
        currency_form.addRow("汇率（1 USD = ? CNY）：", self._rate_input)

        self._currency_combo = QComboBox()
        self._currency_combo.addItem("CNY (￥)", "CNY")
        self._currency_combo.addItem("USD ($)", "USD")
        current = self._config_repo.get_display_currency()
        idx = self._currency_combo.findData(current)
        if idx >= 0:
            self._currency_combo.setCurrentIndex(idx)
        currency_form.addRow("显示货币：", self._currency_combo)
        outer.addWidget(currency_group)

        outer.addStretch()

        save_btn = QPushButton("保存全局设置")
        save_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {Colors.PRIMARY};"
            f"  color: {Colors.TEXT_WHITE};"
            f"  padding: 12px 28px;"
            f"  font-size: {FontSizes.BODY}px;"
            f"  border-radius: {BorderRadius.CAPSULE}px;"
            f"  border: none;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {Colors.PRIMARY_HOVER};"
            f"}}"
        )
        save_btn.clicked.connect(self._save_global)
        outer.addWidget(save_btn)

        return widget

    def _refresh_site_list(self) -> None:
        self._site_list.clear()
        self._sites = self._site_repo.get_all()
        for site in self._sites:
            prefix = "[主站]" if site.type == SiteType.MAIN else "[上游]"
            item = QListWidgetItem(f"{prefix} {site.name}")
            item.setData(Qt.ItemDataRole.UserRole, site.id)
            self._site_list.addItem(item)

    def _on_site_selected(self, row: int) -> None:
        if row < 0 or row >= len(self._sites):
            return
        site = self._sites[row]
        self._form.name_input.setText(site.name)
        idx = self._form.type_combo.findData(site.type.value)
        if idx >= 0:
            self._form.type_combo.setCurrentIndex(idx)
        self._form.url_input.setText(site.url)
        self._form.dashboard_url_input.setText(site.dashboard_url or "")
        idx = self._form.panel_combo.findData(site.panel_type)
        if idx >= 0:
            self._form.panel_combo.setCurrentIndex(idx)
        self._form.css_input.setText(site.css_selector or "")
        self._form.regex_input.setText(site.regex_pattern or "")
        idx = self._form.currency_combo.findData(site.currency.value)
        if idx >= 0:
            self._form.currency_combo.setCurrentIndex(idx)
        self._form.threshold_input.setValue(
            float(site.alert_threshold) if site.alert_threshold else 5.0
        )

    def _add_site(self) -> None:
        data = self._form.get_data()
        if data:
            self._site_repo.create(**data)
            self._refresh_site_list()

    def _save_site(self) -> None:
        current = self._site_list.currentItem()
        if not current:
            self._add_site()
            return
        site_id = current.data(Qt.ItemDataRole.UserRole)
        data = self._form.get_data()
        if data:
            self._site_repo.update(site_id, **data)
            self._refresh_site_list()

    def _delete_site(self) -> None:
        current = self._site_list.currentItem()
        if not current:
            return
        site_id = current.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除站点 '{current.text()}' 吗？",
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._site_repo.delete(site_id)
            self._refresh_site_list()

    def _detect_browser(self) -> None:
        browsers = scan_installed_browsers()
        if not browsers:
            QMessageBox.warning(
                self, "未找到浏览器",
                "未检测到已安装的 Chrome/Edge 浏览器。",
            )
            return

        if len(browsers) == 1:
            chosen = browsers[0]
        else:
            items = [f"{b.display_name}  ({b.profile_path})" for b in browsers]
            from PySide6.QtWidgets import QInputDialog
            item, ok = QInputDialog.getItem(
                self, "选择浏览器", "检测到多个浏览器，请选择：", items, 0, False,
            )
            if not ok:
                return
            chosen = browsers[items.index(item)]

        self._browser_type_label.setText(chosen.display_name)
        self._config_repo.set_browser_type(chosen.browser_type)
        if chosen.executable_path:
            self._config_repo.set_browser_executable(chosen.executable_path)
        QMessageBox.information(
            self, "检测完成",
            f"已检测到浏览器：{chosen.display_name}",
        )

    def _reset_automation_browser(self) -> None:
        reply = QMessageBox.question(
            self, "确认重置",
            "重置自动化浏览器将清空所有登录数据。\n"
            "所有站点需要重新点击「登录此站点」。\n\n"
            "确定要重置吗？",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        from api_finance_dashboard.engine.automation_profile import (
            reset_automation_profile,
        )
        automation_path = self._config_repo.get_automation_profile_path()
        reset_automation_profile(automation_path)
        QMessageBox.information(
            self, "重置完成",
            "自动化浏览器已重置。\n请对每个站点重新执行「登录此站点」。",
        )

    def _login_site(self) -> None:
        url = self._form.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "URL 为空", "请先填写使用日志地址。")
            return

        from api_finance_dashboard.engine.automation_profile import (
            ensure_automation_profile_dir,
        )
        from api_finance_dashboard.ui.automation_login_worker import SiteLoginWorker

        automation_path = self._config_repo.get_automation_profile_path()
        ensure_automation_profile_dir(automation_path)

        executable_path = self._config_repo.get_browser_executable()

        self._form.login_site_btn.setEnabled(False)
        self._form.login_site_btn.setText("登录中（请在浏览器中操作）...")

        self._login_worker = SiteLoginWorker(
            executable_path, automation_path, url,
        )
        self._login_worker.finished.connect(self._on_login_finished)
        self._login_worker.error.connect(self._on_login_error)
        self._login_worker.start()

    def _on_login_finished(self) -> None:
        if not self._form.login_site_btn.isEnabled():
            self._form.login_site_btn.setEnabled(True)
            self._form.login_site_btn.setText("登录此站点")
            QMessageBox.information(
                self, "登录完成",
                "浏览器已关闭，登录数据已保存。\n\n"
                "请点击「测试抓取」验证登录是否成功。",
            )

    def _on_login_error(self, error: str) -> None:
        if not self._form.login_site_btn.isEnabled():
            self._form.login_site_btn.setEnabled(True)
            self._form.login_site_btn.setText("登录此站点")
            QMessageBox.critical(self, "登录失败", f"浏览器启动失败：{error}")

    def _test_scrape(self) -> None:
        from api_finance_dashboard.engine.automation_profile import (
            ensure_automation_profile_dir,
        )
        from api_finance_dashboard.engine.browser_engine import (
            detect_browser_conflict,
            validate_browser_profile_path,
        )

        automation_path = self._config_repo.get_automation_profile_path()
        ensure_automation_profile_dir(automation_path)

        valid, msg = validate_browser_profile_path(automation_path)
        if not valid:
            QMessageBox.warning(self, "配置目录无效", f"{msg}\n\n请检查路径是否正确。")
            return

        has_conflict, conflict_msg = detect_browser_conflict(automation_path)
        if has_conflict:
            QMessageBox.critical(
                self, "⚠️ 自动化浏览器冲突",
                conflict_msg,
            )
            return

        url = self._form.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "URL 为空", "请先填写使用日志地址。")
            return
        panel_type = self._form.panel_combo.currentData()
        css_selector = self._form.css_input.text().strip() or None

        self._form.test_scrape_btn.setEnabled(False)
        self._form.test_scrape_btn.setText("抓取中（请等待浏览器启动）...")

        executable_path = self._config_repo.get_browser_executable()
        dashboard_url = self._form.dashboard_url_input.text().strip() or None
        self._test_worker = _TestScrapeWorker(
            automation_path, url, panel_type, css_selector,
            executable_path=executable_path,
            dashboard_url=dashboard_url,
        )
        self._test_worker.finished.connect(self._on_test_scrape_done)
        self._test_worker.error.connect(self._on_test_scrape_error)
        self._test_worker.start()

    def _on_test_scrape_done(self, result: dict) -> None:
        self._form.test_scrape_btn.setEnabled(True)
        self._form.test_scrape_btn.setText("测试抓取")

        if result.get("success"):
            method_names = {
                "css_selector": "CSS 选择器（第1层）",
                "anchor_text": "锚点文本搜索（第2层）",
                "keyword_proximity": "关键词邻近匹配（第3层）",
                "none": "未匹配",
            }
            parts = []
            if result.get("consumption"):
                c_method = method_names.get(result["consumption_method"], result["consumption_method"])
                parts.append(f"今日消耗：{result['consumption']} {result.get('consumption_currency', '')}\n匹配方式：{c_method}")
            if result.get("balance"):
                b_method = method_names.get(result["balance_method"], result["balance_method"])
                parts.append(f"剩余额度：{result['balance']} {result.get('balance_currency', '')}\n匹配方式：{b_method}")

            if not result.get("balance") and self._form.type_combo.currentData() == "upstream":
                parts.append("余额：将在巡检时从数据看板地址抓取")
            msg = "\n\n".join(parts) if parts else "未提取到有效数据"
            QMessageBox.information(self, "测试抓取结果", msg)
        else:
            error = result.get("error", "")
            snippet = result.get("page_snippet", "")
            if error:
                detail = f"错误：{error}"
            elif snippet:
                detail = (
                    "页面已加载但未提取到数据。\n"
                    f"页面内容预览：\n{snippet[:200]}..."
                )
            else:
                detail = "页面已加载但未提取到数据。"
            QMessageBox.warning(
                self, "测试抓取失败",
                f"{detail}\n\n"
                "排查建议：\n"
                "1. 确认已通过「登录此站点」登录\n"
                "2. 检查面板类型是否匹配\n"
                "3. 尝试使用自定义 CSS 选择器",
            )

    def _on_test_scrape_error(self, error: str) -> None:
        self._form.test_scrape_btn.setEnabled(True)
        self._form.test_scrape_btn.setText("测试抓取")
        error_lower = error.lower()
        if "不受支持的启动参数警告页" in error or "unsupported launch" in error_lower:
            QMessageBox.critical(
                self, "浏览器启动失败",
                "检测到浏览器被不受支持的启动参数阻塞。\n\n"
                "请确认不要传入 --no-sandbox，然后重试。",
            )
        elif "about:blank" in error_lower or "空白页" in error:
            QMessageBox.critical(
                self, "浏览器启动失败",
                "浏览器启动后一直停留在 about:blank。\n\n"
                "这通常表示当前 Chrome/Edge 主配置目录不支持自动化复用。\n"
                "请改用单独的浏览器配置目录或新的用户数据目录后重试。",
            )
        elif "user data dir" in error_lower or "already running" in error_lower:
            QMessageBox.critical(
                self, "浏览器启动失败",
                "无法使用您的浏览器配置启动测试。\n\n"
                "最常见原因：浏览器仍在运行中。\n"
                "请关闭所有浏览器窗口后再试。",
            )
        else:
            QMessageBox.critical(self, "测试抓取异常", f"发生错误：{error}")

    def _save_global(self) -> None:
        rate = self._rate_input.text().strip()
        try:
            Decimal(rate)
        except InvalidOperation:
            QMessageBox.warning(self, "汇率无效", "汇率必须为数字。")
            return
        self._config_repo.set_exchange_rate(rate)
        self._config_repo.set_display_currency(self._currency_combo.currentData())
        QMessageBox.information(self, "已保存", "全局设置已保存。")
