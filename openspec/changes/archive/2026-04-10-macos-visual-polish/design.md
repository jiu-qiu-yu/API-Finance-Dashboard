## Context

API Chancellor 是一个 PyQt6 (PySide6) 桌面应用，为中转站长提供每日利润监控。上一轮改造完成了 S3 布局重构和令牌体系升级，但外观仍偏"企业后台"风格。用户要求向 macOS 原生设计风格靠拢，同时保持品牌一致性。

**品牌 Logo 分析：**
- Logo 位于 `logo/logo.webp`（91KB）和 `logo/logo.png`（1.1MB）
- 设计：电路板纹理构成的 "C" 字母 + "API CHANCELLOR" 文字
- 色彩：海军蓝 `#2c3e50` + 金色 `#c8a84e` 渐变
- 气质：科技感、专业、精密

**约束条件：**
- 纯 PySide6 原生样式（QSS + QGraphicsDropShadowEffect），不引入第三方 UI 框架
- 最小窗口 960×700px，Windows 平台
- `QGraphicsDropShadowEffect` 不能用在顶级窗口（QDialog/QMessageBox）上，否则全黑
- Logo 使用 webp 格式（PySide6 原生支持）

## Goals / Non-Goals

**Goals:**
- 视觉风格从"企业后台"转变为"macOS 原生桌面应用"质感
- 品牌 Logo 自然集成（窗口图标 + 界面展示）
- 卡片具有"浮空"质感（无边框 + 极淡阴影 + 大圆角）
- 充足的留白和呼吸感
- 修复告警弹窗全黑 bug

**Non-Goals:**
- 不做暗黑模式
- 不做自定义窗口边框/标题栏（使用系统原生标题栏）
- 不引入动画/过渡效果（仅保留已有的 hover 和 collapsible）
- 不改变数据层/引擎层逻辑

## Decisions

### Decision 1: 色彩系统 — 暖灰白 + Logo 品牌色

**选择：** 从 Logo 提取品牌色系，搭配 macOS 暖灰白背景

**色彩映射表：**
```
用途           当前值              新值               理由
─────────────────────────────────────────────────────────────
窗口背景       #f0f2f5 (冷灰)     #f5f5f7 (暖灰白)   Apple 经典背景
卡片背景       #fafbfc (灰白)     #ffffff (纯白)      纯净浮空感
卡片边框       #e0e0e0 (可见)     transparent         靠阴影分层
主色调         #3498db (扁平蓝)   #2c3e50 (Logo 海军蓝) 品牌一致
主色调 hover   #2980b9            #1a252f              更深
强调色         无                  #c8a84e (Logo 金色)  品牌点缀
文字主色       #2c3e50            #1d1d1f (近纯黑)     更清晰
文字次色       #7f8c8d            #86868b (Apple 灰)   更柔和
分隔线         #e8ecef            #e5e5ea (Apple 灰)   标准
```

**理由：** 用品牌色替代通用蓝色，同时保持 macOS 的中性灰白底色。金色作为强调色用于特殊元素（如利润正值的趋势箭头、Logo 旁文字），不过度使用。

### Decision 2: 卡片风格 — 无边框浮空

**选择：**
```
属性          当前值                    新值
─────────────────────────────────────────────
背景色        #fafbfc                   #ffffff
边框          1px solid #e0e0e0         无 (transparent)
圆角          8px                       14px
阴影          blur(8px) offset(0,2) α40 blur(24px) offset(0,4) α8
内边距        16px                      24px
```

**理由：** Apple 卡片的核心是"无边框 + 大模糊极淡阴影"创造的浮空感。`blur(24)` + `α8` 产生若有若无的柔和阴影。

### Decision 3: 按钮 — 胶囊形

**选择：**
- 主要按钮：`border-radius: 20px`、`background: #2c3e50`(海军蓝)、`color: white`、`padding: 12px 28px`
- 次要按钮：`border-radius: 20px`、`background: transparent`、`border: 1px solid #e5e5ea`、`padding: 12px 28px`
- 危险按钮：`border-radius: 20px`、`background: transparent`、`border: 1px solid #e74c3c`、`color: #e74c3c`

**理由：** 胶囊形（大圆角）是 macOS 的标志性按钮形态。主色用品牌海军蓝而非通用蓝色。

### Decision 4: 表格 — 极简列表 + 卡片包裹

**选择：**
- 表格外部包裹在白色大圆角卡片中（与告警侧栏视觉一致）
- 表头：去背景色，仅用 `TEXT_SECONDARY` 小字 + 极淡底部分隔线
- 行高：36px → 44px
- 交替行色：关闭或极淡 `#fafafa`
- 行分隔线：每行底部 1px `#f0f0f0` 极淡线
- 徽章：圆角从 4px → 12px（胶囊形）
- 进度条：圆角从 4px → 6px

**理由：** macOS 列表是极简风，像"干净的文字列表"而非"数据表格"。卡片包裹让表格与侧栏视觉层级一致。

### Decision 5: 阴影系统 — 大模糊极低透明度

**选择：**
```
级别     当前                         新值
──────────────────────────────────────────────────────
SM      blur(2) offset(0,1) α25     blur(4) offset(0,1) α6
MD      blur(8) offset(0,2) α40     blur(24) offset(0,4) α8
LG      blur(16) offset(0,4) α60    blur(40) offset(0,8) α12
```

**理由：** Apple 阴影的秘诀是"大模糊半径 + 极低透明度 = 柔和浮起感"。当前阴影偏重偏暗，产生"贴在纸面"而非"浮在空中"的感觉。

### Decision 6: 间距系统 — 拉大呼吸感

**选择：**
```
位置              当前      新值
──────────────────────────────────
窗口边距          16px     24px
卡片内边距        16px     24px
利润卡片 ↔ 底区   24px     28px
侧栏 ↔ 表格      16px     16px (不变)
表格行高          36px     44px
按钮 padding      10px 30px  12px 28px
```

**理由：** macOS 的核心视觉特征之一就是"充裕留白"。目前偏紧凑，通过统一加大间距获得呼吸感。

### Decision 7: Logo 集成方式

**选择：**
1. **窗口图标**：使用 `logo/logo.webp` 设置 `setWindowIcon`
2. **利润卡片标题区**：在"今日盈利"标题左侧放置缩小版 Logo（32×32px），标题改为带品牌感的排版

**理由：** 窗口图标是最基本的品牌集成。卡片内 Logo 让界面有品牌辨识度但不过度。不在标题栏自绘（避免跨平台兼容问题）。

### Decision 8: 弹窗 bug 修复

**选择：** 移除 `main_window.py` 中 `_show_alert_popup` 的 `msg_box.setGraphicsEffect(...)` 和 `msg_box.setStyleSheet(...)` 调用。使用系统原生 `QMessageBox.warning()` 静态方法。

**理由：** `QGraphicsDropShadowEffect` 在顶级窗口（QDialog/QMessageBox）上会导致全黑渲染。这是 Qt 的已知限制。对话框阴影由操作系统窗口管理器提供。

## Risks / Trade-offs

- **[视觉变化幅度大]** 从"企业后台"到"macOS原生"是风格跨越 → **缓解：** 保持功能完全不变，只改视觉层
- **[品牌色作为主按钮色]** 海军蓝 `#2c3e50` 比标准蓝色更深沉，可能对比度不够 → **缓解：** 按钮字色用纯白确保可读性
- **[无边框卡片依赖阴影]** 如果系统/GPU 渲染阴影异常，卡片边界不可见 → **缓解：** 保持卡片背景纯白 vs 窗口暖灰白的色差作为 fallback
- **[Logo webp 格式]** PySide6 6.6+ 原生支持 webp，但低版本可能不支持 → **缓解：** 同目录有 `logo.png` 备用
