## Context

Sub2API 面板抓取在 `/dashboard` 页面上的余额和今日消费均失败（显示 0），定位到两个根因：

1. **`_validate_value` 过于严格**：限制小数位 ≤ 2，但 API 消费金额如 `$0.0015` 有 4 位小数 → 有效值被拒绝
2. **CSS 选择器偏差**：当前选择器未精确匹配 Sub2API Dashboard 的实际 DOM 结构

Sub2API Dashboard DOM 结构中关键卡片：
- **余额卡片**（emerald）：`<p class="text-xl font-bold text-emerald-600 dark:text-emerald-400">$1.67</p>`
- **今日消费卡片**（purple）：值在 `<span class="text-purple-600 dark:text-purple-400" title="实际">$0.0015</span>` 中，且同一卡片内有"总计"行也含 `text-purple-600` span

此外设置界面命名和交互存在可改进空间：窗口标题"设置"不够精准，添加/删除站点缺少合理的默认行为。

## Goals / Non-Goals

**Goals:**

- 修复金额验证函数，允许 API 消费金额常见的 4-6 位小数
- 修正 Sub2API CSS 选择器精确匹配 dashboard 上的余额和今日消费
- 将设置界面标题改为"配置"
- 优化添加站点时的表单清空和默认值逻辑
- 优化删除站点后的列表选中行为

**Non-Goals:**

- 不重写整个设置界面布局（仅调整标题和交互逻辑）
- 不修改 New API、CAP preset
- 不新增面板类型

## Decisions

### 1. 小数位限制放宽到 6 位

当前 `_validate_value` 检查 `exponent < -2` 即拒绝。API 消费金额精度通常为 4-6 位（如 `$0.0015`、`$0.000123`）。

**方案：将检查改为 `exponent < -6`**

理由：6 位小数覆盖所有常见 API 计费精度，同时仍能过滤掉明显错误的超高精度值。

### 2. Sub2API 今日消费选择器策略

今日消费卡片中有两个 `text-purple-600` span：
- 今日值：`<span class="text-purple-600" title="实际">$0.0015</span>`（在 `p.text-xl` 内）
- 总计值：`<span class="text-purple-600" title="实际">$3.3291</span>`（在 `p.text-xs` 内）

**方案：使用 `p.text-xl span.text-purple-600[title]` 限定在大号字体段落内**

配合 `title` 属性过滤掉"标准"价格的 span（标准价格的 span 类名不含 `text-purple-600`）。

### 3. Sub2API 余额选择器

余额值在：`<p class="text-xl font-bold text-emerald-600 dark:text-emerald-400">$1.67</p>`

**方案：使用 `p.text-emerald-600.text-xl` 匹配**

`font-bold` 可以省略以提高容错性。

### 4. 添加站点时清空表单

**方案：新增 `_clear_form()` 方法**，在点击"添加"按钮时先清空表单并设置合理默认值（面板类型默认 new-api、货币默认 USD、阈值默认 10），再让用户填写。

### 5. 删除站点后自动选中相邻项

**方案：删除后选中原位置的前一个项（如果存在），否则选中第一个**。避免删除后表单残留已删除站点的数据。

## Risks / Trade-offs

- **[风险] 放宽小数位限制可能接受意外值** → 缓解：6 位小数足够精确且仍有上限，配合 _MAX_VALID_VALUE 限制最大值
- **[风险] Sub2API DOM 结构版本更新后选择器失效** → 缓解：同时配置 anchor_rules 作为 Tier 2 后备，基于"余额"/"今日消费"文本匹配
- **[权衡] `title` 属性选择器依赖 Sub2API 前端实现** → 收益：精确区分"实际"和"标准"价格，降低误匹配风险
