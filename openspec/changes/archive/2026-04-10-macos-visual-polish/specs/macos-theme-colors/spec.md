## ADDED Requirements

### Requirement: macOS 暖灰白色彩体系
设计令牌色彩 SHALL 切换到暖灰白+品牌色体系：
- 窗口背景：`#f0f2f5` → `#f5f5f7`
- 卡片背景：`#fafbfc` → `#ffffff`
- 主色调：`#3498db` → `#2c3e50`（Logo 海军蓝）
- 主色调 hover：`#2980b9` → `#1a252f`
- 新增强调色：`#c8a84e`（Logo 金色）
- 文字主色：`#2c3e50` → `#1d1d1f`
- 文字次色：`#7f8c8d` → `#86868b`
- 分隔线：`#e8ecef` → `#e5e5ea`
- 卡片边框色：`#e0e0e0` → `transparent`

#### Scenario: 背景层次
- **WHEN** 用户查看应用界面
- **THEN** 窗口背景为温暖的浅灰白色
- **AND** 卡片为纯白色，在背景上有清晰但柔和的层次区分

### Requirement: 极淡大模糊阴影系统
三级阴影 SHALL 调整为大模糊半径 + 极低透明度：
- SM：`blur(4px)` `offset(0,1)` `α6`
- MD：`blur(24px)` `offset(0,4)` `α8`
- LG：`blur(40px)` `offset(0,8)` `α12`

#### Scenario: 卡片阴影效果
- **WHEN** 卡片使用 MD 阴影
- **THEN** 阴影是柔和、大范围、几乎感觉不到但创造深度感

### Requirement: macOS 级间距
全局间距 SHALL 加大以创造呼吸感：
- 窗口边距：16px → 24px
- 卡片内边距：16px → 24px
- 利润卡片与底区间距：24px → 28px

#### Scenario: 界面呼吸感
- **WHEN** 用户查看应用界面
- **THEN** 各元素之间有充裕的空白，不显拥挤
