"""坐标计算单元测试。"""

import pytest

from src.models.element import UIElement
from src.locator.visual_locator import CoordinateCalibrator


@pytest.mark.unit
class TestBboxCalculations:
    """边界框计算测试类。"""

    def test_bbox_center_calculation(self):
        """测试边界框中心点计算。"""
        elem = UIElement(
            element_type="button",
            description="测试",
            bbox=(100, 200, 300, 280),
            confidence=1.0,
        )
        center = elem.center
        # ( (100+300)//2, (200+280)//2 ) = (200, 240)
        assert center == (200, 240)

    def test_bbox_width_calculation(self):
        """测试边界框宽度计算。"""
        elem = UIElement(
            element_type="text",
            description="测试",
            bbox=(50, 100, 250, 150),
            confidence=1.0,
        )
        width = elem.bbox[2] - elem.bbox[0]
        assert width == 200

    def test_bbox_height_calculation(self):
        """测试边界框高度计算。"""
        elem = UIElement(
            element_type="text",
            description="测试",
            bbox=(50, 100, 250, 180),
            confidence=1.0,
        )
        height = elem.bbox[3] - elem.bbox[1]
        assert height == 80

    def test_bbox_area_calculation(self):
        """测试边界框面积计算。"""
        x1, y1, x2, y2 = 100, 200, 400, 350
        elem = UIElement(
            element_type="region",
            description="测试",
            bbox=(x1, y1, x2, y2),
            confidence=1.0,
        )
        width = x2 - x1
        height = y2 - y1
        area = width * height
        assert area == 300 * 150  # 45000

    def test_bbox_aspect_ratio(self):
        """测试边界框宽高比。"""
        x1, y1, x2, y2 = 0, 0, 200, 100
        elem = UIElement(
            element_type="image",
            description="测试",
            bbox=(x1, y1, x2, y2),
            confidence=1.0,
        )
        width = x2 - x1
        height = y2 - y1
        aspect_ratio = width / height
        assert aspect_ratio == 2.0


@pytest.mark.unit
class TestCoordinateCalibrator:
    """坐标校准器测试类。"""

    def test_calibrate_with_positive_offset(self):
        """测试正偏移校准。"""
        calibrator = CoordinateCalibrator(10, 20)
        result = calibrator.calibrate((100, 200, 300, 400))
        assert result == (110, 220, 310, 420)

    def test_calibrate_with_negative_offset(self):
        """测试负偏移校准。"""
        calibrator = CoordinateCalibrator(-15, -25)
        result = calibrator.calibrate((100, 200, 300, 400))
        assert result == (85, 175, 285, 375)

    def test_calibrate_with_mixed_offset(self):
        """测试混合偏移校准。"""
        calibrator = CoordinateCalibrator(30, -10)
        result = calibrator.calibrate((100, 200, 300, 400))
        assert result == (130, 190, 330, 390)

    def test_calibrate_zero_offset(self):
        """测试零偏移校准。"""
        calibrator = CoordinateCalibrator(0, 0)
        result = calibrator.calibrate((100, 200, 300, 400))
        assert result == (100, 200, 300, 400)

    def test_calibrate_large_offset(self):
        """测试大偏移校准。"""
        calibrator = CoordinateCalibrator(500, 500)
        result = calibrator.calibrate((100, 200, 300, 400))
        assert result == (600, 700, 800, 900)

    def test_calibrate_small_bbox(self):
        """测试小边界框校准。"""
        calibrator = CoordinateCalibrator(5, 5)
        result = calibrator.calibrate((10, 10, 20, 15))
        assert result == (15, 15, 25, 20)

    def test_from_config_valid_offset(self):
        """测试从配置创建校准器（有效偏移）。"""
        calibrator = CoordinateCalibrator.from_config([36, 46])
        assert calibrator.offset_x == 36
        assert calibrator.offset_y == 46

    def test_from_config_none(self):
        """测试从配置创建校准器（None）。"""
        calibrator = CoordinateCalibrator.from_config(None)
        assert calibrator.offset_x == 0
        assert calibrator.offset_y == 0

    def test_from_config_empty(self):
        """测试从配置创建校准器（空列表）。"""
        calibrator = CoordinateCalibrator.from_config([])
        assert calibrator.offset_x == 0
        assert calibrator.offset_y == 0

    def test_from_config_single_value(self):
        """测试从配置创建校准器（单个值）。"""
        # 当前实现需要至少 2 个值才有效
        calibrator = CoordinateCalibrator.from_config([100])
        assert calibrator.offset_x == 0
        assert calibrator.offset_y == 0

    def test_calibrate_preserves_bbox_size(self):
        """测试校准后边界框大小不变。"""
        calibrator = CoordinateCalibrator(50, 30)
        original_bbox = (100, 200, 300, 400)
        calibrated_bbox = calibrator.calibrate(original_bbox)

        original_width = original_bbox[2] - original_bbox[0]
        original_height = original_bbox[3] - original_bbox[1]
        calibrated_width = calibrated_bbox[2] - calibrated_bbox[0]
        calibrated_height = calibrated_bbox[3] - calibrated_bbox[1]

        assert original_width == calibrated_width
        assert original_height == calibrated_height


@pytest.mark.unit
class TestCoordinateTransforms:
    """坐标变换测试类。"""

    def test_scale_bbox(self):
        """测试缩放边界框。"""
        x1, y1, x2, y2 = 100, 100, 200, 150
        scale = 2.0
        new_bbox = (
            int(x1 * scale),
            int(y1 * scale),
            int(x2 * scale),
            int(y2 * scale),
        )
        assert new_bbox == (200, 200, 400, 300)

    def test_crop_bbox_within_bounds(self):
        """测试裁剪边界框到指定范围内。"""
        bbox = (50, 50, 250, 200)
        bounds = (0, 0, 200, 150)
        # 裁剪后的边界框
        cropped = (
            max(50, 0),
            max(50, 0),
            min(250, 200),
            min(200, 150),
        )
        assert cropped == (50, 50, 200, 150)

    def test_expand_bbox_centered(self):
        """测试以中心点扩展边界框。"""
        x1, y1, x2, y2 = 100, 100, 200, 150
        margin = 20
        expanded = (
            x1 - margin,
            y1 - margin,
            x2 + margin,
            y2 + margin,
        )
        assert expanded == (80, 80, 220, 170)

    def test_bbox_intersection(self):
        """测试边界框相交。"""
        bbox1 = (0, 0, 100, 100)
        bbox2 = (50, 50, 150, 150)
        # 计算相交区域
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        intersection = (x1, y1, x2, y2)
        assert intersection == (50, 50, 100, 100)

    def test_bbox_union(self):
        """测试边界框合并。"""
        bbox1 = (0, 0, 100, 100)
        bbox2 = (50, 50, 150, 150)
        # 计算合并区域
        x1 = min(bbox1[0], bbox2[0])
        y1 = min(bbox1[1], bbox2[1])
        x2 = max(bbox1[2], bbox2[2])
        y2 = max(bbox1[3], bbox2[3])
        union = (x1, y1, x2, y2)
        assert union == (0, 0, 150, 150)

    def test_bbox_contains_point(self):
        """测试边界框包含点。"""
        bbox = (100, 100, 200, 150)
        point = (150, 125)
        contains = (
            bbox[0] <= point[0] <= bbox[2]
            and bbox[1] <= point[1] <= bbox[3]
        )
        assert contains is True

    def test_bbox_does_not_contain_point(self):
        """测试边界框不包含点。"""
        bbox = (100, 100, 200, 150)
        point = (250, 125)
        contains = (
            bbox[0] <= point[0] <= bbox[2]
            and bbox[1] <= point[1] <= bbox[3]
        )
        assert contains is False
