"""意图识别交互式测试脚本。"""

import os
from zhipuai import ZhipuAI
from src.intent.recognizer import IntentRecognizer
from src.templates.loader import TemplateLoader
from src.templates.engine import TemplateEngine
from src.orchestration.orchestrator import TaskOrchestrator
from src.orchestration.executor import TaskExecutor


def main():
    """主测试函数。"""
    # 设置 API Key
    api_key = os.environ.get("ZHIPUAI_API_KEY", "34eeadd155244053894ffadb2c1999a4.vu8hn2jUQdoGzJ9O")

    # 初始化组件
    llm = ZhipuAI(api_key=api_key)
    recognizer = IntentRecognizer("config/intent_definitions.yaml", llm)
    template_loader = TemplateLoader()
    template_loader.load_from_directory("workflows/templates")
    engine = TemplateEngine()

    print("=" * 60)
    print("Intent Recognition Interactive Test")
    print("=" * 60)

    # 测试用例
    test_cases = [
        "帮我开发一个购物车功能",
        "查看 https://jira.example.com/PROJ-123 的需求并开发",
        "打开浏览器访问 https://www.example.com",
        "帮我查看需求详情",
        "实现用户登录模块",
    ]

    for i, message in enumerate(test_cases, 1):
        print(f"\n[Test {i}] Message: {message}")
        print("-" * 60)

        # 识别意图
        result = recognizer.recognize(message)

        if not result.has_match:
            print("  No intent matched")
            continue

        print(f"  Intent: {result.intent.type}")
        print(f"  Confidence: {result.confidence:.2f}")

        if result.intent.parameters:
            print(f"  Parameters:")
            for key, value in result.intent.parameters.items():
                print(f"    {key}: {value}")

        # 匹配模板
        template = template_loader.get_template_by_intent(result.intent.type)
        if template:
            print(f"  Template: {template.name}")
            print(f"  Steps: {len(template.steps)}")

            # 绑定参数
            bound = engine.bind_parameters(template, result.intent, {})
            for j, step in enumerate(bound.steps):
                print(f"    Step {j}: {step.system}.{step.action}")
                if step.parameters:
                    print(f"      Parameters: {step.parameters}")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
