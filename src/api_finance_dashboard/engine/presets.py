"""Preset scraping rules for common API panels."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnchorRule:
    """Defines how to locate a value using DOM anchor text search (Tier 2)."""
    target: str  # "consumption" or "balance"
    anchor_texts: tuple[str, ...]  # Label texts to search for in DOM
    value_css: str | None = None  # Relative CSS selector from anchor element
    max_dom_depth: int = 3  # Max DOM tree traversal depth


@dataclass(frozen=True)
class PanelPreset:
    name: str
    github_repo: str | None
    # CSS selectors for consumption and balance (ordered list, try in sequence)
    consumption_selectors: tuple[str, ...]
    balance_selectors: tuple[str, ...]
    # Regex keywords to look for near monetary values
    consumption_keywords: tuple[str, ...]
    balance_keywords: tuple[str, ...]
    # Anchor rules for Tier 2 scraping
    anchor_rules: tuple[AnchorRule, ...] = field(default_factory=tuple)


PANEL_PRESETS: dict[str, PanelPreset] = {
    "new-api": PanelPreset(
        name="New API",
        github_repo="QuantumNous/new-api",
        consumption_selectors=(
            ".semi-tag-content",
            ".stat-card .consumption-value",
            ".today-usage .value",
            ".MuiCard-root .consumption-value",
        ),
        balance_selectors=(
            ".stat-card .balance-value",
            ".quota-remaining .value",
            ".MuiCard-root .balance-value",
        ),
        consumption_keywords=("消耗额度", "今日消耗", "消耗", "Today Usage", "consumption", "used"),
        balance_keywords=("当前余额", "剩余额度", "余额", "Balance", "Remaining", "quota"),
        anchor_rules=(
            AnchorRule(
                target="consumption",
                anchor_texts=("消耗额度", "今日消耗", "Today Usage", "Today's Usage"),
            ),
            AnchorRule(
                target="balance",
                anchor_texts=("当前余额", "剩余额度", "Remaining Quota", "Balance"),
            ),
        ),
    ),
    "sub2api": PanelPreset(
        name="Sub2API",
        github_repo="Wei-Shaw/sub2api",
        consumption_selectors=(
            ".text-green-600",
            ".usage-card .value",
            ".stat-item .consumption",
            ".dashboard-stat .amount",
        ),
        balance_selectors=(
            ".text-emerald-600",
            ".balance-card .value",
            ".stat-item .balance",
            ".quota-display .remaining",
        ),
        consumption_keywords=("总消费", "今日消耗", "消耗", "Usage", "Cost", "consumed", "已用"),
        balance_keywords=("余额", "剩余", "Balance", "Remaining", "Points", "点数", "可用"),
        anchor_rules=(
            AnchorRule(
                target="consumption",
                anchor_texts=("总消费", "今日消耗", "Today Cost", "Usage", "已用额度"),
            ),
            AnchorRule(
                target="balance",
                anchor_texts=("余额", "Balance", "Remaining", "剩余点数", "可用"),
            ),
        ),
    ),
    "cap": PanelPreset(
        name="CAP (CLIProxyAPI)",
        github_repo="router-for-me/CLIProxyAPIPlus",
        consumption_selectors=(
            ".usage-stat .value",
            ".dashboard-card .amount",
            ".statistic-card .value",
        ),
        balance_selectors=(
            ".balance-stat .value",
            ".dashboard-card .balance",
            ".statistic-card .balance-value",
        ),
        consumption_keywords=("今日消耗", "消耗", "Usage", "Consumed", "used today"),
        balance_keywords=("余额", "剩余", "Balance", "Remaining", "quota"),
        anchor_rules=(
            AnchorRule(
                target="consumption",
                anchor_texts=("今日消耗", "Today Usage", "Today Consumption"),
            ),
            AnchorRule(
                target="balance",
                anchor_texts=("余额", "Balance", "剩余额度", "Remaining"),
            ),
        ),
    ),
    "custom": PanelPreset(
        name="Custom",
        github_repo=None,
        consumption_selectors=(),
        balance_selectors=(),
        consumption_keywords=("消耗", "Usage", "Consumed", "Cost"),
        balance_keywords=("余额", "Balance", "Remaining", "Quota"),
        anchor_rules=(),
    ),
}


def get_preset(panel_type: str) -> PanelPreset:
    """Get preset by panel type key, falling back to custom."""
    return PANEL_PRESETS.get(panel_type, PANEL_PRESETS["custom"])
