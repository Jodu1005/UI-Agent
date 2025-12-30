"""意图识别数据模型。"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntentParameter:
    """意图参数定义。

    Attributes:
        name: 参数名称
        type: 参数类型
        description: 参数描述
        required: 是否必需
        examples: 示例值列表
        pattern: 正则表达式模式（可选）
    """

    name: str
    type: str
    description: str
    required: bool = True
    examples: list[str] = field(default_factory=list)
    pattern: str | None = None


@dataclass
class IntentDefinition:
    """意图定义。

    Attributes:
        name: 意图名称
        type: 意图类型（single-system 或 composite）
        description: 意图描述
        system: 目标系统（单系统意图）
        systems: 目标系统列表（组合意图）
        parameters: 参数定义映射
    """

    name: str
    type: str
    description: str
    system: str | None = None
    systems: list[str] = field(default_factory=list)
    parameters: dict[str, IntentParameter] = field(default_factory=dict)


@dataclass
class Intent:
    """识别到的意图。

    Attributes:
        type: 意图类型
        parameters: 提取的参数字典
        confidence: 识别置信度（0-1）
        raw_message: 原始用户消息
        reasoning: 识别理由
    """

    type: str
    parameters: dict[str, Any]
    confidence: float
    raw_message: str
    reasoning: str = ""

    def is_valid(self) -> bool:
        """检查意图是否有效。

        Returns:
            置信度是否大于等于阈值
        """
        return self.confidence >= 0.85


@dataclass
class IntentMatchResult:
    """意图匹配结果。

    Attributes:
        intent: 匹配到的意图（如果没有匹配则为 None）
        confidence: 置信度
        all_matches: 所有可能的意图匹配（按置信度排序）
    """

    intent: Intent | None
    confidence: float
    all_matches: list[Intent] = field(default_factory=list)

    @property
    def has_match(self) -> bool:
        """是否有匹配的意图。"""
        return self.intent is not None and self.intent.is_valid()
