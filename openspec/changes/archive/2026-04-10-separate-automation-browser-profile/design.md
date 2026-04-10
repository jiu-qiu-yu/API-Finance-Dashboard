## Context

当前 `BrowserEngine` 使用 `launch_persistent_context(user_data_dir=<用户主浏览器 User Data>)` 来复用登录态。Chrome 近期政策变更后，直接自动化主 User Data 目录已不被稳定支持（Playwright 官方文档明确警告）。实测表现为 warning page、about:blank 卡死、或浏览器崩溃。且因共用目录，用户每次巡检前必须关闭日常浏览器。

项目是一个桌面 RPA 工具（PySide6 + Playwright），目标是长期稳定复用登录态抓取真实业务后台页面。用户群体为 API 站长，非技术开发者。每个站点使用不同的账号登录。

当前配置链路：
1. `browser_detector.py` 扫描已安装浏览器 → 得到 `profile_path` (User Data 目录) + `executable_path`
2. `config_repository.py` 持久化 `browser_profile_path`、`browser_profile_dir`、`browser_executable`
3. `BrowserEngine(profile_path, profile_dir, executable_path)` → `launch_persistent_context`
4. `settings_panel.py` 提供 UI 配置入口

## Goals / Non-Goals

**Goals:**
- 将 `user_data_dir` 从用户主 profile 目录切换为项目专用目录，彻底消除与日常浏览器的目录冲突
- 用户日常浏览器可以保持打开，巡检/抓取不再要求关闭浏览器
- 提供按站点的"登录此站点"流程——每个站点独立登录、独立验证
- 登录完成后自动执行测试抓取作为验证，不做额外状态追踪
- 保持 `launch_persistent_context` 架构不变（对下游 ScrapingEngine 透明）
- 兼容 Chrome 和 Edge

**Non-Goals:**
- 不实现 `storageState` 登录快照方案
- 不实现自动登录/凭证管理
- 不做 cookie 导入/导出
- 不做 per-site 登录状态持久化追踪（用测试抓取结果验证即可）
- 不支持多个 automation profile 目录

## Decisions

### Decision 1: 专用 profile 目录位置

**选择**: 放在项目数据目录下 `<app_data>/automation_profile/`

- Windows: `%LOCALAPPDATA%/api-finance-dashboard/automation_profile/`
- macOS: `~/Library/Application Support/api-finance-dashboard/automation_profile/`

**替代方案**:
- A) 放在用户浏览器 User Data 同级目录 → 不好，可能被 Chrome 扫到或用户误删
- B) 让用户自选路径 → 增加操作复杂度，非技术用户容易配错

**理由**: 统一在 app data 下管理，与现有 SQLite 数据库同级，便于备份和清理。目录首次使用时自动创建，无需用户干预。

### Decision 2: 按站点登录，不做全局初始化

**选择**: 站点编辑表单中"测试抓取"旁新增"登录此站点"按钮，每个站点独立登录。

**流程**:
1. 用户在站点表单中点击"登录此站点"
2. 系统用专用 profile 启动浏览器，导航到该站点 URL
3. 用户手动登录（就像平时用浏览器一样）
4. 用户关闭浏览器
5. 系统自动执行一次测试抓取验证登录是否成功
6. 成功 → 完成；失败 → 用户再次点击登录

**替代方案**:
- A) 全局"初始化自动化浏览器"按钮 → 不好，每个站点账号不同，不知道该导航到哪个 URL；需要额外的 initialized 状态追踪
- B) 全局初始化 + per-site 状态追踪 → 过度设计，用测试抓取本身就能验证

**理由**: 每个站点账号不同，按站点登录是最自然的操作；用测试抓取验证登录状态，不需要额外状态标记（KISS 原则）。

### Decision 3: 浏览器可执行文件复用

**选择**: 继续复用 `find_chrome_executable()` 发现的真实 Chrome/Edge 二进制。浏览器检测逻辑保持不变，只用它获取 executable_path。

**理由**: 专用 profile 目录变了，但浏览器本身不变。使用用户真实安装的浏览器保证最佳兼容性。

### Decision 4: 不再需要关闭日常浏览器

**选择**: 移除"检测到浏览器冲突 → 要求关闭浏览器"的前置阻断逻辑。冲突检测仅针对 automation profile 目录自身的 lock file。

**原理**: Chrome 支持同一个 chrome.exe 同时运行多个实例，只要 `--user-data-dir` 不同就不冲突。专用 profile 目录与日常浏览器 User Data 完全独立，因此两者可以并行运行。

**替代方案**:
- 保留旧的冲突检测 → 没有意义了，专用目录不会和日常浏览器冲突

**理由**: 这是新方案最大的用户体验改进之一——不再打断用户的日常浏览器使用。

### Decision 5: 向后兼容

**选择**: 保留旧配置字段（`browser_profile_path`、`browser_profile_dir`）在数据库中，但 UI 不再主推。全局设置中的旧"浏览器配置"区域降级为 legacy 选项，标注"推荐使用专用自动化浏览器"。

**理由**: 避免数据库 migration 复杂度，旧数据不删除但不再是主路径。

## Risks / Trade-offs

- **[Risk] 某个站点登录过期** → 用户点击该站点的"登录此站点"重新登录即可。无需额外引导——测试抓取失败本身就是信号。
- **[Risk] 首次添加站点多一步登录操作** → "登录此站点"紧挨"测试抓取"，操作路径极短。相比旧方案的不稳定，多一步是值得的。
- **[Risk] 专用 profile 目录被误删或损坏** → 全局设置提供"重置自动化浏览器"按钮，一键清空重来。所有站点需要重新登录一次。
- **[Risk] 同时运行日常浏览器和自动化** → 这正是新方案的核心优势。不同 user-data-dir 互不干扰，无 lock file 冲突。
- **[Trade-off] 不再自动继承日常浏览器的登录态** → 设计如此。稳定性 + 并行运行 > 免登录便利性。
