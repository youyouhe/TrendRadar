#!/usr/bin/env python3
"""测试全国各省政府采购网站可访问性"""

import sys
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from trendradar.crawler.agent_browser import AgentBrowser

# 全国各省政府采购网站列表
test_sites = [
    # 国家级平台
    {"region": "国家", "name": "中国政府采购网", "url": "http://www.ccgp.gov.cn/"},
    {"region": "国家", "name": "全国公共资源交易平台", "url": "http://ggzy.gov.cn/"},

    # 华东地区（优先测试，网络通常较好）
    {"region": "上海", "name": "上海市政府采购网", "url": "http://www.ccgp-shanghai.gov.cn/"},
    {"region": "浙江", "name": "浙江政府采购网", "url": "http://www.ccgp-zhejiang.gov.cn/"},
    {"region": "江苏", "name": "江苏省政府采购网", "url": "http://www.ccgp-jiangsu.gov.cn/"},
    {"region": "安徽", "name": "安徽省政府采购网", "url": "http://www.ccgp-anhui.gov.cn/"},
    {"region": "福建", "name": "福建省政府采购网", "url": "http://www.ccgp-fujian.gov.cn/"},

    # 华南地区
    {"region": "广东", "name": "广东省政府采购网", "url": "https://gdgpo.czt.gd.gov.cn/"},
    {"region": "广西", "name": "广西政府采购网", "url": "http://www.ccgp-guangxi.gov.cn/"},

    # 华北地区
    {"region": "北京", "name": "北京市政府采购网", "url": "http://www.ccgp-beijing.gov.cn/"},
    {"region": "天津", "name": "天津市政府采购网", "url": "http://www.ccgp-tianjin.gov.cn/"},
    {"region": "河北", "name": "河北省政府采购网", "url": "http://www.ccgp-hebei.gov.cn/"},

    # 华中地区
    {"region": "湖北", "name": "湖北省政府采购网", "url": "http://www.ccgp-hubei.gov.cn/"},
    {"region": "湖南", "name": "湖南省政府采购网", "url": "http://www.ccgp-hunan.gov.cn/"},
    {"region": "河南", "name": "河南省政府采购网", "url": "http://www.ccgp-henan.gov.cn/"},

    # 西南地区
    {"region": "重庆", "name": "重庆市政府采购网", "url": "http://www.ccgp-chongqing.gov.cn/"},
    {"region": "四川", "name": "四川政府采购网", "url": "http://www.ccgp-sichuan.gov.cn/"},

    # 问题网站（最后测试）
    {"region": "山东", "name": "山东省政府采购网", "url": "http://www.ccgp-shandong.gov.cn/"},
]

print("=" * 80)
print("全国各省政府采购网站可访问性测试")
print("=" * 80)
print()
print(f"总共测试 {len(test_sites)} 个网站")
print("测试策略: 快速测试，超时时间 15 秒")
print()

browser = None
results = []
start_time = time.time()

try:
    # 创建浏览器实例
    print("创建浏览器实例...")
    browser = AgentBrowser(
        session_name="nationwide_test",
        headless=True,
        timeout=15000  # 15秒超时，加快测试速度
    )
    print(f"✓ {browser}")
    print()
    print("-" * 80)

    for i, site in enumerate(test_sites, 1):
        region = site["region"]
        name = site["name"]
        url = site["url"]

        print(f"[{i}/{len(test_sites)}] {region} - {name}")
        print(f"    {url}")

        try:
            browser.goto(url)
            time.sleep(1)  # 等待1秒

            # 尝试获取快照
            snapshot = browser.snapshot(interactive_only=True)
            element_count = len(snapshot.get("elements", []))

            print(f"    ✅ 成功！元素: {element_count} 个")
            results.append({
                "region": region,
                "name": name,
                "url": url,
                "status": "成功",
                "elements": element_count
            })

        except Exception as e:
            error_msg = str(e)

            # 提取关键错误信息
            if "ERR_NAME_NOT_RESOLVED" in error_msg:
                error_type = "DNS失败"
            elif "ERR_CONNECTION_REFUSED" in error_msg:
                error_type = "连接拒绝"
            elif "ERR_CONNECTION_TIMED_OUT" in error_msg or "10060" in error_msg:
                error_type = "连接超时"
            elif "ERR_SSL" in error_msg:
                error_type = "SSL错误"
            elif "timeout" in error_msg.lower() or "超时" in error_msg:
                error_type = "超时"
            else:
                error_type = "未知错误"

            print(f"    ❌ {error_type}")
            results.append({
                "region": region,
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
elapsed = time.time() - start_time
print("=" * 80)
print("测试结果汇总")
print("=" * 80)
print()

success_count = sum(1 for r in results if r["status"] == "成功")
fail_count = len(results) - success_count

print(f"总共测试: {len(results)} 个网站")
print(f"成功: {success_count} 个 ({success_count/len(results)*100:.1f}%)")
print(f"失败: {fail_count} 个 ({fail_count/len(results)*100:.1f}%)")
print(f"总耗时: {elapsed:.1f} 秒")
print()

if success_count > 0:
    print("=" * 80)
    print("✅ 可访问的网站（推荐使用这些网站进行测试）")
    print("=" * 80)
    print()

    for r in results:
        if r["status"] == "成功":
            print(f"【{r['region']}】{r['name']}")
            print(f"  URL: {r['url']}")
            print(f"  可交互元素: {r['elements']} 个")
            print()

if fail_count > 0:
    print("=" * 80)
    print("❌ 无法访问的网站")
    print("=" * 80)
    print()

    # 按错误类型分组
    error_groups = {}
    for r in results:
        if r["status"] != "成功":
            error_type = r["status"]
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(r)

    for error_type, sites in error_groups.items():
        print(f"{error_type}: {len(sites)} 个")
        for r in sites:
            print(f"  - {r['region']} - {r['name']}")
        print()

print("=" * 80)
print("下一步建议")
print("=" * 80)

if success_count == 0:
    print("⚠️  所有网站都无法访问，可能的原因:")
    print("  1. 网络连接问题或防火墙限制")
    print("  2. 需要特定的网络环境（VPN等）")
    print("  3. Agent-browser 的网络配置问题")
    print()
    print("建议:")
    print("  - 检查网络连接和防火墙设置")
    print("  - 在普通浏览器中手动访问这些网址")
    print("  - 尝试使用非 headless 模式")
elif success_count > 0:
    print("✅ 发现可访问的网站！")
    print()
    print("推荐下一步:")
    print("  1. 选择一个可访问的网站进行深入测试")
    print("  2. 编写自动化搜索和数据提取脚本")
    print("  3. 如果需要访问失败的网站，可以尝试:")
    print("     - 使用非 headless 模式")
    print("     - 配置代理或网络设置")
    print("     - 检查是否有反爬机制")
