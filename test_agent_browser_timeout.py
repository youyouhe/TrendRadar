#!/usr/bin/env python3
"""测试 agent-browser 带超时控制"""

import sys
import time
import signal
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from trendradar.crawler.agent_browser import AgentBrowser

def timeout_handler(signum, frame):
    raise TimeoutError("操作超时")

print("=" * 60)
print("AgentBrowser 超时测试")
print("=" * 60)
print()

# Windows 上需要用不同的方式处理超时
def test_with_timeout(func, timeout_seconds=30):
    """执行函数，如果超时则抛出异常"""
    import threading

    result = [None]
    exception = [None]

    def wrapper():
        try:
            result[0] = func()
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)

    if thread.is_alive():
        print(f"  ✗ 操作超时 ({timeout_seconds}秒)")
        return None

    if exception[0]:
        raise exception[0]

    return result[0]

try:
    # 测试1: 创建实例
    print("测试1: 创建浏览器实例...")
    print("  (超时: 10秒)")

    browser = test_with_timeout(
        lambda: AgentBrowser(headless=True),
        timeout_seconds=10
    )

    if browser is None:
        print("  创建实例超时，可能 daemon 启动很慢")
        sys.exit(1)

    print(f"  ✓ 实例创建成功: {browser}")
    print()

    # 测试2: 简单导航
    print("测试2: 访问 example.com...")
    print("  (超时: 30秒)")

    def navigate_test():
        browser.goto("https://example.com")
        return browser.snapshot()

    snapshot = test_with_timeout(navigate_test, timeout_seconds=30)

    if snapshot is None:
        print("  导航超时")
    else:
        print(f"  ✓ 导航成功")
        print(f"  页面标题: {snapshot.get('title', 'N/A')}")
        print(f"  元素数量: {len(snapshot.get('elements', []))}")

    print()

    # 测试3: 快速测试
    print("测试3: 快速快照测试...")
    print("  (超时: 20秒)")

    def quick_snapshot():
        return browser.snapshot()

    snapshot2 = test_with_timeout(quick_snapshot, timeout_seconds=20)

    if snapshot2 is None:
        print("  快照超时")
    else:
        print(f"  ✓ 快照成功: {len(snapshot2.get('elements', []))} 个元素")

    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)

except KeyboardInterrupt:
    print()
    print("用户中断测试")
    sys.exit(1)

except Exception as e:
    print(f"  ✗ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
