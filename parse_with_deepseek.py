#!/usr/bin/env python3
"""使用 DeepSeek API 解析招标网页内容，提取结构化数据"""

import sys
import json
import os
from pathlib import Path
from openai import OpenAI

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
        print(f"✓ 从 {env_path} 加载配置")
except ImportError:
    # 如果没有安装 python-dotenv，从环境变量读取
    pass

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 提取提示词
EXTRACTION_PROMPT = """
请从以下招标公告网页HTML中提取关键信息，以JSON格式输出。

要提取的字段：
- title: 项目标题
- category: 公告类型（招标公告/中标公告/更正公告等）
- region: 所属地区（如有）
- budget: 预算金额（万元，数字）
- publish_date: 发布日期（YYYY-MM-DD格式）
- deadline: 截止日期（YYYY-MM-DD格式，如有）
- purchaser: 采购人/业主单位
- agent: 采购代理机构（如有）
- contact_person: 联系人
- contact_phone: 联系电话
- items: 采购项目清单（数组，每项包含 name, quantity, budget）
- requirements: 主要技术要求（摘要，不超过200字）
- attachments: 附件列表（文件名数组）

如果某个字段在网页中找不到，设为 null。
只返回JSON，不要其他说明文字。

HTML内容：
{html_content}
"""


def parse_page_with_deepseek(html_content: str, api_key: str, custom_prompt: str = None) -> dict:
    """
    使用 DeepSeek API 解析网页内容

    Args:
        html_content: 网页HTML内容
        api_key: DeepSeek API密钥
        custom_prompt: 自定义提示词模板（可选，默认使用 EXTRACTION_PROMPT）

    Returns:
        解析后的结构化数据（dict）
    """
    client = OpenAI(
        api_key=api_key,
        base_url=DEEPSEEK_BASE_URL
    )

    # 构建提示词
    prompt_template = custom_prompt or EXTRACTION_PROMPT
    prompt = prompt_template.format(html_content=html_content[:20000])  # 限制长度避免超token

    print("  调用 DeepSeek API...")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个专业的政府采购信息提取助手，擅长从招标公告中提取结构化数据。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,  # 低温度保证稳定输出
        response_format={"type": "json_object"}  # DeepSeek 支持 JSON 模式
    )

    # 解析返回的JSON
    result_text = response.choices[0].message.content
    result_json = json.loads(result_text)

    return result_json


def main():
    print("=" * 80)
    print("使用 DeepSeek API 解析招标页面")
    print("=" * 80)
    print()

    # 检查 API Key
    api_key = DEEPSEEK_API_KEY
    if not api_key:
        print("❌ 未找到 DEEPSEEK_API_KEY")
        print()
        print("配置方式（任选其一）:")
        print("  1. 创建 .env 文件并添加:")
        print("     DEEPSEEK_API_KEY=sk-xxxxxx")
        print()
        print("  2. 设置环境变量:")
        print("     Windows: set DEEPSEEK_API_KEY=sk-xxxxxx")
        print("     Linux/Mac: export DEEPSEEK_API_KEY=sk-xxxxxx")
        print()
        print("获取 API Key:")
        print("  访问 https://platform.deepseek.com/")
        print()
        return

    print(f"✓ 使用 API Key: {api_key[:20]}...{api_key[-4:]}")
    print()

    try:
        # 创建浏览器实例
        print("步骤1: 创建浏览器实例...")
        browser = AgentBrowser(
            session_name="deepseek_parse",
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
        print("步骤4: 搜索'软件开发'...")
        browser._run("fill", '[placeholder="请输入搜索内容"]', "软件开发", capture_output=False)
        browser.press("Enter")
        browser.wait(3000)
        print("  ✓ 搜索完成")
        print()

        # 获取搜索结果页HTML
        print("步骤5: 获取搜索结果页HTML...")
        search_html = browser.get_content()
        print(f"  ✓ 获取到 {len(search_html)} 字符的HTML")
        print()

        # 使用 DeepSeek 解析搜索结果，提取项目列表
        print("步骤6: 使用 DeepSeek 解析搜索结果页...")
        list_prompt = """
请从以下招标搜索结果页面HTML中提取项目列表，以JSON格式输出。

要提取的字段（数组，每个项目包含）：
- title: 项目完整标题
- category: 公告类型（从标题中提取，如：公开招标、中标公告等）
- region: 所属地区（从标题中提取，如有）

只返回前5个项目的JSON数组，不要其他说明文字。

HTML内容：
{html_content}
"""

        list_result = parse_page_with_deepseek(
            search_html[:20000],
            api_key,
            custom_prompt=list_prompt
        )
        print("  ✓ 解析完成")

        # 提取项目列表
        projects = list_result if isinstance(list_result, list) else list_result.get('projects', [])
        print(f"  ✓ 找到 {len(projects)} 个项目")
        print()

        # 显示搜索结果
        print("=" * 80)
        print("搜索结果列表")
        print("=" * 80)
        print()
        print(json.dumps(projects, ensure_ascii=False, indent=2))
        print()

        # 保存搜索结果
        search_output = "deepseek_search_results.json"
        with open(search_output, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
        print(f"✓ 搜索结果已保存到: {search_output}")
        print()

        # 关闭浏览器
        browser.close()
        print("✓ 浏览器已关闭")
        print()

        print("=" * 80)
        print("✅ 成功！")
        print("=" * 80)
        print()

        print("📊 统计:")
        print(f"  - 搜索关键词: 软件开发")
        print(f"  - 找到项目: {len(projects)} 个")
        print(f"  - 输出文件: {search_output}")
        print()

        print("💡 优势:")
        print("  - 使用 LLM 智能解析，无需写复杂规则")
        print("  - 自动识别页面结构和语义")
        print("  - 适应各种网站布局")
        print("  - 页面改版后仍能正常工作")
        print()

        print("💰 成本（DeepSeek）:")
        print("  - 输入: ¥0.001 / 1K tokens")
        print("  - 输出: ¥0.002 / 1K tokens")
        print("  - 本次解析: ~¥0.02")
        print()

        print("🎯 下一步:")
        print("  1. 查看 deepseek_search_results.json")
        print("  2. 遍历项目列表，访问每个详情页")
        print("  3. 用 DeepSeek 提取详细信息（预算、联系人等）")
        print("  4. 保存到数据库")

    except Exception as e:
        print()
        print(f"❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
