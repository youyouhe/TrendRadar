#!/usr/bin/env python3
"""批量采集招标信息 - 完整流程"""

import sys
import json
import os
import time
from pathlib import Path
from openai import OpenAI
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from trendradar.crawler.agent_browser import AgentBrowser

# 尝试从 .env 文件加载环境变量
try:
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 搜索结果列表提取提示词
LIST_PROMPT = """
请从以下招标搜索结果页面HTML中提取项目列表，以JSON格式输出。

要提取的字段（数组，每个项目包含）：
- title: 项目完整标题
- category: 公告类型（从标题中提取，如：公开招标、中标公告、合同公告等）
- region: 所属地区（从标题中提取，如有，如"石景山区"）
- url_hint: 如果能从HTML中找到项目详情页链接，提取链接文本特征（用于后续定位）

只返回JSON数组，不要其他说明文字。提取前10个项目。

HTML内容：
{html_content}
"""

# 详情页提取提示词
DETAIL_PROMPT = """
请从以下招标公告详情页HTML中提取关键信息，以JSON格式输出。

要提取的字段：
- title: 项目标题
- category: 公告类型（招标公告/中标公告/更正公告等）
- project_number: 项目编号/招标编号
- budget: 预算金额（万元，纯数字，如多个包则提取总和）
- publish_date: 发布日期（YYYY-MM-DD格式）
- deadline: 截止日期/开标时间（YYYY-MM-DD HH:MM格式，如有）
- purchaser: 采购人/业主单位名称
- agent: 采购代理机构名称（如有）
- contact_person: 联系人姓名
- contact_phone: 联系电话
- contact_email: 联系邮箱（如有）
- items: 采购项目清单（数组，每项包含 name, quantity, budget，最多5项）
- requirements: 主要技术要求摘要（不超过200字）
- address: 项目地址/实施地点（如有）

如果某个字段在网页中找不到，设为 null。
只返回JSON对象，不要其他说明文字。

HTML内容：
{html_content}
"""


def call_deepseek_api(html_content: str, api_key: str, prompt_template: str) -> dict:
    """调用 DeepSeek API 解析内容"""
    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    prompt = prompt_template.format(html_content=html_content[:30000])

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是专业的政府采购信息提取助手。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    result_text = response.choices[0].message.content
    return json.loads(result_text)


def collect_tenders(keyword: str, api_key: str, max_items: int = 5):
    """
    完整的招标信息采集流程

    Args:
        keyword: 搜索关键词
        api_key: DeepSeek API Key
        max_items: 最多采集多少个项目详情
    """
    print("=" * 80)
    print(f"批量采集招标信息: {keyword}")
    print("=" * 80)
    print()

    browser = None
    results = []

    try:
        # 创建浏览器
        print("步骤1: 创建浏览器实例...")
        browser = AgentBrowser(
            session_name=f"batch_collect_{int(time.time())}",
            headless=True,
            timeout=60000
        )
        print(f"  ✓ {browser}")
        print()

        # 预热
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

        # 搜索
        print(f"步骤4: 搜索关键词 '{keyword}'...")
        browser._run("fill", '[placeholder="请输入搜索内容"]', keyword, capture_output=False)
        browser.press("Enter")
        browser.wait(3000)
        print("  ✓ 搜索完成")
        print()

        # 获取搜索结果页HTML
        print("步骤5: 解析搜索结果列表...")
        search_html = browser.get_content()

        list_result = call_deepseek_api(search_html, api_key, LIST_PROMPT)
        projects = list_result if isinstance(list_result, list) else list_result.get('projects', [])

        print(f"  ✓ 找到 {len(projects)} 个项目")
        print()

        # 保存列表
        with open('batch_collect_list.json', 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)

        # 限制采集数量
        projects_to_collect = projects[:max_items]

        print(f"步骤6: 采集前 {len(projects_to_collect)} 个项目详情...")
        print()

        # 逐个采集详情
        for i, project in enumerate(projects_to_collect, 1):
            title = project.get('title', 'Unknown')
            print(f"  [{i}/{len(projects_to_collect)}] {title[:60]}...")

            try:
                # 方法：在当前搜索结果页，查找包含标题关键词的链接并点击
                # 使用标题的前30个字符作为特征
                title_keyword = title[:30].replace('[', '').replace(']', '')

                # 尝试点击链接
                # 注意：这里使用文本内容定位，agent-browser 支持 text= 语法
                try:
                    # 尝试使用部分标题文本定位链接
                    browser._run("click", f'a:has-text("{title_keyword[:20]}")', capture_output=False)
                    browser.wait(3000)
                except:
                    # 如果失败，尝试备用方案：使用第N个项目链接
                    print(f"    ⚠️  无法通过标题定位，跳过")
                    continue

                # 获取详情页HTML
                detail_html = browser.get_content()

                # 解析详情
                detail = call_deepseek_api(detail_html, api_key, DETAIL_PROMPT)

                # 合并列表信息和详情信息
                result = {**project, **detail, 'collected_at': datetime.now().isoformat()}
                results.append(result)

                print(f"    ✓ 预算: {detail.get('budget', 'N/A')} 万元")
                print(f"    ✓ 采购人: {detail.get('purchaser', 'N/A')}")

                # 返回搜索结果页（点击浏览器后退按钮）
                browser.press("Escape")  # 可能有弹窗
                browser.wait(500)
                # 注意：agent-browser 可能没有 back() 方法，需要重新搜索
                # 这里简化处理：重新访问搜索页面
                browser.goto("http://www.ccgp-beijing.gov.cn/")
                browser.wait(1000)
                browser._run("fill", '[placeholder="请输入搜索内容"]', keyword, capture_output=False)
                browser.press("Enter")
                browser.wait(2000)

            except Exception as e:
                print(f"    ❌ 采集失败: {e}")
                # 尝试恢复到搜索页
                try:
                    browser.goto("http://www.ccgp-beijing.gov.cn/")
                    browser.wait(1000)
                    browser._run("fill", '[placeholder="请输入搜索内容"]', keyword, capture_output=False)
                    browser.press("Enter")
                    browser.wait(2000)
                except:
                    pass

            print()

        # 保存最终结果
        output_file = f"batch_collect_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("=" * 80)
        print("✅ 采集完成！")
        print("=" * 80)
        print()
        print(f"📊 统计:")
        print(f"  - 搜索关键词: {keyword}")
        print(f"  - 找到项目: {len(projects)} 个")
        print(f"  - 成功采集: {len(results)} 个")
        print(f"  - 输出文件: {output_file}")
        print()
        print(f"💰 成本估算:")
        print(f"  - 列表解析: 1次 × ¥0.02 = ¥0.02")
        print(f"  - 详情解析: {len(results)}次 × ¥0.03 = ¥{len(results) * 0.03:.2f}")
        print(f"  - 总成本: ≈ ¥{0.02 + len(results) * 0.03:.2f}")

    except Exception as e:
        print()
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if browser:
            browser.close()
            print()
            print("✓ 浏览器已关闭")


def main():
    # 检查 API Key
    api_key = DEEPSEEK_API_KEY
    if not api_key:
        print("❌ 未找到 DEEPSEEK_API_KEY")
        print("请在 .env 文件中配置")
        return

    # 开始采集
    collect_tenders(
        keyword="软件开发",
        api_key=api_key,
        max_items=3  # 先采集3个测试
    )


if __name__ == '__main__':
    main()
