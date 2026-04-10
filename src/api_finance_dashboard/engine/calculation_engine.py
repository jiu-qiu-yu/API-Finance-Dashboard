"""Finance calculation engine with exchange rate conversion."""

from decimal import Decimal, ROUND_HALF_UP

from api_finance_dashboard.data.models import (
    Currency, InspectionResult, SiteResult, SiteStatus, SiteType,
)

TWO_PLACES = Decimal("0.01")


def convert_currency(
    amount: Decimal,
    from_currency: Currency,
    to_currency: Currency,
    exchange_rate: Decimal,
) -> Decimal:
    """Convert amount between currencies.

    exchange_rate is USD-to-CNY (e.g., 7.2 means $1 = ¥7.2).
    """
    if from_currency == to_currency:
        return amount
    if from_currency == Currency.USD and to_currency == Currency.CNY:
        return (amount * exchange_rate).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    if from_currency == Currency.CNY and to_currency == Currency.USD:
        return (amount / exchange_rate).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    return amount


def calculate_net_profit(
    site_results: list[SiteResult],
    exchange_rate: Decimal,
    target_currency: Currency = Currency.CNY,
) -> InspectionResult:
    """Calculate net profit: main site consumption - sum(upstream consumption).

    Returns an InspectionResult with calculated profit and warnings.
    """
    warnings = []
    main_total = Decimal("0")
    upstream_total = Decimal("0")
    has_main = False

    for result in site_results:
        site = result.site
        consumption = result.consumption

        if consumption is None:
            warnings.append(
                f"{site.name}: data unavailable, excluded from calculation"
            )
            continue

        converted = convert_currency(
            consumption, site.currency, target_currency, exchange_rate
        )

        if site.type == SiteType.MAIN:
            main_total += converted
            has_main = True
        else:
            upstream_total += converted

    net_profit = None
    if has_main:
        net_profit = (main_total - upstream_total).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )
    else:
        warnings.append("No main site data available - cannot calculate net profit")

    return InspectionResult(
        site_results=tuple(site_results),
        net_profit=net_profit,
        profit_currency=target_currency,
        warnings=tuple(warnings),
    )
