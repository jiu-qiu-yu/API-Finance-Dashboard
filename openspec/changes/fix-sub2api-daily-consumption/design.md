## Context

API Finance Dashboard 通过 Playwright 自动抓取各上游面板的消耗和余额数据。当前 sub2api 面板存在两个问题：

1. **选择器误匹配**：`presets.py` 中 sub2api 的 `consumption_selectors`（如 `.text-green-600`）在实际页面上命中的是「剩余额度」而非「今日消耗」，导致 consumption 字段数据错误。
2. **页面交互缺失**：sub2api 的使用记录页（`/usage`）默认展示近 7 天总消费。获取今日消耗需要：点击时间范围选择器 → 选择「今天」 → 点击应用。当前 scraping engine 只做页面加载和静态抓取，没有交互操作能力。

**现有架构**：`ScrapingEngine.scrape_site()` 流程为 `goto(url) → wait → extract`，无中间交互步骤。`PanelPreset` 仅包含选择器和关键词，无操作序列。

## Goals / Non-Goals

**Goals:**
- 修正 sub2api consumption 字段抓取到正确的今日消耗值
- 在 scraping 流程中支持「抓取前页面交互」，自动化时间范围选择
- 保持向后兼容——不影响 new-api、cap 等其他面板的现有行为

**Non-Goals:**
- 不构建通用的页面自动化框架（仅支持当前场景所需的操作类型）
- 不修改 UI 或数据模型层（`SiteResult`、`SiteConfig` 不变）
- 不处理其他面板类型的类似问题（如有需要可后续复用此机制）

## Decisions

### D1: Pre-scrape Actions 数据结构

**选择**：在 `PanelPreset` 中新增 `pre_scrape_actions: tuple[PreScrapeAction, ...]` 字段，每个 action 是一个 frozen dataclass，包含 `action_type`（click / select_option / wait）、`selector`（CSS 选择器）和 `value`（可选参数）。

**替代方案**：
- _使用 JavaScript 脚本字符串_：灵活但难以维护和测试，且存在安全隐患
- _在 SiteConfig 中配置_：过于细粒度，用户不需要关心这些细节，应属于 preset 层

**理由**：声明式 action 结构清晰、可序列化、易于测试，且与现有 preset 的 frozen dataclass 风格一致。

### D2: Action 执行时机

**选择**：在 `scrape_site()` 中，`page.goto()` + `wait_for_timeout()` 之后、`_get_value_tiered()` 之前执行 pre-scrape actions。

**理由**：页面需要先完全加载，交互元素就绪后才能执行操作。操作完成后页面数据刷新，再进行数据提取。

### D3: Sub2API 选择器修正策略

**选择**：基于 sub2api 实际页面结构重写 `consumption_selectors`、`consumption_keywords` 和 `anchor_rules`，确保消耗相关选择器不会命中余额元素。关键改动：
- 移除 `.text-green-600` 等可能同时匹配余额的通用颜色类选择器
- 将消耗关键词更精确化，添加负向排除逻辑（anchor 搜索时跳过包含「余额」「剩余」的上下文）
- 优化 anchor_rules 的 anchor_texts 为更精确的标签

**理由**：根治选择器歧义问题，比调整优先级更可靠。

### D4: 操作失败处理

**选择**：pre-scrape action 执行失败时记录警告日志但继续抓取流程（降级为默认页面状态抓取），不中断整个 scrape。

**替代方案**：_失败则返回 NEEDS_CHECK 状态_——过于严格，7 天数据虽不理想但仍有参考价值。

**理由**：容错优先，避免因交互失败导致完全无数据。

## Risks / Trade-offs

- **Sub2API 页面结构变更** → 选择器失效是 web scraping 的固有风险。缓解：保留多级 fallback（CSS → Anchor → Keyword），action 失败不阻断流程
- **时间范围选择器 DOM 结构不一致** → 不同 sub2api 部署版本可能有差异。缓解：action selector 支持多个候选，按序尝试
- **交互操作增加抓取时间** → 每个 action 额外增加约 1-2 秒。缓解：仅在需要的 preset 中配置，不影响其他面板
