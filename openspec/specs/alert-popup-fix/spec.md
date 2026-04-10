# alert-popup-fix Specification

## Purpose
TBD - created by archiving change macos-visual-polish. Update Purpose after archive.
## Requirements
### Requirement: 告警弹窗正常渲染
告警弹窗 SHALL 使用系统原生 `QMessageBox.warning()` 静态方法，不应用 `QGraphicsDropShadowEffect` 或自定义 `setStyleSheet`。弹窗阴影和圆角由操作系统窗口管理器提供。

#### Scenario: 告警弹窗正常显示
- **WHEN** 巡检完成且存在告急上游
- **THEN** 弹窗正常显示（非全黑）
- **AND** 弹窗包含告急站点信息列表

#### Scenario: 弹窗无 QGraphicsEffect
- **WHEN** 告警弹窗被创建
- **THEN** 不对弹窗调用 `setGraphicsEffect`
- **AND** 不对弹窗设置自定义 `setStyleSheet`

