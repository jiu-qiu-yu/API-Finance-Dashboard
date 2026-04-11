## Why

Sub2API 上游面板的今日消耗数据抓取存在两个关键问题：
1. **消耗字段抓到了余额值**：当前 sub2api preset 的 consumption CSS 选择器（如 `.text-green-600`）和关键词匹配错误地命中了「剩余额度」而非「今日消耗」的元素，导致利润计算完全失准。
2. **使用记录页面默认显示 7 天数据**：Sub2API 的使用记录页（如 `https://65535.space/usage`）默认展示 7 天总消费，必须手动点击时间范围选择器并选择「今天」才能获取当日消耗。当前 scraping engine 没有页面交互能力，无法自动切换时间范围。

## What Changes

- **修正 sub2api preset 选择器**：更新 `presets.py` 中 sub2api 的 `consumption_selectors`、`consumption_keywords` 和 `anchor_rules`，避免匹配到余额/剩余额度相关的元素
- **新增页面交互自动化**：在 scraping engine 中引入「预操作步骤」机制，支持在抓取前自动执行页面交互（如点击时间范围选择器、选择「今天」、点击应用）
- **扩展 PanelPreset 数据结构**：为 preset 添加可选的 `pre_scrape_actions` 字段，定义抓取前的自动化操作序列
- **sub2api preset 配置预操作**：为 sub2api 配置在 `/usage` 页面自动选择「今天」时间范围的操作步骤

## Capabilities

### New Capabilities
- `pre-scrape-actions`: 抓取前页面交互自动化机制——支持在数据提取前执行一系列页面操作（点击、选择、等待），解决需要手动交互才能显示目标数据的场景
- `sub2api-preset-fix`: 修正 sub2api 面板预设的消耗数据选择器和关键词，确保 consumption 字段准确抓取消耗值而非余额

### Modified Capabilities
_无需修改现有 spec 级别的需求_

## Impact

- **代码文件**：`engine/presets.py`（preset 数据结构 + sub2api 配置）、`engine/scraping_engine.py`（预操作执行逻辑）
- **数据模型**：`PanelPreset` dataclass 新增 `pre_scrape_actions` 可选字段
- **向后兼容**：新字段默认为空，不影响其他面板类型的现有行为
- **依赖**：无新外部依赖，利用已有的 Playwright Page API 实现交互
