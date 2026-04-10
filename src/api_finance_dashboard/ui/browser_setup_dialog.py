"""Browser setup dialog - guides user through browser installation on first launch."""

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from api_finance_dashboard.engine.browser_bootstrap import install_playwright_chromium
from api_finance_dashboard.ui.styles import (
    BorderRadius,
    Colors,
    FontSizes,
    FontWeights,
    INSPECT_BTN_STYLE,
    Spacing,
)


class _InstallWorker(QThread):
    """Background thread for Playwright Chromium installation."""

    finished = Signal(bool, str)  # (success, message)

    def run(self):
        success, message = install_playwright_chromium()
        self.finished.emit(success, message)


class BrowserSetupDialog(QDialog):
    """Dialog shown when no compatible browser is detected at startup."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("浏览器配置")
        self.setFixedWidth(480)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint
        )
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.LG)
        layout.setContentsMargins(
            Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL
        )

        # Title
        title = QLabel("未检测到兼容的浏览器")
        title.setStyleSheet(
            f"font-size: {FontSizes.TITLE_LARGE}px;"
            f" font-weight: {FontWeights.BOLD};"
            f" color: {Colors.TEXT_PRIMARY};"
        )
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "本应用需要 Chrome 或 Edge 浏览器来自动采集财务数据。\n\n"
            "推荐方案：安装 Google Chrome 或 Microsoft Edge\n"
            "备选方案：自动下载 Playwright 内置 Chromium（约 150MB）"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(
            f"font-size: {FontSizes.BODY}px;"
            f" color: {Colors.TEXT_SECONDARY};"
            f" line-height: 1.6;"
        )
        layout.addWidget(desc)

        # Progress bar (hidden initially)
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # indeterminate
        self._progress.setVisible(False)
        self._progress.setStyleSheet(
            f"QProgressBar {{"
            f"  border: none;"
            f"  border-radius: {BorderRadius.PROGRESS}px;"
            f"  background-color: {Colors.PROGRESS_BG};"
            f"  height: 6px;"
            f"}}"
            f"QProgressBar::chunk {{"
            f"  border-radius: {BorderRadius.PROGRESS}px;"
            f"  background-color: {Colors.PRIMARY};"
            f"}}"
        )
        layout.addWidget(self._progress)

        # Status label (hidden initially)
        self._status = QLabel()
        self._status.setAlignment(Qt.AlignCenter)
        self._status.setWordWrap(True)
        self._status.setVisible(False)
        layout.addWidget(self._status)

        # Install button
        self._install_btn = QPushButton("下载 Chromium 浏览器")
        self._install_btn.setStyleSheet(INSPECT_BTN_STYLE)
        self._install_btn.clicked.connect(self._on_install)
        layout.addWidget(self._install_btn)

        # Skip button
        self._skip_btn = QPushButton("稍后手动安装 Chrome")
        self._skip_btn.setStyleSheet(
            f"QPushButton {{"
            f"  padding: 8px 20px;"
            f"  font-size: {FontSizes.BODY}px;"
            f"  border: none;"
            f"  background: transparent;"
            f"  color: {Colors.TEXT_SECONDARY};"
            f"}}"
            f"QPushButton:hover {{"
            f"  color: {Colors.TEXT_PRIMARY};"
            f"}}"
        )
        self._skip_btn.clicked.connect(self.reject)
        layout.addWidget(self._skip_btn)

    def _on_install(self):
        self._install_btn.setEnabled(False)
        self._skip_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._status.setVisible(True)
        self._status.setText("正在下载 Chromium，请稍候...")
        self._status.setStyleSheet(
            f"font-size: {FontSizes.BODY_SMALL}px;"
            f" color: {Colors.TEXT_SECONDARY};"
        )

        self._worker = _InstallWorker()
        self._worker.finished.connect(self._on_install_finished)
        self._worker.start()

    def _on_install_finished(self, success: bool, message: str):
        self._progress.setVisible(False)

        if success:
            self._status.setText("Chromium 安装成功！")
            self._status.setStyleSheet(
                f"font-size: {FontSizes.BODY}px;"
                f" color: {Colors.SUCCESS};"
                f" font-weight: {FontWeights.SEMIBOLD};"
            )
            self._install_btn.setText("完成")
            self._install_btn.setEnabled(True)
            self._install_btn.clicked.disconnect()
            self._install_btn.clicked.connect(self.accept)
            self._skip_btn.setVisible(False)
        else:
            self._status.setText(f"安装失败：{message}")
            self._status.setStyleSheet(
                f"font-size: {FontSizes.BODY_SMALL}px;"
                f" color: {Colors.DANGER};"
            )
            self._install_btn.setText("重试")
            self._install_btn.setEnabled(True)
            self._skip_btn.setEnabled(True)
