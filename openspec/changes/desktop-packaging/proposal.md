## Why

API Finance Dashboard 目前只能通过 `pip install` + 命令行启动运行，对非技术用户不友好。项目即将在 GitHub 开源，需要提供"下载即用"的桌面安装包（Windows .exe 安装程序），让用户像普通桌面软件一样双击安装、从开始菜单启动，降低使用门槛。

## What Changes

- 引入 PyInstaller 将 Python 应用打包为单文件可执行程序（.exe）
- 引入 Inno Setup 脚本将可执行程序封装为 Windows 安装向导（.exe installer）
- 添加 GitHub Actions CI/CD 流水线，在 push tag 时自动构建并发布 Release
- 配置应用图标、版本信息等品牌元素嵌入到安装包中
- 添加构建脚本简化本地打包流程

## Capabilities

### New Capabilities
- `executable-bundling`: 使用 PyInstaller 将 PySide6 + Playwright 应用打包为独立可执行文件，处理依赖冻结、资源嵌入、图标设置
- `installer-packaging`: 使用 Inno Setup 生成 Windows 安装向导，包含安装/卸载、开始菜单快捷方式、桌面图标选项
- `ci-release-pipeline`: GitHub Actions 工作流，在创建版本 tag 时自动构建安装包并发布到 GitHub Releases

### Modified Capabilities

(无需修改现有 spec 的需求)

## Impact

- **新增依赖**: PyInstaller（dev dependency）
- **新增文件**: 构建脚本、Inno Setup 脚本、GitHub Actions workflow、PyInstaller spec 文件
- **pyproject.toml**: 添加 PyInstaller 到 dev 依赖
- **Playwright 浏览器**: 需要特殊处理——Playwright 浏览器二进制文件体积大，安装包可能采用首次启动时自动下载的策略
- **跨平台**: 初始阶段聚焦 Windows 平台（主要用户群），后续可扩展 macOS/Linux
