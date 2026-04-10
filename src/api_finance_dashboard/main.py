"""Application entry point."""

import sys

from PySide6.QtWidgets import QApplication

from api_finance_dashboard.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("API Finance Dashboard")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
