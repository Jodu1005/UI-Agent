"""任务流模板引擎。"""

import logging
import re
from typing import Any

from src.intent.models import Intent
from src.templates.models import TaskFlowTemplate, TemplateStep

logger = logging.getLogger(__name__)


class TemplateEngine:
    """任务流模板引擎。

    负责模板的参数绑定和条件执行。
    """

    def bind_parameters(
        self, template: TaskFlowTemplate, intent: Intent, context_data: dict[str, Any]
    ) -> TaskFlowTemplate:
        """绑定模板参数。

        Args:
            template: 原始模板
            intent: 识别到的意图
            context_data: 上下文数据

        Returns:
            参数绑定后的新模板
        """
        # 合并参数来源
        all_params = {}
        all_params.update(intent.parameters)  # 意图参数
        all_params.update(context_data)  # 上下文参数

        # 创建新步骤（绑定参数后）
        bound_steps: list[TemplateStep] = []
        for step in template.steps:
            bound_step = self._bind_step_parameters(step, all_params)
            bound_steps.append(bound_step)

        # 返回新模板
        return TaskFlowTemplate(
            name=template.name,
            description=template.description,
            intent_types=template.intent_types,
            steps=bound_steps,
            parameters=template.parameters,
        )

    def _bind_step_parameters(self, step: TemplateStep, params: dict[str, Any]) -> TemplateStep:
        """绑定步骤参数。

        Args:
            step: 原始步骤
            params: 参数字典

        Returns:
            参数绑定后的步骤
        """
        bound_params = {}

        for key, value in step.parameters.items():
            if isinstance(value, str):
                # 处理参数替换
                bound_params[key] = self._replace_placeholders(value, params)
            else:
                bound_params[key] = value

        # 处理 input_from（从上下文读取数据）
        if step.input_from and step.input_from in params:
            input_data = params[step.input_from]
            # 将输入数据合并到参数中
            if isinstance(input_data, dict):
                bound_params.update(input_data)
            else:
                bound_params["input_data"] = input_data

        return TemplateStep(
            system=step.system,
            action=step.action,
            parameters=bound_params,
            condition=step.condition,
            input_from=step.input_from,
            output_to=step.output_to,
            continue_on_error=step.continue_on_error,
        )

    def _replace_placeholders(self, text: str, params: dict[str, Any]) -> Any:
        """替换文本中的占位符。

        Args:
            text: 包含占位符的文本
            params: 参数字典

        Returns:
            替换后的值
        """
        # 处理 {{intent.param}} 格式
        pattern = r"\{\{intent\.(\w+)\}\}"

        def replacer(match: re.Match) -> str:
            param_key = match.group(1)
            if param_key in params:
                value = params[param_key]
                return str(value) if not isinstance(value, (str, int, float, bool)) else value
            return match.group(0)

        result = re.sub(pattern, replacer, text)

        # 尝试转换为数字或布尔值
        if result.isdigit():
            return int(result)
        if result.replace(".", "", 1).isdigit():
            return float(result)
        if result.lower() == "true":
            return True
        if result.lower() == "false":
            return False

        return result

    def should_execute_step(self, step: TemplateStep, previous_success: bool | None) -> bool:
        """判断步骤是否应该执行。

        Args:
            step: 模板步骤
            previous_success: 上一步是否成功（None 表示第一步）

        Returns:
            是否应该执行
        """
        if step.condition is None:
            return True

        # 第一步忽略条件
        if previous_success is None:
            return True

        if step.condition == "if_success":
            return previous_success is True
        if step.condition == "if_failure":
            return previous_success is False

        return True

    def extract_output_data(
        self, step_result: dict[str, Any], step: TemplateStep
    ) -> dict[str, Any]:
        """从步骤结果中提取输出数据。

        Args:
            step_result: 步骤执行结果
            step: 模板步骤

        Returns:
            提取的数据
        """
        if step.output_to:
            return {step.output_to: step_result}
        return {}
