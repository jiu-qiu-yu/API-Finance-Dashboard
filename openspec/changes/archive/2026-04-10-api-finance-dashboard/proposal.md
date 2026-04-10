## Why

API 中转站长每天需手动登录数十个上游面板网页查看"今日消耗"与"剩余额度"，耗时极长且极易因上游余额耗尽导致下游断供。缺乏统筹工具让站长无法直观计算每日净利润。需要一款基于 RPA 桌面自动化的本地轻量级监控软件，通过复用本地浏览器已有登录状态，实现"免配 API、免输密码"的数据抓取、利润自动计算与余额低水位告警。

## What Changes

- 新增本地环境接管引擎：通过 Playwright `user-data-dir` 加载用户真实浏览器配置，复用 Cookie 登录状态
- 新增数据抓取与解析引擎：支持 CSS 选择器 + 正则表达式双模式提取金额，带数据清洗
- 新增财务计算与汇率转换：全局汇率设置，多币种统一转换后计算净利润
- 新增系统级告警模块：余额低于阈值时调用 OS 原生通知 API（Windows Toast / macOS Notification）
- 新增 PySide6/Flet 桌面 UI：包含核心数据看板、上游健康列表、站点管理设置三大区域
- 新增本地 SQLite 数据存储：持久化站点配置和抓取规则

## Capabilities

### New Capabilities

- `local-browser-context`: 本地浏览器环境接管，通过 user-data-dir 复用 Cookie 登录状态
- `web-scraping-engine`: 网页数据抓取与解析引擎，CSS 选择器 + 正则表达式双模式提取金额
- `finance-calculation`: 财务计算与汇率转换逻辑，多币种统一转换并计算净利润
- `alert-system`: 系统级告警模块，余额低水位时发送 OS 原生通知
- `dashboard-ui`: 桌面 UI 界面，包含看板、健康列表、站点管理三大模块
- `site-config-storage`: 站点配置与抓取规则的本地 SQLite 持久化存储

### Modified Capabilities

(无 - 全新项目)

## Impact

- **技术栈**: Python 3.10+, Playwright for Python, PySide6/Flet, SQLite
- **系统依赖**: 需要用户本地安装 Chrome/Edge 浏览器
- **平台兼容**: Windows (Toast 通知) + macOS (Notification Center)
- **安全考量**: 不存储用户账号密码，仅复用本地浏览器 Cookie；本地 SQLite 不含敏感凭据
- **性能要求**: 自动化任务在后台线程/异步执行，UI 主线程不可卡死
