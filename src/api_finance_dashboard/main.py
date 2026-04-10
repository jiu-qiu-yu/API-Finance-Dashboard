"""Application entry point."""

import sys

from PySide6.QtWidgets import QApplication

from api_finance_dashboard.engine.browser_bootstrap import check_browser_availability
from api_finance_dashboard.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("API Finance Dashboard")

    # First-launch browser check
    result = check_browser_availability()
    if not result.available:
        from api_finance_dashboard.ui.browser_setup_dialog import (
            BrowserSetupDialog,
        )

        dialog = BrowserSetupDialog()
        dialog.exec()  # Non-blocking: user can skip and install Chrome later

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
