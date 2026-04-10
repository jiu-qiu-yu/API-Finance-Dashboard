## Context

当前系统是一个 PySide6 桌面应用，通过 Playwright 自动化浏览器访问 API 管理面板网页，抓取今日消耗和余额数据，计算净利润。现有问题：

1. 站点配置中 MAIN 和 UPSTREAM 共用同一个 `url` 字段，但上游站点实际需要分别访问「使用日志页」和「数据看板页」
2. 浏览器 profile 需手动输入 `user-data-dir` 路径，普通用户难以找到
3. 面板预设只有 new-api、one-api、custom 三种，缺少当前主流面板
4. 抓取依赖单一 CSS 选择器 + 正则回退，容易被页面其他数值干扰

## Goals / Non-Goals

**Goals:**
- 上游站点支持双 URL（使用日志 + 数据看板），MAIN 站点保持单 URL
- 用户通过选择桌面浏览器快捷方式即可完成浏览器配置
- 内置 5+ 主流开源面板预设规则
- 通过锚点策略提升数据抓取准确性，减少误匹配

**Non-Goals:**
- 不支持同时使用多个浏览器 profile
- 不支持自动登录/密码管理
- 不构建面板预设的在线更新机制
- 不支持 Linux 桌面环境（当前仅 Windows + macOS）

## Decisions

### D1: 上游站点双 URL 数据模型

**选择**: 在 `SiteConfig` 新增 `dashboard_url: str | None` 字段

**理由**: MAIN 站点只需查看「今日消耗」，一个使用日志页面 URL 即可；UPSTREAM 站点需要同时查看「今日消耗」（使用日志页）和「剩余额度」（数据看板页），需要两个 URL。

- `url` 字段：始终指向使用日志页面（MAIN/UPSTREAM 通用），用于获取今日消耗
- `dashboard_url` 字段：仅 UPSTREAM 使用，指向数据看板页面，用于获取剩余额度

**替代方案**: 用 JSON 数组存多个 URL → 过于灵活，增加复杂度，不利于 UI 表达

**Migration**: 数据库添加 `dashboard_url TEXT` 列，默认 NULL。现有 UPSTREAM 站点的 `url` 继续用于消耗抓取，用户需手动补填 `dashboard_url`。

### D2: 浏览器快捷方式自动检测

**选择**: 解析桌面浏览器快捷方式文件自动提取配置

**实现方案**:
- **Windows**: 使用 PowerShell `COM` 对象解析 `.lnk` 文件，提取 `TargetPath` 和 `Arguments`（含 `--user-data-dir`），无需额外依赖
- **macOS**: 读取 `.app/Contents/Info.plist` 获取浏览器类型，推断默认 profile 路径（`~/Library/Application Support/Google/Chrome`）

**检测流程**:
1. 用户点击「选择浏览器」按钮，弹出文件选择对话框
2. Windows 过滤 `.lnk` 文件，macOS 过滤 `.app` 文件
3. 解析快捷方式 → 识别浏览器类型（Chrome/Edge/Chromium）
4. 推断或提取 `user-data-dir` 路径
5. 显示检测结果，用户确认

**替代方案**: 扫描注册表/系统已安装浏览器列表 → 无法区分多 profile 场景；需要 `pylnk3` 依赖 → PowerShell COM 零依赖更轻量

**回退**: 保留手动输入路径作为备用选项

### D3: 面板预设库扩展

**选择**: 扩展 `presets.py` 中的 `PANEL_PRESETS` 字典

**内置预设列表**（基于 GitHub Stars 和社区活跃度）:

| 面板名称 | GitHub 项目 | 特征 |
|---------|------------|------|
| New API | QuantumNous/new-api | 统一 AI 模型网关，OpenAI/Claude/Gemini 兼容 |
| One API | songquanpeng/one-api | LLM API 管理和 Key 分发系统 |
| One Hub | 基于 one-api 的增强分支 | one-api 生态衍生 |
| Chat Nio (CoAI) | Deeptrain-Community/chatnio | 下一代 AI 一站式解决方案，含计费系统 |
| Uni API | yym68686/uni-api | 统一 LLM API 管理，支持负载均衡 |
| Custom | - | 用户自定义选择器 |

**每个预设包含**:
- `consumption_selectors`: 消耗值 CSS 选择器列表（按优先级）
- `balance_selectors`: 余额值 CSS 选择器列表
- `consumption_keywords`: 消耗关键词元组
- `balance_keywords`: 余额关键词元组
- `anchor_rules`: 锚点定位规则（新增）

### D4: 锚点抓取策略（Anchor-Based Scraping）

**选择**: 三重验证定位机制

**问题分析**: 当前网页上可能同时出现多个金额数值（今日消耗、历史消耗、余额、充值金额等），简单 CSS 选择器或正则匹配无法确保定位正确。

**锚点策略**:

```
第1层：CSS 选择器精确定位
  ↓ 匹配失败
第2层：标签文本锚点 + DOM 邻近搜索
  ↓ 匹配失败  
第3层：关键词邻近度 + 数值格式校验（现有正则回退增强版）
```

**第2层「标签文本锚点」详细设计**:
- 在页面中搜索包含锚点文本（如"今日消耗"）的 DOM 元素
- 从该锚点元素出发，在 DOM 树中搜索相邻/子级的数值元素
- 搜索范围：同级兄弟节点、父节点的兄弟节点、最多向上3层
- 找到数值后进行格式校验（必须是有效货币数值）

**每个预设的锚点规则结构**:
```python
@dataclass(frozen=True)
class AnchorRule:
    target: str              # "consumption" 或 "balance"
    anchor_texts: tuple[str, ...]  # 锚点文本列表，如 ("今日消耗", "Today Usage")
    value_css: str | None    # 从锚点出发的相对 CSS 选择器
    max_dom_depth: int = 3   # DOM 搜索最大深度
```

**替代方案**: XPath 精确路径 → 页面结构变动时易失效，维护成本高

### D5: 测试抓取预览

**选择**: 在设置面板站点编辑表单中增加「测试抓取」按钮

**流程**:
1. 用户填写完 URL 和面板类型后，点击「测试抓取」
2. 系统打开浏览器访问目标页面
3. 按锚点策略执行抓取
4. 在对话框中展示：匹配到的消耗值、余额值、匹配方式（哪一层命中）
5. 用户确认数值正确后保存

## Risks / Trade-offs

**[面板预设需持续维护]** → 面板项目 UI 更新可能导致选择器失效。Mitigation: 三层回退策略确保至少关键词层能兜底；预设结构化便于用户在 UI 中微调。

**[快捷方式解析平台差异]** → Windows .lnk 和 macOS .app 解析逻辑完全不同。Mitigation: 分平台实现 + 保留手动输入回退。

**[数据库 migration]** → 新增字段需要更新 schema。Mitigation: `ALTER TABLE ADD COLUMN` 对 SQLite 安全，默认 NULL 不影响现有数据。

**[DOM 锚点搜索性能]** → 复杂页面可能搜索较慢。Mitigation: 限制最大搜索深度 (3层)，CSS 选择器命中则跳过锚点搜索。

**[测试抓取需要浏览器]** → 用户首次配置时浏览器可能未设置。Mitigation: 测试抓取按钮仅在浏览器已配置时可用，否则提示先完成浏览器配置。
