"""Tests for the finance calculation engine."""

from datetime import datetime
from decimal import Decimal

import pytest

from api_finance_dashboard.data.models import (
    Currency, SiteConfig, SiteResult, SiteStatus, SiteType,
)
from api_finance_dashboard.engine.calculation_engine import (
    TWO_PLACES,
    calculate_net_profit,
    convert_currency,
)


def _make_site(
    name: str = "test",
    site_type: SiteType = SiteType.UPSTREAM,
    currency: Currency = Currency.USD,
) -> SiteConfig:
    return SiteConfig(
        id=1, name=name, type=site_type, url="https://example.com",
        panel_type="custom", css_selector=None, regex_pattern=None,
        currency=currency, alert_threshold=Decimal("5"),
        dashboard_url=None,
        created_at=datetime.now(), updated_at=datetime.now(),
    )


class TestConvertCurrency:
    def test_same_currency(self):
        assert convert_currency(Decimal("10"), Currency.USD, Currency.USD, Decimal("7.2")) == Decimal("10")

    def test_usd_to_cny(self):
        result = convert_currency(Decimal("10"), Currency.USD, Currency.CNY, Decimal("7.2"))
        assert result == Decimal("72.00")

    def test_cny_to_usd(self):
        result = convert_currency(Decimal("72"), Currency.CNY, Currency.USD, Decimal("7.2"))
        assert result == Decimal("10.00")

    def test_precision(self):
        result = convert_currency(Decimal("1"), Currency.USD, Currency.CNY, Decimal("7.23"))
        assert result == Decimal("7.23")


class TestCalculateNetProfit:
    def test_basic_profit(self):
        main = SiteResult(
            site=_make_site("main", SiteType.MAIN, Currency.CNY),
            consumption=Decimal("100.00"),
            status=SiteStatus.NORMAL,
        )
        upstream = SiteResult(
            site=_make_site("up1", SiteType.UPSTREAM, Currency.USD),
            consumption=Decimal("5.00"),
            status=SiteStatus.NORMAL,
        )
        result = calculate_net_profit(
            [main, upstream], Decimal("7.2"), Currency.CNY
        )
        # 100 - 5*7.2 = 100 - 36 = 64
        assert result.net_profit == Decimal("64.00")

    def test_multi_currency(self):
        """From spec: main=￥100, up_a=$5, up_b=$3, rate=7.2 → profit=￥42.40"""
        main = SiteResult(
            site=_make_site("main", SiteType.MAIN, Currency.CNY),
            consumption=Decimal("100.00"),
            status=SiteStatus.NORMAL,
        )
        up_a = SiteResult(
            site=_make_site("A", SiteType.UPSTREAM, Currency.USD),
            consumption=Decimal("5.00"),
            status=SiteStatus.NORMAL,
        )
        up_b = SiteResult(
            site=_make_site("B", SiteType.UPSTREAM, Currency.USD),
            consumption=Decimal("3.00"),
            status=SiteStatus.NORMAL,
        )
        result = calculate_net_profit(
            [main, up_a, up_b], Decimal("7.2"), Currency.CNY
        )
        assert result.net_profit == Decimal("42.40")

    def test_partial_data(self):
        main = SiteResult(
            site=_make_site("main", SiteType.MAIN, Currency.CNY),
            consumption=Decimal("100.00"),
            status=SiteStatus.NORMAL,
        )
        ok = SiteResult(
            site=_make_site("ok", SiteType.UPSTREAM, Currency.USD),
            consumption=Decimal("5.00"),
            status=SiteStatus.NORMAL,
        )
        failed = SiteResult(
            site=_make_site("fail", SiteType.UPSTREAM, Currency.USD),
            consumption=None,
            status=SiteStatus.NEEDS_CHECK,
            error_message="timeout",
        )
        result = calculate_net_profit(
            [main, ok, failed], Decimal("7.2"), Currency.CNY
        )
        assert result.net_profit == Decimal("64.00")
        assert len(result.warnings) == 1
        assert "fail" in result.warnings[0]

    def test_no_main_site(self):
        up = SiteResult(
            site=_make_site("up", SiteType.UPSTREAM, Currency.USD),
            consumption=Decimal("5.00"),
            status=SiteStatus.NORMAL,
        )
        result = calculate_net_profit([up], Decimal("7.2"), Currency.CNY)
        assert result.net_profit is None
        assert any("main" in w.lower() for w in result.warnings)

    def test_decimal_precision_no_float_drift(self):
        """Verify 0.1 + 0.2 = 0.30 exactly."""
        main = SiteResult(
            site=_make_site("main", SiteType.MAIN, Currency.CNY),
            consumption=Decimal("0.30"),
            status=SiteStatus.NORMAL,
        )
        up = SiteResult(
            site=_make_site("up", SiteType.UPSTREAM, Currency.CNY),
            consumption=Decimal("0"),
            status=SiteStatus.NORMAL,
        )
        result = calculate_net_profit(
            [main, up], Decimal("7.2"), Currency.CNY
        )
        assert result.net_profit == Decimal("0.30")
