"""任务流模板数据模型。"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TemplateStep:
    """模板步骤。

    Attributes:
        system: 目标系统（browser、ide、terminal 等）
        action: 执行动作
        parameters: 参数配置
        condition: 执行条件（if_success、if_failure）
        input_from: 输入数据来源（从上下文读取的键）
        output_to: 输出数据目标（保存到上下文的键）
        continue_on_error: 失败时是否继续执行
    """

    system: str
    action: str
    parameters: dict[str, Any] = field(default_factory=dict)
    condition: str | None = None
    input_from: str | None = None
    output_to: str | None = None
    continue_on_error: bool = False


@dataclass
class TaskFlowTemplate:
    """任务流模板。

    Attributes:
        name: 模板名称
        description: 模板描述
        intent_types: 适用的意图类型列表
        steps: 任务步骤列表
        parameters: 模板级参数定义
    """

    name: str
    description: str
    intent_types: list[str]
    steps: list[TemplateStep]
    parameters: dict[str, Any] = field(default_factory=dict)

    def matches_intent(self, intent_type: str) -> bool:
        """检查模板是否匹配指定意图。

        Args:
            intent_type: 意图类型

        Returns:
            是否匹配
        """
        return intent_type in self.intent_types
