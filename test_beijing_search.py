#!/usr/bin/env python3
"""北京市政府采购网 - 自动化搜索测试"""

import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from trendradar.crawler.agent_browser import AgentBrowser

print("=" * 80)
print("北京市政府采购网 - 自动化搜索测试")
print("=" * 80)
print()

# 搜索关键词
SEARCH_KEYWORD = "软件开发"

try:
    # 创建浏览器实例
    print("步骤1: 创建浏览器实例...")
    browser = AgentBrowser(
        session_name="beijing_search",
        headless=True,
        timeout=60000
    )
    print(f"  ✓ {browser}")
    print()

    # 预热浏览器
    print("步骤2: 预热浏览器...")
    browser.goto("https://example.com/")
    browser.wait(1000)
    print("  ✓ 预热完成")
    print()

    # 访问北京市政府采购网
    print("步骤3: 访问北京市政府采购网...")
    browser.goto("http://www.ccgp-beijing.gov.cn/")
    browser.wait(2000)
    print("  ✓ 页面加载完成")
    print()

    # 输入搜索关键词
    print(f"步骤4: 输入搜索关键词 '{SEARCH_KEYWORD}'...")
    # 使用语义化定位器：placeholder="请输入搜索内容"
    browser.fill(placeholder="请输入搜索内容", value=SEARCH_KEYWORD)
    browser.wait(500)
    print("  ✓ 关键词已输入")
    print()

    # 按 Enter 键搜索
    print("步骤5: 按 Enter 键搜索...")
    browser.press("Enter")
    browser.wait(3000)  # 等待搜索结果加载
    print("  ✓ 搜索完成")
    print()

    # 获取搜索结果页面快照
    print("步骤6: 获取搜索结果页面...")
    results_snapshot = browser.snapshot(interactive_only=True)
    result_elements = results_snapshot.get("elements", [])
    print(f"  ✓ 找到 {len(result_elements)} 个可交互元素")
    print()

    # 保存搜索结果快照
    results_file = "beijing_search_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results_snapshot, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 搜索结果已保存: {results_file}")
    print()

    # 分析搜索结果
    print("步骤7: 分析搜索结果...")
    print()

    # 统计元素类型
    role_stats = {}
    for elem in result_elements:
        role = elem.get("role", "unknown")
        role_stats[role] = role_stats.get(role, 0) + 1

    print("  📊 元素类型统计:")
    for role, count in sorted(role_stats.items(), key=lambda x: -x[1]):
        print(f"    {role}: {count} 个")
    print()

    # 查找招标项目链接
    tender_links = []
    for elem in result_elements:
        role = elem.get("role", "")
        name = elem.get("name", "")

        if role == "link":
            # 招标项目通常包含这些关键词
            if any(kw in name for kw in ["招标", "采购", "公告", "中标", "项目", SEARCH_KEYWORD]):
                tender_links.append(elem)

    print(f"  🔍 找到 {len(tender_links)} 个相关招标项目链接")
    print()

    if tender_links:
        print("  📋 前10个招标项目:")
        for i, elem in enumerate(tender_links[:10], 1):
            ref = elem.get("ref", "")
            name = elem.get("name", "")
            # 截断过长的标题
            if len(name) > 60:
                name = name[:57] + "..."
            print(f"    {i:2}. {ref:6} | {name}")

        if len(tender_links) > 10:
            print(f"    ... 还有 {len(tender_links) - 10} 个项目")
        print()

        # 演示：点击第一个项目查看详情
        if len(tender_links) > 0:
            first_project = tender_links[0]
            first_ref = first_project.get("ref")
            first_name = first_project.get("name")

            print(f"  💡 演示：点击第一个项目查看详情")
            print(f"     项目: {first_name}")
            print(f"     引用: {first_ref}")
            print()

            print("  步骤8: 点击项目查看详情...")
            browser.click(first_ref)
            browser.wait(3000)
            print("  ✓ 详情页已加载")
            print()

            # 获取详情页快照
            print("  步骤9: 获取详情页内容...")
            detail_snapshot = browser.snapshot(interactive_only=False)  # 获取所有元素
            detail_elements = detail_snapshot.get("elements", [])
            print(f"  ✓ 找到 {len(detail_elements)} 个元素")
            print()

            # 保存详情页快照
            detail_file = "beijing_project_detail.json"
            with open(detail_file, "w", encoding="utf-8") as f:
                json.dump(detail_snapshot, f, ensure_ascii=False, indent=2)
            print(f"  ✓ 详情页已保存: {detail_file}")
            print()

            # 显示详情页元素
            print("  📄 详情页前20个元素:")
            for i, elem in enumerate(detail_elements[:20], 1):
                ref = elem.get("ref", "")
                role = elem.get("role", "")
                name = elem.get("name", "")
                if name:
                    if len(name) > 50:
                        name = name[:47] + "..."
                    print(f"    {i:2}. {ref:6} | {role:12} | {name}")

            if len(detail_elements) > 20:
                print(f"    ... 还有 {len(detail_elements) - 20} 个元素")
            print()

    else:
        print("  ⚠️  未找到相关招标项目链接")
        print()
        print("  显示搜索结果页前20个元素:")
        for i, elem in enumerate(result_elements[:20], 1):
            ref = elem.get("ref", "")
            role = elem.get("role", "")
            name = elem.get("name", "")
            if name:
                if len(name) > 50:
                    name = name[:47] + "..."
                print(f"    {i:2}. {ref:6} | {role:12} | {name}")
        print()

    # 关闭浏览器
    print("=" * 80)
    print("测试完成")
    print("=" * 80)
    browser.close()
    print("✓ 浏览器已关闭")
    print()

    print("📋 总结:")
    print(f"  - 搜索关键词: {SEARCH_KEYWORD}")
    print(f"  - 搜索结果元素: {len(result_elements)} 个")
    print(f"  - 相关项目链接: {len(tender_links)} 个")
    if tender_links:
        print(f"  - 详情页元素: {len(detail_elements)} 个")
    print()
    print("📁 保存的文件:")
    print(f"  - {results_file} (搜索结果页)")
    if tender_links:
        print(f"  - {detail_file} (项目详情页)")
    print()
    print("🎯 下一步:")
    print("  1. 查看保存的JSON文件了解页面结构")
    print("  2. 编写数据提取函数（标题、金额、日期等）")
    print("  3. 实现批量采集和存储")

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
