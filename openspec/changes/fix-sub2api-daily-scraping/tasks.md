## 1. 新增 text_click pre-scrape action 类型

- [x] 1.1 在 `engine/scraping_engine.py` 的 `_execute_pre_scrape_actions` 中新增 `text_click` 分支：解析 `selector` 字段为逗号分隔的候选文本列表，依次尝试 `page.get_by_text(text, exact=True).click()`，首个匹配即停止
- [x] 1.2 编写 `text_click` 的单元测试：覆盖精确匹配、无匹配（日志警告不报错）、多候选文本按序匹配三种场景

## 2. 修正 Sub2API preset 选择器和 pre-scrape actions

- [x] 2.1 更新 `engine/presets.py` 中 sub2api preset 的 `pre_scrape_actions`：第一步点击 `.date-picker-trigger`，第二步使用 `text_click` 匹配 "今天,今日,Today"，第三步等待 2000ms
- [x] 2.2 更新 sub2api preset 的 `consumption_selectors` 为更精确的选择器（如 `.text-green-600.dark\\:text-green-400`），`consumption_keywords` 聚焦 "总消费" 相关词汇
- [x] 2.3 更新 sub2api preset 的 `balance_selectors` 为 `.text-emerald-600.dark\\:text-emerald-400` 等精确选择器
- [x] 2.4 更新 sub2api preset 的 `anchor_rules`：consumption 锚点文本为 ("总消费", "Total Cost")，balance 锚点文本为 ("余额", "Balance", "可用")

## 3. 测试验证

- [x] 3.1 更新 `tests/test_presets.py`：验证 sub2api preset 包含正确的 pre_scrape_actions（含 text_click 类型）
- [x] 3.2 更新 `tests/test_pre_scrape_actions.py`：新增 text_click 相关的测试用例
- [x] 3.3 运行全部测试确认 new-api、cap preset 未受影响（回归测试通过）
