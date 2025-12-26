"""意图类型单元测试。"""

import pytest

from src.parser.intents import IntentType, INTENT_KEYWORDS


class TestIntentType:
    """测试 IntentType 枚举。"""

    def test_input_intent_exists(self):
        """测试 INPUT 意图类型存在。"""
        assert IntentType.INPUT is not None
        assert IntentType.INPUT.value == "input"

    def test_input_keywords_defined(self):
        """测试 INPUT 意图关键词已定义。"""
        assert IntentType.INPUT in INTENT_KEYWORDS
        keywords = INTENT_KEYWORDS[IntentType.INPUT]
        assert "输入" in keywords
        assert "输入文本" in keywords
        assert "在输入框中输入" in keywords

    def test_all_intents_have_keywords(self):
        """测试所有意图类型都有关键词映射。"""
        for intent in IntentType:
            if intent != IntentType.UNKNOWN:
                assert intent in INTENT_KEYWORDS, f"{intent} 缺少关键词映射"


class TestIntentKeywordMatching:
    """测试意图关键词匹配。"""

    @pytest.mark.parametrize(
        "text, should_match",
        [
            ("输入", True),
            ("输入文本", True),
            ("在输入框中输入", True),
            ("input", True),
            ("type", True),
            ("enter", True),
        ],
    )
    def test_input_keywords_match(self, text, should_match):
        """测试输入关键词能匹配到 INPUT 意图。"""
        text_lower = text.lower()
        input_keywords = INTENT_KEYWORDS[IntentType.INPUT]
        has_match = any(keyword in text_lower for keyword in input_keywords)
        assert has_match == should_match, f"文本 '{text}' 匹配结果应为 {should_match}"

    def test_non_input_text_no_match(self):
        """测试非输入相关文本不匹配 INPUT 意图。"""
        text = "打开文件 main.py"
        text_lower = text.lower()

        # 不应该匹配 INPUT 意图
        input_keywords = INTENT_KEYWORDS[IntentType.INPUT]
        assert not any(keyword in text_lower for keyword in input_keywords)

    def test_input_keyword_priority(self):
        """测试"输入"关键词的优先级。

        注意：由于关键词可能重叠（如"搜索"既是 SEARCH 也是 INPUT 的一部分），
        实际意图识别取决于关键词在 INTENT_KEYWORDS 中的顺序。
        """
        text = "请输入用户名"
        text_lower = text.lower()

        # 应该能匹配到 INPUT 意图（因为包含"输入"）
        input_keywords = INTENT_KEYWORDS[IntentType.INPUT]
        assert any(keyword in text_lower for keyword in input_keywords)