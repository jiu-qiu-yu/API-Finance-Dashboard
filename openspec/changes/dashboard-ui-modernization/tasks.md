## 1. 设计令牌体系升级 (styles.py)

- [x] 1.1 更新 `Colors` 类：窗口背景 `#f0f2f5`、卡片背景 `#fafbfc`、新增浅色语义背景（`BG_SUCCESS_SOFT=#f0faf4`、`BG_DANGER_SOFT=#fff2f0`、`BG_WARNING_SOFT=#fff8e6`、`BG_DANGER_HOVER=#ffe8e5`、`ROW_HOVER=#f5f7fa`、`PROGRESS_BG=#e8ecef`、`SEPARATOR=#e8ecef`），新增状态徽章深色文字色
- [x] 1.2 新增 `Shadows` 类：定义三级阴影工厂方法 `create_sm(parent)` / `create_md(parent)` / `create_lg(parent)`，返回 `QGraphicsDropShadowEffect` 实例（2px/8px/16px blur，半透明黑色）
- [x] 1.3 新增 `FontWeights` 类：`REGULAR=400` / `MEDIUM=500` / `SEMIBOLD=600` / `BOLD=700`
- [x] 1.4 新增 `BorderRadius` 类：`SM=4` / `MD=8` / `LG=12`
- [x] 1.5 更新 `Spacing` 类：增加 `XXXL=48`
- [x] 1.6 更新所有预定义样式模板：引用新令牌值（背景色、阴影参数、圆角、字重）

## 2. 卡片基础组件优化 (card_widget.py)

- [x] 2.1 更新 `CardWidget` 样式：使用 `Colors.BG_CARD`（`#fafbfc`）、`BorderRadius.MD`、`Shadows.create_md()` 替换硬编码值
- [x] 2.2 优化卡片标题样式：使用 `FontWeights.SEMIBOLD`

## 3. 利润卡片重设计 (main_window.py - profit card)

- [x] 3.1 实现紧凑摘要行：在利润卡片顶部添加水平布局 "站点: N | 上游: N | 告警: N | 总消耗: $X"，12px `TEXT_SECONDARY` 文字，告警数量根据值着色（0=绿色，>0=红色）
- [x] 3.2 增强利润数字展示：正利润添加 "↑" 前缀（绿色），负利润添加 "↓"（红色），使用 `WEIGHT_BOLD` 48px
- [x] 3.3 为 CollapsiblePanel 设置 max-height 200px，超出部分内部滚动（QScrollArea 包裹）
- [x] 3.4 优化明细面板排版：表格式布局展示各站点消耗明细
- [x] 3.5 更新按钮样式：巡检按钮 `RADIUS_SM` 圆角，设置按钮使用次要样式（灰色边框）
- [x] 3.6 在巡检完成回调中计算并传递摘要数据（站点总数、上游数、告警数量、总消耗）

## 4. 布局架构重构 (main_window.py - S3 layout)

- [x] 4.1 删除中间层的 `_quota_card` 和 `_build_quota_card()` 相关代码
- [x] 4.2 重构下半区布局：从 GridLayout(3:2) 改为 QHBoxLayout — 左侧告警侧栏 (~200px fixedWidth) + 右侧超级表格 (stretch)
- [x] 4.3 告警侧栏使用 `AlignTop` 对齐，不强制与表格等高
- [x] 4.4 利润卡片与下方区域间距改为 `XL`（24px），告警侧栏与表格间距 `LG`（16px）
- [x] 4.5 更新窗口背景色为 `#f0f2f5`

## 5. 告警侧栏设计 (main_window.py - alert sidebar)

- [x] 5.1 无告警状态：白色背景卡片，绿色 "✅ 所有上游额度正常" 文字，`WEIGHT_SEMIBOLD`
- [x] 5.2 告警状态：卡片背景改为 `#fff2f0`（浅红），左侧 border-left 4px `Colors.DANGER` 红色边条
- [x] 5.3 告警列表：每个告急站点作为独立条目（站点名 + 余额/阈值），带红色圆点标记

## 6. 超级表格实现 (status_list.py → unified site table)

- [x] 6.1 扩展表格为 5 列：站点名(Stretch) | 今日消耗(100px) | 当前余额(100px) | 额度比(150px) | 状态(90px)
- [x] 6.2 实现表格内嵌 QProgressBar：上游行的"额度比"列使用 `setCellWidget`，主站行显示 "--" 文字
- [x] 6.3 实现交替行底色：使用 `setAlternatingRowColors(True)` + QSS `alternate-background-color`
- [x] 6.4 实现现代化状态徽章：使用 QLabel + stylesheet 作为 cellWidget，浅色底+深色字+4px圆角
- [x] 6.5 改进表头样式：灰色背景 `#f0f2f5`、`WEIGHT_SEMIBOLD`、12px 字号、底部分隔线
- [x] 6.6 实现告急行浅红背景：`#fff2f0` 覆盖交替行色，文字 `WEIGHT_SEMIBOLD` 深红
- [x] 6.7 金额列右对齐 + `WEIGHT_MEDIUM` 字重
- [x] 6.8 实现行 hover 效果：普通行 hover `#f5f7fa`，告急行 hover `#ffe8e5`，150ms 过渡
- [x] 6.9 表格排序：告急行排最前（主站之后），然后正常行

## 7. 设置面板美化 (settings_panel.py)

- [x] 7.1 统一输入框样式：边框 `#d9d9d9`、焦点蓝色高亮 `Colors.PRIMARY`、`RADIUS_SM` 圆角
- [x] 7.2 优化按钮层级：主要=蓝色、次要=灰色边框、危险=红色
- [x] 7.3 对话框整体样式：`SHADOW_LG`、`RADIUS_LG`、改进分区间距

## 8. 告警弹窗升级 (main_window.py - alert popup)

- [x] 8.1 更新告警弹窗样式：`SHADOW_LG` + `RADIUS_LG`，现代化列表样式

## 9. 收尾验证

- [x] 9.1 全面视觉回归测试：启动应用检查布局无错位，利润卡片/告警侧栏/超级表格正确显示
- [x] 9.2 运行现有单元测试确保功能无回归
- [ ] 9.3 验证巡检完整流程：摘要行更新、利润显示、告警侧栏、超级表格（含进度条）、hover 效果
- [ ] 9.4 验证 15+ 站点场景下的滚动体验和性能
