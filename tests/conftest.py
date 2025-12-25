"""测试配置和共享 fixtures。"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PIL import Image

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_config_dir():
    """创建临时配置目录。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config(temp_config_dir):
    """创建模拟配置文件。"""
    # 主配置文件
    config_file = temp_config_dir / "main.yaml"
    config_content = """
system:
  log_level: INFO
  log_file: logs/test.log
  screenshot_dir: /tmp/screenshots/

ide:
  name: test_ide
  config_path: test_operations.yaml

api:
  zhipuai_api_key: test_api_key
  model: glm-4v-flash
  timeout: 30

automation:
  default_timeout: 5.0
  max_retries: 3
  retry_delay: 1.0
  action_delay: 0.2

safety:
  dangerous_operations: []
  require_confirmation: false
  enable_undo: false
"""
    config_file.write_text(config_content, encoding="utf-8")

    # 操作配置文件
    op_file = temp_config_dir / "test_operations.yaml"
    op_content = """
ide: test_ide
version: ">=1.0"

operations:
  - name: test_operation
    aliases: [test op]
    intent: edit
    description: 测试操作
    visual_prompt: "找到测试元素"
    actions:
      - type: click
        target: "0"
        timeout: 1.0
    requires_confirmation: false
"""
    op_file.write_text(op_content, encoding="utf-8")

    yield config_file


@pytest.fixture
def mock_screenshot():
    """创建模拟截图。"""
    # 创建一个简单的测试图像（1920x1080）
    img = Image.new("RGB", (1920, 1080), color="white")
    return img


@pytest.fixture
def mock_ocr_result():
    """模拟 OCR 返回结果。"""
    return [
        (
            [[100, 100], [200, 100], [200, 120], [100, 120]],  # bbox
            "test.py",  # text
            0.95,  # confidence
        )
    ]


@pytest.fixture
def mock_glm_response():
    """模拟 GLM API 返回结果。"""
    return {
        "choices": [
            {
                "message": {
                    "content": '''
[
  {
    "element_type": "tree",
    "description": "文件树节点 'main.py'",
    "bbox": [100, 200, 300, 250],
    "confidence": 0.95
  }
]
'''
                }
            }
        ]
    }


@pytest.fixture
def mock_api_key():
    """模拟 API key。"""
    return os.environ.get("ZHIPUAI_API_KEY", "test_api_key")


@pytest.fixture
def sample_operation_config():
    """示例操作配置。"""
    return {
        "name": "test_operation",
        "aliases": ["测试操作", "test op"],
        "intent": "edit",
        "description": "测试操作描述",
        "visual_prompt": "在截图中找到测试元素",
        "actions": [
            {
                "type": "click",
                "target": "0",
                "parameters": None,
                "timeout": 1.0,
                "retry": 3,
            }
        ],
        "requires_confirmation": False,
        "risk_level": "low",
    }
