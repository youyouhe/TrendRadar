#!/usr/bin/env python3
"""测试山东省政府采购网站 - agent-browser 实战"""

import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from trendradar.crawler.agent_browser import AgentBrowser

print("=" * 60)
print("山东省政府采购网测试")
print("网址: http://www.ccgp-shandong.gov.cn/home")
print("=" * 60)
print()

try:
    # 创建浏览器实例
    print("步骤1: 创建浏览器实例...")
    browser = AgentBrowser(
        session_name="shandong_test",
        headless=True,
        timeout=60000  # 60秒超时
    )
    print(f"  ✓ {browser}")
    print()

    # 访问山东省政府采购网
    print("步骤2: 访问山东省政府采购网...")
    url = "http://www.ccgp-shandong.gov.cn/home"
    print(f"  URL: {url}")
    browser.goto(url)
    print("  ✓ 页面加载完成")
    print()

    # 等待页面稳定
    print("步骤3: 等待页面稳定...")
    browser.wait(3000)
    print("  ✓ 等待完成")
    print()

    # 获取页面快照
    print("步骤4: 获取页面快照（可交互元素）...")
    snapshot = browser.snapshot(interactive_only=True)
    elements = snapshot.get("elements", [])
    print(f"  ✓ 找到 {len(elements)} 个可交互元素")
    print()

    # 保存完整快照到文件
    snapshot_file = "shandong_snapshot.json"
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 完整快照已保存到: {snapshot_file}")
    print()

    # 分析元素类型
    print("步骤5: 分析页面元素...")
    role_stats = {}
    for elem in elements:
        role = elem.get("role", "unknown")
        role_stats[role] = role_stats.get(role, 0) + 1

    print("  元素类型统计:")
    for role, count in sorted(role_stats.items(), key=lambda x: -x[1]):
        print(f"    - {role}: {count} 个")
    print()

    # 查找关键元素
    print("步骤6: 查找关键元素...")

    # 查找搜索相关元素
    search_elements = []
    nav_elements = []

    for elem in elements[:50]:  # 只看前50个元素
        name = elem.get("name", "").lower()
        placeholder = elem.get("placeholder", "").lower()
        role = elem.get("role", "")

        if any(keyword in name or keyword in placeholder for keyword in ["搜索", "查询", "关键", "search"]):
            search_elements.append(elem)

        if role == "link" and any(keyword in name for keyword in ["招标", "采购", "公告", "结果"]):
            nav_elements.append(elem)

    print(f"  ✓ 找到 {len(search_elements)} 个搜索相关元素")
    if search_elements:
        print("    搜索元素:")
        for elem in search_elements[:5]:
            ref = elem.get("ref", "")
            role = elem.get("role", "")
            name = elem.get("name", "")
            placeholder = elem.get("placeholder", "")
            print(f"      {ref}: {role} '{name or placeholder}'")
    print()

    print(f"  ✓ 找到 {len(nav_elements)} 个导航链接")
    if nav_elements:
        print("    导航链接:")
        for elem in nav_elements[:10]:
            ref = elem.get("ref", "")
            name = elem.get("name", "")
            print(f"      {ref}: {name}")
    print()

    # 显示前10个元素
    print("步骤7: 前10个可交互元素:")
    for i, elem in enumerate(elements[:10], 1):
        ref = elem.get("ref", "")
        role = elem.get("role", "")
        name = elem.get("name", "")
        placeholder = elem.get("placeholder", "")
        display_name = name or placeholder or "(无名称)"
        print(f"  {i}. {ref}: {role} '{display_name}'")
    print()

    # 关闭浏览器
    print("步骤8: 关闭浏览器...")
    browser.close()
    print("  ✓ 浏览器已关闭")
    print()

    print("=" * 60)
    print("✅ 山东省政府采购网测试完成！")
    print("=" * 60)
    print()
    print("下一步建议:")
    print("  1. 查看 shandong_snapshot.json 了解页面完整结构")
    print("  2. 根据元素引用（@e1, @e2...）编写自动化脚本")
    print("  3. 测试搜索功能（如果找到了搜索框）")
    print()

except KeyboardInterrupt:
    print()
    print("⚠️  用户中断测试")
    sys.exit(1)

except Exception as e:
    print()
    print(f"❌ 测试失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
