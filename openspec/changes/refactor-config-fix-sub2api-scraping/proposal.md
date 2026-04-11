## Why

Sub2API 面板抓取余额和今日消费均失败（显示 0），原因有二：(1) `_validate_value` 限制最多 2 位小数，但 API 消费金额常为 4+ 位小数（如 `$0.0015`），导致有效值被拒绝；(2) 当前 CSS 选择器与 Sub2API `/dashboard` 实际 DOM 结构存在偏差。此外，设置界面命名为"设置"不够准确（实际核心功能是配置站点），添加/删除站点的交互流程也需优化。

## What Changes

- **修复金额验证逻辑**：将 `_validate_value` 的小数位限制从 2 位放宽至 6 位，兼容 API 消费金额的高精度场景（如 `$0.0015`、`$0.000123`）
- **修正 Sub2API Dashboard CSS 选择器**：基于实际 DOM 结构重写选择器——余额使用 `p.text-emerald-600`（emerald 卡片），今日消费使用 `span.text-purple-600[title]`（purple 卡片内带 title 属性的 span），确保不误匹配"总计"行的值
- **重命名设置界面为"配置"**：窗口标题和相关文案从"设置"改为"配置"，更准确反映功能定位
- **优化添加站点流程**：新增站点时表单自动清空并重置为合理默认值，避免残留上一个站点的数据；面板类型选择后自动提示对应的 URL 模板
- **优化删除站点流程**：删除后自动选中列表中相邻项（而非清空表单），保持操作连贯性

## Capabilities

### New Capabilities

_(无新增能力)_

### Modified Capabilities

- `web-scraping-engine`: 金额验证规则放宽小数位限制；Sub2API preset 选择器和 anchor 配置更新
- `site-config-storage`: 设置界面重命名为"配置"，添加/删除站点交互逻辑优化

## Impact

- `engine/scraping_engine.py`：修改 `_validate_value` 函数的小数位检查
- `engine/presets.py`：更新 Sub2API preset 的 CSS 选择器和 anchor_rules
- `ui/settings_panel.py`：重命名窗口标题、优化添加/删除站点逻辑
- `tests/test_scraping_validation.py`：更新验证函数的测试用例
- `tests/test_presets.py`：更新 Sub2API preset 的测试断言
