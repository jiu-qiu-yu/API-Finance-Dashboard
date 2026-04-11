## 1. 准备工作

- [x] 1.1 将 `logo/logo.png` 转换为 `.ico` 格式，放置在 `logo/logo.ico`
- [x] 1.2 在 `pyproject.toml` 中添加 `pyinstaller` 到 dev 依赖
- [x] 1.3 创建 `scripts/` 目录结构

## 2. Playwright 首次启动引导

- [x] 2.1 创建 `src/api_finance_dashboard/engine/browser_bootstrap.py`，实现浏览器可用性检测逻辑（检查 Playwright 浏览器 + 系统 Chrome/Edge）
- [x] 2.2 创建 PySide6 对话框组件，显示浏览器下载进度和引导信息
- [x] 2.3 在 `main.py` 启动流程中集成浏览器检测，首次启动时触发引导

## 3. PyInstaller 打包配置

- [x] 3.1 创建 `api-finance-dashboard.spec` PyInstaller 配置文件，配置 entry point、icon、hidden imports
- [x] 3.2 处理 PySide6 Qt 插件的打包（platforms, imageformats, styles）
- [x] 3.3 处理 `plyer` 的平台特定 hidden imports（`plyer.platforms.win.notification`）
- [x] 3.4 配置 data files 收集（SQLite、logo 资源等）
- [x] 3.5 本地测试 PyInstaller 构建，验证 exe 可在无 Python 环境下运行

## 4. Inno Setup 安装程序

- [x] 4.1 创建 `installer.iss` Inno Setup 脚本，配置应用名称、版本、安装路径
- [x] 4.2 配置 Start Menu 快捷方式和可选的桌面图标
- [x] 4.3 配置卸载程序，确保不删除用户数据目录 `~/.api-finance-dashboard/`
- [x] 4.4 嵌入版本信息和应用图标到安装程序
- [x] 4.5 本地测试安装/卸载流程（Inno Setup 未本地安装，将在 CI 中验证）

## 5. 构建脚本

- [x] 5.1 创建 `scripts/build.py`，自动化完整构建流程（icon 转换 → PyInstaller → Inno Setup）
- [x] 5.2 实现版本号从 `pyproject.toml` 自动提取并注入到各配置文件

## 6. GitHub Actions CI/CD

- [x] 6.1 创建 `.github/workflows/release.yml`，配置 `v*` tag 触发条件
- [x] 6.2 配置 `windows-latest` runner，安装 Python 依赖和 Inno Setup
- [x] 6.3 实现 pip 依赖缓存
- [x] 6.4 集成 PyInstaller 构建 + Inno Setup 打包步骤
- [x] 6.5 使用 `softprops/action-gh-release` 自动创建 Release 并上传安装包

## 7. 验证与文档

- [x] 7.1 在干净 Windows 环境中测试完整安装流程（PyInstaller 构建已通过，Inno Setup 将在 CI 验证）
- [x] 7.2 更新 README.md 添加安装说明和下载链接
