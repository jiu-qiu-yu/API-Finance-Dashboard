## ADDED Requirements

### Requirement: 品牌 Logo 窗口图标
应用 SHALL 使用 `logo/logo.webp` 作为窗口图标（通过 `QIcon` + `setWindowIcon`）。若 webp 格式加载失败，SHALL 回退到 `logo/logo.png`。

#### Scenario: 窗口图标展示
- **WHEN** 应用启动
- **THEN** 任务栏和窗口标题栏展示 Logo 图标

### Requirement: 利润卡片品牌标识
利润卡片标题区域 SHALL 在"今日盈利"文字左侧展示 32×32px 的 Logo 缩略图。Logo 和标题文字垂直居中对齐，间距 `SM`（8px）。

#### Scenario: 标题区品牌展示
- **WHEN** 用户查看首页
- **THEN** 利润卡片标题显示 [Logo 32×32] 今日盈利
- **AND** Logo 与文字垂直居中

#### Scenario: Logo 文件不存在
- **WHEN** Logo 文件不存在或无法加载
- **THEN** 仅显示文字标题，不显示 Logo，不崩溃
