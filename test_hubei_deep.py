#!/usr/bin/env python3
"""湖北省政府采购网深度测试 - 搜索和数据提取"""

import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from trendradar.crawler.agent_browser import AgentBrowser

print("=" * 80)
print("湖北省政府采购网深度测试")
print("网址: http://www.ccgp-hubei.gov.cn/")
print("=" * 80)
print()

try:
    # 创建浏览器实例
    print("步骤1: 创建浏览器实例...")
    browser = AgentBrowser(
        session_name="hubei_deep",
        headless=True,
        timeout=60000
    )
    print(f"  ✓ {browser}")
    print()

    # 访问湖北省政府采购网
    print("步骤2: 访问湖北省政府采购网...")
    url = "http://www.ccgp-hubei.gov.cn/"
    browser.goto(url)
    print("  ✓ 页面加载完成")
    print()

    # 等待页面稳定
    print("步骤3: 等待页面稳定...")
    browser.wait(3000)
    print("  ✓ 等待完成")
    print()

    # 获取页面快照
    print("步骤4: 获取页面快照...")
    snapshot = browser.snapshot(interactive_only=True)
    elements = snapshot.get("elements", [])
    print(f"  ✓ 找到 {len(elements)} 个可交互元素")
    print()

    # 保存完整快照
    snapshot_file = "hubei_deep_snapshot.json"
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 完整快照已保存: {snapshot_file}")
    print()

    # 分析元素
    print("步骤5: 分析页面元素...")
    print()

    # 统计元素类型
    role_stats = {}
    for elem in elements:
        role = elem.get("role", "unknown")
        role_stats[role] = role_stats.get(role, 0) + 1

    print("  📊 元素类型统计:")
    for role, count in sorted(role_stats.items(), key=lambda x: -x[1]):
        print(f"    {role}: {count} 个")
    print()

    # 查找关键功能元素
    print("  🔍 查找关键元素:")
    print()

    # 搜索相关
    search_elements = []
    # 导航链接
    nav_links = []
    # 按钮
    buttons = []
    # 输入框
    inputs = []

    for elem in elements:
        role = elem.get("role", "")
        name = elem.get("name", "")
        placeholder = elem.get("placeholder", "")
        ref = elem.get("ref", "")

        # 搜索相关
        if any(kw in name.lower() or kw in placeholder.lower()
               for kw in ["搜索", "查询", "关键", "search", "keyword"]):
            search_elements.append(elem)

        # 导航链接
        if role == "link":
            nav_links.append(elem)

        # 按钮
        if role == "button":
            buttons.append(elem)

        # 输入框
        if role in ["textbox", "searchbox"]:
            inputs.append(elem)

    # 输出搜索元素
    print(f"  📝 输入框: {len(inputs)} 个")
    for elem in inputs[:10]:
        ref = elem.get("ref", "")
        name = elem.get("name", "")
        placeholder = elem.get("placeholder", "")
        print(f"    {ref}: {name or placeholder or '(无标签)'}")
    if len(inputs) > 10:
        print(f"    ... 还有 {len(inputs) - 10} 个")
    print()

    print(f"  🔘 按钮: {len(buttons)} 个")
    for elem in buttons[:10]:
        ref = elem.get("ref", "")
        name = elem.get("name", "")
        print(f"    {ref}: {name}")
    if len(buttons) > 10:
        print(f"    ... 还有 {len(buttons) - 10} 个")
    print()

    print(f"  🔗 导航链接: {len(nav_links)} 个")
    # 只显示招标相关的链接
    tender_links = [e for e in nav_links if any(kw in e.get("name", "")
                    for kw in ["招标", "采购", "公告", "结果", "中标"])]
    for elem in tender_links[:15]:
        ref = elem.get("ref", "")
        name = elem.get("name", "")
        print(f"    {ref}: {name}")
    if len(tender_links) > 15:
        print(f"    ... 还有 {len(tender_links) - 15} 个招标相关链接")
    print()

    # 显示所有元素详情（限制前50个，避免输出太长）
    print("=" * 80)
    print("前50个可交互元素详情")
    print("=" * 80)
    print()

    for i, elem in enumerate(elements[:50], 1):
        ref = elem.get("ref", "")
        role = elem.get("role", "")
        name = elem.get("name", "")
        placeholder = elem.get("placeholder", "")

        display_name = name or placeholder or "(无名称)"
        # 截断过长的名称
        if len(display_name) > 40:
            display_name = display_name[:37] + "..."

        print(f"{i:2}. {ref:6} | {role:12} | {display_name}")

    if len(elements) > 50:
        print()
        print(f"... 还有 {len(elements) - 50} 个元素（详见 {snapshot_file}）")

    print()

    # 尝试查找搜索功能
    print("=" * 80)
    print("搜索功能分析")
    print("=" * 80)
    print()

    # 查找可能的搜索输入框
    search_input = None
    search_button = None

    for elem in elements:
        role = elem.get("role", "")
        name = elem.get("name", "")
        placeholder = elem.get("placeholder", "")

        # 查找搜索输入框
        if role in ["textbox", "searchbox"]:
            if any(kw in name.lower() or kw in placeholder.lower()
                   for kw in ["搜索", "关键", "keyword", "查询", "请输入"]):
                search_input = elem
                print(f"  ✅ 找到搜索输入框: {elem.get('ref')}")
                print(f"     角色: {role}")
                print(f"     名称: {name or placeholder or '(无名称)'}")
                print()
                break

    # 查找搜索按钮
    for elem in elements:
        role = elem.get("role", "")
        name = elem.get("name", "")

        if role == "button":
            if any(kw in name for kw in ["搜索", "查询", "search"]):
                search_button = elem
                print(f"  ✅ 找到搜索按钮: {elem.get('ref')}")
                print(f"     名称: {name}")
                print()
                break

    if not search_input:
        print("  ⚠️  未找到明显的搜索输入框")
        print("     （可能需要先点击某个导航链接进入搜索页面）")
        print()

    if not search_button:
        print("  ⚠️  未找到明显的搜索按钮")
        print("     （可能按Enter键即可搜索）")
        print()

    if search_input:
        print("  💡 可以尝试的自动化操作:")
        print(f"     browser.fill('{search_input.get('ref')}', '软件开发')")
        if search_button:
            print(f"     browser.click('{search_button.get('ref')}')")
        else:
            print("     browser.press('Enter')")
        print("     browser.wait(2000)")
        print("     results = browser.snapshot()")
        print()

    # 关闭浏览器
    print("=" * 80)
    print("测试完成")
    print("=" * 80)
    browser.close()
    print("✓ 浏览器已关闭")
    print()

    print("📋 总结:")
    print(f"  - 可交互元素: {len(elements)} 个")
    print(f"  - 输入框: {len(inputs)} 个")
    print(f"  - 按钮: {len(buttons)} 个")
    print(f"  - 链接: {len(nav_links)} 个")
    print(f"  - 招标相关链接: {len(tender_links)} 个")
    print(f"  - 快照文件: {snapshot_file}")
    print()
    print("🎯 下一步:")
    print("  1. 查看快照文件了解完整页面结构")
    print("  2. 根据元素引用编写自动化搜索脚本")
    print("  3. 测试数据提取功能")

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
