"""QThread worker for per-site login via automation browser."""

import asyncio

from PySide6.QtCore import QThread, Signal


class SiteLoginWorker(QThread):
    """Launches automation browser for manual login, emits when done."""

    finished = Signal()
    error = Signal(str)

    def __init__(
        self,
        executable_path: str | None,
        automation_profile_path: str,
        target_url: str,
    ) -> None:
        super().__init__()
        self._executable_path = executable_path
        self._automation_profile_path = automation_profile_path
        self._target_url = target_url

    def run(self) -> None:
        try:
            from api_finance_dashboard.engine.automation_login import (
                run_login_session,
            )

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    run_login_session(
                        self._executable_path,
                        self._automation_profile_path,
                        self._target_url,
                    )
                )
                self.finished.emit()
            finally:
                loop.close()
        except Exception as e:
            self.error.emit(str(e))
