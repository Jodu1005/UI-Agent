"""UI-Agent API 测试客户端。"""

import json
import time

import requests


def test_intent_api(
    message: str,
    execute: bool = True,
    base_url: str = "http://127.0.0.1:8000",
) -> dict:
    """测试意图识别 API。

    Args:
        message: 用户消息
        execute: 是否执行任务
        base_url: API 服务器地址

    Returns:
        API 响应
    """
    url = f"{base_url}/api/intent"

    payload = {"message": message, "execute": execute}

    print(f"\n{'='*60}")
    print(f"请求: {message}")
    print(f"{'='*60}")

    start_time = time.time()
    response = requests.post(url, json=payload, timeout=60)
    duration = (time.time() - start_time) * 1000

    result = response.json()

    print(f"\n响应 (耗时 {duration:.0f}ms):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return result


def test_health_check(base_url: str = "http://127.0.0.1:8000"):
    """测试健康检查接口。"""
    url = f"{base_url}/api/health"
    response = requests.get(url)
    print(f"健康检查: {response.json()}")


def test_list_intents(base_url: str = "http://127.0.0.1:8000"):
    """测试列出所有意图接口。"""
    url = f"{base_url}/api/intents"
    response = requests.get(url)
    intents = response.json()
    print(f"\n可用意图 ({len(intents['intents'])} 个):")
    for intent in intents["intents"]:
        print(f"  - {intent['name']}: {intent['description']}")


def main():
    """主测试函数。"""
    import argparse

    parser = argparse.ArgumentParser(description="UI-Agent API 测试客户端")
    parser.add_argument(
        "--url", default="http://127.0.0.1:8000", help="API 服务器地址"
    )
    parser.add_argument("--message", help="要测试的消息")
    parser.add_argument("--no-execute", action="store_true", help="仅识别意图，不执行")
    args = parser.parse_args()

    print("=" * 60)
    print("UI-Agent API 测试客户端")
    print("=" * 60)
    print(f"API 服务器: {args.url}")

    # 健康检查
    print("\n[1] 健康检查...")
    try:
        test_health_check(args.url)
    except Exception as e:
        print(f"错误: {e}")
        print("请确保 API 服务器正在运行: python -m src.api.app")
        return

    # 列出所有意图
    print("\n[2] 列出所有意图...")
    test_list_intents(args.url)

    # 测试用例
    if args.message:
        # 使用用户指定的消息
        test_intent_api(args.message, execute=not args.no_execute, base_url=args.url)
    else:
        # 默认测试用例
        print("\n[3] 测试意图识别...")

        test_cases = [
            # 单场景 - IDE
            ("帮我开发一个购物车功能", True),
            # 单场景 - 浏览器
            ("帮我查看 https://github.com/zhaohuijuan2017/UI-Agent/issues/4 的需求详情", True),
            # 组合场景
            ("查看 https://jira.example.com/PROJ-123 的需求并开发", False),
        ]

        for message, execute in test_cases:
            test_intent_api(message, execute=execute, base_url=args.url)
            time.sleep(1)  # 避免 API 速率限制

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
