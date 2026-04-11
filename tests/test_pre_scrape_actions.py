"""Unit tests for pre-scrape actions execution."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api_finance_dashboard.engine.presets import PreScrapeAction
from api_finance_dashboard.engine.scraping_engine import _execute_pre_scrape_actions


@pytest.fixture
def mock_page():
    """Create a mock Playwright Page with async methods."""
    page = AsyncMock()
    element = AsyncMock()
    page.wait_for_selector.return_value = element
    page.wait_for_timeout.return_value = None
    return page


class TestExecutePreScrapeActions:
    @pytest.mark.asyncio
    async def test_click_action(self, mock_page):
        actions = (PreScrapeAction(action_type="click", selector=".btn"),)
        await _execute_pre_scrape_actions(mock_page, actions)

        mock_page.wait_for_selector.assert_called_once_with(".btn", timeout=5000)
        element = mock_page.wait_for_selector.return_value
        element.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_select_option_action(self, mock_page):
        actions = (
            PreScrapeAction(
                action_type="select_option", selector="select.range", value="today"
            ),
        )
        await _execute_pre_scrape_actions(mock_page, actions)

        mock_page.wait_for_selector.assert_called_once_with("select.range", timeout=5000)
        element = mock_page.wait_for_selector.return_value
        element.select_option.assert_called_once_with("today")

    @pytest.mark.asyncio
    async def test_wait_action(self, mock_page):
        actions = (PreScrapeAction(action_type="wait", selector="body", value="2000"),)
        await _execute_pre_scrape_actions(mock_page, actions)

        mock_page.wait_for_timeout.assert_called_with(2000)

    @pytest.mark.asyncio
    async def test_wait_action_default_ms(self, mock_page):
        actions = (PreScrapeAction(action_type="wait", selector="body"),)
        await _execute_pre_scrape_actions(mock_page, actions)

        mock_page.wait_for_timeout.assert_called_with(1000)

    @pytest.mark.asyncio
    async def test_multiple_actions_in_order(self, mock_page):
        actions = (
            PreScrapeAction(action_type="click", selector=".btn1"),
            PreScrapeAction(action_type="click", selector=".btn2"),
            PreScrapeAction(action_type="wait", selector="body", value="500"),
        )
        await _execute_pre_scrape_actions(mock_page, actions)

        assert mock_page.wait_for_selector.call_count == 2
        # wait_for_timeout is called: once after click1, once after click2, once for wait action
        assert mock_page.wait_for_timeout.call_count == 3

    @pytest.mark.asyncio
    async def test_click_failure_continues(self, mock_page):
        """Action failure should not prevent subsequent actions from executing."""
        mock_page.wait_for_selector.side_effect = [
            Exception("Element not found"),
            AsyncMock(),  # Second call succeeds
        ]

        actions = (
            PreScrapeAction(action_type="click", selector=".missing"),
            PreScrapeAction(action_type="wait", selector="body", value="100"),
        )
        # Should not raise
        await _execute_pre_scrape_actions(mock_page, actions)

        # The wait action should still execute
        mock_page.wait_for_timeout.assert_called_with(100)

    @pytest.mark.asyncio
    async def test_selector_returns_none_logs_warning(self, mock_page):
        mock_page.wait_for_selector.return_value = None

        actions = (PreScrapeAction(action_type="click", selector=".missing"),)
        with patch("api_finance_dashboard.engine.scraping_engine.logger") as mock_logger:
            await _execute_pre_scrape_actions(mock_page, actions)
            mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_empty_actions_is_noop(self, mock_page):
        await _execute_pre_scrape_actions(mock_page, ())
        mock_page.wait_for_selector.assert_not_called()

    @pytest.mark.asyncio
    async def test_text_click_exact_match(self, mock_page):
        """text_click should click the first matching candidate text."""
        locator = AsyncMock()
        locator.count.return_value = 1
        locator.first = AsyncMock()
        # get_by_text is synchronous in Playwright (returns a Locator)
        mock_page.get_by_text = MagicMock(return_value=locator)

        actions = (PreScrapeAction(action_type="text_click", selector="今天,今日,Today"),)
        await _execute_pre_scrape_actions(mock_page, actions)

        mock_page.get_by_text.assert_called_once_with("今天", exact=True)
        locator.first.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_text_click_no_match_logs_warning(self, mock_page):
        """text_click with no matching text should log a warning without raising."""
        locator = AsyncMock()
        locator.count.return_value = 0
        mock_page.get_by_text = MagicMock(return_value=locator)

        actions = (PreScrapeAction(action_type="text_click", selector="不存在,Missing"),)
        with patch("api_finance_dashboard.engine.scraping_engine.logger") as mock_logger:
            await _execute_pre_scrape_actions(mock_page, actions)
            mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_text_click_tries_candidates_in_order(self, mock_page):
        """text_click should try each candidate in order and stop at first match."""
        no_match = AsyncMock()
        no_match.count.return_value = 0

        match = AsyncMock()
        match.count.return_value = 1
        match.first = AsyncMock()

        mock_page.get_by_text = MagicMock(side_effect=[no_match, match])

        actions = (PreScrapeAction(action_type="text_click", selector="今天,今日,Today"),)
        await _execute_pre_scrape_actions(mock_page, actions)

        # First candidate "今天" has no match, second candidate "今日" matches
        assert mock_page.get_by_text.call_count == 2
        mock_page.get_by_text.assert_any_call("今天", exact=True)
        mock_page.get_by_text.assert_any_call("今日", exact=True)
        match.first.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_unknown_action_type_logs_warning(self, mock_page):
        actions = (PreScrapeAction(action_type="unknown", selector=".x"),)
        with patch("api_finance_dashboard.engine.scraping_engine.logger") as mock_logger:
            await _execute_pre_scrape_actions(mock_page, actions)
            mock_logger.warning.assert_called()
