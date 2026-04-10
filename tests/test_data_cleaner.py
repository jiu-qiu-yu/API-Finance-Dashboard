"""Tests for the monetary value data cleaner."""

from decimal import Decimal

import pytest

from api_finance_dashboard.data.models import Currency
from api_finance_dashboard.engine.data_cleaner import (
    clean_monetary_value,
    detect_currency,
    extract_values_near_keywords,
)


class TestDetectCurrency:
    def test_usd_symbol(self):
        assert detect_currency("$12.50") == Currency.USD

    def test_cny_symbol(self):
        assert detect_currency("￥88.00") == Currency.CNY

    def test_cny_yen_symbol(self):
        assert detect_currency("¥88.00") == Currency.CNY

    def test_cny_text(self):
        assert detect_currency("88.00 CNY") == Currency.CNY

    def test_cny_chinese(self):
        assert detect_currency("88.00 元") == Currency.CNY

    def test_default_usd(self):
        assert detect_currency("12.50") == Currency.USD


class TestCleanMonetaryValue:
    def test_dollar_sign(self):
        result = clean_monetary_value("$12.50")
        assert result == (Decimal("12.50"), Currency.USD)

    def test_yuan_sign(self):
        result = clean_monetary_value("￥88.00")
        assert result == (Decimal("88.00"), Currency.CNY)

    def test_trailing_currency(self):
        result = clean_monetary_value("12.50 USD")
        assert result == (Decimal("12.50"), Currency.USD)

    def test_trailing_yuan(self):
        result = clean_monetary_value("88.00 元")
        assert result == (Decimal("88.00"), Currency.CNY)

    def test_comma_separator(self):
        result = clean_monetary_value("$1,234.56")
        assert result == (Decimal("1234.56"), Currency.USD)

    def test_bare_number(self):
        result = clean_monetary_value("12.50")
        assert result == (Decimal("12.50"), Currency.USD)

    def test_no_value(self):
        assert clean_monetary_value("no money here") is None

    def test_surrounded_by_text(self):
        result = clean_monetary_value("Balance: $42.00 remaining")
        assert result == (Decimal("42.00"), Currency.USD)


class TestExtractValuesNearKeywords:
    def test_finds_value_near_keyword(self):
        text = "Today's consumption: $12.50 used so far"
        results = extract_values_near_keywords(text, ("consumption",))
        assert len(results) == 1
        assert results[0] == (Decimal("12.50"), Currency.USD)

    def test_chinese_keywords(self):
        text = "Dashboard showing 今日消耗 ￥88.00 on main site"
        results = extract_values_near_keywords(text, ("今日消耗",))
        assert len(results) == 1
        assert results[0] == (Decimal("88.00"), Currency.CNY)

    def test_no_match(self):
        text = "Nothing relevant here"
        results = extract_values_near_keywords(text, ("balance",))
        assert len(results) == 0

    def test_multiple_keywords(self):
        text = "Balance: $5.00 | Remaining quota: $5.00"
        results = extract_values_near_keywords(text, ("Balance", "Remaining"))
        assert len(results) >= 1
        assert results[0] == (Decimal("5.00"), Currency.USD)
