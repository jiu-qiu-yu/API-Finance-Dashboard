"""Scraping engine that extracts monetary values from web pages."""

from decimal import Decimal

from playwright.async_api import Page

from api_finance_dashboard.data.models import Currency, SiteConfig, SiteResult, SiteStatus, SiteType
from api_finance_dashboard.engine.browser_engine import BrowserEngine
from api_finance_dashboard.engine.data_cleaner import clean_monetary_value, extract_values_near_keywords
from api_finance_dashboard.engine.presets import AnchorRule, get_preset

# Maximum valid monetary value for format validation
_MAX_VALID_VALUE = Decimal("1000000")


async def _extract_by_css_selectors(
    page: Page, selectors: tuple[str, ...]
) -> tuple[Decimal, Currency] | None:
    """Tier 1: Try each CSS selector in order, return first valid value."""
    for selector in selectors:
        try:
            element = await page.query_selector(selector.strip())
            if element:
                raw = await element.text_content()
                if raw:
                    result = clean_monetary_value(raw)
                    if result and _validate_value(result[0]):
                        return result
        except Exception:
            continue
    return None


async def _extract_by_anchor(
    page: Page, anchor_rules: tuple[AnchorRule, ...], target: str
) -> tuple[Decimal, Currency] | None:
    """Tier 2: Locate anchor text in DOM and search adjacent nodes for values."""
    rules = [r for r in anchor_rules if r.target == target]
    for rule in rules:
        for anchor_text in rule.anchor_texts:
            result = await _search_anchor_value(page, anchor_text, rule)
            if result and _validate_value(result[0]):
                return result
    return None


async def _search_anchor_value(
    page: Page, anchor_text: str, rule: AnchorRule
) -> tuple[Decimal, Currency] | None:
    """Find an anchor text element and search adjacent nodes for a monetary value."""
    try:
        # Find elements containing the anchor text
        js_find_anchor = """
        (anchorText, maxDepth) => {
            function findElementsWithText(root, text) {
                const results = [];
                const walker = document.createTreeWalker(
                    root, NodeFilter.SHOW_TEXT, null
                );
                while (walker.nextNode()) {
                    if (walker.currentNode.textContent.includes(text)) {
                        results.push(walker.currentNode.parentElement);
                    }
                }
                return results;
            }

            function getAdjacentTexts(el, depth) {
                const texts = [];
                if (depth <= 0 || !el) return texts;

                // Check siblings
                let sibling = el.nextElementSibling;
                for (let i = 0; i < 3 && sibling; i++) {
                    texts.push(sibling.textContent);
                    sibling = sibling.nextElementSibling;
                }
                sibling = el.previousElementSibling;
                for (let i = 0; i < 3 && sibling; i++) {
                    texts.push(sibling.textContent);
                    sibling = sibling.previousElementSibling;
                }

                // Check children
                for (const child of el.children) {
                    texts.push(child.textContent);
                }

                // Go up and check parent's siblings
                if (depth > 1 && el.parentElement) {
                    texts.push(...getAdjacentTexts(el.parentElement, depth - 1));
                }

                return texts;
            }

            const anchors = findElementsWithText(document.body, anchorText);
            const allTexts = [];
            for (const anchor of anchors) {
                allTexts.push(...getAdjacentTexts(anchor, maxDepth));
            }
            return allTexts.filter(t => t && t.trim().length > 0);
        }
        """
        adjacent_texts = await page.evaluate(
            js_find_anchor, [anchor_text, rule.max_dom_depth]
        )

        for text in adjacent_texts:
            result = clean_monetary_value(text.strip())
            if result and _validate_value(result[0]):
                return result

    except Exception:
        pass
    return None


async def _extract_by_keywords(
    page: Page, keywords: tuple[str, ...]
) -> tuple[Decimal, Currency] | None:
    """Tier 3: Scan page text for monetary values near keywords with validation."""
    try:
        text = await page.inner_text("body")
    except Exception:
        return None
    results = extract_values_near_keywords(text, keywords)
    for value, currency in results:
        if _validate_value(value):
            return value, currency
    return None


def _validate_value(value: Decimal) -> bool:
    """Validate monetary value: non-negative, ≤2 decimal places, within range."""
    if value < 0:
        return False
    if value > _MAX_VALID_VALUE:
        return False
    # Check decimal places
    sign, digits, exponent = value.as_tuple()
    if exponent < -2:
        return False
    return True


async def _get_value_tiered(
    page: Page,
    css_selectors: tuple[str, ...],
    anchor_rules: tuple[AnchorRule, ...],
    target: str,
    keywords: tuple[str, ...],
) -> tuple[tuple[Decimal, Currency] | None, str]:
    """Three-tier extraction: CSS → Anchor → Keyword. Returns (result, method)."""
    # Tier 1: CSS selectors
    if css_selectors:
        result = await _extract_by_css_selectors(page, css_selectors)
        if result:
            return result, "css_selector"

    # Tier 2: Anchor text search
    if anchor_rules:
        result = await _extract_by_anchor(page, anchor_rules, target)
        if result:
            return result, "anchor_text"

    # Tier 3: Keyword proximity
    result = await _extract_by_keywords(page, keywords)
    if result:
        return result, "keyword_proximity"

    return None, "none"


class ScrapingEngine:
    """Orchestrates data extraction from a single site."""

    def __init__(self, browser_engine: BrowserEngine) -> None:
        self._browser = browser_engine

    async def scrape_site(self, site: SiteConfig) -> SiteResult:
        """Navigate to site and extract consumption/balance data."""
        page = None
        try:
            page = await self._browser.new_page()
            await page.goto(site.url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)

            content = await page.content()
            if BrowserEngine.detect_startup_warning_page(content):
                raise RuntimeError(
                    "浏览器启动失败：检测到不受支持的启动参数警告页。"
                )

            # Check for Cloudflare challenge
            if BrowserEngine.detect_cloudflare_challenge(content, page.url):
                return SiteResult(
                    site=site,
                    status=SiteStatus.NEEDS_CHECK,
                    error_message=(
                        "检测到 Cloudflare 验证页面，请点击「登录此站点」"
                        "手动通过验证后重试"
                    ),
                )

            # Check for expired session
            if BrowserEngine.detect_session_expired(content, page.url):
                return SiteResult(
                    site=site,
                    status=SiteStatus.NEEDS_CHECK,
                    error_message="Session expired - please re-login in your browser",
                )

            preset = get_preset(site.panel_type)

            # Build effective selectors
            custom_selectors = tuple(
                s.strip() for s in (site.css_selector or "").split(",") if s.strip()
            )
            consumption_css = custom_selectors or preset.consumption_selectors
            balance_css = custom_selectors or preset.balance_selectors

            methods = []

            # Extract consumption from usage log page
            consumption_result, c_method = await _get_value_tiered(
                page, consumption_css, preset.anchor_rules,
                "consumption", preset.consumption_keywords,
            )
            methods.append(f"consumption:{c_method}")

            balance_result = None
            # Extract balance for upstream sites
            if site.type == SiteType.UPSTREAM:
                if site.dashboard_url:
                    # Visit separate dashboard page for balance
                    await page.goto(
                        site.dashboard_url,
                        wait_until="networkidle",
                        timeout=30000,
                    )
                    await page.wait_for_timeout(3000)

                balance_result, b_method = await _get_value_tiered(
                    page, balance_css, preset.anchor_rules,
                    "balance", preset.balance_keywords,
                )
                methods.append(f"balance:{b_method}")

            # Determine status
            consumption_val = consumption_result[0] if consumption_result else None
            balance_val = balance_result[0] if balance_result else None
            status = SiteStatus.NORMAL

            if site.type == SiteType.UPSTREAM and balance_val is not None:
                if site.alert_threshold and balance_val <= site.alert_threshold:
                    status = SiteStatus.LOW_BALANCE

            if consumption_val is None and balance_val is None:
                status = SiteStatus.NEEDS_CHECK

            return SiteResult(
                site=site,
                consumption=consumption_val,
                balance=balance_val,
                status=status,
                extraction_method=", ".join(methods),
            )

        except Exception as e:
            return SiteResult(
                site=site,
                status=SiteStatus.NEEDS_CHECK,
                error_message=str(e),
            )
        finally:
            if page:
                await self._browser.close_page(page)

    async def test_scrape(
        self, url: str, panel_type: str, css_selector: str | None = None,
        dashboard_url: str | None = None,
    ) -> dict:
        """Run a test scrape and return detailed results for preview."""
        page = None
        try:
            page = await self._browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)

            content = await page.content()
            if BrowserEngine.detect_cloudflare_challenge(content, page.url):
                return {
                    "success": False,
                    "error": (
                        "检测到 Cloudflare 验证页面。\n"
                        "请先点击「登录此站点」手动通过 CF 验证，"
                        "然后再测试抓取。"
                    ),
                }

            preset = get_preset(panel_type)
            custom_selectors = tuple(
                s.strip() for s in (css_selector or "").split(",") if s.strip()
            )
            selectors = custom_selectors or preset.consumption_selectors

            consumption_result, c_method = await _get_value_tiered(
                page, selectors, preset.anchor_rules,
                "consumption", preset.consumption_keywords,
            )

            # Visit dashboard URL for balance if provided
            if dashboard_url:
                await page.goto(dashboard_url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(3000)

                dash_content = await page.content()
                if BrowserEngine.detect_cloudflare_challenge(dash_content, page.url):
                    return {
                        "success": consumption_result is not None,
                        "consumption": str(consumption_result[0]) if consumption_result else None,
                        "consumption_currency": consumption_result[1].value if consumption_result else None,
                        "consumption_method": c_method,
                        "balance": None,
                        "balance_currency": None,
                        "balance_method": "none",
                        "error": "数据看板被 Cloudflare 拦截，请先登录该站点通过 CF 验证",
                    }

            balance_selectors = custom_selectors or preset.balance_selectors
            balance_result, b_method = await _get_value_tiered(
                page, balance_selectors, preset.anchor_rules,
                "balance", preset.balance_keywords,
            )

            # Get a text snippet around matched area for context
            try:
                page_text = await page.inner_text("body")
                snippet = page_text[:500] if page_text else ""
            except Exception:
                snippet = ""

            return {
                "success": consumption_result is not None or balance_result is not None,
                "consumption": str(consumption_result[0]) if consumption_result else None,
                "consumption_currency": consumption_result[1].value if consumption_result else None,
                "consumption_method": c_method,
                "balance": str(balance_result[0]) if balance_result else None,
                "balance_currency": balance_result[1].value if balance_result else None,
                "balance_method": b_method,
                "page_snippet": snippet,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if page:
                await self._browser.close_page(page)
