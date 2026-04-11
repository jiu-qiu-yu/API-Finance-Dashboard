## Context

API Finance Dashboard 是一个基于 PySide6 的桌面应用，当前通过 `pip install` + CLI 命令启动。项目依赖 PySide6（Qt GUI）、Playwright（浏览器自动化）、Plyer（系统通知）。Playwright 比较特殊——它需要独立的浏览器二进制文件（Chromium ~150MB+），这对打包策略有重大影响。

项目即将在 GitHub 开源，需要让非技术用户也能"下载 → 安装 → 使用"。

## Goals / Non-Goals

**Goals:**
- 生成 Windows 平台可独立运行的 .exe 安装包
- 用户无需安装 Python 环境即可使用
- GitHub Actions 自动构建，push tag 时自动发布 Release
- 安装包包含开始菜单快捷方式、卸载程序
- 合理处理 Playwright 浏览器依赖

**Non-Goals:**
- macOS / Linux 打包（后续迭代）
- 自动更新机制（后续迭代）
- 应用商店分发（Microsoft Store 等）
- 代码签名证书（开源项目初期不需要）

## Decisions

### 1. 打包工具：PyInstaller

**选择**: PyInstaller
**备选**: cx_Freeze, Nuitka, briefcase

**理由**:
- PyInstaller 对 PySide6 支持最成熟，社区生态最大
- 支持 `--onedir` 模式，适合后续用 Inno Setup 打包
- Nuitka 虽然性能更好，但编译时间长、配置复杂，不适合 CI
- briefcase（BeeWare）对 Playwright 这类复杂依赖支持不够好

### 2. 安装程序生成：Inno Setup

**选择**: Inno Setup
**备选**: NSIS, WiX Toolset, 直接分发 zip

**理由**:
- Inno Setup 脚本简洁、文档完善、输出体积小
- 自动生成卸载程序、开始菜单快捷方式、桌面图标
- 在 GitHub Actions 中通过 Chocolatey 安装即可使用
- NSIS 语法更复杂；WiX 面向企业场景过重；zip 缺乏用户体验

### 3. Playwright 浏览器处理策略：首次启动下载

**选择**: 不将 Playwright 浏览器打入安装包，首次启动时检测并引导下载
**备选**: 将浏览器二进制文件打入安装包

**理由**:
- Chromium 二进制 ~150MB+，打入安装包会导致体积膨胀到 400MB+
- 浏览器版本需要与 Playwright 版本严格匹配，打包进去容易过期
- 首次启动时运行 `playwright install chromium`，用进度对话框提示用户
- 检测系统已安装的 Chrome/Edge 作为备选（项目已有 `browser_detector.py`）

### 4. CI/CD：GitHub Actions + tag 触发

**选择**: GitHub Actions，通过 `v*` tag 触发构建
**理由**:
- 项目已托管 GitHub，无需额外 CI 服务
- `windows-latest` runner 预装 Python，可直接构建
- 使用 `softprops/action-gh-release` 自动上传安装包到 Release

### 5. PyInstaller 打包模式：onedir

**选择**: `--onedir`（目录模式）而非 `--onefile`（单文件模式）
**理由**:
- onefile 启动时需解压到临时目录，启动慢 5-10 秒
- onedir 配合 Inno Setup 安装后，启动速度与原生应用一致
- PySide6 的 Qt 插件在 onedir 模式下更稳定

## Risks / Trade-offs

- **[Playwright 首次下载失败]** → 提供清晰的错误提示和重试按钮；检测本地已有的 Chrome/Edge 作为降级方案
- **[安装包体积较大 ~100-150MB]** → PySide6 + Python runtime 体积不可避免；使用 UPX 压缩可缩减 20-30%
- **[杀毒软件误报]** → PyInstaller 打包的 exe 常被误报；README 中说明，后续可考虑代码签名
- **[Playwright 版本锁定]** → pyproject.toml 中锁定 Playwright 版本，确保浏览器兼容性
- **[Windows Defender SmartScreen 警告]** → 无代码签名时不可避免；README 中提供说明
