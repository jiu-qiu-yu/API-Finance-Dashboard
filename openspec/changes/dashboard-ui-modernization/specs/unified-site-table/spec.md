## ADDED Requirements

### Requirement: 统一站点健康总览表格
系统 SHALL 使用单一表格展示所有站点（主站 + 上游）的全部关键信息，替代原来的"额度概览卡片 + 状态表格"双视图结构。表格 SHALL 包含 5 列：站点名称（stretch）、今日消耗（100px, 右对齐）、当前余额（100px, 右对齐）、额度比（150px, 内嵌进度条）、状态（90px, 徽章样式）。表格 SHALL 是下半区域的唯一滚动区域。

#### Scenario: 15+ 站点的完整展示
- **WHEN** 巡检完成，有 2 个主站和 15 个上游站点
- **THEN** 表格以 17 行展示所有站点
- **AND** 主站行的站点名前缀 "[主站]"，余额列和额度比列显示 "--"
- **AND** 上游行显示完整的消耗、余额、进度条和状态
- **AND** 表格可以垂直滚动查看超出可视区的行

### Requirement: 表格内嵌迷你进度条
上游站点行的"额度比"列 SHALL 使用 `setCellWidget` 嵌入 `QProgressBar`。进度条 SHALL 使用 `RADIUS_SM`（4px）圆角、16px 高度、浅灰背景 `#e8ecef`。进度条颜色 SHALL 根据余额/阈值比值变化：>100% 绿色（`Colors.SUCCESS`）、50%-100% 黄色（`Colors.WARNING`）、<50% 红色（`Colors.DANGER`）。进度条内 SHALL 显示百分比数值。主站行的额度比列 SHALL 显示 "--" 文字。

#### Scenario: 上游进度条颜色
- **WHEN** 上游余额为 $10.00，阈值为 $5.00（比值 200%）
- **THEN** 额度比列显示绿色进度条，标注 "200%"

#### Scenario: 主站无进度条
- **WHEN** 主站行显示在表格中
- **THEN** 额度比列显示 "--" 文字，无进度条

### Requirement: 交替行底色
表格 SHALL 使用交替行底色：偶数行 `#fafbfc`（微灰白），奇数行 `#ffffff`（纯白）。告急行的浅红高亮 SHALL 覆盖交替行色。

#### Scenario: 多行数据交替展示
- **WHEN** 表格显示 6 个站点
- **THEN** 第 1、3、5 行背景白色，第 2、4、6 行背景微灰白
- **AND** 告急站点行使用浅红背景 `#fff2f0`，覆盖交替色

### Requirement: 现代化状态徽章
状态列 SHALL 使用圆角徽章样式：正常 = 浅绿底 `#f0faf4` + 深绿字 `#2ecc71`、告急 = 浅红底 `#fff2f0` + 深红字 `#e74c3c`、待核实 = 浅橙底 `#fff8e6` + 深橙字 `#f39c12`。徽章 SHALL 使用 `RADIUS_SM`（4px）圆角和水平内边距。

#### Scenario: 正常状态徽章
- **WHEN** 上游站点余额正常
- **THEN** 状态列显示浅绿底 + 深绿文字的 "正常" 徽章

#### Scenario: 告急状态徽章
- **WHEN** 上游站点余额低于阈值
- **THEN** 状态列显示浅红底 + 深红文字的 "额度告急" 徽章

### Requirement: 改进表头样式
表头 SHALL 使用 `WEIGHT_SEMIBOLD` 字重、12px 字号、`TEXT_SECONDARY` 灰色文字。表头背景 SHALL 为 `#f0f2f5`。表头底部 SHALL 有 1px 分隔线。

#### Scenario: 表头视觉区分
- **WHEN** 用户查看表格
- **THEN** 表头有灰色背景和灰色加粗文字
- **AND** 表头与数据行之间有清晰分隔线

### Requirement: 表格行 hover 效果
表格行 SHALL 在鼠标悬停时显示轻微的背景色变化，过渡时间 150ms。普通行 hover 背景为 `#f5f7fa`。告急行 hover 背景从 `#fff2f0` 变为 `#ffe8e5`。

#### Scenario: 普通行 hover
- **WHEN** 鼠标悬停在正常状态的行上
- **THEN** 行背景在 150ms 内过渡为 `#f5f7fa`

#### Scenario: 告急行 hover
- **WHEN** 鼠标悬停在告急状态的行上
- **THEN** 行背景在 150ms 内从 `#fff2f0` 过渡为 `#ffe8e5`

### Requirement: 金额列右对齐
消耗和余额列 SHALL 右对齐显示。金额数值 SHALL 使用 `WEIGHT_MEDIUM`（500）字重。

#### Scenario: 多行金额对齐
- **WHEN** 表格有 3 个站点，消耗分别为 $5.30、$125.00、$42.75
- **THEN** 金额数字右对齐显示，小数点纵向对齐
