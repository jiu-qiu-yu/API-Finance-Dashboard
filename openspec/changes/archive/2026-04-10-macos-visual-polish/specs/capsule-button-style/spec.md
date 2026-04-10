## ADDED Requirements

### Requirement: 胶囊形主要按钮
主要操作按钮（如"开始巡检"）SHALL 使用胶囊形（`border-radius: 20px`），品牌海军蓝背景 `#2c3e50`，白色文字，`padding: 12px 28px`。Hover 时背景加深为 `#1a252f`。

#### Scenario: 主要按钮展示
- **WHEN** 用户查看包含主要按钮的界面
- **THEN** 按钮呈胶囊形（两端完全圆弧）
- **AND** 背景色为品牌海军蓝

### Requirement: 胶囊形次要按钮
次要操作按钮（如"设置"）SHALL 使用胶囊形（`border-radius: 20px`），透明背景，`1px solid #e5e5ea` 淡灰边框，品牌色文字 `#2c3e50`，`padding: 12px 28px`。

#### Scenario: 次要按钮展示
- **WHEN** 用户查看包含次要按钮的界面
- **THEN** 按钮呈胶囊形，透明背景，淡灰色边框

### Requirement: 胶囊形危险按钮
危险操作按钮（如"删除"、"重置"）SHALL 使用胶囊形（`border-radius: 20px`），透明背景，`1px solid #e74c3c` 红色边框，红色文字。

#### Scenario: 危险按钮展示
- **WHEN** 用户查看包含危险按钮的界面
- **THEN** 按钮呈胶囊形，透明背景，红色边框和文字
