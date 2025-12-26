# 变更：激活窗口功能

## 为什么

当前项目在执行 IDE 自动化操作时，假定目标窗口（如 PyCharm）已经处于活动状态。然而在实际使用中：

1. 用户可能同时打开多个应用程序
2. PyCharm 窗口可能被最小化或被其他窗口遮挡
3. 在执行任何 UI 操作前，需要确保目标窗口处于活动状态

这导致以下问题：
- 自动化操作可能作用于错误的窗口
- 需要手动切换窗口，影响自动化体验的连贯性
- 某些操作（如截图）可能获取到错误的内容

## 变更内容

- 新增 `WindowManager` 类：提供跨平台窗口管理功能
- 新增 `activate_window(title: str)` 方法：通过窗口标题激活窗口
- 新增 `activate_by_process(process_name: str)` 方法：通过进程名激活窗口
- 新增 `find_window(title: str)` 方法：根据标题查找窗口
- 新增 `find_by_process_name(process_name: str)` 方法：根据进程名查找窗口
- 集成到 `IDEController`：添加 `activate_window()` 公共方法
- 更新 `config/operations/pycharm.yaml`：添加 `activate_window` 操作配置
- 新增自然语言命令别名：激活窗口、切换到 PyCharm、activate window
- 新增窗口相关异常类：`WindowNotFoundError`、`WindowActivationError`

## 影响

### 受影响规范
- 新增规范：`window-activation`（窗口激活功能）

### 受影响代码
- `src/window/window_manager.py`（新增）
- `src/window/exceptions.py`（新增）
- `src/controller/ide_controller.py`（添加窗口管理器集成）
- `config/operations/pycharm.yaml`（添加激活窗口操作）
- `config/schema.py`（可选：添加窗口配置 schema）

### 依赖变更
- 新增依赖：`pygetwindow` >= 0.0.9（已在 uv.lock 中）
- 可选依赖：`pywin32`（Windows 平台增强功能）
- 可选依赖：`psutil`（进程查找功能）

### 风险与影响
- **平台依赖**：主要依赖 Windows API，其他平台可能需要不同实现
- **窗口标题变化**：不同版本的 IDE 窗口标题格式可能不同
- **权限问题**：某些情况下可能无法激活其他应用的窗口

### 缓解措施
1. 使用 `pygetwindow` 作为跨平台抽象层
2. 提供配置化的窗口标题匹配模式
3. 添加错误处理和用户友好的提示信息
