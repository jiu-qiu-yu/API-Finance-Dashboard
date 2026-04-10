## Why

当前仪表盘在上一轮改造中完成了布局重构（S3 方案）和设计令牌体系升级，但**内部令牌更新并未转化为外部视觉质变**——窗口外壳、卡片质感、表格外观、按钮形态仍然保持"企业后台管理系统"的观感。用户反馈"内部变化但整体外部没有变化，感觉更割裂了"。此外，`QMessageBox` 上误用 `setGraphicsEffect` 导致**告警弹窗渲染全黑**的严重 bug。

用户明确要求参考 **macOS / Apple 原生设计风格**：大圆角浮空卡片、极淡阴影、胶囊按钮、极简列表、充裕留白。同时需要将品牌 Logo（`logo/logo.webp`）集成到应用标题栏，并从 Logo 的海军蓝+金色电路板配色中提取品牌色体系。

## What Changes

- **修复告警弹窗全黑 bug**：移除 `QMessageBox` 上的 `setGraphicsEffect`（顶级窗口不支持 `QGraphicsEffect`）
- **品牌 Logo 集成**：在窗口标题栏/利润卡片区域展示 `logo/logo.webp`，设置窗口图标
- **色彩系统重映射**：从冷灰蓝切换到暖灰白 + Logo 品牌色（海军蓝 `#2c3e50` + 金色 `#c8a84e`）
- **卡片 macOS 化**：去边框、大圆角(14px)、极淡大模糊阴影、纯白背景、宽松内边距
- **按钮胶囊化**：所有按钮改为大圆角(20px)胶囊形
- **表格极简化**：去 header 背景色、行分隔线极淡化、行高加大、徽章胶囊化、表格包裹在卡片容器中
- **阴影系统升级**：小模糊高透明度 → 大模糊极低透明度（"若有若无的浮起感"）
- **全局间距拉大**：窗口边距、卡片内边距、区域间距统一加大，创造 macOS 级呼吸感
- **告警侧栏微调**：更大圆角、更细边条、更多内边距

## Capabilities

### New Capabilities
- `brand-logo-integration`: 在应用窗口集成品牌 Logo（标题栏图标 + 利润卡片区域展示）
- `macos-card-style`: macOS 风格卡片组件（无边框 + 14px 大圆角 + 极淡大模糊阴影 + 纯白背景）
- `capsule-button-style`: 胶囊形按钮系统（20px 圆角 + 主要/次要/危险三种层级）
- `minimal-list-table`: macOS 极简列表风格的表格（无 header 背景 + 极淡行分隔线 + 胶囊徽章 + 卡片包裹）

### Modified Capabilities
- `modern-theme-system`: 色彩从冷灰蓝切换到暖灰白+品牌色，阴影参数全面调整，间距拉大
- `dashboard-ui`: 全局间距加大创造呼吸感，弹窗 bug 修复
- `threshold-alert-ui`: 告警弹窗 bug 修复（移除 `setGraphicsEffect`），告警侧栏圆角加大

## Impact

- **大幅改动文件**：`styles.py`（色彩/阴影/间距/按钮模板全面重写）、`card_widget.py`（去边框+新阴影+大圆角）、`status_list.py`（表格极简化+卡片包裹）、`main_window.py`（Logo 集成+弹窗修复+间距调大）
- **中等改动文件**：`settings_panel.py`（按钮胶囊化+输入框微调）
- **新增资源引用**：`logo/logo.webp` 作为窗口图标
- **无后端变更**：纯 UI 层改动
- **无新依赖**：仅使用 PySide6 原生能力
