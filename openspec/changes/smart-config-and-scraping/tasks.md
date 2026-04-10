## 1. 数据模型与数据库迁移

- [x] 1.1 在 `SiteConfig` dataclass 中新增 `dashboard_url: str | None` 字段
- [x] 1.2 更新 `database.py` 添加 schema migration 逻辑：检测并添加 `dashboard_url` 列
- [x] 1.3 更新 `site_repository.py` 的 CRUD 方法支持 `dashboard_url` 字段的读写
- [x] 1.4 在 `ConfigRepository` 中新增 `get_browser_type()` / `set_browser_type()` 方法

## 2. 浏览器快捷方式自动检测

- [x] 2.1 创建 `engine/browser_detector.py` 模块，实现 Windows `.lnk` 文件解析（PowerShell COM）
- [x] 2.2 实现 macOS `.app` bundle 解析（读取 `Info.plist`）
- [x] 2.3 实现浏览器类型识别（Chrome/Edge/Chromium）和默认 profile 路径推断
- [x] 2.4 更新 `settings_panel.py` 浏览器配置区域：添加「选择浏览器」按钮和文件对话框，保留手动输入作为回退
- [x] 2.5 检测结果确认对话框：显示浏览器类型和 profile 路径，用户确认后保存

## 3. 面板预设库扩展

- [x] 3.1 定义 `AnchorRule` 数据类（target, anchor_texts, value_css, max_dom_depth）
- [x] 3.2 更新 `PanelPreset` 数据类，新增 `anchor_rules` 字段和多选择器支持
- [x] 3.3 添加 One Hub 面板预设（CSS 选择器 + 关键词 + 锚点规则）
- [x] 3.4 添加 Chat Nio (CoAI) 面板预设
- [x] 3.5 添加 Uni API 面板预设
- [x] 3.6 更新面板类型下拉框显示格式为 "面板名 (github-org/repo)"

## 4. 锚点抓取策略

- [x] 4.1 在 `scraping_engine.py` 中实现 Tier 2 锚点文本搜索：在页面中定位锚点文本元素，搜索 DOM 邻近节点获取数值
- [x] 4.2 实现 DOM 邻近搜索算法：同级兄弟 → 父级兄弟 → 向上最多3层
- [x] 4.3 增强 Tier 3 关键词邻近提取：添加数值格式校验（非负、≤2位小数、0~1,000,000 范围）
- [x] 4.4 重构 `scrape_site()` 方法为三层回退策略：CSS 选择器 → 锚点搜索 → 关键词邻近
- [x] 4.5 在抓取结果中记录命中的提取方式（css_selector / anchor_text / keyword_proximity）

## 5. 双 URL 抓取支持

- [x] 5.1 更新 `scrape_site()` 方法：UPSTREAM 站点支持分别访问 `url` 和 `dashboard_url` 提取消耗和余额
- [x] 5.2 处理 `dashboard_url` 为空的回退情况：从单页面同时提取消耗和余额
- [x] 5.3 更新 `settings_panel.py` 站点编辑表单：UPSTREAM 类型显示两个 URL 输入框（使用日志 + 数据看板）

## 6. 测试抓取预览

- [x] 6.1 在站点编辑表单中添加「测试抓取」按钮（仅在浏览器已配置时可用）
- [x] 6.2 实现测试抓取逻辑：调用抓取引擎，收集提取结果和方法元数据
- [x] 6.3 创建测试抓取结果对话框：显示提取到的数值、匹配层级、原始文本片段
- [x] 6.4 处理测试抓取失败场景：显示失败详情和排查建议

## 7. 测试

- [x] 7.1 编写 `browser_detector.py` 单元测试（模拟 .lnk 和 .app 解析）
- [x] 7.2 编写锚点搜索算法单元测试（模拟 DOM 结构）
- [x] 7.3 编写数值格式校验单元测试
- [x] 7.4 更新 `test_site_repository.py` 覆盖 `dashboard_url` 字段的 CRUD
- [x] 7.5 编写面板预设完整性测试（确保每个预设有必要的选择器和锚点规则）
