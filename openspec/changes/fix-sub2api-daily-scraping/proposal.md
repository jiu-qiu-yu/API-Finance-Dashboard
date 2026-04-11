## Why

Sub2API 面板类型的上游站点无法正确获取今日消耗额度——当前的 pre-scrape actions 使用了通用 CSS 选择器（`.date-picker-btn` 等），与 Sub2API 实际 DOM 结构（`.date-picker-trigger`、日期快捷选项）不匹配，导致日期切换失败。页面默认展示"近 7 天"而非"今天"，使得抓取到的消耗数据不是当日数据。此外，消耗值和余额值在 Sub2API 面板上来源于不同页面（使用记录 `/usage` vs 仪表盘 `/dashboard`），但当前抓取逻辑未能正确区分两个页面的数据，导致消耗与余额混淆重复。

## What Changes

- **修正 Sub2API pre-scrape actions 选择器**：更新为匹配实际 DOM 的 `.date-picker-trigger` 触发日期选择器，然后点击"今天"快捷选项将时间范围切换为当日
- **修正 Sub2API 消耗/余额 CSS 选择器**：根据实际页面结构更新：
  - 消耗页面（`/usage`）：总消费显示在 `.text-green-600` 容器中，锚点文本为"总消费"
  - 余额页面（`/dashboard`）：余额显示在 `.text-emerald-600` 容器中，锚点文本为"余额"
- **确保消耗和余额分别从不同页面抓取**：消耗从使用记录页面（url）抓取，余额从仪表盘页面（dashboard_url）抓取，两页数据提取完全隔离

## Capabilities

### New Capabilities

_(无新增能力)_

### Modified Capabilities

- `web-scraping-engine`: pre-scrape actions 执行逻辑需支持更精确的选择器匹配，以及处理 Sub2API 特有的日期选择器交互流程
- `site-config-storage`: _(无变更)_

## Impact

- `engine/presets.py`：更新 sub2api preset 的 `pre_scrape_actions`、`consumption_selectors`、`balance_selectors`、`anchor_rules`
- `engine/scraping_engine.py`：可能需要调整 pre-scrape action 执行策略，确保日期切换生效后再提取数据
- `tests/test_presets.py`、`tests/test_pre_scrape_actions.py`：更新对应测试
