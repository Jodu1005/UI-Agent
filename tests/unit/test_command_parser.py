"""命令解析器单元测试。"""

import pytest
from unittest.mock import MagicMock, patch

from src.parser.command_parser import CommandParser
from src.parser.intents import IntentType
from src.models.command import ParsedCommand


@pytest.mark.unit
class TestCommandParser:
    """命令解析器测试类。"""

    @pytest.fixture
    def parser(self, mock_config):
        """创建解析器实例。"""
        # 创建模拟的配置管理器
        config_manager = MagicMock()
        config_manager.list_operations.return_value = []
        config_manager.get_operation.return_value = None

        return CommandParser(
            config_manager=config_manager,
            api_key="test_key",
            model="glm-4-flash",
        )

    def test_parse_simple_file_command(self, parser):
        """测试简单文件命令解析。"""
        # 模拟操作匹配
        with patch.object(parser, "_match_operation") as mock_match:
            mock_op = MagicMock()
            mock_op.name = "open_file"
            mock_op.intent = "file_operation"
            mock_op.aliases = ["打开文件", "open file"]
            mock_match.return_value = mock_op

            # 模拟参数提取
            with patch.object(parser, "_extract_parameters") as mock_extract:
                mock_extract.return_value = {"filename": "main.py"}

                result = parser.parse("打开 main.py")

                assert result.action == "open_file"
                assert result.intent == "file_operation"
                assert result.parameters["filename"] == "main.py"
                assert result.confidence > 0.9

    def test_extract_filename_with_quotes(self, parser):
        """测试提取带引号的文件名。"""
        mock_op = MagicMock()
        mock_op.name = "test"
        mock_op.aliases = ["test"]

        result = parser._extract_parameters('双击 "main.py"', mock_op)
        assert result["filename"] == "main.py"

    def test_extract_filename_with_extension(self, parser):
        """测试提取带扩展名的文件名。"""
        mock_op = MagicMock()
        mock_op.name = "double_click_file"
        mock_op.aliases = ["双击", "双击文件"]

        result = parser._extract_parameters("双击 main.py", mock_op)
        assert result["filename"] == "main.py"

    def test_extract_generic_keyword(self, parser):
        """测试提取通用关键字。"""
        mock_op = MagicMock()
        mock_op.name = "double_click_file"
        mock_op.aliases = ["双击"]

        result = parser._extract_parameters("双击 运行按钮", mock_op)
        assert result["filename"] == "运行按钮"

    def test_extract_line_number(self, parser):
        """测试提取行号。"""
        mock_op = MagicMock()
        mock_op.name = "test"
        mock_op.aliases = ["test"]

        result = parser._extract_parameters("跳转到 第 42 行", mock_op)
        assert result["line_number"] == 42

    def test_extract_symbol_name(self, parser):
        """测试提取符号名。"""
        mock_op = MagicMock()
        mock_op.name = "rename"
        mock_op.aliases = ["重命名"]

        result = parser._extract_parameters("重命名 为 foo", mock_op)
        assert result["new_name"] == "foo"

    def test_intent_classification_file_operation(self, parser):
        """测试文件操作意图分类。"""
        result = parser._parse_with_rules("打开 main.py", {})
        assert result.intent == IntentType.FILE_OPERATION.value

    def test_intent_classification_edit(self, parser):
        """测试编辑操作意图分类。"""
        result = parser._parse_with_rules("复制当前行", {})
        assert result.intent == IntentType.EDIT.value

    def test_intent_classification_navigation(self, parser):
        """测试导航操作意图分类。"""
        result = parser._parse_with_rules("跳转到第100行", {})
        assert result.intent == IntentType.NAVIGATION.value

    def test_intent_classification_run(self, parser):
        """测试运行操作意图分类。"""
        result = parser._parse_with_rules("运行当前文件", {})
        assert result.intent == IntentType.RUN.value

    def test_validate_valid_command(self, parser):
        """测试验证有效命令。"""
        cmd = ParsedCommand(
            intent="file_operation",
            action="open_file",
            parameters={"filename": "main.py"},
            confidence=0.9,
            context={},
        )
        assert cmd.validate() is True

    def test_validate_invalid_command(self, parser):
        """测试验证无效命令。"""
        cmd = ParsedCommand(
            intent="unknown",
            action="",
            parameters={},
            confidence=0.3,
            context={},
        )
        assert cmd.validate() is False


@pytest.mark.unit
class TestCoordinateCalibrator:
    """坐标校准器测试类。"""

    from src.locator.visual_locator import CoordinateCalibrator

    def test_calibrate_with_offset(self):
        """测试带偏移的校准。"""
        calibrator = self.CoordinateCalibrator(10, 20)
        result = calibrator.calibrate((100, 200, 300, 400))
        assert result == (110, 220, 310, 420)

    def test_calibrate_no_offset(self):
        """测试无偏移的校准。"""
        calibrator = self.CoordinateCalibrator(0, 0)
        result = calibrator.calibrate((100, 200, 300, 400))
        assert result == (100, 200, 300, 400)

    def test_from_config_with_offset(self):
        """测试从配置创建校准器。"""
        calibrator = self.CoordinateCalibrator.from_config([50, -30])
        assert calibrator.offset_x == 50
        assert calibrator.offset_y == -30

    def test_from_config_no_offset(self):
        """测试从配置创建校准器（无偏移）。"""
        calibrator = self.CoordinateCalibrator.from_config(None)
        assert calibrator.offset_x == 0
        assert calibrator.offset_y == 0

    def test_from_config_empty_list(self):
        """测试从配置创建校准器（空列表）。"""
        calibrator = self.CoordinateCalibrator.from_config([])
        assert calibrator.offset_x == 0
        assert calibrator.offset_y == 0
