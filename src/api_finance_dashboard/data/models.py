"""Data models for site configuration and scraping results."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum


class SiteType(Enum):
    MAIN = "main"
    UPSTREAM = "upstream"


class Currency(Enum):
    USD = "USD"
    CNY = "CNY"


class SiteStatus(Enum):
    NORMAL = "normal"         # 正常
    LOW_BALANCE = "low"       # 额度告急
    NEEDS_CHECK = "check"     # 需核实


@dataclass(frozen=True)
class SiteConfig:
    id: int
    name: str
    type: SiteType
    url: str
    panel_type: str
    css_selector: str | None
    regex_pattern: str | None
    currency: Currency
    alert_threshold: Decimal | None
    dashboard_url: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class SiteResult:
    site: SiteConfig
    consumption: Decimal | None = None
    balance: Decimal | None = None
    status: SiteStatus = SiteStatus.NEEDS_CHECK
    error_message: str | None = None
    extraction_method: str | None = None


@dataclass(frozen=True)
class InspectionResult:
    site_results: tuple[SiteResult, ...]
    net_profit: Decimal | None = None
    profit_currency: Currency = Currency.CNY
    warnings: tuple[str, ...] = field(default_factory=tuple)
    inspected_at: datetime = field(default_factory=datetime.now)
