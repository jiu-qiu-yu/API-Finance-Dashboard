"""Tests for panel preset completeness and integrity."""

import pytest

from api_finance_dashboard.engine.presets import PANEL_PRESETS, get_preset


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
