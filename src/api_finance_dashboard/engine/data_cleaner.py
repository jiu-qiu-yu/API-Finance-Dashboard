"""Monetary value extraction and cleaning utilities."""

import re
from decimal import Decimal, InvalidOperation

from api_finance_dashboard.data.models import Currency

# Patterns for extracting monetary values
_MONEY_PATTERN = re.compile(
    r'[￥¥$]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,6})?)'   # ￥123.45 or $0.0015
    r'|(\d{1,3}(?:,\d{3})*(?:\.\d{1,6})?)\s*(?:USD|CNY|元|美元|人民币)',  # 123.45 USD
    re.IGNORECASE,
)

_BARE_NUMBER_PATTERN = re.compile(
    r'(\d{1,3}(?:,\d{3})*\.\d{1,6})',
)


def detect_currency(raw: str) -> Currency:
    """Detect currency from a raw string."""
    if any(c in raw for c in ("￥", "¥", "CNY", "元", "人民币")):
        return Currency.CNY
    return Currency.USD


def clean_monetary_value(raw: str) -> tuple[Decimal, Currency] | None:
    """Extract and clean a monetary value from a raw string.

    Returns (value, currency) or None if no value found.
    """
    currency = detect_currency(raw)

    # Try structured pattern first
    match = _MONEY_PATTERN.search(raw)
    if match:
        num_str = match.group(1) or match.group(2)
        if num_str:
            num_str = num_str.replace(",", "")
            try:
                return Decimal(num_str), currency
            except InvalidOperation:
                pass

    # Fallback: bare decimal number
    match = _BARE_NUMBER_PATTERN.search(raw)
    if match:
        num_str = match.group(1).replace(",", "")
        try:
            return Decimal(num_str), currency
        except InvalidOperation:
            pass

    return None


def extract_values_near_keywords(
    text: str,
    keywords: tuple[str, ...],
    search_radius: int = 100,
) -> list[tuple[Decimal, Currency]]:
    """Find monetary values in text that appear near given keywords.

    Searches within `search_radius` characters around each keyword occurrence.
    """
    results = []
    text_lower = text.lower()

    for keyword in keywords:
        keyword_lower = keyword.lower()
        start = 0
        while True:
            idx = text_lower.find(keyword_lower, start)
            if idx == -1:
                break
            region_start = max(0, idx - search_radius)
            region_end = min(len(text), idx + len(keyword) + search_radius)
            region = text[region_start:region_end]

            result = clean_monetary_value(region)
            if result and result not in results:
                results.append(result)
            start = idx + 1

    return results
