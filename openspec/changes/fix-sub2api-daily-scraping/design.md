## Context

Sub2API 面板与 New API 面板的页面结构差异显著：

- **New API**：数据看板页面直接展示今日消耗和余额，无需额外交互
- **Sub2API**：
  - 使用记录页面（`/usage`）默认展示"近 7 天"数据，需要手动点击日期选择器并切换为"今天"才能获取当日消耗
  - 仪表盘页面（`/dashboard`）展示余额信息
  - 日期选择器的触发按钮实际 CSS 类为 `.date-picker-trigger`，内含 `.date-picker-value` 显示当前选中范围
  - 消耗数据的标签文本为"总消费"，金额使用 `.text-green-600` 类
  - 余额数据的标签文本为"余额"，金额使用 `.text-emerald-600` 类

当前问题：
1. pre-scrape actions 中的日期选择器选择器（`.date-picker-btn` 等）无法匹配实际 DOM
2. 消耗页面未成功切换到"今天"导致数据不准确
3. 余额的 `.text-emerald-600` 选择器被放在了 `balance_selectors` 中是正确的，但消耗选择器不够精确

## Goals / Non-Goals

**Goals:**

- 修正 Sub2API preset 的 pre-scrape actions，使日期选择器能正确切换到"今天"
- 修正消耗和余额的 CSS 选择器和 anchor 文本，准确匹配 Sub2API 实际 DOM
- 确保消耗从 `/usage` 页面抓取、余额从 `/dashboard` 页面抓取，数据完全隔离

**Non-Goals:**

- 不修改 New API、CAP 或 Custom preset 的逻辑
- 不修改 settings_panel.py 的 UI 布局
- 不新增面板类型

## Decisions

### 1. Sub2API 日期选择器交互策略

**选择：精确匹配 Sub2API 的 Vue 组件选择器**

更新 pre-scrape actions 为：
1. 点击 `.date-picker-trigger`（日期选择器触发按钮）
2. 等待下拉面板展开（500ms）
3. 点击包含"今天"或"今日"文本的快捷选项按钮
4. 等待数据刷新（2000ms）

**备选方案：使用 JavaScript 直接操作 Vue 组件状态** → 过于侵入，依赖框架内部实现，维护成本高。

### 2. 消耗/余额选择器修正

根据用户提供的实际 DOM 结构：

- 消耗（`/usage` 页面）：锚点 "总消费"，值在相邻 `.text-green-600` 元素中
- 余额（`/dashboard` 页面）：锚点 "余额"，值在相邻 `.text-emerald-600` 元素中

**方案：优先依赖 anchor_rules（Tier 2），CSS selectors 作为辅助**

anchor 方式更稳健，因为它基于语义标签文本定位而非 CSS 类名（类名可能随主题变化）。

### 3. Pre-scrape action 中的"今天"按钮点击

Sub2API 的日期选择器下拉中包含快捷选项。需要使用文本匹配方式定位"今天"按钮，因为该按钮没有特定的 CSS 类标识。

**方案：新增 `text_click` action type**

在 `PreScrapeAction` 中新增 `action_type="text_click"` 支持，使用 Playwright 的 `page.get_by_text()` 精确匹配文本内容后点击。这比依赖不稳定的 CSS 选择器更可靠。

## Risks / Trade-offs

- **[风险] 日期选择器 DOM 结构可能在 Sub2API 版本更新后变化** → 缓解：使用 anchor text 匹配而非硬编码 CSS 路径，更具弹性
- **[风险] "今天"按钮文本可能有变体（"今天"/"今日"/"Today"）** → 缓解：在 pre-scrape action 中支持多候选文本匹配，使用 `selector` 字段存储逗号分隔的候选文本
- **[权衡] 新增 `text_click` action type 增加了 pre-scrape action 的复杂度** → 收益大于成本：文本匹配在没有稳定 CSS 选择器的场景下是更可靠的交互方式
