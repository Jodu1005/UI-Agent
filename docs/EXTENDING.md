# 扩展指南

本指南介绍如何扩展 UI-Agent 系统的功能。

## 目录

- [添加新操作](#添加新操作)
- [支持新 IDE](#支持新-ide)
- [自定义定位策略](#自定义定位策略)
- [自定义执行动作](#自定义执行动作)
- [插件开发](#插件开发)

## 添加新操作

最简单的扩展方式是在配置文件中添加新操作。

### 步骤

1. 打开 IDE 操作配置文件
2. 添加新的操作定义
3. 测试新操作

### 示例：添加"折叠代码"操作

编辑 `config/operations/pycharm.yaml`：

```yaml
operations:
  # ... 现有操作 ...

  - name: fold_code
    aliases: [折叠代码, fold code, 折叠]
    intent: edit
    description: 折叠当前代码块

    actions:
      - type: shortcut
        keys: ["ctrl", "shift", "."]
        timeout: 0.5
```

使用新操作：
```bash
python -m src.main "折叠代码"
```

### 复杂操作：多步骤操作

```yaml
- name: refactor_extract_variable
    aliases: [提取变量, extract variable]
    intent: refactor
    description: 将选中的表达式提取为变量

    visual_prompt: |
      在截图中找到：
      1. 当前编辑器窗口
      2. 确认有选中的文本

    preconditions:
      - has_selection  # 需要选中文本

    actions:
      - type: shortcut
        keys: ["ctrl", "alt", "v"]
        timeout: 1.0

      - type: wait_for_dialog
        dialog_title: "Extract Variable"

      - type: type
        text: "{var_name}"  # 用户提供的变量名
        delay: 0.1

      - type: shortcut
        keys: ["enter"]
        timeout: 1.0

    post_check:
      type: verify_refactoring
      expected_pattern: "{var_name} = "

    requires_confirmation: true
    risk_level: medium
```

## 支持 IDE

添加对新 IDE 的支持需要创建新的操作配置文件。

### 步骤

1. 创建新的操作配置文件
2. 定义 IDE 特定的操作和快捷键
3. 更新主配置指向新文件

### 示例：添加 VS Code 支持

#### 1. 创建配置文件

创建 `config/operations/vscode.yaml`：

```yaml
ide: vscode
version: ">=1.80"

operations:
  - name: open_file
    aliases: [打开文件, open file, 打开]
    intent: file_operation
    description: 在 VS Code 中打开指定文件

    actions:
      - type: shortcut
        keys: ["ctrl", "p"]
        timeout: 1.0

      - type: type
        text: "{filename}"
        delay: 0.1

      - type: shortcut
        keys: ["enter"]
        timeout: 1.0

  - name: go_to_line
    aliases: [跳转到行, go to line, 跳转]
    intent: navigation
    description: 跳转到指定行

    actions:
      - type: shortcut
        keys: ["ctrl", "g"]
        timeout: 1.0

      - type: type
        text: "{line_number}"
        delay: 0.1

      - type: shortcut
        keys: ["enter"]
        timeout: 1.0

  # ... 添加更多操作 ...
```

#### 2. 更新主配置

编辑 `config/main.yaml`：

```yaml
ide:
  name: vscode
  version: ">=1.80"
  config_path: config/operations/vscode.yaml
```

## 自定义定位策略

当默认的视觉定位不够准确时，可以实现自定义定位策略。

### 继承 VisualLocator

```python
from src.locator.visual_locator import VisualLocator
from src.models.element import UIElement
from typing import Any

class MyCustomLocator(VisualLocator):
    """自定义定位器"""

    async def locate(
        self,
        operation: OperationConfig,
        params: dict[str, Any]
    ) -> dict[str, UIElement]:
        """使用自定义策略定位"""

        # 1. 尝试默认策略
        try:
            return await super().locate(operation, params)
        except ElementNotFoundError:
            pass

        # 2. 使用自定义策略
        if operation.name == "my_special_operation":
            return await self._locate_custom(params)

        # 3. 如果都失败，抛出异常
        raise ElementNotFoundError(f"无法定位: {operation.name}")

    async def _locate_custom(self, params: dict) -> dict[str, UIElement]:
        """自定义定位逻辑"""

        # 示例：使用颜色定位
        screenshot = self.screenshot_capture.capture_full_screen()

        # 找到特定颜色的元素
        elements = self._find_by_color(screenshot, target_color=(255, 0, 0))

        return {"0": elements[0]}

    def _find_by_color(self, image, target_color):
        """通过颜色查找元素"""
        # 实现颜色定位逻辑
        pass
```

### 使用自定义定位器

```python
# 在 IDEController 中使用
from src.locator.visual_locator import VisualLocator
from my_custom_locator import MyCustomLocator

# 替换默认定位器
controller.locator = MyCustomLocator(controller.config.api_config)
```

## 自定义执行动作

添加新的动作类型需要扩展 `ActionType` 和 `AutomationExecutor`。

### 步骤

1. 扩展 `ActionType` 枚举
2. 在 `AutomationExecutor` 中实现处理逻辑
3. 在配置中使用新动作

### 示例：添加"滚动"动作

#### 1. 扩展 ActionType

编辑 `src/automation/actions.py`：

```python
class ActionType(Enum):
    # ... 现有动作 ...
    SCROLL = "scroll"  # 新增
```

#### 2. 实现处理逻辑

编辑 `src/automation/executor.py`：

```python
class AutomationExecutor:
    # ... 现有代码 ...

    def _execute_action(self, action: Action, element: UIElement | None) -> bool:
        # ... 现有 case 语句 ...

        elif action.type == ActionType.SCROLL:
            return self._execute_scroll(action, element)

        # ... 其他 ...

    def _execute_scroll(self, action: Action, element: UIElement | None) -> bool:
        """执行滚动操作"""
        params = action.parameters or {}
        direction = params.get("direction", "down")  # up, down, left, right
        amount = params.get("amount", 5)  # 滚动次数

        try:
            if direction == "up":
                pyautogui.scroll(amount)
            elif direction == "down":
                pyautogui.scroll(-amount)
            elif direction == "left":
                pyautogui.hscroll(amount)
            elif direction == "right":
                pyautogui.hscroll(-amount)

            logger.info(f"滚动: {direction} {amount}")
            return True
        except Exception as e:
            logger.error(f"滚动失败: {e}")
            return False
```

#### 3. 在配置中使用

```yaml
- name: scroll_to_bottom
    aliases: [滚动到底部, scroll to bottom]
    intent: navigation
    description: 滚动到文件底部

    actions:
      - type: shortcut
        keys: ["ctrl", "end"]
        timeout: 0.5

      # 或使用自定义滚动动作
      - type: scroll
        parameters:
          direction: down
          amount: 100
        timeout: 1.0
```

## 插件开发

插件系统允许在不修改核心代码的情况下扩展功能。

### 插件结构

```
plugins/
├── my_plugin/
│   ├── __init__.py
│   ├── plugin.py       # 插件主文件
│   ├── operations.yaml # 操作配置
│   └── README.md       # 插件文档
```

### 插件接口

```python
# plugins/my_plugin/plugin.py
from abc import ABC, abstractmethod

class Plugin(ABC):
    """插件基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass

    @abstractmethod
    def initialize(self, controller):
        """初始化插件"""
        pass

    @abstractmethod
    def shutdown(self):
        """关闭插件"""
        pass
```

### 示例插件

```python
# plugins/my_plugin/plugin.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.controller.ide_controller import IDEController

class TimestampPlugin:
    """时间戳插件 - 插入当前时间戳"""

    name = "timestamp"
    version = "1.0.0"

    def initialize(self, controller: "IDEController"):
        """注册新操作"""
        self.controller = controller

        # 注册操作
        controller.parser.register_operation(
            name="insert_timestamp",
            aliases=["插入时间戳", "timestamp"],
            handler=self._insert_timestamp
        )

    def shutdown(self):
        """清理资源"""
        pass

    async def _insert_timestamp(self, params: dict):
        """插入时间戳"""
        from datetime import datetime

        # 生成时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 输入时间戳
        await self.controller.executor.execute(
            Action(type=ActionType.TYPE, parameters={"text": timestamp}),
            None
        )

        return ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            message=f"已插入时间戳: {timestamp}"
        )
```

### 加载插件

编辑 `config/main.yaml`：

```yaml
plugins:
  enabled:
    - timestamp
    - my_plugin
  paths:
    - plugins/
```

## 测试扩展

### 单元测试

创建 `tests/plugins/test_my_plugin.py`：

```python
import pytest
from plugins.my_plugin.plugin import TimestampPlugin

@pytest.mark.unit
class TestTimestampPlugin:
    """时间戳插件测试"""

    def test_plugin_properties(self):
        """测试插件属性"""
        plugin = TimestampPlugin()
        assert plugin.name == "timestamp"
        assert plugin.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_insert_timestamp(self):
        """测试插入时间戳"""
        plugin = TimestampPlugin()
        # Mock controller
        result = await plugin._insert_timestamp({})
        assert result.status == ExecutionStatus.SUCCESS
```

### 集成测试

```python
@pytest.mark.integration
async def test_plugin_with_controller():
    """测试插件与控制器集成"""
    from src.controller.ide_controller import IDEController
    from src.config.config_manager import ConfigManager

    config = ConfigManager("config/main.yaml")
    controller = IDEController(config)

    # 加载插件
    plugin = TimestampPlugin()
    plugin.initialize(controller)

    # 执行插件命令
    result = await controller.execute_command("插入时间戳")
    assert result.success
```

## 最佳实践

### 1. 配置优先

优先使用配置文件而非代码：
- ✅ 在 YAML 中定义新操作
- ❌ 直接修改 Python 代码

### 2. 复用现有组件

- 使用现有的 `ActionType`
- 扩展而非重写 `VisualLocator`
- 组合现有的 `Action`

### 3. 错误处理

提供清晰的错误信息：

```python
try:
    element = await self.locator.locate(operation, params)
except ElementNotFoundError:
    return ExecutionResult(
        status=ExecutionStatus.FAILED,
        message=f"无法找到 {params.get('filename')}",
        error="ELEMENT_NOT_FOUND"
    )
```

### 4. 文档化

为扩展添加文档：
- README 说明用途
- API 文档说明接口
- 示例代码展示用法

### 5. 测试覆盖

- 单元测试：测试核心逻辑
- 集成测试：测试与系统交互
- 视觉测试：验证 UI 定位

## 发布扩展

### 分发配置

将配置文件提交到项目的 `config/operations/` 目录。

### 分发插件

1. 在项目根目录创建 `plugins/` 目录
2. 将插件放入其中
3. 在配置中启用插件

### 贡献回项目

1. Fork 项目仓库
2. 创建功能分支
3. 提交扩展代码
4. 发起 Pull Request

## 贡献指南

### 代码规范

- 遵循 PEP 8 编码规范
- 使用类型提示
- 添加文档字符串
- 编写单元测试

### 提交流程

1. 描述扩展的功能
2. 提供使用示例
3. 说明测试覆盖
4. 更新相关文档

### 审查标准

- 代码质量
- 文档完整性
- 测试覆盖率
- 向后兼容性
