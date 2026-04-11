<div align="center">

<img src="logo/logo.png" alt="API Chancellor" width="180" />

# API Chancellor

**API 站长自动化财务看板**

基于 RPA 的本地轻量级监控工具 — 自动采集、实时算利、智能告警

[![Release](https://img.shields.io/github/v/release/jiu-qiu-yu/API_Chancellor?style=flat-square&color=blue)](https://github.com/jiu-qiu-yu/API_Chancellor/releases)
[![License](https://img.shields.io/github/license/jiu-qiu-yu/API_Chancellor?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078d4?style=flat-square&logo=windows&logoColor=white)](https://github.com/jiu-qiu-yu/API_Chancellor/releases)

[下载安装](#-快速开始) · [功能介绍](#-核心功能) · [接入上游](#-上游接入--站长推荐) · [开发指南](#-开发者指南)

</div>

---

## 这是什么？

你是 API 中转站长吗？每天需要登录多个平台查余额、算利润、盯消耗？

**API Chancellor** 帮你自动完成这一切。它在你的电脑本地运行，自动打开浏览器、采集各平台数据、计算净利润，余额不足时还会弹窗提醒。

> 一句话：**打开软件，一键巡检，利润一目了然。**

---

## 🔐 安全声明

| | 说明 |
|---|---|
| **完全开源** | 代码公开透明，接受社区审查 |
| **数据纯本地** | 所有数据存储在本机 SQLite 数据库，**不会上传任何数据到任何服务器** |
| **无后台联网** | 无数据回传、无第三方追踪、无遥测 |
| **免密登录** | 复用你已登录的 Chrome/Edge 浏览器会话，软件本身不存储任何密码 |

---

## ✨ 核心功能

### 多平台数据自动采集

- 内置 **new-api**、**sub2api**、**cap** 面板预设，开箱即用
- 支持自定义 CSS 选择器 + 正则表达式，适配任意面板
- 4 层智能提取策略：CSS 选择器 → 锚点定位 → 关键词匹配 → 正则兜底

### 利润实时计算

- 主站消耗 vs 上游消耗自动对比
- 多币种自动换算（USD / CNY）
- 净利润一目了然，告别手动算账

### 智能告警通知

- 余额低于设定阈值时自动弹出系统通知
- 支持自定义告警阈值，不同站点独立配置

### 定时巡检

- 设定巡检间隔，自动周期采集
- 实时掌握各平台财务状态

---

## 📦 快速开始

### 下载安装（推荐）

前往 **[Releases](https://github.com/jiu-qiu-yu/API_Chancellor/releases)** 页面，下载最新 `API-Finance-Dashboard-Setup-x.x.x.exe`，双击安装即可。

**系统要求：**
- Windows 10 / 11（64 位）
- 已安装 Google Chrome 或 Microsoft Edge

> **提示：** Windows SmartScreen 可能弹出安全警告，点击「更多信息」→「仍要运行」即可。这是因为安装包暂无代码签名证书，不影响安全性。

### 从源码运行

```bash
git clone https://github.com/jiu-qiu-yu/API_Chancellor.git
cd API_Chancellor

python -m venv .venv
.venv\Scripts\activate

pip install -e .
api-finance-dashboard
```

### 使用流程

```
1. 安装并打开 API Chancellor
2. 在设置面板添加你的站点（选择面板预设或自定义选择器）
3. 配置主站 / 上游关系及告警阈值
4. 点击「巡检」→ 自动采集数据、计算利润、检查余额
```

---

## 🤝 上游接入 & 站长推荐

> 欢迎各位 API 中转站长接入上游，自建 MAX 号池！

### 👉 [jiuqiuai.top](https://www.jiuqiuai.top)

| 优势 | 说明 |
|------|------|
| **稳定可靠** | 长期运营，服务稳定 |
| **价格透明** | 合理定价，互惠共赢 |
| **技术支持** | 接入问题随时沟通 |

如果你正在寻找靠谱的上游渠道，欢迎访问 **[jiuqiuai.top](https://www.jiuqiuai.top)** 了解详情。

使用 API Chancellor 可以轻松监控你的上游消耗与余额，接入后一键掌控全局。

---

## 🛠 开发者指南

### 技术栈

| 组件 | 技术 |
|------|------|
| GUI | PySide6 (Qt for Python) |
| 浏览器自动化 | Playwright |
| 数据库 | SQLite（纯本地存储） |
| 系统通知 | Plyer |
| 打包 | PyInstaller + Inno Setup |
| CI/CD | GitHub Actions |

### 开发环境搭建

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行单个测试
pytest tests/test_presets.py -v
```

### 构建安装包

```bash
# 完整构建（exe + 安装程序，需要 Inno Setup）
python scripts/build.py

# 仅构建 exe
python scripts/build.py --skip-installer
```

### 发布新版本

```bash
# 1. 更新 pyproject.toml 中的 version
# 2. 提交并推送代码
# 3. 创建 tag，GitHub Actions 自动构建并发布
git tag v0.2.0
git push origin v0.2.0
```

---

## 📄 License

[MIT](LICENSE) — 自由使用、修改和分发。

---

<div align="center">

**[⬇ 立即下载](https://github.com/jiu-qiu-yu/API_Chancellor/releases)** · **[🌐 jiuqiuai.top](https://www.jiuqiuai.top)**

Made with ❤️ for API 站长们

</div>
