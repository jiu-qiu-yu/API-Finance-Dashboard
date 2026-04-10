## ADDED Requirements

### Requirement: macOS 极简列表风格表格
站点健康总览表格 SHALL 采用 macOS 极简列表风格：
- 表格外部 SHALL 包裹在白色大圆角(14px)卡片容器中
- 表头 SHALL 无背景色，使用 `#86868b` 灰色小字(12px) + `SEMIBOLD` 字重，底部 1px `#e5e5ea` 分隔线
- 行高 SHALL 为 44px（从 36px 加大）
- 交替行色 SHALL 极淡或关闭（若使用，交替色为 `#fafafa`）
- 每行底部 SHALL 有 1px `#f0f0f0` 极淡分隔线
- Hover 效果保持 `#f5f5f7`

#### Scenario: 表格整体视觉
- **WHEN** 用户查看站点表格
- **THEN** 表格看起来像 macOS 原生列表（Finder 列表视图风格）
- **AND** 表格被白色圆角卡片包裹
- **AND** 表头与数据行之间仅有极淡分隔线

### Requirement: 胶囊形状态徽章
状态列的徽章 SHALL 使用胶囊形圆角（`border-radius: 12px`），替换当前的 4px 方角。

#### Scenario: 徽章形状
- **WHEN** 表格显示状态徽章
- **THEN** 徽章为胶囊形（两端圆弧）

### Requirement: 进度条圆角加大
额度比列的迷你进度条 SHALL 使用 6px 圆角（从 4px 加大）。

#### Scenario: 进度条形状
- **WHEN** 上游站点行显示额度比进度条
- **THEN** 进度条两端呈圆弧形，更柔和
