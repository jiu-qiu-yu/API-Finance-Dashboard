## Context

API 中转站长使用 New API / One API 等面板管理 1-2 个主站和数十个上游渠道。当前需手动登录各上游面板查看消耗与余额，缺乏自动化工具。本项目构建一款本地桌面应用，通过 Playwright RPA 技术复用浏览器 Cookie 状态自动抓取数据，计算净利润并告警。

**约束条件：**
- 不存储用户账号密码，仅复用本地浏览器 Cookie
- 需处理 Cloudflare 5s 盾等反爬机制
- UI 主线程不可阻塞
- 跨平台支持 Windows + macOS

## Goals / Non-Goals

**Goals:**
- 一键巡检所有配置站点，自动抓取今日消耗和当前余额
- 自动计算今日净利润（主站消耗 - 上游消耗总和），支持多币种汇率转换
- 余额低于阈值时发送 OS 原生通知告警
- 提供清爽的数据看板 UI，展示上游健康状态
- 站点配置支持增删改查，持久化到本地 SQLite

**Non-Goals:**
- 不做自动充值/续费功能
- 不做历史趋势图表（v1 仅当日数据）
- 不做多用户/云端同步
- 不做定时自动巡检（v1 仅手动触发）
- 不做上游 API 对接（仅 RPA 抓取）

## Decisions

### Decision 1: UI 框架选择 PySide6

**选择**: PySide6 (Qt for Python)
**替代方案**: Flet (Flutter-based)
**理由**: PySide6 生态成熟、跨平台能力强、原生控件性能好、文档丰富。Flet 虽然开发更快但生态较新，对系统托盘通知等原生功能支持不够完善。PySide6 的 QThread 机制天然适合后台自动化任务与 UI 线程分离。

### Decision 2: 自动化引擎选择 Playwright

**选择**: Playwright for Python
**替代方案**: Selenium, Puppeteer (Node.js)
**理由**: Playwright 原生支持 `user-data-dir` 加载本地浏览器配置文件，速度优于 Selenium，且对 Chromium 内核的控制更精细。Python 版本与项目技术栈一致，无需引入 Node.js 运行时。

### Decision 3: 数据抓取策略 - CSS 选择器优先 + 正则降级

**选择**: 双模式提取（CSS Selector 优先，Regex 降级）
**替代方案**: 仅 CSS 选择器 / 仅正则 / AI 识别
**理由**: 不同面板 DOM 结构差异大，CSS 选择器精准但脆弱；正则表达式兼容性强但可能误匹配。双模式结合可覆盖绝大多数场景。AI 识别成本过高且不稳定。

### Decision 4: 数据存储选择 SQLite

**选择**: SQLite
**替代方案**: JSON 文件, TinyDB
**理由**: SQLite 零配置、支持事务、查询能力强，适合存储结构化站点配置。JSON 文件在并发写入时不安全，TinyDB 功能受限。

### Decision 5: 应用架构 - 分层 + 异步

**架构分层**:
```
┌─────────────────────────────────┐
│         UI Layer (PySide6)       │
│  Dashboard | StatusList | Settings│
├─────────────────────────────────┤
│       Service Layer (async)      │
│  InspectionService | AlertService│
├─────────────────────────────────┤
│        Engine Layer              │
│  BrowserEngine | ScrapingEngine  │
│  CalculationEngine               │
├─────────────────────────────────┤
│       Data Layer (SQLite)        │
│  SiteRepository | ConfigRepository│
└─────────────────────────────────┘
```

**异步策略**: 使用 QThread + asyncio event loop 在工作线程中运行 Playwright 异步 API，通过 Qt Signal/Slot 机制将结果回传 UI 线程。

## Risks / Trade-offs

- **[Cookie 过期]** → 用户需定期在浏览器中重新登录上游面板以刷新 Cookie。抓取失败时 UI 显示"需核实"状态提醒用户。
- **[DOM 结构变更]** → 上游面板更新可能导致 CSS 选择器失效。提供自定义选择器配置能力，并内置常见面板（New API、One API）的预设规则。
- **[Cloudflare 拦截]** → 依赖本地浏览器真实指纹通过验证。若仍被拦截，用户需手动在浏览器中访问一次以通过验证。
- **[浏览器 Profile 锁定]** → Chrome 不允许同一 user-data-dir 被两个进程同时使用。需检测浏览器是否正在运行，提示用户关闭或使用独立 Profile。
- **[浮点精度]** → 金额计算使用 Python `Decimal` 类型而非 `float`，确保精度到小数点后两位。
- **[跨平台通知差异]** → Windows 使用 `win10toast` / `plyer`，macOS 使用 `osascript`。封装统一的 Notifier 接口屏蔽差异。
