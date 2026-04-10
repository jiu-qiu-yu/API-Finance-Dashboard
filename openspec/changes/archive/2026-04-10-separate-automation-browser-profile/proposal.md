## Why

当前项目使用 `launch_persistent_context` 直接复用用户日常浏览器的主 User Data 目录（Chrome/Edge 默认配置）来获取登录态。但 Chrome 近期策略变更后，自动化主用户配置不再被稳定支持——实测表现为 `--no-sandbox` 警告页、`AutomationControlled` 警告页、或启动后卡在 `about:blank`。Playwright 官方文档已明确声明："automating the default Chrome user profile is not supported"。此外，由于共用同一个 User Data 目录，用户每次巡检前必须关闭日常浏览器，严重影响使用体验。需要将浏览器自动化策略从"复用主 profile"迁移到"使用项目专用 automation profile"。

## What Changes

- **新增专用自动化浏览器配置目录**：项目自动维护独立的 `automation_profile` 目录（首次使用时自动创建），不再指向 Chrome/Edge 主 `User Data`。因为目录独立，用户日常浏览器可以同时运行，无需关闭。
- **新增按站点登录流程**：站点编辑表单中"测试抓取"旁新增"登录此站点"按钮。点击后弹出专用 profile 的浏览器窗口并导航到该站点 URL，用户手动登录后关闭浏览器，系统自动执行一次测试抓取验证登录是否成功。
- **修改 BrowserEngine 启动链路**：`user_data_dir` 默认指向专用 automation profile 目录，不再使用用户日常浏览器的主配置目录。
- **修改配置层**：`ConfigRepository` 新增 `automation_profile_path` 字段。移除 `automation_profile_initialized` 概念——不做状态追踪，用测试抓取结果本身判断登录是否有效。
- **修改 UI 全局设置**：原有"浏览器配置"区域简化，新增"自动化浏览器"区块仅显示路径（只读）和一个"重置"按钮。移除浏览器账号选择下拉框（不再需要选择 profile）。
- **移除"关闭浏览器"前置要求**：因为专用 profile 与日常浏览器目录独立，冲突检测仅针对 automation profile 自身的 lock file，不再阻止用户在日常浏览器运行时进行巡检。
- **BREAKING**：不再默认支持直接复用用户主浏览器 User Data 目录进行自动化。已有配置的用户需要对每个站点通过"登录此站点"重新登录一次。

## Capabilities

### New Capabilities
- `automation-profile-management`: 专用自动化浏览器 profile 目录的自动创建、重置功能
- `per-site-login`: 按站点的手动登录流程——在站点编辑表单中"登录此站点"按钮触发，登录完成后自动测试抓取验证

### Modified Capabilities
- `local-browser-context`: BrowserEngine 的 `user_data_dir` 来源从"用户主浏览器 User Data"变更为"项目专用 automation profile 目录"；移除"必须关闭日常浏览器"的前置要求；冲突检测仅针对 automation profile 目录

## Impact

- **engine/browser_engine.py**: `BrowserEngine.__init__` 参数语义变更——`profile_path` 指向专用 automation profile 目录；`validate_browser_profile_path` 放宽校验（不要求 `Default/` 或 `Local State`）；冲突检测只检查 automation profile 的 lock file
- **engine/automation_profile.py**（新文件）: 专用 profile 目录路径解析、自动创建、重置
- **engine/automation_login.py**（新文件）: 按站点登录会话——启动浏览器、导航到站点 URL、等待用户关闭
- **data/config_repository.py**: 新增 `automation_profile_path` 存取方法；移除 `browser_profile_path`、`browser_profile_dir` 的主要使用场景（降级为 legacy fallback）
- **ui/settings_panel.py**: 站点表单新增"登录此站点"按钮；全局设置简化为"自动化浏览器路径 + 重置"；`_TestScrapeWorker` 切换到使用专用 profile；移除 profile 下拉选择
- **ui/automation_login_worker.py**（新文件）: QThread 封装按站点登录流程
- **service/inspection_service.py**: `BrowserEngine` 参数来源切换到专用 profile
- **ui/inspection_worker.py**: 同上
- **tests/**: 适配新配置字段和按站点登录流程
