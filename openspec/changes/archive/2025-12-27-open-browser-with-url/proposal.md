# 变更：打开浏览器并访问指定网址

## 为什么

当前 UI-Agent 系统主要专注于 IDE 内部的自动化操作，但用户在实际工作流程中经常需要：

1. 查阅在线文档和参考资料
2. 搜索技术问题的解决方案
3. 访问 API 文档、GitHub 仓库等资源
4. 快速打开特定的开发工具网页（如 CI/CD 平台、监控面板）

目前系统无法直接控制浏览器打开指定网址，用户需要手动切换应用并输入网址，这打断了自动化工作流程的连贯性。

## 变更内容

- 新增 `BrowserLauncher` 类：封装浏览器启动和 URL 打开功能
- 新增 `open_browser_with_url(url: str, browser: str)` 方法：打开指定浏览器并访问网址
- 新增 `open_default_browser(url: str)` 方法：使用系统默认浏览器打开网址
- 集成到 `IDEController`：添加 `open_browser()` 公共方法
- 更新 `config/operations/pycharm.yaml`：添加 `open_browser` 操作配置
- 新增自然语言命令别名：打开浏览器、访问网址、在浏览器中打开等
- 新增浏览器相关异常类：`BrowserNotFoundError`、`BrowserLaunchError`

## 影响

### 受影响规范
- 新增规范：`browser-launch`（浏览器启动功能）

### 受影响代码
- `src/automation/`（新增）或 `src/browser/`（新增）：浏览器启动模块
- `src/controller/ide_controller.py`：添加浏览器启动功能集成
- `config/operations/pycharm.yaml`：添加打开浏览器操作

### 依赖变更
- **新增依赖**：`webbrowser`（Python 标准库，无需安装）
- **可选依赖**：无（使用 Python 内置 webbrowser 模块）

### 风险与影响
- **跨平台兼容性**：webbrowser 模块支持 Windows、macOS、Linux，但不同系统的默认浏览器行为可能不同
- **浏览器依赖**：功能依赖于系统已安装浏览器
- **URL 验证**：需要验证 URL 格式，避免安全问题

### 缓解措施
1. 添加 URL 格式验证
2. python.org
2. 提供友好的错误提示
3. 支持多种常见浏览器的指定打开
4. 记录操作日志便于调试

## 验收标准

1. 能够通过"打开浏览器访问 https://example.com"命令打开浏览器并访问指定网址
2. 能够使用系统默认浏览器打开网址
3. 能够指定浏览器类型（Chrome、Edge、Firefox 等）打开网址
4. 当浏览器未安装时给出清晰的错误提示
5. 当 URL 格式错误时给出友好的错误提示
6. 单元测试覆盖核心浏览器启动功能
7. 支持常用自然语言命令格式

## 后续工作

1. 支持浏览器操作自动化（点击、滚动等）
2. 支持多标签页管理
3. 支持浏览器书签操作
