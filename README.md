# API Finance Dashboard

**API站长自动化财务看板** - 基于 RPA 的本地轻量级监控软件。

自动采集多个 API 平台的余额、消费数据，实时计算利润，余额不足时发送桌面告警通知。

## 安全声明

- 本项目完全开源，代码公开透明，接受社区审查
- 所有数据均存储在本地 SQLite 数据库（`~/.api-finance-dashboard/data.db`），**不会上传任何网页数据到任何服务器**
- 浏览器自动化操作全部在本机执行，采集的财务数据不会离开你的电脑
- 无后台联网、无数据回传、无第三方追踪，安全可靠

## 功能特性

- 多平台余额/消费自动采集（支持自定义 CSS 选择器和正则提取）
- 主站 vs 上游消耗对比，自动计算净利润
- 余额低于阈值时弹窗告警 + 系统通知
- 支持多币种（USD/CNY）自动换算
- 定时巡检，实时掌握财务状态
- 本地浏览器复用（Chrome/Edge），无需额外登录

## 安装

### 方式一：下载安装包（推荐）

前往 [Releases](https://github.com/jiu-qiu-yu/API_Chancellor/releases) 页面，下载最新版本的 `API-Finance-Dashboard-Setup-x.x.x.exe`，双击安装即可。

**系统要求：**
- Windows 10/11 (64-bit)
- Google Chrome 或 Microsoft Edge 浏览器

> Windows Defender SmartScreen 可能会显示安全警告，点击"更多信息" → "仍要运行"即可。这是因为安装包没有代码签名证书，不影响安全性。

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/jiu-qiu-yu/API_Chancellor.git
cd API_Chancellor

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .

# 启动应用
api-finance-dashboard
```

## 上游接入

欢迎各 API 站长接入上游，自建 MAX 号池！

我的站点：**[jiuqiuai.top](https://www.jiuqiuai.top)**

如果你是 API 中转站长，可以用本工具监控上游消耗和余额，轻松管理多平台财务。欢迎来接入当上游，互惠共赢。

## 本地构建安装包

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行构建脚本（需要 Inno Setup）
python scripts/build.py

# 仅构建 exe（不生成安装程序）
python scripts/build.py --skip-installer
```

## 发布新版本

1. 更新 `pyproject.toml` 中的 `version`
2. 提交并推送
3. 创建并推送 tag：
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
4. GitHub Actions 将自动构建安装包并创建 Release

## 技术栈

- **GUI**: PySide6 (Qt for Python)
- **浏览器自动化**: Playwright
- **数据库**: SQLite（纯本地存储）
- **系统通知**: Plyer
- **打包**: PyInstaller + Inno Setup
- **CI/CD**: GitHub Actions

## License

[MIT](LICENSE)
