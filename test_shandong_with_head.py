#!/usr/bin/env python3
"""测试山东省政府采购网 - 使用非 headless 模式绕过反爬"""

import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from trendradar.crawler.agent_browser import AgentBrowser

print("=" * 60)
print("山东省政府采购网测试（非 headless 模式）")
print("网址: http://www.ccgp-shandong.gov.cn/home")
print("=" * 60)
print()
print("⚠️  注意: 这次会弹出浏览器窗口，可以看到真实的访问过程")
print()

try:
    # 创建浏览器实例 - 使用非 headless 模式
    print("步骤1: 创建浏览器实例（有界面模式）...")
    browser = AgentBrowser(
        session_name="shandong_head_test",
        headless=False,  # 关键：使用有界面模式
        timeout=60000
    )
    print(f"  ✓ {browser}")
    print()

    # 访问山东省政府采购网
    print("步骤2: 访问山东省政府采购网...")
    url = "http://www.ccgp-shandong.gov.cn/home"
    print(f"  URL: {url}")
    print("  （浏览器窗口会弹出，请观察）")
    browser.goto(url)
    print("  ✓ 页面加载完成")
    print()

    # 等待页面稳定
    print("步骤3: 等待页面稳定（10秒）...")
    print("  （可以在浏览器窗口中查看页面）")
    browser.wait(10000)
    print("  ✓ 等待完成")
    print()

    # 获取页面快照
    print("步骤4: 获取页面快照...")
    snapshot = browser.snapshot(interactive_only=True)
    elements = snapshot.get("elements", [])
    print(f"  ✓ 找到 {len(elements)} 个可交互元素")
    print()

    # 保存快照
    snapshot_file = "shandong_snapshot_with_head.json"
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 快照已保存到: {snapshot_file}")
    print()

    # 显示前10个元素
    print("步骤5: 前10个可交互元素:")
    for i, elem in enumerate(elements[:10], 1):
        ref = elem.get("ref", "")
        role = elem.get("role", "")
        name = elem.get("name", "")
        placeholder = elem.get("placeholder", "")
        display_name = name or placeholder or "(无名称)"
        print(f"  {i}. {ref}: {role} '{display_name}'")
    print()

    print("=" * 60)
    print("✅ 测试成功！")
    print("=" * 60)
    print()
    print("说明:")
    print("  如果这次成功了，说明网站确实有反爬检测")
    print("  非 headless 模式可以绕过大部分检测")
    print()
    print("按 Enter 键关闭浏览器...")
    input()

    browser.close()
    print("✓ 浏览器已关闭")

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
