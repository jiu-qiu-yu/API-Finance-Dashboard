"""Inspection service that orchestrates the full inspection workflow."""

import asyncio
from decimal import Decimal
from typing import Callable

from api_finance_dashboard.data.models import (
    Currency, InspectionResult, SiteConfig, SiteResult,
)
from api_finance_dashboard.engine.browser_engine import BrowserEngine
from api_finance_dashboard.engine.calculation_engine import calculate_net_profit
from api_finance_dashboard.engine.notifier import check_and_alert
from api_finance_dashboard.engine.scraping_engine import ScrapingEngine


class InspectionService:
    """Coordinates full inspection: scrape all sites, calculate, alert."""

    def __init__(
        self,
        automation_profile_path: str,
        exchange_rate: Decimal,
        target_currency: Currency = Currency.CNY,
        executable_path: str | None = None,
    ) -> None:
        self._profile_path = automation_profile_path
        self._executable_path = executable_path
        self._exchange_rate = exchange_rate
        self._target_currency = target_currency
        self._on_progress: Callable[[int, int, str], None] | None = None

    def set_progress_callback(
        self, callback: Callable[[int, int, str], None]
    ) -> None:
        """Set callback for progress updates: (current, total, site_name)."""
        self._on_progress = callback

    async def run_inspection(
        self, sites: list[SiteConfig]
    ) -> InspectionResult:
        """Run full inspection across all configured sites."""
        browser = BrowserEngine(
            self._profile_path,
            executable_path=self._executable_path,
        )
        scraper = ScrapingEngine(browser)
        results: list[SiteResult] = []

        await browser.start()
        try:
            for i, site in enumerate(sites):
                if self._on_progress:
                    self._on_progress(i + 1, len(sites), site.name)

                result = await scraper.scrape_site(site)
                results.append(result)
        finally:
            await browser.stop()  # stop() never raises

        # Calculate net profit
        inspection = calculate_net_profit(
            results, self._exchange_rate, self._target_currency
        )

        # Check thresholds and send alerts
        check_and_alert(results)

        return inspection
