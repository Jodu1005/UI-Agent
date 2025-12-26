"""基于 OpenCV 的模板匹配定位器。"""

import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image

from src.models.element import UIElement

logger = logging.getLogger(__name__)

# OpenCV 匹配方法映射
CV2_MATCH_METHODS = {
    "TM_SQDIFF": cv2.TM_SQDIFF,
    "TM_SQDIFF_NORMED": cv2.TM_SQDIFF_NORMED,
    "TM_CCORR": cv2.TM_CCORR,
    "TM_CCORR_NORMED": cv2.TM_CCORR_NORMED,
    "TM_CCOEFF": cv2.TM_CCOEFF,
    "TM_CCOEFF_NORMED": cv2.TM_CCOEFF_NORMED,
}


class TemplateMatcher:
    """基于 OpenCV 模板匹配的 UI 元素定位器。

    使用模板图片在屏幕截图中查找匹配的 UI 元素位置。
    """

    def __init__(
        self,
        template_dir: str = "templates/",
        default_confidence: float = 0.8,
        method: str = "TM_CCOEFF_NORMED",
        enable_multiscale: bool = False,
        scales: list[float] | None = None,
    ) -> None:
        """初始化模板匹配器。

        Args:
            template_dir: 模板图片存储目录（相对于项目根目录）
            default_confidence: 默认匹配置信度阈值 (0.0-1.0)
            method: OpenCV 匹配方法
            enable_multiscale: 是否启用多尺度匹配
            scales: 多尺度匹配的缩放比例列表
        """
        self.template_dir = Path(template_dir)
        self.default_confidence = default_confidence
        self.enable_multiscale = enable_multiscale
        self.scales = scales or [0.8, 0.9, 1.0, 1.1, 1.2]

        # 验证匹配方法
        if method not in CV2_MATCH_METHODS:
            logger.warning(f"未知的匹配方法 {method}，使用默认 TM_CCOEFF_NORMED")
            method = "TM_CCOEFF_NORMED"
        self.method = method
        self.cv2_method = CV2_MATCH_METHODS[method]

        # 模板缓存
        self._template_cache: dict[str, np.ndarray] = {}

    def load_template(self, template_name: str) -> np.ndarray:
        """加载模板图片。

        Args:
            template_name: 模板图片文件名

        Returns:
            模板图片的 numpy 数组（灰度图）

        Raises:
            FileNotFoundError: 模板图片不存在
        """
        # 检查缓存
        if template_name in self._template_cache:
            return self._template_cache[template_name]

        # 构建模板文件路径
        template_path = self.template_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"模板图片不存在: {template_path}")

        # 读取模板图片
        template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"无法读取模板图片: {template_path}")

        # 缓存模板
        self._template_cache[template_name] = template
        logger.info(f"加载模板: {template_name}, 尺寸: {template.shape}")

        # 打印模板信息（调试用）
        print(f"[模板加载] 文件: {template_name}")
        print(f"[模板加载] 路径: {template_path}")
        print(f"[模板加载] 尺寸: {template.shape[1]}x{template.shape[0]} (宽x高)")

        return template

    def match(
        self,
        screenshot: Image.Image,
        template_name: str,
        threshold: float | None = None,
    ) -> list[UIElement]:
        """在截图中匹配模板。

        Args:
            screenshot: 屏幕截图
            template_name: 模板图片文件名
            threshold: 匹配阈值（可选，默认使用配置的 default_confidence）

        Returns:
            匹配到的 UI 元素列表，按置信度降序排列
        """
        if threshold is None:
            threshold = self.default_confidence

        # 显示截图信息（调试用）
        print(f"[模板匹配] 截图尺寸: {screenshot.size[0]}x{screenshot.size[1]} (宽x高)")
        print(f"[模板匹配] 匹配阈值: {threshold}")

        try:
            # 加载模板
            template = self.load_template(template_name)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"加载模板失败: {e}")
            print(f"[模板匹配] 错误: {e}")
            return []

        # 转换截图格式
        screenshot_array = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # 检查模板是否大于截图
        if (template.shape[0] > screenshot_array.shape[0] or
            template.shape[1] > screenshot_array.shape[1]):
            print(f"[模板匹配] 警告: 模板尺寸 ({template.shape[1]}x{template.shape[0]}) 大于截图尺寸 ({screenshot.size[0]}x{screenshot.size[1]})")

        if self.enable_multiscale:
            results = self._match_multiscale(screenshot_array, template, threshold, template_name)
        else:
            results = self._match_single_scale(screenshot_array, template, threshold, template_name)

        # 按置信度降序排序
        results.sort(key=lambda x: x.confidence, reverse=True)

        # 显示匹配结果摘要
        if results:
            print(f"[模板匹配] 找到 {len(results)} 个匹配结果")
            for i, r in enumerate(results):
                print(f"  结果 {i+1}: 置信度={r.confidence:.3f}, bbox={r.bbox}")
        else:
            print(f"[模板匹配] 未找到匹配结果（阈值={threshold}）")

        logger.info(f"模板匹配完成: {template_name}, 找到 {len(results)} 个结果")
        return results

    def _match_single_scale(
        self,
        screenshot: np.ndarray,
        template: np.ndarray,
        threshold: float,
        template_name: str = "template",
    ) -> list[UIElement]:
        """单尺度模板匹配。

        Args:
            screenshot: 截图数组
            template: 模板数组
            threshold: 匹配阈值
            template_name: 模板名称（用于描述）

        Returns:
            匹配到的 UI 元素列表
        """
        result = cv2.matchTemplate(screenshot, template, self.cv2_method)

        # 获取最大和最小匹配值
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 根据匹配方法处理结果
        if self.method in ["TM_SQDIFF", "TM_SQDIFF_NORMED"]:
            # 对于 SQDIFF 方法，值越小匹配越好
            match_val = 1.0 - min_val  # 转换为置信度
            print(f"[模板匹配] 最大置信度: {match_val:.3f} (阈值: {threshold})")

            if match_val >= threshold:
                return [
                    UIElement(
                        element_type="template_match",
                        description=f"模板匹配: {template_name}",
                        bbox=self._loc_to_bbox(min_loc, template.shape),
                        confidence=match_val,
                    )
                ]
        else:
            # 对于其他方法，值越大匹配越好
            print(f"[模板匹配] 最大置信度: {max_val:.3f} (阈值: {threshold})")

            if max_val >= threshold:
                return [
                    UIElement(
                        element_type="template_match",
                        description=f"模板匹配: {template_name}",
                        bbox=self._loc_to_bbox(max_loc, template.shape),
                        confidence=max_val,
                    )
                ]

        return []

    def _match_multiscale(
        self,
        screenshot: np.ndarray,
        template: np.ndarray,
        threshold: float,
        template_name: str = "template",
    ) -> list[UIElement]:
        """多尺度模板匹配。

        Args:
            screenshot: 截图数组
            template: 模板数组
            threshold: 匹配阈值
            template_name: 模板名称（用于描述）

        Returns:
            匹配到的 UI 元素列表
        """
        all_results = []

        for scale in self.scales:
            # 缩放模板
            scaled_template = cv2.resize(
                template,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC,
            )

            # 检查缩放后的模板是否大于截图
            if (
                scaled_template.shape[0] > screenshot.shape[0]
                or scaled_template.shape[1] > screenshot.shape[1]
            ):
                continue

            # 执行匹配
            result = cv2.matchTemplate(screenshot, scaled_template, self.cv2_method)

            # 获取所有匹配位置
            if self.method in ["TM_SQDIFF", "TM_SQDIFF_NORMED"]:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                match_val = 1.0 - min_val
                if match_val >= threshold:
                    all_results.append(
                        UIElement(
                            element_type="template_match",
                            description=f"模板匹配: {template_name} (scale={scale:.1f})",
                            bbox=self._loc_to_bbox(min_loc, scaled_template.shape),
                            confidence=match_val,
                            metadata={"scale": scale},
                        )
                    )
            else:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                if max_val >= threshold:
                    all_results.append(
                        UIElement(
                            element_type="template_match",
                            description=f"模板匹配: {template_name} (scale={scale:.1f})",
                            bbox=self._loc_to_bbox(max_loc, scaled_template.shape),
                            confidence=max_val,
                            metadata={"scale": scale},
                        )
                    )

        return all_results

    def _loc_to_bbox(
        self,
        loc: tuple[int, int],
        template_shape: tuple[int, int, int],
    ) -> tuple[int, int, int, int]:
        """将匹配位置转换为边界框。

        Args:
            loc: 匹配位置 (x, y)
            template_shape: 模板形状 (height, width, channels)

        Returns:
            边界框 (x1, y1, x2, y2)
        """
        x, y = loc
        h, w = template_shape[:2]
        return (x, y, x + w, y + h)

    def clear_cache(self) -> None:
        """清空模板缓存。"""
        self._template_cache.clear()
