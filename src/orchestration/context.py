"""任务执行上下文。"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class StepExecutionResult:
    """步骤执行结果。

    Attributes:
        step_index: 步骤索引
        success: 是否成功
        output: 输出数据
        error: 错误信息
        duration: 执行时长（秒）
    """

    step_index: int
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration: float = 0.0


@dataclass
class ExecutionContext:
    """任务执行上下文。

    存储任务执行状态、步骤间传递的数据和执行历史。

    Attributes:
        shared_data: 共享数据字典
        step_results: 步骤执行结果列表
        current_step: 当前步骤索引
        status: 执行状态（pending、running、completed、failed）
        start_time: 开始时间
    """

    shared_data: dict[str, Any] = field(default_factory=dict)
    step_results: list[StepExecutionResult] = field(default_factory=list)
    current_step: int = 0
    status: str = "pending"
    start_time: datetime = field(default_factory=datetime.now)

    def get_data(self, key: str, default: Any = None) -> Any:
        """获取共享数据。

        Args:
            key: 数据键
            default: 默认值

        Returns:
            数据值
        """
        return self.shared_data.get(key, default)

    def set_data(self, key: str, value: Any) -> None:
        """设置共享数据。

        Args:
            key: 数据键
            value: 数据值
        """
        self.shared_data[key] = value
        logger.debug(f"设置上下文数据: {key} = {value}")

    def save_step_result(self, result: StepExecutionResult) -> None:
        """保存步骤执行结果。

        Args:
            result: 步骤执行结果
        """
        self.step_results.append(result)
        logger.info(f"步骤 {result.step_index} 执行{'成功' if result.success else '失败'}")

    def get_step_result(self, step_index: int) -> StepExecutionResult | None:
        """获取指定步骤的执行结果。

        Args:
            step_index: 步骤索引

        Returns:
            步骤执行结果，如果不存在则返回 None
        """
        for result in self.step_results:
            if result.step_index == step_index:
                return result
        return None

    def get_last_step_result(self) -> StepExecutionResult | None:
        """获取最后一步的执行结果。

        Returns:
            最后一步的执行结果，如果没有则返回 None
        """
        if self.step_results:
            return self.step_results[-1]
        return None

    def get_execution_summary(self) -> dict[str, Any]:
        """获取执行摘要。

        Returns:
            执行摘要字典
        """
        total_steps = len(self.step_results)
        successful_steps = sum(1 for r in self.step_results if r.success)
        failed_steps = total_steps - successful_steps
        total_duration = sum(r.duration for r in self.step_results)

        return {
            "status": self.status,
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "total_duration": total_duration,
            "start_time": self.start_time.isoformat(),
        }
