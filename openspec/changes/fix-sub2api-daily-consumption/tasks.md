## 1. PreScrapeAction 数据模型

- [x] 1.1 在 `engine/presets.py` 中定义 `PreScrapeAction` frozen dataclass，包含 `action_type`、`selector`、`value` 字段
- [x] 1.2 在 `PanelPreset` 中新增 `pre_scrape_actions: tuple[PreScrapeAction, ...] = field(default_factory=tuple)` 字段
- [x] 1.3 为 `PreScrapeAction` 编写单元测试，验证各 action_type 的实例化

## 2. Scraping Engine 执行 Pre-Scrape Actions

- [x] 2.1 在 `engine/scraping_engine.py` 中新增 `_execute_pre_scrape_actions(page, actions)` 异步函数，支持 click/select_option/wait 三种操作
- [x] 2.2 在 `scrape_site()` 方法中，页面加载后、数据提取前调用 `_execute_pre_scrape_actions`
- [x] 2.3 在 `test_scrape()` 方法中同步添加 pre-scrape actions 执行逻辑
- [x] 2.4 实现 action 失败的容错处理：捕获异常后记录日志并继续

## 3. 修正 Sub2API Preset

- [x] 3.1 移除 sub2api preset 中的通用颜色类选择器（`.text-green-600` 等），替换为更精确的消耗数据选择器
- [x] 3.2 更新 `consumption_keywords` 为更精确的消耗相关关键词，排除可能匹配余额的模糊词汇
- [x] 3.3 更新 consumption `anchor_rules` 的 `anchor_texts` 为明确的消耗标签文本
- [x] 3.4 为 sub2api preset 配置 `pre_scrape_actions`：点击时间范围选择器 → 选择「今天」→ 等待数据刷新

## 4. 测试验证

- [x] 4.1 为 `_execute_pre_scrape_actions` 编写单元测试，覆盖 click/select_option/wait 及失败场景
- [x] 4.2 更新 `test_presets.py`，验证 sub2api preset 的选择器不包含通用颜色类
- [x] 4.3 验证现有 new-api 和 cap preset 未受影响（回归测试）
