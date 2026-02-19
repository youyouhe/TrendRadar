#!/usr/bin/env python3
"""测试多个招标网站的可访问性"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from trendradar.crawler.agent_browser import AgentBrowser

# 测试网站列表
test_sites = [
    {
        "name": "山东省政府采购网",
        "url": "http://www.ccgp-shandong.gov.cn/home",
        "备注": "山东省政府采购官网"
    },
    {
        "name": "山东省公共资源交易平台",
        "url": "http://ggzy.shandong.gov.cn/",
        "备注": "旧地址（可能已失效）"
    },
    {
        "name": "中国政府采购网",
        "url": "http://www.ccgp.gov.cn/",
        "备注": "国家级采购网"
    },
    {
        "name": "中国招标投标公共服务平台",
        "url": "http://www.cebpubservice.com/",
        "备注": "国家级招标平台"
    },
    {
        "name": "全国公共资源交易平台",
        "url": "http://www.ggzyfw.gov.cn/",
        "备注": "国家级资源交易平台"
    },
    {
        "name": "Example.com（对照组）",
        "url": "https://example.com/",
        "备注": "国际测试网站，验证网络基本连接"
    },
]

print("=" * 70)
print("招标网站可访问性测试")
print("=" * 70)
print()

browser = None
results = []

try:
    # 创建浏览器实例（复用同一个实例）
    print("创建浏览器实例...")
    browser = AgentBrowser(
        session_name="site_test",
        headless=True,
        timeout=30000  # 30秒超时
    )
    print(f"✓ {browser}")
    print()

    for i, site in enumerate(test_sites, 1):
        name = site["name"]
        url = site["url"]
        note = site["备注"]

        print(f"[{i}/{len(test_sites)}] 测试: {name}")
        print(f"    URL: {url}")
        print(f"    备注: {note}")

        try:
            browser.goto(url)
            browser.wait(2000)  # 等待2秒

            # 尝试获取快照
            snapshot = browser.snapshot(interactive_only=True)
            element_count = len(snapshot.get("elements", []))

            print(f"    ✅ 成功访问！找到 {element_count} 个可交互元素")
            results.append({
                "name": name,
                "url": url,
                "status": "成功",
                "elements": element_count
            })

        except Exception as e:
            error_msg = str(e)

            # 提取关键错误信息
            if "ERR_NAME_NOT_RESOLVED" in error_msg:
                error_type = "DNS解析失败"
            elif "ERR_CONNECTION_REFUSED" in error_msg:
                error_type = "连接被拒绝"
            elif "ERR_CONNECTION_TIMED_OUT" in error_msg:
                error_type = "连接超时"
            elif "ERR_SSL" in error_msg:
                error_type = "SSL证书错误"
            elif "timeout" in error_msg.lower():
                error_type = "超时"
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

except KeyboardInterrupt:
    print()
    print("⚠️  用户中断测试")

except Exception as e:
    print()
    print(f"❌ 测试异常: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

finally:
    if browser:
        try:
            browser.close()
            print("✓ 浏览器已关闭")
            print()
        except:
            pass

# 输出汇总
print("=" * 70)
print("测试结果汇总")
print("=" * 70)
print()

success_count = sum(1 for r in results if r["status"] == "成功")
fail_count = len(results) - success_count

print(f"总共测试: {len(results)} 个网站")
print(f"成功: {success_count} 个")
print(f"失败: {fail_count} 个")
print()

if success_count > 0:
    print("✅ 可访问的网站:")
    for r in results:
        if r["status"] == "成功":
            print(f"  - {r['name']}")
            print(f"    {r['url']}")
            print(f"    元素数量: {r['elements']}")
            print()

if fail_count > 0:
    print("❌ 无法访问的网站:")
    for r in results:
        if r["status"] != "成功":
            print(f"  - {r['name']}: {r['status']}")
            print(f"    {r['url']}")
            print()

# 给出建议
print("=" * 70)
print("建议:")
print("=" * 70)

if success_count == 0:
    print("⚠️  所有网站都无法访问，可能的原因:")
    print("  1. 网络连接问题")
    print("  2. 防火墙或代理设置")
    print("  3. 需要在中国大陆网络环境访问")
    print()
    print("建议:")
    print("  - 检查网络连接")
    print("  - 在浏览器中手动访问这些网址")
    print("  - 确认是否需要VPN或特定网络环境")
elif success_count < len(results):
    print("✓ 部分网站可访问，建议:")
    print("  1. 使用成功访问的网站进行测试")
    print("  2. 检查失败网站的URL是否已变更")
    print("  3. 在浏览器中手动验证失败的网址")
else:
    print("✅ 所有网站都可访问！可以选择任意网站进行自动化测试")
