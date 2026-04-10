## 0. Bug 修复（紧急）

- [x] 0.1 修复告警弹窗全黑：移除 `_show_alert_popup` 中的 `msg_box.setGraphicsEffect(...)` 和 `msg_box.setStyleSheet(...)`，改用 `QMessageBox.warning()` 静态方法

## 1. 色彩与阴影令牌升级 (styles.py)

- [x] 1.1 更新 `Colors` 类品牌色：`PRIMARY=#2c3e50`(Logo海军蓝)、`PRIMARY_HOVER=#1a252f`、新增 `ACCENT_GOLD=#c8a84e`(Logo金色)
- [x] 1.2 更新 `Colors` 类背景色：`BG_WINDOW=#f5f5f7`(暖灰白)、`BG_CARD=#ffffff`(纯白)、`CARD_BORDER=transparent`
- [x] 1.3 更新 `Colors` 类文字色：`TEXT_PRIMARY=#1d1d1f`、`TEXT_SECONDARY=#86868b`、`SEPARATOR=#e5e5ea`
- [x] 1.4 更新 `Shadows` 三级阴影参数：SM → `blur(4) offset(0,1) α6`、MD → `blur(24) offset(0,4) α8`、LG → `blur(40) offset(0,8) α12`
- [x] 1.5 更新 `BorderRadius`：新增 `XL=14`(卡片专用)、新增 `CAPSULE=20`(按钮胶囊)、新增 `BADGE=12`(徽章胶囊)、新增 `PROGRESS=6`(进度条)
- [x] 1.6 更新 `Spacing` 类：`WINDOW=24`(窗口边距)、`CARD_INNER=24`(卡片内边距)
- [x] 1.7 重写主按钮样式模板 `INSPECT_BTN_STYLE`：`#2c3e50` 海军蓝 + `border-radius:20px` 胶囊 + `padding:12px 28px`
- [x] 1.8 重写次按钮样式模板 `SETTINGS_BTN_STYLE`：透明底 + `1px solid #e5e5ea` + `border-radius:20px` 胶囊
- [x] 1.9 更新所有其他样式模板引用新令牌值

## 2. 卡片 macOS 化 (card_widget.py)

- [x] 2.1 去除卡片边框：`border: none`
- [x] 2.2 卡片圆角改为 `BorderRadius.XL`(14px)
- [x] 2.3 卡片阴影改用新的 `Shadows.create_md()` (blur24 α8)
- [x] 2.4 卡片内边距加大为 `Spacing.CARD_INNER`(24px)
- [x] 2.5 卡片背景改为纯白 `Colors.BG_CARD`(#ffffff)

## 3. 品牌 Logo 集成 (main_window.py)

- [x] 3.1 设置窗口图标：使用 `QIcon("logo/logo.webp")` 调用 `setWindowIcon`，失败时 fallback `logo/logo.png`
- [x] 3.2 利润卡片标题区集成 Logo：在"今日盈利"左侧添加 32×32 QLabel+QPixmap 展示 Logo，水平排列+垂直居中

## 4. 主窗口间距与弹窗修复 (main_window.py)

- [x] 4.1 窗口边距改为 `Spacing.WINDOW`(24px)
- [x] 4.2 利润卡片与底区间距改为 28px
- [x] 4.3 告警侧栏圆角确保使用 `BorderRadius.XL`(14px)
- [x] 4.4 修复 `_show_alert_popup`：移除 `setGraphicsEffect` 和自定义 `setStyleSheet`，改为 `QMessageBox.warning()` 静态调用

## 5. 表格极简化 (status_list.py)

- [x] 5.1 表格外部包裹 `CardWidget` 容器（白色+14px圆角+极淡阴影）
- [x] 5.2 表头去背景色：改为透明底 + `#86868b` 灰色文字 + 底部 1px `#e5e5ea` 分隔线
- [x] 5.3 行高从 36px → 44px
- [x] 5.4 交替行色改为极淡：`#fafafa` 或关闭交替色，改用每行底部 1px `#f0f0f0` 分隔线
- [x] 5.5 状态徽章圆角改为 `BorderRadius.BADGE`(12px) 胶囊形
- [x] 5.6 进度条圆角改为 `BorderRadius.PROGRESS`(6px)
- [x] 5.7 确保告急行浅红背景在新配色方案下仍醒目

## 6. 设置面板适配 (settings_panel.py)

- [x] 6.1 保存按钮改用海军蓝胶囊形（`INSPECT_BTN_STYLE` 或等效）
- [x] 6.2 删除/重置按钮改用危险胶囊形
- [x] 6.3 输入框焦点高亮色改为海军蓝 `#2c3e50`
- [x] 6.4 对话框背景色确保使用 `Colors.BG_CARD`(#ffffff)

## 7. 收尾验证

- [x] 7.1 全模块导入验证（`python -c "from ... import ..."`）
- [x] 7.2 运行全部单元测试确保无回归
- [ ] 7.3 启动应用视觉验证：卡片浮空感、按钮胶囊形、表格极简化、Logo 展示、告警弹窗正常
- [ ] 7.4 验证告警弹窗不再全黑
