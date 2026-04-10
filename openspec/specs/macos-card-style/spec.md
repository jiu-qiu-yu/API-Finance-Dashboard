# macos-card-style Specification

## Purpose
TBD - created by archiving change macos-visual-polish. Update Purpose after archive.
## Requirements
### Requirement: macOS 风格卡片容器
`CardWidget` SHALL 采用 macOS 原生设计语言：纯白背景 `#ffffff`、无边框（`border: none`）、14px 大圆角、极淡大模糊阴影（`blur(24px)` `offset(0,4)` `α8`）、24px 内边距。卡片在暖灰白窗口背景上 SHALL 呈现"浮空"效果。

#### Scenario: 卡片浮空视觉
- **WHEN** 用户查看包含卡片的界面
- **THEN** 卡片在 `#f5f5f7` 背景上显示为纯白圆角矩形
- **AND** 卡片无可见边线
- **AND** 卡片四周有若有若无的柔和阴影

#### Scenario: 卡片内边距
- **WHEN** 卡片内部有内容
- **THEN** 内容与卡片边缘至少有 24px 的间距

