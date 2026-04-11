## 1. 修复金额验证逻辑

- [x] 1.1 修改 `engine/scraping_engine.py` 中 `_validate_value` 函数：将小数位检查从 `exponent < -2` 改为 `exponent < -6`
- [x] 1.2 更新 `tests/test_scraping_validation.py`：新增 4 位小数（$0.0015）和 6 位小数（$0.000123）的通过测试，新增 7 位小数的拒绝测试，修改原有 `test_too_many_decimals` 用例

## 2. 修正 Sub2API preset 选择器

- [x] 2.1 更新 `engine/presets.py` 中 sub2api preset 的 `consumption_selectors` 为 `p.text-xl span.text-purple-600[title]`、`span.text-purple-600[title="实际"]`
- [x] 2.2 更新 sub2api preset 的 `balance_selectors` 为 `p.text-emerald-600.text-xl`、`p.text-xl.font-bold.text-emerald-600`
- [x] 2.3 更新 sub2api preset 的 `anchor_rules`：consumption 锚点为 ("今日消费", "Today Cost")，balance 锚点为 ("余额", "Balance", "可用")
- [x] 2.4 更新 `tests/test_presets.py` 中 Sub2API 相关测试断言

## 3. 设置界面重命名与交互优化

- [x] 3.1 修改 `ui/settings_panel.py` 中 `SettingsPanel` 的窗口标题从 "设置" 改为 "配置"
- [x] 3.2 在 `SiteEditForm` 中新增 `clear_form()` 方法：清空所有字段并设置默认值（面板类型 new-api、货币 USD、阈值 10.00）
- [x] 3.3 修改 `_add_site` 方法：点击添加按钮时先调用 `clear_form()` 清空表单、取消列表选中，让用户在空白表单上填写
- [x] 3.4 修改 `_delete_site` 方法：删除成功后自动选中相邻项（前一个，若删除的是第一个则选新的第一个；若列表空了则清空表单）

## 4. 测试验证

- [x] 4.1 运行全部测试确认所有变更通过（回归测试）
- [x] 4.2 打包生成安装包
