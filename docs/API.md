# API 参考文档

本文档提供 UI-Agent 核心模块的 API 参考。

## 目录

- [命令解析器](#命令解析器-commandparser)
- [视觉定位器](#视觉定位器-visuallocator)
- [自动化执行器](#自动化执行器-automationexecutor)
- [配置管理器](#配置管理器-configmanager)
- [IDE 控制器](#ide-控制器-idecontroller)
- [数据模型](#数据-models)

---

## 命令解析器 (CommandParser)

**模块**: `src.parser.command_parser.CommandParser`

### 初始化

```python
from src.parser.command_parser import CommandParser
from src.config.config_manager import ConfigManager

config = ConfigManager("config/main.yaml")
parser = CommandParser(config)
```

### 方法

#### parse()

```python
def parse(self, text: str) -> ParsedCommand
```

解析自然语言命令。

**参数**:
- `text` (str): 用户输入的自然语言命令

**返回**: `ParsedCommand` - 解析后的命令对象

**异常**:
- `ValueError`: 命令格式无效或无法识别

**示例**:
```python
result = parser.parse("双击 main.py")
# ParsedCommand(
#     intent="file_operation",
#     action="double_click_file",
#     parameters={"filename": "main.py"},
#     confidence=0.95,
#     context={}
# )
```

---

## 视觉定位器 (VisualLocator)

**模块**: `src.locator.visual_locator.VisualLocator`

### 初始化

```python
from src.locator.visual_locator import VisualLocator
from src.config.schema import APIConfig

api_config = APIConfig(
    zhipuai_api_key="your_api_key",
    model="glm-4v-flash"
)
locator = VisualLocator(api_config)
```

### 方法

#### locate()

```python
async def locate(
    self,
    operation: OperationConfig,
    params: dict[str, Any]
) -> dict[str, UIElement]
```

定位 UI 元素。

**参数**:
- `operation` (OperationConfig): 操作配置
- `params` (dict): 命令参数

**返回**: `dict[str, UIElement]` - 元素索引到元素的映射

**异常**:
- `ElementNotFoundError`: 无法找到目标元素
- `APIError`: API 调用失败

**示例**:
```python
elements = await locator.locate(operation, {"filename": "main.py"})
# {"0": UIElement(...)}
```

#### set_calibrator()

```python
def set_calibrator(self, calibrator: CoordinateCalibrator) -> None
```

设置坐标校准器。

**参数**:
- `calibrator` (CoordinateCalibrator): 校准器实例

---

### CoordinateCalibrator

**类**: `src.locator.visual_locator.CoordinateCalibrator`

#### 初始化

```python
from src.locator.visual_locator import CoordinateCalibrator

calibrator = CoordinateCalibrator(offset_x=36, offset_y=46)
```

#### 方法

##### calibrate()

```python
def calibrate(self, bbox: tuple[int, int, int, int]) -> tuple[int, int, int, int]
```

应用坐标偏移。

**参数**:
- `bbox` (tuple): 原始边界框 (x1, y1, x2, y2)

**返回**: `tuple` - 校准后的边界框

**示例**:
```python
calibrated = calibrator.calibrate((100, 200, 300, 400))
# (136, 246, 336, 446)
```

##### from_config()

```python
@staticmethod
def from_config(offset: list[int] | None) -> CoordinateCalibrator
```

从配置创建校准器。

**参数**:
- `offset` (list | None): 偏移量配置 [x, y]

**返回**: `CoordinateCalibrator`

---

## 自动化执行器 (AutomationExecutor)

**模块**: `src.automation.executor.AutomationExecutor`

### 初始化

```python
from src.automation.executor import AutomationExecutor

executor = AutomationExecutor(
    default_timeout=5.0,
    max_retries=3,
    action_delay=0.2
)
```

### 方法

#### execute()

```python
def execute(self, action: Action, element: UIElement | None) -> bool
```

执行单个操作。

**参数**:
- `action` (Action): 要执行的操作
- `element` (UIElement | None): 目标元素

**返回**: `bool` - 是否成功

**示例**:
```python
from src.automation.actions import Action, ActionType

action = Action(type=ActionType.CLICK, target="0")
success = executor.execute(action, element)
```

#### execute_sequence()

```python
def execute_sequence(
    self,
    actions: list[Action],
    elements: dict[str, UIElement]
) -> bool
```

执行操作序列。

**参数**:
- `actions` (list[Action]): 操作列表
- `elements` (dict): 元素映射

**返回**: `bool` - 是否全部成功

---

## 配置管理器 (ConfigManager)

**模块**: `src.config.config_manager.ConfigManager`

### 初始化

```python
from src.config.config_manager import ConfigManager

manager = ConfigManager(
    config_path="config/main.yaml",
    enable_hot_reload=True,
    reload_interval=5.0
)
```

### 方法

#### load_config()

```python
def load_config(self, path: str | None = None) -> MainConfig
```

加载配置文件。

**参数**:
- `path` (str | None): 配置文件路径

**返回**: `MainConfig` - 主配置对象

**异常**:
- `FileNotFoundError`: 配置文件不存在
- `ValueError`: 配置格式错误

#### get_operation()

```python
def get_operation(self, name: str) -> OperationConfig | None
```

获取操作配置。

**参数**:
- `name` (str): 操作名称或别名

**返回**: `OperationConfig | None` - 操作配置，不存在则返回 None

#### list_operations()

```python
def list_operations(self) -> list[str]
```

列出所有可用操作。

**返回**: `list[str]` - 操作名称列表

#### reload_now()

```python
def reload_now(self) -> bool
```

立即重新加载配置。

**返回**: `bool` - 是否成功

#### stop_hot_reload()

```python
def stop_hot_reload(self) -> None
```

停止配置热更新。

---

## IDE 控制器 (IDEController)

**模块**: `src.controller.ide_controller.IDEController`

### 初始化

```python
from src.controller.ide_controller import IDEController
from src.config.config_manager import ConfigManager

config_manager = ConfigManager("config/main.yaml")
controller = IDEController(config_manager)
```

### 方法

#### execute_command()

```python
async def execute_command(self, command: str) -> ExecutionResult
```

执行用户命令。

**参数**:
- `command` (str): 自然语言命令

**返回**: `ExecutionResult` - 执行结果

**示例**:
```python
result = await controller.execute_command("双击 main.py")
if result.success:
    print("操作成功")
else:
    print(f"操作失败: {result.error}")
```

#### stop()

```python
def stop(self) -> None
```

停止当前执行。

---

## 数据 Models

### ParsedCommand

**模块**: `src.models.command.ParsedCommand`

解析后的命令模型。

```python
@dataclass
class ParsedCommand:
    intent: str           # 操作意图
    action: str           # 操作名称
    parameters: dict      # 操作参数
    confidence: float     # 置信度 (0-1)
    context: dict         # 上下文信息

    def validate(self) -> bool:
        """验证命令是否有效"""
```

### UIElement

**模块**: `src.models.element.UIElement`

UI 元素模型。

```python
@dataclass
class UIElement:
    element_type: str              # 元素类型
    description: str               # 元素描述
    bbox: tuple[int, int, int, int]  # 边界框 (x1, y1, x2, y2)
    confidence: float              # 置信度
    metadata: dict | None = None   # 元数据

    @property
    def center(self) -> tuple[int, int]:
        """计算中心点坐标"""
```

### ExecutionResult

**模块**: `src.models.result.ExecutionResult`

执行结果模型。

```python
@dataclass
class ExecutionResult:
    status: ExecutionStatus    # 执行状态
    message: str               # 结果消息
    data: dict | None = None   # 附加数据
    error: str | None = None   # 错误信息

    @property
    def success(self) -> bool:
        """是否成功"""
```

### ExecutionStatus

**模块**: `src.models.result.ExecutionStatus`

执行状态枚举。

```python
class ExecutionStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

### Action

**模块**: `src.automation.actions.Action`

操作模型。

```python
@dataclass
class Action:
    type: ActionType                    # 操作类型
    target: str | None = None           # 目标元素索引
    parameters: dict | None = None      # 操作参数
    timeout: float = 5.0                # 超时时间
    retry: int = 3                      # 重试次数
```

### ActionType

**模块**: `src.automation.actions.ActionType`

操作类型枚举。

```python
class ActionType(Enum):
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    SHORTCUT = "shortcut"
    WAIT = "wait"
    DRAG = "drag"
```

### OperationConfig

**模块**: `src.config.schema.OperationConfig`

操作配置模型。

```python
@dataclass
class OperationConfig:
    name: str                          # 操作名称
    aliases: list[str]                 # 别名列表
    intent: str                        # 操作意图
    description: str                   # 操作描述
    visual_prompt: str                 # 视觉提示词
    actions: list[ActionConfig]        # 操作序列
    preconditions: list[str] | None    # 前置条件
    post_check: PostCheckConfig | None # 后置检查
    requires_confirmation: bool        # 是否需要确认
    risk_level: str                    # 风险等级
```

### MainConfig

**模块**: `src.config.schema.MainConfig`

主配置模型。

```python
@dataclass
class MainConfig:
    system: SystemConfig       # 系统配置
    ide: IDEConfig            # IDE 配置
    api: APIConfig            # API 配置
    automation: AutomationConfig  # 自动化配置
    safety: SafetyConfig      # 安全配置
```

## 使用示例

### 完整示例

```python
import asyncio
from src.controller.ide_controller import IDEController
from src.config.config_manager import ConfigManager

async def main():
    # 初始化
    config_manager = ConfigManager("config/main.yaml")
    controller = IDEController(config_manager)

    # 执行命令
    result = await controller.execute_command("双击 main.py")

    # 处理结果
    if result.success:
        print(f"成功: {result.message}")
    else:
        print(f"失败: {result.error}")

    # 清理
    controller.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### 单独使用模块

```python
# 只使用命令解析器
from src.parser.command_parser import CommandParser
from src.config.config_manager import ConfigManager

config = ConfigManager("config/main.yaml")
parser = CommandParser(config)

cmd = parser.parse("跳转到第 50 行")
print(cmd.action)        # "go_to_line"
print(cmd.parameters)    # {"line_number": 50}
```

```python
# 只使用视觉定位器
from src.locator.visual_locator import VisualLocator
from src.config.schema import APIConfig
from PIL import Image

api_config = APIConfig(
    zhipuai_api_key="your_key",
    model="glm-4v-flash"
)
locator = VisualLocator(api_config)

# 截图
screenshot = Image.open("screenshot.png")

# 定位
elements = await locator.locate_with_screenshot(
    screenshot=screenshot,
    prompt="找到文件 main.py"
)
```

```python
# 只使用执行器
from src.automation.executor import AutomationExecutor
from src.automation.actions import Action, ActionType

executor = AutomationExecutor()
action = Action(type=ActionType.SHORTCUT, parameters={"keys": ["ctrl", "s"]})

executor.execute(action, None)
```

## 错误处理

### 常见异常

| 异常 | 说明 | 处理方式 |
|------|------|----------|
| `ValueError` | 命令格式无效 | 提示用户重新输入 |
| `ElementNotFoundError` | 无法找到元素 | 检查截图和提示词 |
| `APIError` | API 调用失败 | 检查网络和密钥 |
| `TimeoutError` | 操作超时 | 增加超时时间 |

### 错误处理示例

```python
try:
    result = await controller.execute_command(command)
except ValueError as e:
    print(f"命令格式错误: {e}")
    # 提示用户正确的格式
except ElementNotFoundError as e:
    print(f"无法找到元素: {e}")
    # 建议用户检查 IDE 状态
except APIError as e:
    print(f"API 调用失败: {e}")
    # 检查网络连接
```

## 类型提示

所有模块都提供完整的类型提示，可用于 IDE 自动补全和类型检查。

```python
from src.parser.command_parser import CommandParser
from src.models.command import ParsedCommand

parser: CommandParser = CommandParser(config)
result: ParsedCommand = parser.parse("打开 main.py")
```
