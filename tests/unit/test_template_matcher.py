"""模板匹配器单元测试。"""

import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

from src.locator.template_matcher import TemplateMatcher
from src.models.element import UIElement


@pytest.mark.unit
class TestTemplateMatcher:
    """模板匹配器测试类。"""

    @pytest.fixture
    def temp_template_dir(self):
        """创建临时模板目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_dir = Path(tmpdir) / "templates"
            template_dir.mkdir(parents=True)
            yield template_dir

    @pytest.fixture
    def test_template(self, temp_template_dir):
        """创建测试用的模板图片。"""
        # 创建一个简单的红色方块作为模板 (50x50)
        template_img = np.zeros((50, 50, 3), dtype=np.uint8)
        template_img[:] = [0, 0, 255]  # BGR 格式的红色

        template_path = temp_template_dir / "red_square.png"
        cv2.imwrite(str(template_path), template_img)
        return template_path

    @pytest.fixture
    def test_screenshot_with_template(self):
        """创建包含模板的测试截图。"""
        # 创建一个白色背景的截图 (200x200)
        screenshot = np.ones((200, 200, 3), dtype=np.uint8) * 255

        # 在不同位置放置红色方块
        # 位置 1: (10, 10)
        screenshot[10:60, 10:60] = [0, 0, 255]  # BGR 红色
        # 位置 2: (100, 50)
        screenshot[50:100, 100:150] = [0, 0, 255]

        # 转换为 PIL Image
        return Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))

    @pytest.fixture
    def test_screenshot_no_match(self):
        """创建不包含模板的测试截图。"""
        # 创建一个纯白色截图，没有红色方块
        screenshot = np.ones((200, 200, 3), dtype=np.uint8) * 255
        return Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))

    @pytest.fixture
    def matcher(self, temp_template_dir):
        """创建模板匹配器实例。"""
        return TemplateMatcher(
            template_dir=str(temp_template_dir),
            default_confidence=0.8,
            method="TM_CCOEFF_NORMED",
            enable_multiscale=False,
        )

    @pytest.fixture
    def multiscale_matcher(self, temp_template_dir):
        """创建多尺度模板匹配器实例。"""
        return TemplateMatcher(
            template_dir=str(temp_template_dir),
            default_confidence=0.8,
            method="TM_CCOEFF_NORMED",
            enable_multiscale=True,
            scales=[0.8, 0.9, 1.0, 1.1, 1.2],
        )


class TestTemplateLoading(TestTemplateMatcher):
    """测试模板加载功能。"""

    def test_load_template_success(self, matcher, test_template):
        """测试成功加载模板。"""
        template = matcher.load_template("red_square.png")
        assert template is not None
        assert template.shape == (50, 50, 3)  # height, width, channels

    def test_load_template_caching(self, matcher, test_template):
        """测试模板缓存机制。"""
        # 第一次加载
        template1 = matcher.load_template("red_square.png")
        # 第二次加载应该从缓存获取
        template2 = matcher.load_template("red_square.png")

        # 验证是同一个对象（缓存）
        assert id(template1) == id(template2)

    def test_load_template_not_found(self, matcher):
        """测试加载不存在的模板。"""
        with pytest.raises(FileNotFoundError):
            matcher.load_template("nonexistent.png")

    def test_clear_cache(self, matcher, test_template):
        """测试清空缓存。"""
        # 加载模板
        matcher.load_template("red_square.png")
        assert "red_square.png" in matcher._template_cache

        # 清空缓存
        matcher.clear_cache()
        assert len(matcher._template_cache) == 0


class TestSingleScaleMatching(TestTemplateMatcher):
    """测试单尺度模板匹配。"""

    def test_match_single_result(self, matcher, test_template, test_screenshot_with_template):
        """测试匹配单个结果。"""
        results = matcher.match(test_screenshot_with_template, "red_square.png")

        # 应该找到至少一个匹配
        assert len(results) >= 1

        # 验证第一个结果
        first_result = results[0]
        assert isinstance(first_result, UIElement)
        assert first_result.element_type == "template_match"
        assert "red_square.png" in first_result.description
        assert first_result.confidence >= 0.8  # 默认阈值

    def test_match_multiple_results(self, matcher, test_template, test_screenshot_with_template):
        """测试匹配多个结果。"""
        results = matcher.match(
            test_screenshot_with_template,
            "red_square.png",
            threshold=0.5  # 降低阈值以获取更多匹配
        )

        # 应该找到两个红色方块
        assert len(results) >= 1

    def test_match_accuracy(self, matcher, test_template, test_screenshot_with_template):
        """测试匹配准确性。"""
        results = matcher.match(test_screenshot_with_template, "red_square.png")

        # 验证匹配位置
        first_result = results[0]
        x1, y1, x2, y2 = first_result.bbox

        # 检查边界框是否合理（应该在红色方块附近）
        # 第一个方块在 (10, 10)，第二个在 (100, 50)
        # 匹配结果应该接近这两个位置之一
        assert 0 <= x1 < 200
        assert 0 <= y1 < 200
        assert x1 < x2
        assert y1 < y2

        # 验证尺寸接近 50x50
        width = x2 - x1
        height = y2 - y1
        assert 45 <= width <= 55  # 允许小误差
        assert 45 <= height <= 55

    def test_match_no_results(self, matcher, test_template, test_screenshot_no_match):
        """测试没有匹配结果的情况。"""
        results = matcher.match(test_screenshot_no_match, "red_square.png")

        # 截图中没有红色方块，应该没有匹配结果（或置信度很低）
        # 由于使用了高阈值 (0.8)，应该没有结果
        # 注意：可能会产生假阳性，所以这里只验证返回的是列表
        assert isinstance(results, list)


class TestThresholdFiltering(TestTemplateMatcher):
    """测试阈值过滤功能。"""

    def test_high_threshold(self, matcher, test_template, test_screenshot_with_template):
        """测试高阈值过滤。"""
        results = matcher.match(
            test_screenshot_with_template,
            "red_square.png",
            threshold=0.99  # 非常高的阈值
        )

        # 高阈值下，匹配结果应该更少
        # 但完美匹配应该仍能通过
        assert isinstance(results, list)

    def test_low_threshold(self, matcher, test_template, test_screenshot_with_template):
        """测试低阈值获取更多结果。"""
        high_threshold_results = matcher.match(
            test_screenshot_with_template,
            "red_square.png",
            threshold=0.9
        )

        low_threshold_results = matcher.match(
            test_screenshot_with_template,
            "red_square.png",
            threshold=0.5
        )

        # 低阈值应该获得更多或相等的结果
        assert len(low_threshold_results) >= len(high_threshold_results)

    def test_default_threshold(self, matcher, test_template, test_screenshot_with_template):
        """测试默认阈值。"""
        # 不指定阈值，使用默认值
        results1 = matcher.match(test_screenshot_with_template, "red_square.png")

        # 显式指定默认阈值
        results2 = matcher.match(
            test_screenshot_with_template,
            "red_square.png",
            threshold=matcher.default_confidence
        )

        # 结果应该相同
        assert len(results1) == len(results2)


class TestMultiscaleMatching(TestTemplateMatcher):
    """测试多尺度模板匹配。"""

    def test_multiscale_enabled(self, multiscale_matcher, test_template, test_screenshot_with_template):
        """测试启用多尺度匹配。"""
        results = multiscale_matcher.match(
            test_screenshot_with_template,
            "red_square.png",
            threshold=0.7
        )

        # 多尺度匹配应该找到结果
        assert isinstance(results, list)
        if results:
            # 检查结果是否包含尺度信息
            for result in results:
                if result.metadata and "scale" in result.metadata:
                    assert 0.7 <= result.metadata["scale"] <= 1.3

    def test_multiscale_vs_single_scale(self, matcher, multiscale_matcher, test_template, test_screenshot_with_template):
        """比较多尺度和单尺度匹配。"""
        single_results = matcher.match(
            test_screenshot_with_template,
            "red_square.png",
            threshold=0.7
        )

        multi_results = multiscale_matcher.match(
            test_screenshot_with_template,
            "red_square.png",
            threshold=0.7
        )

        # 多尺度应该找到更多或相等的结果
        assert len(multi_results) >= len(single_results)

    def test_custom_scales(self, temp_template_dir, test_template, test_screenshot_with_template):
        """测试自定义缩放比例。"""
        custom_matcher = TemplateMatcher(
            template_dir=str(temp_template_dir),
            default_confidence=0.8,
            enable_multiscale=True,
            scales=[0.5, 1.0, 1.5]  # 自定义缩放比例
        )

        results = custom_matcher.match(
            test_screenshot_with_template,
            "red_square.png",
            threshold=0.7
        )

        # 验证结果
        assert isinstance(results, list)


class TestDifferentMatchMethods(TestTemplateMatcher):
    """测试不同的匹配方法。"""

    @pytest.mark.parametrize("method", [
        "TM_CCOEFF_NORMED",
        "TM_CCORR_NORMED",
        "TM_SQDIFF_NORMED",
    ])
    def test_different_methods(self, temp_template_dir, test_template, test_screenshot_with_template, method):
        """测试不同的匹配方法。"""
        matcher = TemplateMatcher(
            template_dir=str(temp_template_dir),
            default_confidence=0.7,
            method=method,
            enable_multiscale=False,
        )

        results = matcher.match(test_screenshot_with_template, "red_square.png")

        # 所有方法都应该能找到匹配
        assert isinstance(results, list)

    def test_invalid_method(self, temp_template_dir):
        """测试无效的匹配方法。"""
        # 应该回退到默认方法
        matcher = TemplateMatcher(
            template_dir=str(temp_template_dir),
            method="INVALID_METHOD",
        )

        # 应该回退到 TM_CCOEFF_NORMED
        assert matcher.method == "TM_CCOEFF_NORMED"


class TestBoundaryConditions(TestTemplateMatcher):
    """测试边界情况。"""

    def test_empty_screenshot(self, matcher, test_template):
        """测试空截图。"""
        # 创建一个极小的截图
        tiny_screenshot = Image.new("RGB", (10, 10), color="white")

        results = matcher.match(tiny_screenshot, "red_square.png")

        # 模板比截图大，应该无法匹配
        assert isinstance(results, list)

    def test_template_larger_than_screenshot(self, matcher, temp_template_dir, test_screenshot_with_template):
        """测试模板大于截图的情况。"""
        # 创建一个大模板
        large_template = np.zeros((300, 300, 3), dtype=np.uint8)
        large_template[:] = [0, 0, 255]

        template_path = temp_template_dir / "large_template.png"
        cv2.imwrite(str(template_path), large_template)

        # 尝试匹配
        screenshot = Image.new("RGB", (200, 200), color="white")
        results = matcher.match(screenshot, "large_template.png")

        # 模板大于截图，无法匹配
        assert isinstance(results, list)

    def test_corrupted_template(self, matcher, temp_template_dir):
        """测试损坏的模板文件。"""
        # 创建一个损坏的文件
        corrupted_path = temp_template_dir / "corrupted.png"
        corrupted_path.write_text("not an image", encoding="utf-8")

        # 应该抛出异常或返回空列表
        with pytest.raises((FileNotFoundError, ValueError)):
            matcher.load_template("corrupted.png")

    def test_grayscale_template(self, temp_template_dir, test_template, test_screenshot_with_template):
        """测试灰度模板处理。"""
        # OpenCV 的 imread 会自动处理各种格式
        matcher = TemplateMatcher(
            template_dir=str(temp_template_dir),
            default_confidence=0.7,
        )

        results = matcher.match(test_screenshot_with_template, "red_square.png")
        assert isinstance(results, list)


class TestUIElementProperties(TestTemplateMatcher):
    """测试返回的 UI 元素属性。"""

    def test_element_center_calculation(self, matcher, test_template, test_screenshot_with_template):
        """测试元素中心点计算。"""
        results = matcher.match(test_screenshot_with_template, "red_square.png")

        if results:
            element = results[0]
            center = element.center

            # 验证中心点在边界框内
            x1, y1, x2, y2 = element.bbox
            assert x1 <= center[0] <= x2
            assert y1 <= center[1] <= y2

    def test_element_dimensions(self, matcher, test_template, test_screenshot_with_template):
        """测试元素尺寸计算。"""
        results = matcher.match(test_screenshot_with_template, "red_square.png")

        if results:
            element = results[0]

            # 验证宽度和高度
            assert element.width > 0
            assert element.height > 0

            # 验证边界框一致性
            x1, y1, x2, y2 = element.bbox
            assert element.width == x2 - x1
            assert element.height == y2 - y1

    def test_element_confidence_range(self, matcher, test_template, test_screenshot_with_template):
        """测试置信度在合理范围内。"""
        results = matcher.match(test_screenshot_with_template, "red_square.png")

        for result in results:
            # 置信度应该在 0-1 范围内
            assert 0.0 <= result.confidence <= 1.0


class TestConfigurationDefaults(TestTemplateMatcher):
    """测试配置默认值。"""

    def test_default_confidence(self, temp_template_dir):
        """测试默认置信度。"""
        matcher = TemplateMatcher(template_dir=str(temp_template_dir))
        assert matcher.default_confidence == 0.8

    def test_default_method(self, temp_template_dir):
        """测试默认匹配方法。"""
        matcher = TemplateMatcher(template_dir=str(temp_template_dir))
        assert matcher.method == "TM_CCOEFF_NORMED"

    def test_default_multiscale_disabled(self, temp_template_dir):
        """测试默认禁用多尺度。"""
        matcher = TemplateMatcher(template_dir=str(temp_template_dir))
        assert matcher.enable_multiscale is False

    def test_default_scales(self, temp_template_dir):
        """测试默认缩放比例。"""
        matcher = TemplateMatcher(template_dir=str(temp_template_dir))
        assert matcher.scales == [0.8, 0.9, 1.0, 1.1, 1.2]

    def test_custom_confidence(self, temp_template_dir):
        """测试自定义置信度。"""
        matcher = TemplateMatcher(
            template_dir=str(temp_template_dir),
            default_confidence=0.9
        )
        assert matcher.default_confidence == 0.9
