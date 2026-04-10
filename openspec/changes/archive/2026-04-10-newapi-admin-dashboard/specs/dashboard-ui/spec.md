## MODIFIED Requirements

### Requirement: Top dashboard with net profit display
系统 SHALL 以卡片式布局在主窗口顶部显示今日净利润。利润金额以大号加粗字体居中显示，格式为 "￥XXX.XX" 或 "$XXX.XX"。利润下方 SHALL 显示公式提示："净利润 = 主站消耗 - 上游总消耗"。仪表盘 SHALL 包含醒目的 "开始巡检" 按钮和上次巡检时间戳。利润金额 SHALL 可点击，点击后展开/收起消耗明细。

#### Scenario: Dashboard after successful inspection
- **WHEN** 巡检完成，计算净利润为 ￥42.40
- **THEN** 仪表盘以绿色大号字体显示 "￥42.40"
- **AND** 显示上次巡检时间
- **AND** "开始巡检" 按钮恢复为可用状态

#### Scenario: 点击利润金额展开明细
- **WHEN** 用户点击利润金额
- **THEN** 卡片下方平滑展开消耗明细面板

### Requirement: Upstream health status list
系统 SHALL 以卡片列表形式展示所有已配置上游站点，列包含：站点名称 | 今日消耗 | 当前余额 | 阈值 | 状态。状态指示器 SHALL 遵循颜色编码规则。列表 SHALL 按状态排序（告急在前）。

#### Scenario: Healthy upstream display
- **WHEN** 上游余额 ($10.00) 高于阈值 ($5.00)
- **THEN** 状态列显示绿色 "正常" 标识

#### Scenario: Low balance upstream display
- **WHEN** 上游余额 ($3.00) 等于或低于阈值 ($5.00)
- **THEN** 整行显示红色背景，状态显示 "额度告急"

#### Scenario: Failed scraping display
- **WHEN** 上游站点抓取失败（页面不可达或需要登录）
- **THEN** 状态显示黄色 "需核实" 标识

### Requirement: Inspection progress feedback
巡检过程中，UI SHALL 显示进度条。UI 主线程 SHALL 不因巡检而冻结。

#### Scenario: Inspection in progress
- **WHEN** 用户点击 "开始巡检"
- **THEN** 按钮变为不可用，进度条出现
- **AND** UI 保持响应（可滚动、调整窗口大小等）

#### Scenario: Inspection completes
- **WHEN** 所有站点巡检完成
- **THEN** 进度条消失，结果显示，告警摘要高亮

### Requirement: Site management settings panel
系统 SHALL 提供中文设置面板用于管理站点配置。用户 SHALL 可以添加、编辑、删除站点。每个站点表单 SHALL 包含：站点类型（主站/上游）、URL、面板类型（预设下拉或自定义）、CSS 选择器、正则表达式、告警阈值（仅上游站点）。

#### Scenario: Add new upstream site
- **WHEN** 用户填写站点名称、URL，选择面板类型 "New API"，设置阈值为 $5.00
- **THEN** 系统保存配置，站点出现在状态列表中

#### Scenario: Edit existing site
- **WHEN** 用户修改已有站点的 URL 并保存
- **THEN** 系统更新配置，下次巡检使用新 URL

#### Scenario: Delete site
- **WHEN** 用户删除一个站点
- **THEN** 系统移除配置，该站点不再出现在状态列表中
