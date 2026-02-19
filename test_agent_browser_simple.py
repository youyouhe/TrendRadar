#!/usr/bin/env python3
# coding=utf-8
"""
AgentBrowser 简单测试 - 使用可靠的测试网站

测试网站: httpbin.org (HTTP 测试服务)
"""

import sys
from trendradar.crawler.agent_browser import AgentBrowser


def test_basic_navigation():
    """测试基础导航功能"""
    print("=" * 60)
    print("AgentBrowser 基础功能测试")
    print("=" * 60)
    print()

    try:
        # 测试1：创建浏览器实例
        print("测试1: 创建浏览器实例...")
        browser = AgentBrowser(
            session_name=f"test_{int(__import__('time').time())}",
            headless=True
        )
        print(f"  ✓ 实例创建成功: {browser}")
        print()

        # 测试2：访问简单网站
        print("测试2: 访问 httpbin.org...")
        try:
            browser.goto("https://httpbin.org/")
            print("  ✓ 页面加载成功")
        except Exception as e:
            print(f"  ✗ 页面加载失败: {e}")
            return False

        # 测试3：等待页面稳定
        print()
        print("测试3: 等待页面稳定...")
        browser.wait(2000)
        print("  ✓ 等待完成")

        # 测试4：获取快照
        print()
        print("测试4: 获取页面快照...")
        try:
            snapshot = browser.snapshot(interactive_only=True)
            elements = snapshot.get("elements", [])
            print(f"  ✓ 快照获取成功")
            print(f"  ✓ 找到 {len(elements)} 个可交互元素")

            # 显示前3个元素
            if elements:
                print()
                print("  前3个元素:")
                for elem in elements[:3]:
                    role = elem.get("role", "")
                    name = elem.get("name", "")
                    ref = elem.get("ref", "")
                    print(f"    - {ref}: {role} '{name}'")
        except Exception as e:
            print(f"  ✗ 快照获取失败: {e}")
            return False

        # 测试5：关闭浏览器
        print()
        print("测试5: 关闭浏览器...")
        browser.close()
        print("  ✓ 浏览器已关闭")

        print()
        print("=" * 60)
        print("✅ 所有测试通过！agent-browser 工作正常")
        print("=" * 60)
        return True

    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


def test_chinese_website():
    """测试访问中文网站（百度）"""
    print()
    print("=" * 60)
    print("测试访问中文网站 - 百度")
    print("=" * 60)
    print()

    try:
        browser = AgentBrowser(
            session_name=f"baidu_{int(__import__('time').time())}",
            headless=True
        )

        print("访问 https://www.baidu.com ...")
        browser.goto("https://www.baidu.com")
        browser.wait(2000)
        print("  ✓ 百度首页加载成功")

        print()
        print("获取快照...")
        snapshot = browser.snapshot(interactive_only=True)
        elements = snapshot.get("elements", [])
        print(f"  ✓ 找到 {len(elements)} 个可交互元素")

        # 查找搜索框
        search_box = None
        for elem in elements:
            if elem.get("role") == "searchbox" or "搜索" in elem.get("name", ""):
                search_box = elem
                break

        if search_box:
            print(f"  ✓ 找到搜索框: {search_box.get('ref')} - {search_box.get('name')}")
        else:
            print("  ⚠️  未找到搜索框（可能是因为页面结构）")

        browser.close()

        print()
        print("✅ 中文网站测试完成")
        return True

    except Exception as e:
        print(f"  ✗ 中文网站测试失败: {e}")
        return False


if __name__ == "__main__":
    success1 = test_basic_navigation()
    success2 = test_chinese_website()

    if success1 and success2:
        print()
        print("🎉 agent-browser 完全正常工作！")
        print("   可以继续测试招标网站")
        sys.exit(0)
    else:
        print()
        print("⚠️  部分测试失败，请检查:")
        print("   1. agent-browser 是否正确安装")
        print("   2. 网络连接是否正常")
        print("   3. 浏览器是否可以启动")
        sys.exit(1)
