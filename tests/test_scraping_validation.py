"""Unit tests for scraping value validation and anchor search."""

from decimal import Decimal

import pytest

from api_finance_dashboard.engine.scraping_engine import _validate_value


class TestValidateValue:
    def test_valid_normal(self):
        assert _validate_value(Decimal("12.50")) is True

    def test_valid_zero(self):
        assert _validate_value(Decimal("0")) is True

    def test_valid_max(self):
        assert _validate_value(Decimal("1000000")) is True

    def test_negative(self):
        assert _validate_value(Decimal("-1.00")) is False

    def test_exceeds_max(self):
        assert _validate_value(Decimal("1000001")) is False

    def test_too_many_decimals_seven(self):
        """7+ decimal places should be rejected."""
        assert _validate_value(Decimal("0.0000001")) is False

    def test_four_decimals_api_billing(self):
        """4 decimal places (e.g. API cost $0.0015) should be accepted."""
        assert _validate_value(Decimal("0.0015")) is True

    def test_six_decimals_api_billing(self):
        """6 decimal places (e.g. API cost $0.000123) should be accepted."""
        assert _validate_value(Decimal("0.000123")) is True

    def test_three_decimals(self):
        assert _validate_value(Decimal("12.555")) is True

    def test_five_decimals(self):
        assert _validate_value(Decimal("1.00015")) is True

    def test_two_decimals(self):
        assert _validate_value(Decimal("12.55")) is True

    def test_one_decimal(self):
        assert _validate_value(Decimal("12.5")) is True

    def test_integer(self):
        assert _validate_value(Decimal("100")) is True

    def test_large_valid(self):
        assert _validate_value(Decimal("999999.99")) is True

    def test_zero_point_zero(self):
        assert _validate_value(Decimal("0.00")) is True
