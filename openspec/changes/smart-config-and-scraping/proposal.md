## Why

当前站点配置流程存在多个痛点：用户需要手动输入浏览器 profile 路径（容易出错）、上游站点的使用日志页面和额度看板页面无法分别配置、面板预设仅硬编码了 new-api/one-api 两种缺乏扩展性、且网页抓取缺少结构化的数据定位策略容易被页面其他数值干扰。需要一次性解决配置体验和抓取准确性问题。

## What Changes

- **站点 URL 配置拆分**：自己站点（MAIN）只需配置一个使用日志页面 URL 获取今日消耗；上游站点（UPSTREAM）需配置两个 URL —— 使用日志页面（今日消耗）+ 数据看板页面（剩余额度）
- **浏览器快捷方式自动识别**：用户选择桌面浏览器快捷方式文件（.lnk/.desktop/.app），系统自动解析出浏览器类型和 user-data-dir 路径，无需手动输入
- **面板预设库扩展**：内置当前主流开源 API 管理面板预设（new-api、one-api、one-hub、chat-nio、uni-api 等 GitHub 热门项目），用户从下拉列表选择即可
- **精准抓取策略设计**：为每个面板预设引入"数据锚点"机制 —— 通过标签层级路径 + 关键词邻近度 + 数值格式校验三重定位，避免被页面其他数据干扰
- **抓取规则可视化预览**：设置站点时可执行一次"测试抓取"，预览实际匹配到的数值，用户确认后再保存

## Capabilities

### New Capabilities
- `browser-shortcut-detection`: 通过桌面浏览器快捷方式自动检测浏览器类型（Chrome/Edge/etc）和 user-data-dir 路径，支持 Windows .lnk、macOS .app、Linux .desktop 文件解析
- `panel-preset-library`: 扩展面板预设库，内置主流开源 API 管理面板（new-api、one-api、one-hub、chat-nio、uni-api 等）的抓取规则，包含消耗和余额的 CSS 选择器与关键词
- `anchor-based-scraping`: 基于"数据锚点"的精准抓取策略 —— 使用 DOM 结构路径定位 + 关键词邻近度匹配 + 数值格式校验三重验证，确保提取正确数据

### Modified Capabilities
- `site-config-storage`: 上游站点新增 `dashboard_url` 字段用于存储数据看板页面地址，MAIN 站点仅需 `url`（使用日志页面）
- `local-browser-context`: 浏览器配置方式从手动输入路径改为选择桌面快捷方式自动解析，保留手动输入作为备用
- `web-scraping-engine`: 抓取引擎引入锚点定位策略替代简单的 CSS 选择器 + 正则回退机制，提升抓取准确性

## Impact

- **数据模型变更**：`SiteConfig` 新增 `dashboard_url` 字段，需数据库 migration
- **抓取引擎重构**：`scraping_engine.py` 和 `presets.py` 需较大改动，引入锚点策略
- **设置面板 UI**：`settings_panel.py` 浏览器配置区域重构，站点编辑表单适配双 URL
- **依赖项**：可能需要 `pylnk3` 或类似库解析 Windows .lnk 文件（或使用 PowerShell/COM 对象）
