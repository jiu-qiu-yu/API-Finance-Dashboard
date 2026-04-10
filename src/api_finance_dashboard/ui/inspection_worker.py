"""QThread worker for running inspection in background."""

import asyncio
from decimal import Decimal

from PySide6.QtCore import QThread, Signal

from api_finance_dashboard.data.models import Currency, InspectionResult, SiteConfig
from api_finance_dashboard.service.inspection_service import InspectionService


class InspectionWorker(QThread):
    """Runs inspection in a background thread with async event loop."""

    progress = Signal(int, int, str)  # current, total, site_name
    finished = Signal(object)         # InspectionResult
    error = Signal(str)               # error message

    def __init__(
        self,
        sites: list[SiteConfig],
        automation_profile_path: str,
        exchange_rate: Decimal,
        target_currency: Currency,
        executable_path: str | None = None,
    ) -> None:
        super().__init__()
        self._sites = sites
        self._automation_profile_path = automation_profile_path
        self._exchange_rate = exchange_rate
        self._target_currency = target_currency
        self._executable_path = executable_path

    def run(self) -> None:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            service = InspectionService(
                self._automation_profile_path,
                self._exchange_rate,
                self._target_currency,
                self._executable_path,
            )
            service.set_progress_callback(
                lambda cur, total, name: self.progress.emit(cur, total, name)
            )

            result = loop.run_until_complete(
                service.run_inspection(self._sites)
            )
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            loop.close()
