## ADDED Requirements

### Requirement: 现代化配色令牌体系
系统 SHALL 在 `styles.py` 中定义完整的颜色梯度体系。主色调蓝色 SHALL 包含从 Blue-50（最浅）到 Blue-900（最深）的梯度。语义色（Success `#2ecc71`、Danger `#e74c3c`、Warning `#f39c12`）SHALL 保持不变以维持用户认知连续性。背景色体系 SHALL 包含：窗口背景 `#f0f2f5`、卡片背景 `#fafbfc`、悬浮背景 `#ffffff`。

#### Scenario: 配色令牌在组件中应用
- **WHEN** 开发者引用 `Colors.BG_CARD` 创建卡片
- **THEN** 卡片背景为 `#fafbfc`（微灰白），与窗口背景 `#f0f2f5` 形成清晰的层次区分

### Requirement: 三级阴影令牌
系统 SHALL 定义三级阴影体系：`SHADOW_SM`（2px blur，用于按钮/输入框）、`SHADOW_MD`（8px blur，用于卡片/面板）、`SHADOW_LG`（16px blur，用于模态对话框/悬浮层）。每级阴影 SHALL 使用 `QGraphicsDropShadowEffect` 实现，颜色为半透明黑色。

#### Scenario: 卡片使用中等阴影
- **WHEN** 卡片组件初始化
- **THEN** 卡片应用 `SHADOW_MD`（8px blur），呈现适度的浮起效果

#### Scenario: 模态对话框使用大阴影
- **WHEN** 设置面板（QDialog）打开
- **THEN** 对话框应用 `SHADOW_LG`（16px blur），呈现强烈的浮起效果

### Requirement: 字重令牌体系
系统 SHALL 定义字重令牌：`WEIGHT_REGULAR`（400）、`WEIGHT_MEDIUM`（500）、`WEIGHT_SEMIBOLD`（600）、`WEIGHT_BOLD`（700）。标题类文本 SHALL 使用 `WEIGHT_SEMIBOLD` 或更高，正文使用 `WEIGHT_REGULAR`，强调数据使用 `WEIGHT_BOLD`。

#### Scenario: 利润数字使用粗体
- **WHEN** 利润金额显示在仪表盘
- **THEN** 金额数字使用 `WEIGHT_BOLD`（700），与周围文本形成强烈对比

### Requirement: 圆角令牌体系
系统 SHALL 定义统一的圆角令牌：`RADIUS_SM`（4px，用于按钮/输入框/徽章）、`RADIUS_MD`（8px，用于卡片）、`RADIUS_LG`（12px，用于大型容器/对话框）。所有组件 SHALL 引用这些令牌而非硬编码数值。

#### Scenario: 统一组件圆角
- **WHEN** 按钮和卡片同时显示
- **THEN** 按钮使用 `RADIUS_SM`（4px），卡片使用 `RADIUS_MD`（8px），形成一致且有层次的圆角体系

### Requirement: 间距令牌增强
系统 SHALL 在现有间距令牌基础上增加 `XXXL`（48px）间距等级。利润卡片与下方卡片之间 SHALL 使用 `XL`（24px）间距。同级卡片之间 SHALL 使用 `LG`（16px）间距。卡片内部标题与内容之间 SHALL 使用 `MD`（12px）间距。

#### Scenario: 卡片间距层级
- **WHEN** 利润卡片和额度卡片在页面中排列
- **THEN** 利润卡片下方留有 24px 间距，额度卡片与告警卡片之间留有 16px 间距
