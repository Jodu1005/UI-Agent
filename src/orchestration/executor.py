"""任务执行器。"""

import logging
import time

from src.orchestration.adapters import SystemAdapter
from src.orchestration.context import ExecutionContext, StepExecutionResult
from src.templates.models import TemplateStep

logger = logging.getLogger(__name__)


class TaskExecutor:
    """任务执行器。

    负责执行单个任务步骤，管理跨系统切换和数据传递。
    """

    def __init__(self):
        """初始化任务执行器。"""
        self._adapters: dict[str, SystemAdapter] = {}

    def register_adapter(self, system: str, adapter: SystemAdapter) -> None:
        """注册系统适配器。

        Args:
            system: 系统名称（browser、ide、terminal 等）
            adapter: 系统适配器
        """
        self._adapters[system] = adapter
        logger.info(f"已注册系统适配器: {system}")

    def execute_step(
        self, step: TemplateStep, context: ExecutionContext, step_index: int
    ) -> StepExecutionResult:
        """执行单个任务步骤。

        Args:
            step: 模板步骤
            context: 执行上下文
            step_index: 步骤索引

        Returns:
            步骤执行结果
        """
        start_time = time.time()

        try:
            # 检查是否有对应的适配器
            adapter = self._adapters.get(step.system)
            if not adapter:
                return StepExecutionResult(
                    step_index=step_index,
                    success=False,
                    error=f"未找到系统适配器: {step.system}",
                )

            logger.info(f"执行步骤 [{step_index}]: {step.system}.{step.action}")

            # 执行动作
            result = adapter.execute(step.action, step.parameters)

            # 保存输出数据到上下文
            if result.success and result.output:
                if step.output_to:
                    context.set_data(step.output_to, result.output)
                # 同时也保存到步骤特定的键
                context.set_data(f"step_{step_index}_output", result.output)

            # 计算执行时长
            result.duration = time.time() - start_time
            result.step_index = step_index

            return result

        except Exception as e:
            logger.error(f"步骤执行异常: {e}")
            return StepExecutionResult(
                step_index=step_index,
                success=False,
                error=str(e),
                duration=time.time() - start_time,
            )
