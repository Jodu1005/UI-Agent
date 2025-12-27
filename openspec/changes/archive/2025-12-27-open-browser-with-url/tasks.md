# 任务列表

## 阶段 1：核心功能实现

### 1.1 创建浏览器启动模块
- [x] 创建 `src/browser/` 目录结构
- [x] 创建 `src/browser/__init__.py` 模块
- [x] 创建 `src/browser/exceptions.py` 模块（异常类定义）
- [x] 创建 `src/browser/browser_launcher.py` 模块
- [x] 实现 `BrowserLauncher` 类
- [x] 实现 `open_default_browser(url: str)` 方法：使用默认浏览器打开网址
- [x] 实现 `open_browser(url: str, browser: str)` 方法：使用指定浏览器打开网址
- [x] 实现 `validate_url(url: str)` 方法：验证 URL 格式
- [x] 实现 `normalize_url(url: str)` 方法：标准化 URL（自动添加协议）
- [x] 添加错误处理和日志记录

### 1.2 集成到 IDE 控制器
- [x] 在 `IDEController` 中添加 `_browser_launcher` 成员
- [x] 在 `IDEController.__init__()` 中初始化 `BrowserLauncher`
- [x] 添加 `open_browser(url: str, browser: str = None)` 公共方法

### 1.3 配置浏览器打开操作
- [x] 在 `config/operations/pycharm.yaml` 中添加 `open_browser` 操作
- [x] 定义操作别名：打开浏览器、访问网址、在浏览器中打开等
- [x] 配置命令解析规则以提取 URL 和浏览器类型

## 阶段 2：测试与验证

### 2.1 单元测试
- [x] 创建 `tests/unit/test_browser_launcher.py`
- [x] 测试 URL 验证功能
- [x] 测试 URL 标准化功能
- [x] 测试使用默认浏览器打开网址（使用 mock）
- [x] 测试使用指定浏览器打开网址（使用 mock）
- [x] 测试无效 URL 格式的处理
- [x] 测试浏览器未找到的场景
- [x] 测试异常处理和错误信息

### 2.2 集成测试
- [ ] 创建 `tests/integration/test_browser_launch_integration.py`
- [ ] 测试在真实环境中打开默认浏览器
- [ ] 测试在真实环境中打开指定浏览器（如果可用）
- [ ] 测试与 IDE 控制器的集成

### 2.3 手动验证
- [ ] 在实际环境中测试"打开浏览器访问 https://www.baidu.com"
- [ ] 在实际环境中测试"在 Chrome 中打开 https://github.com"
- [ ] 在实际环境中测试"访问 https://www.python.org"
- [ ] 测试无效 URL 的错误处理
- [ ] 测试未安装浏览器的错误处理

## 阶段 3：文档与完善

### 3.1 更新文档
- [x] 在 README.md 中添加浏览器打开功能说明
- [x] 在 COMMANDS.md 中添加浏览器打开命令示例
- [x] 更新 INSTALL.md 中的依赖说明（无需新依赖）

### 3.2 代码质量
- [x] 运行 black 格式化代码
- [x] 运行 ruff 检查代码
- [x] 运行 mypy 类型检查
- [x] 确保测试覆盖率 >= 80% (实际: 88%)

## 任务依赖关系

```
1.1 ───> 1.2 ───> 1.3
                │
                └──> 2.1 ───> 2.2 ───> 2.3
                                          │
                                          └──> 3.1 ───> 3.2
```

## 可并行任务

- 2.1（单元测试）可与 1.3（配置操作）并行开发
- 3.1（文档）可与 2.3（手动验证）并行进行

## 验收检查点

每个阶段完成后应满足：
1. **阶段 1**：代码编译通过，基本功能可用 ✅
2. **阶段 2**：所有测试通过，功能验证完毕（单元测试完成 ✅，集成测试和手动验证待完成）
3. **阶段 3**：文档完整，代码质量检查通过 ✅

## 实现说明

### 支持的浏览器类型

系统应支持以下常见浏览器：
- **默认浏览器**：使用系统默认浏览器
- **Chrome**：Google Chrome（chrome.exe）
- **Edge**：Microsoft Edge（msedge.exe）
- **Firefox**：Mozilla Firefox（firefox.exe）
- **Safari**：macOS 上的 Safari（仅 macOS）
- **Opera**：Opera 浏览器（opera.exe）

### URL 处理规则

1. **自动添加协议**：如果 URL 不以 `http://` 或 `https://` 开头，自动添加 `https://`
2. **URL 验证**：使用正则表达式验证 URL 格式
3. **URL 编码**：正确处理 URL 中的特殊字符

### 错误处理

1. **无效 URL**：返回清晰的错误信息和格式示例
2. **浏览器未找到**：列出可用的浏览器
3. **打开失败**：记录详细日志并返回友好提示

### 日志记录

- 记录每次浏览器打开操作
- 记录浏览器类型和 URL
- 记录操作结果（成功/失败）
