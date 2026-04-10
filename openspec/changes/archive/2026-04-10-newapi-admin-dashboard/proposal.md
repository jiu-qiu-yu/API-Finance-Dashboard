## Why

当前 API Finance Dashboard 界面全为英文，且 UI 交互较为基础，缺乏面向 New API 站长的高效运营体验。站长需要快速掌握当日盈利情况、各上游渠道的剩余额度，并在额度低于阈值时获得醒目的视觉告警和主动提醒，以便及时充值避免服务中断。现有界面缺少这些关键的可视化与告警能力。

## What Changes

- 全面汉化界面文字（按钮、标签、提示信息、对话框等）
- 重新设计仪表盘首页布局：卡片式设计展示今日盈利、上游额度概览、告警摘要
- 新增上游额度监控面板：以可视化列表/卡片展示每个上游的剩余额度
- 新增阈值告警系统：低于阈值的上游自动标红 + 弹窗/系统通知提醒站长
- 新增快捷配置面板：站长可高效配置阈值、汇率、上游站点等参数
- 优化盈利展示：点击盈利数字可展开查看详细的消耗/收入分项

## Capabilities

### New Capabilities
- `chinese-localization`: 全站中文本地化，覆盖所有 UI 文字和提示信息
- `dashboard-cards`: 卡片式仪表盘首页，包含今日盈利卡片、上游额度概览卡片、告警摘要卡片
- `upstream-quota-monitor`: 上游额度监控面板，可视化展示各上游剩余额度与阈值对比
- `threshold-alert-ui`: 阈值告警 UI，低于阈值自动标红 + 弹窗提醒 + 系统托盘通知
- `profit-detail-view`: 盈利详情展开视图，点击可查看主站消耗与各上游消耗的明细

### Modified Capabilities
- `dashboard-ui`: 重构现有仪表盘布局为卡片式中文界面
- `alert-system`: 增强告警系统支持阈值标红和系统托盘通知

## Impact

- **UI 层**：`main_window.py`、`status_list.py`、`settings_panel.py` 需要重构
- **数据层**：`models.py` 可能需要扩展字段以支持额度详情
- **服务层**：`inspection_service.py` 需要增加阈值判断逻辑
- **通知层**：`notifier.py` 需要支持系统托盘通知
- **依赖**：无新增外部依赖（PySide6 已支持系统托盘通知）
