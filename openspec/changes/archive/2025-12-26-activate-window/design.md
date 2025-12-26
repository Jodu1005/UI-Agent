# 窗口激活功能设计文档

## 1. 架构设计

### 1.1 模块结构

```
src/
├── window/
│   ├── __init__.py
│   ├── window_manager.py       # 窗口管理核心模块
│   └── exceptions.py           # 窗口相关异常定义
├── controller/
│   └── ide_controller.py       # 集成窗口激活功能
└── config/
    ├── schema.py               # 添加窗口配置 schema
    └── operations/
        └── pycharm.yaml        # 添加激活窗口操作
```

### 1.2 核心类设计

#### WindowManager 类

```python
class WindowManager:
    """跨平台窗口管理器。"""

    def __init__(self) -> None:
        """初始化窗口管理器。"""

    def find_window(self, title: str, exact_match: bool = False) -> Optional[BaseWindow]:
        """根据标题查找窗口。

        Args:
            title: 窗口标题（支持部分匹配）
            exact_match: 是否精确匹配

        Returns:
            窗口对象，未找到返回 None
        """

    def activate_window(self, title: str) -> bool:
        """激活指定标题的窗口。

        Args:
            title: 窗口标题

        Returns:
            是否成功激活

        Raises:
            WindowNotFoundError: 窗口未找到
            WindowActivationError: 激活失败
        """

    def is_window_minimized(self, title: str) -> bool:
        """检查窗口是否最小化。

        Args:
            title: 窗口标题

        Returns:
            是否最小化
        """

    def restore_window(self, title: str) -> bool:
        """恢复最小化的窗口。

        Args:
            title: 窗口标题

        Returns:
            是否成功恢复
        """

    def list_windows(self, title_filter: str = "") -> list[str]:
        """列出所有窗口标题。

        Args:
            title_filter: 标题过滤关键词

        Returns:
            窗口标题列表
        """
```

#### 异常类设计

```python
class WindowError(Exception):
    """窗口操作基础异常。"""

class WindowNotFoundError(WindowError):
    """窗口未找到异常。"""

class WindowActivationError(WindowError):
    """窗口激活失败异常。"""
```

## 2. Windows 平台实现细节

### 2.1 窗口激活机制

在 Windows 平台上，窗口激活需要处理以下情况：

1. **正常窗口**：直接调用 `activate()` 方法
2. **最小化窗口**：先恢复（`restore()`），再激活
3. **被遮挡窗口**：激活会自动将其置于前台

### 2.2 pygetwindow API 使用

```python
import pygetwindow as gw

# 查找窗口
windows = gw.getWindowsWithTitle(title_pattern)
if not windows:
    raise WindowNotFoundError(f"未找到窗口: {title_pattern}")

window = windows[0]

# 激活窗口
if window.isMinimized:
    window.restore()

window.activate()
```

### 2.3 窗口标题匹配策略

PyCharm 窗口标题格式示例：
- `PyCharm - [项目名称] - [文件名]`
- `PyCharm - [项目名称]`

匹配策略：
1. 尝试精确匹配
2. 尝试包含匹配（如包含 "PyCharm"）
3. 使用正则表达式模式匹配

## 3. 配置设计

### 3.1 操作配置（pycharm.yaml）

```yaml
operations:
  - name: activate_window
    aliases: [激活窗口, 切换到 PyCharm, activate window, 切换窗口]
    intent: window_management
    description: 将 PyCharm 窗口置于前台

    # 窗口配置
    window_patterns:
      - "PyCharm"
      - ".*PyCharm.*"

    actions:
      - type: activate_window
        window_pattern: "PyCharm"
        timeout: 2.0

    requires_confirmation: false
```

### 3.2 主配置扩展

在 `config/schema.py` 中添加窗口配置：

```python
class WindowConfig(BaseModel):
    """窗口配置。"""

    enable_activation: bool = True
    default_title_pattern: str = "PyCharm"
    activation_timeout: float = 2.0
    restore_minimized: bool = True
```

## 4. IDE 控制器集成

### 4.1 初始化

```python
class IDEController:
    def __init__(self, config_path: str, api_key: str) -> None:
        # ... 现有初始化代码 ...

        # 初始化窗口管理器
        from src.window.window_manager import WindowManager

        self._window_manager = WindowManager()
```

### 4.2 公共 API

```python
def activate_window(self, title: str) -> ExecutionResult:
    """激活指定窗口。

    Args:
        title: 窗口标题

    Returns:
        执行结果
    """
    try:
        success = self._window_manager.activate_window(title)
        if success:
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                message=f"窗口已激活: {title}",
            )
        else:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"窗口激活失败: {title}",
            )
    except WindowNotFoundError as e:
        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            message="窗口未找到",
            error=str(e),
        )
```

### 4.3 便捷方法

```python
def activate_pycharm(self) -> ExecutionResult:
    """激活 PyCharm 窗口。"""
    pattern = self.config.window.default_title_pattern
    return self.activate_window(pattern)
```

## 5. 测试策略

### 5.1 单元测试

使用 `unittest.mock` 模拟 `pygetwindow`：

```python
from unittest.mock import Mock, patch

def test_activate_window_success():
    """测试成功激活窗口。"""
    with patch('pygetwindow.getWindowsWithTitle') as mock_get:
        mock_window = Mock()
        mock_window.isMinimized = False
        mock_get.return_value = [mock_window]

        manager = WindowManager()
        result = manager.activate_window("PyCharm")

        assert result is True
        mock_window.activate.assert_called_once()
```

### 5.2 集成测试

在实际环境中测试（标记为 `integration` 和 `windows`）：

```python
@pytest.mark.integration
@pytest.mark.skipif(not sys.platform == "win32", reason="Windows only")
def test_activate_real_pycharm_window():
    """测试激活真实的 PyCharm 窗口。"""
    manager = WindowManager()
    # 假设测试环境中有 PyCharm 运行
    result = manager.activate_window("PyCharm")
    # 验证结果...
```

## 6. 错误处理

### 6.1 错误场景

| 场景 | 处理方式 |
|------|----------|
| 窗口未找到 | 抛出 `WindowNotFoundError`，返回友好提示 |
| 激活失败 | 抛出 `WindowActivationError`，记录详细日志 |
| 多个匹配窗口 | 选择第一个，记录警告日志 |
| 权限不足 | 返回错误，提示用户检查权限 |

### 6.2 用户友好的错误信息

```
错误：无法找到窗口 "PyCharm"
提示：请确保 PyCharm 正在运行，窗口标题包含 "PyCharm"
可用窗口：Visual Studio Code, Chrome, Microsoft Edge
```

## 7. 性能考虑

1. **窗口查找缓存**：缓存窗口列表，避免频繁查询
2. **超时机制**：激活操作设置超时，避免长时间阻塞
3. **异步选项**：未来可考虑异步激活窗口

## 8. 未来扩展

### 8.1 多平台支持

```python
# 平台检测
if sys.platform == "win32":
    from src.window.windows_manager import WindowsWindowManager as WindowManager
elif sys.platform == "darwin":
    from src.window.macos_manager import MacOSWindowManager as WindowManager
else:
    from src.window.linux_manager import LinuxWindowManager as WindowManager
```

### 8.2 高级功能

- 窗口位置和大小管理
- 多显示器支持
- 窗口分组和标签页管理
- 窗口快照和恢复
