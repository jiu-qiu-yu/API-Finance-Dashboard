## MODIFIED Requirements

### Requirement: 低于阈值自动标红
巡检完成后，系统 SHALL 自动将余额低于或等于阈值的上游站点行标记为告急状态。告急行 SHALL 使用浅红色背景 `#fff2f0` 配合深红色文字，文字使用 `WEIGHT_SEMIBOLD` 字重。此样式 SHALL 覆盖交替行底色。hover 时告急行背景从 `#fff2f0` 变为 `#ffe8e5`。

#### Scenario: 单个上游低于阈值
- **WHEN** 巡检完成，上游 "ProviderA" 余额 $3.00 低于阈值 $5.00
- **THEN** "ProviderA" 所在行背景变为 `#fff2f0`，文字为深红色 `WEIGHT_SEMIBOLD`

#### Scenario: 余额恢复正常
- **WHEN** 下次巡检时 "ProviderA" 余额 $8.00 高于阈值 $5.00
- **THEN** "ProviderA" 所在行恢复正常交替行底色

### Requirement: 告警弹窗汇总
巡检完成后，若存在低于阈值的上游站点，系统 SHALL 弹出汇总告警弹窗。弹窗 SHALL 使用 `SHADOW_LG` 和 `RADIUS_LG` 圆角，现代化列表样式展示告急站点。

#### Scenario: 多个上游告急弹窗
- **WHEN** 巡检完成，"ProviderA" 和 "ProviderB" 告急
- **THEN** 弹出告警弹窗，标题为 "额度告急警告"
- **AND** 以列表形式展示告急站点信息
- **AND** 弹窗有 `SHADOW_LG` 阴影和 `RADIUS_LG` 圆角

#### Scenario: 无告急不弹窗
- **WHEN** 所有上游余额均高于阈值
- **THEN** 系统不弹出告警弹窗

### Requirement: 系统托盘通知告警
当存在告急上游时，系统 SHALL 通过通知器发送 OS 级通知。

#### Scenario: 系统通知发送
- **WHEN** 巡检完成，存在告急上游
- **THEN** 系统发送 OS 通知，标题为 "New API 额度告急"
