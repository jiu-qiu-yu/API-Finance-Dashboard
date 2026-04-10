## MODIFIED Requirements

### Requirement: Top dashboard with net profit display
系统 SHALL 以卡片式布局在主窗口顶部显示今日净利润。利润金额以大号加粗字体（48px, `WEIGHT_BOLD`）居中显示，格式为 "￥XXX.XX" 或 "$XXX.XX"。利润数字 SHALL 配合趋势指示符号：正利润前显示 "↑"（绿色），负利润显示 "↓"（红色），零或无数据不显示符号。利润下方 SHALL 显示公式提示。利润卡片顶部 SHALL 包含紧凑摘要行。利润金额 SHALL 可点击展开/收起消耗明细。

#### Scenario: Dashboard after successful inspection
- **WHEN** 巡检完成，计算净利润为 ￥42.40
- **THEN** 仪表盘以绿色大号字体显示 "↑ ￥42.40"
- **AND** 顶部摘要行更新
- **AND** "开始巡检" 按钮恢复

#### Scenario: Dashboard with negative profit
- **WHEN** 巡检完成，计算净利润为 -￥15.20
- **THEN** 仪表盘以红色大号字体显示 "↓ -￥15.20"

#### Scenario: 点击利润金额展开明细
- **WHEN** 用户点击利润金额
- **THEN** 卡片下方平滑展开消耗明细面板
- **AND** 面板设置 max-height 200px，超出部分内部滚动

### Requirement: Upstream health status list
系统 SHALL 以统一表格形式展示所有站点（主站 + 上游），表格含 5 列：站点名称、今日消耗、当前余额、额度比（内嵌进度条）、状态（徽章）。详见 `unified-site-table` spec。**BREAKING**: 此需求不再以独立的"上游健康状态"标题卡片实现，而是作为超级表格集成在布局下半区。

#### Scenario: Healthy upstream display
- **WHEN** 上游余额 ($10.00) 高于阈值 ($5.00)
- **THEN** 状态列显示浅绿底徽章 "正常"，额度比列显示绿色进度条 200%

#### Scenario: Low balance upstream display
- **WHEN** 上游余额 ($3.00) 等于或低于阈值 ($5.00)
- **THEN** 整行显示浅红背景 `#fff2f0`，状态显示浅红底徽章 "额度告急"，额度比显示红色进度条

#### Scenario: Failed scraping display
- **WHEN** 上游站点抓取失败
- **THEN** 消耗/余额/额度比列显示 "--"，状态显示浅橙底徽章 "待核实"

### Requirement: Inspection progress feedback
巡检过程中，UI SHALL 显示进度条，使用主色调蓝色填充。UI 主线程 SHALL 不冻结。

#### Scenario: Inspection in progress
- **WHEN** 用户点击 "开始巡检"
- **THEN** 按钮变为不可用，进度条出现并显示 "正在巡检 {站点名}... (X/Y)"

#### Scenario: Inspection completes
- **WHEN** 所有站点巡检完成
- **THEN** 进度条消失，超级表格和告警侧栏更新

### Requirement: Site management settings panel
系统 SHALL 提供中文设置面板。输入框 SHALL 有清晰边框和焦点蓝色高亮。按钮层级：主要蓝色、次要灰色边框、危险红色。对话框 SHALL 使用 `SHADOW_LG` 和 `RADIUS_LG`。

#### Scenario: Add new upstream site
- **WHEN** 用户填写站点名称、URL，选择面板类型，设置阈值
- **THEN** 系统保存配置

#### Scenario: Edit existing site
- **WHEN** 用户修改已有站点的 URL 并保存
- **THEN** 系统更新配置

#### Scenario: Delete site
- **WHEN** 用户删除一个站点
- **THEN** 系统移除配置
