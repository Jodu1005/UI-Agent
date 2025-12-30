"""任务流模板加载器。"""

import logging
from pathlib import Path
from typing import Any

import yaml

from src.templates.models import TaskFlowTemplate, TemplateStep

logger = logging.getLogger(__name__)


class TemplateLoader:
    """任务流模板加载器。

    从 YAML 文件或代码定义加载任务流模板。
    """

    def __init__(self):
        """初始化模板加载器。"""
        self._templates: dict[str, TaskFlowTemplate] = {}

    def load_from_file(self, path: str) -> TaskFlowTemplate:
        """从 YAML 文件加载模板。

        Args:
            path: 模板文件路径

        Returns:
            加载的模板

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 模板格式错误
        """
        template_file = Path(path)
        if not template_file.exists():
            raise FileNotFoundError(f"模板文件不存在: {path}")

        with open(template_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        template = self._parse_template(data)
        self._templates[template.name] = template
        logger.info(f"已加载模板: {template.name}")
        return template

    def load_from_directory(self, directory: str) -> dict[str, TaskFlowTemplate]:
        """从目录加载所有模板。

        Args:
            directory: 模板目录路径

        Returns:
            模板字典
        """
        templates: dict[str, TaskFlowTemplate] = {}
        template_dir = Path(directory)

        if not template_dir.exists():
            logger.warning(f"模板目录不存在: {directory}")
            return templates

        for yaml_file in template_dir.glob("*.yaml"):
            try:
                template = self.load_from_file(str(yaml_file))
                templates[template.name] = template
            except Exception as e:
                logger.error(f"加载模板失败 {yaml_file}: {e}")

        return templates

    def register_template(self, template: TaskFlowTemplate) -> None:
        """注册模板。

        Args:
            template: 模板对象
        """
        self._templates[template.name] = template
        logger.info(f"已注册模板: {template.name}")

    def get_template(self, name: str) -> TaskFlowTemplate | None:
        """获取模板。

        Args:
            name: 模板名称

        Returns:
            模板对象，如果不存在则返回 None
        """
        return self._templates.get(name)

    def get_template_by_intent(self, intent_type: str) -> TaskFlowTemplate | None:
        """根据意图类型获取模板。

        Args:
            intent_type: 意图类型

        Returns:
            匹配的模板，如果没有匹配则返回 None
        """
        for template in self._templates.values():
            if template.matches_intent(intent_type):
                return template
        return None

    def list_templates(self) -> list[str]:
        """列出所有模板名称。

        Returns:
            模板名称列表
        """
        return list(self._templates.keys())

    def _parse_template(self, data: dict[str, Any]) -> TaskFlowTemplate:
        """解析模板数据。

        Args:
            data: 模板数据字典

        Returns:
            模板对象

        Raises:
            ValueError: 数据格式错误
        """
        # 解析步骤
        steps: list[TemplateStep] = []
        for step_data in data.get("steps", []):
            step = TemplateStep(
                system=step_data.get("system", ""),
                action=step_data.get("action", ""),
                parameters=step_data.get("parameters", {}),
                condition=step_data.get("condition"),
                input_from=step_data.get("input_from"),
                output_to=step_data.get("output_to"),
                continue_on_error=step_data.get("continue_on_error", False),
            )
            steps.append(step)

        return TaskFlowTemplate(
            name=data.get("name", ""),
            description=data.get("description", ""),
            intent_types=data.get("intent_types", []),
            steps=steps,
            parameters=data.get("parameters", {}),
        )
