#!/usr/bin/env python3
"""测试会话复用 - 先访问简单网站，再访问政府采购网"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from trendradar.crawler.agent_browser import AgentBrowser

print("=" * 80)
print("会话复用测试")
print("=" * 80)
print()

try:
    # 创建浏览器实例
    print("步骤1: 创建浏览器实例...")
    browser = AgentBrowser(
        session_name="stable_test",  # 使用固定的会话名
        headless=True,
        timeout=60000
    )
    print(f"  ✓ {browser}")
    print()

    # 先访问一个简单的网站，确保浏览器正常工作
    print("步骤2: 预热 - 访问 example.com...")
    browser.goto("https://example.com/")
    browser.wait(2000)
    print("  ✓ 预热成功")
    print()

    # 现在访问政府采购网站
    test_sites = [
        {"name": "湖北省政府采购网", "url": "http://www.ccgp-hubei.gov.cn/"},
        {"name": "安徽省政府采购网", "url": "http://www.ccgp-anhui.gov.cn/"},
        {"name": "北京市政府采购网", "url": "http://www.ccgp-beijing.gov.cn/"},
        {"name": "山东省政府采购网", "url": "http://www.ccgp-shandong.gov.cn/"},
    ]

    print("步骤3: 访问政府采购网站（复用同一个浏览器会话）...")
    print()

    results = []

    for i, site in enumerate(test_sites, 1):
        name = site["name"]
        url = site["url"]

        print(f"[{i}/{len(test_sites)}] 测试: {name}")
        print(f"    URL: {url}")

        try:
            browser.goto(url)
            browser.wait(2000)

            snapshot = browser.snapshot(interactive_only=True)
            element_count = len(snapshot.get("elements", []))

            print(f"    ✅ 成功！元素: {element_count} 个")
            results.append({
                "name": name,
                "url": url,
                "status": "成功",
                "elements": element_count
            })

        except Exception as e:
            error_msg = str(e)
            if "10060" in error_msg or "timeout" in error_msg.lower():
                error_type = "连接超时"
            elif "ERR_NAME_NOT_RESOLVED" in error_msg:
                error_type = "DNS失败"
            else:
                error_type = "未知错误"

            print(f"    ❌ 失败: {error_type}")
            results.append({
                "name": name,
                "url": url,
                "status": f"失败 ({error_type})",
                "elements": 0
            })

        print()

    # 关闭浏览器
    print("步骤4: 关闭浏览器...")
    browser.close()
    print("  ✓ 浏览器已关闭")
    print()

    # 输出汇总
    print("=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print()

    success_count = sum(1 for r in results if r["status"] == "成功")

    if success_count > 0:
        print(f"✅ 成功访问 {success_count}/{len(results)} 个网站")
        print()
        for r in results:
            if r["status"] == "成功":
                print(f"  - {r['name']}: {r['elements']} 个元素")
        print()
        print("💡 结论: 使用同一个浏览器会话复用可以成功访问！")
        print()
        print("下一步:")
        print("  1. 选择一个成功的网站进行深入测试")
        print("  2. 使用相同的会话名策略编写自动化脚本")
    else:
        print("❌ 所有网站都失败了")
        print()
        print("可能的原因:")
        print("  1. 网络环境限制了政府采购网站的访问")
        print("  2. 需要配置代理或特殊网络设置")
        print("  3. agent-browser 的 Chromium 配置问题")

except KeyboardInterrupt:
    print()
    print("⚠️  用户中断测试")
    if browser:
        browser.close()

except Exception as e:
    print()
    print(f"❌ 测试失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    if browser:
        try:
            browser.close()
        except:
            pass
