"""Tests for panel preset completeness and integrity."""

import pytest

from api_finance_dashboard.engine.presets import PANEL_PRESETS, PreScrapeAction, get_preset


class TestPanelPresets:
    def test_required_presets_exist(self):
        required = ["new-api", "sub2api", "cap", "custom"]
        for key in required:
            assert key in PANEL_PRESETS, f"Missing preset: {key}"

    def test_all_presets_have_keywords(self):
        for key, preset in PANEL_PRESETS.items():
            assert len(preset.consumption_keywords) > 0, f"{key}: missing consumption keywords"
            assert len(preset.balance_keywords) > 0, f"{key}: missing balance keywords"

    def test_non_custom_presets_have_selectors(self):
        for key, preset in PANEL_PRESETS.items():
            if key == "custom":
                continue
            assert len(preset.consumption_selectors) > 0, f"{key}: missing consumption selectors"
            assert len(preset.balance_selectors) > 0, f"{key}: missing balance selectors"

    def test_non_custom_presets_have_anchor_rules(self):
        for key, preset in PANEL_PRESETS.items():
            if key == "custom":
                continue
            assert len(preset.anchor_rules) > 0, f"{key}: missing anchor rules"
            targets = {r.target for r in preset.anchor_rules}
            assert "consumption" in targets, f"{key}: missing consumption anchor rule"
            assert "balance" in targets, f"{key}: missing balance anchor rule"

    def test_non_custom_presets_have_github_repo(self):
        for key, preset in PANEL_PRESETS.items():
            if key == "custom":
                assert preset.github_repo is None
                continue
            assert preset.github_repo is not None, f"{key}: missing github_repo"

    def test_custom_preset_is_empty(self):
        custom = PANEL_PRESETS["custom"]
        assert len(custom.consumption_selectors) == 0
        assert len(custom.balance_selectors) == 0
        assert len(custom.anchor_rules) == 0

    def test_get_preset_known(self):
        preset = get_preset("new-api")
        assert preset.name == "New API"

    def test_get_preset_unknown_falls_back(self):
        preset = get_preset("unknown-panel")
        assert preset.name == "Custom"

    def test_anchor_rules_have_texts(self):
        for key, preset in PANEL_PRESETS.items():
            for rule in preset.anchor_rules:
                assert len(rule.anchor_texts) > 0, f"{key}/{rule.target}: empty anchor_texts"
                assert rule.target in ("consumption", "balance"), f"{key}: invalid target '{rule.target}'"
                assert rule.max_dom_depth >= 1, f"{key}/{rule.target}: invalid max_dom_depth"


class TestPreScrapeAction:
    def test_click_action(self):
        action = PreScrapeAction(action_type="click", selector=".date-picker-btn")
        assert action.action_type == "click"
        assert action.selector == ".date-picker-btn"
        assert action.value is None

    def test_select_option_action(self):
        action = PreScrapeAction(
            action_type="select_option",
            selector=".time-range select",
            value="today",
        )
        assert action.action_type == "select_option"
        assert action.selector == ".time-range select"
        assert action.value == "today"

    def test_wait_action(self):
        action = PreScrapeAction(action_type="wait", selector="body", value="2000")
        assert action.action_type == "wait"
        assert action.value == "2000"

    def test_frozen_immutability(self):
        action = PreScrapeAction(action_type="click", selector=".btn")
        with pytest.raises(AttributeError):
            action.action_type = "wait"  # type: ignore[misc]

    def test_default_value_is_none(self):
        action = PreScrapeAction(action_type="click", selector=".btn")
        assert action.value is None


class TestSub2apiPresetFix:
    """Verify sub2api preset uses correct selectors for dashboard DOM."""

    def test_consumption_selectors_match_purple_card(self):
        """Consumption selectors must target purple card with title attribute."""
        preset = PANEL_PRESETS["sub2api"]
        assert "p.text-xl span.text-purple-600[title]" in preset.consumption_selectors
        assert 'span.text-purple-600[title="实际"]' in preset.consumption_selectors

    def test_balance_selectors_match_emerald_card(self):
        """Balance selectors must target emerald card."""
        preset = PANEL_PRESETS["sub2api"]
        assert "p.text-emerald-600.text-xl" in preset.balance_selectors
        assert "p.text-xl.font-bold.text-emerald-600" in preset.balance_selectors

    def test_consumption_anchor_rules(self):
        """Consumption anchor rules must use 今日消费/Today Cost."""
        preset = PANEL_PRESETS["sub2api"]
        consumption_rules = [r for r in preset.anchor_rules if r.target == "consumption"]
        assert len(consumption_rules) == 1
        assert "今日消费" in consumption_rules[0].anchor_texts
        assert "Today Cost" in consumption_rules[0].anchor_texts

    def test_balance_anchor_rules(self):
        """Balance anchor rules must use 余额/Balance/可用."""
        preset = PANEL_PRESETS["sub2api"]
        balance_rules = [r for r in preset.anchor_rules if r.target == "balance"]
        assert len(balance_rules) == 1
        assert "余额" in balance_rules[0].anchor_texts
        assert "Balance" in balance_rules[0].anchor_texts
        assert "可用" in balance_rules[0].anchor_texts

    _FORBIDDEN_COLOR_CLASSES = (
        ".text-green-600",
        ".text-green-500",
        ".text-emerald-600",
        ".text-emerald-500",
        ".text-blue-600",
        ".text-red-600",
    )

    def test_no_standalone_color_class_in_consumption_selectors(self):
        """Consumption selectors must not be standalone ambiguous color classes.

        Compound selectors like `.text-green-600.dark\\:text-green-400` are
        acceptable because they are more specific than a bare color class.
        """
        preset = PANEL_PRESETS["sub2api"]
        for selector in preset.consumption_selectors:
            for forbidden in self._FORBIDDEN_COLOR_CLASSES:
                assert selector.strip() != forbidden, (
                    f"sub2api consumption_selectors contains standalone ambiguous color class: {selector}"
                )

    def test_consumption_keywords_exclude_balance_terms(self):
        preset = PANEL_PRESETS["sub2api"]
        balance_terms = {"余额", "剩余", "Balance", "Remaining", "可用"}
        for kw in preset.consumption_keywords:
            assert kw not in balance_terms, (
                f"sub2api consumption_keywords contains balance term: {kw}"
            )

    def test_consumption_anchor_texts_are_specific(self):
        preset = PANEL_PRESETS["sub2api"]
        consumption_rules = [r for r in preset.anchor_rules if r.target == "consumption"]
        assert len(consumption_rules) > 0
        for rule in consumption_rules:
            for text in rule.anchor_texts:
                assert text not in ("余额", "Balance", "Remaining", "剩余"), (
                    f"sub2api consumption anchor contains balance text: {text}"
                )

    def test_no_pre_scrape_actions_needed(self):
        """Sub2API dashboard page has today's data directly — no interactions needed."""
        preset = PANEL_PRESETS["sub2api"]
        assert len(preset.pre_scrape_actions) == 0, (
            "sub2api should have no pre_scrape_actions (dashboard shows today's data directly)"
        )


class TestPresetRegression:
    """Verify existing presets are not broken by changes."""

    def test_new_api_preset_unchanged(self):
        preset = PANEL_PRESETS["new-api"]
        assert preset.name == "New API"
        assert len(preset.consumption_selectors) > 0
        assert len(preset.balance_selectors) > 0
        assert len(preset.anchor_rules) > 0
        # new-api should not have pre_scrape_actions (no change needed)
        assert len(preset.pre_scrape_actions) == 0

    def test_cap_preset_unchanged(self):
        preset = PANEL_PRESETS["cap"]
        assert preset.name == "CAP (CLIProxyAPI)"
        assert len(preset.consumption_selectors) > 0
        assert len(preset.balance_selectors) > 0
        assert len(preset.anchor_rules) > 0
        assert len(preset.pre_scrape_actions) == 0

    def test_custom_preset_unchanged(self):
        preset = PANEL_PRESETS["custom"]
        assert len(preset.consumption_selectors) == 0
        assert len(preset.balance_selectors) == 0
        assert len(preset.anchor_rules) == 0
        assert len(preset.pre_scrape_actions) == 0
