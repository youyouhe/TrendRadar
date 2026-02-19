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


def parse_page_with_deepseek(html_content: str, api_key: str) -> dict:
    """
    使用 DeepSeek API 解析网页内容

    Args:
        html_content: 网页HTML内容
        api_key: DeepSeek API密钥

    Returns:
        解析后的结构化数据（dict）
    """
    client = OpenAI(
        api_key=api_key,
        base_url=DEEPSEEK_BASE_URL
    )

    # 构建提示词
    prompt = EXTRACTION_PROMPT.format(html_content=html_content[:20000])  # 限制长度避免超token

    print("  调用 DeepSeek API 解析页面...")

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

        # 点击第一个项目
        print("步骤5: 进入第一个项目详情...")
        # 需要找到第一个项目链接并点击
        # 这里简化处理，直接使用CSS选择器
        browser._run("click", "a[title*='招标'], a[title*='采购']", capture_output=False)
        browser.wait(3000)
        print("  ✓ 详情页加载完成")
        print()

        # 获取页面HTML
        print("步骤6: 获取页面HTML内容...")
        html_content = browser.get_content()
        print(f"  ✓ 获取到 {len(html_content)} 字符的HTML")
        print()

        # 使用 DeepSeek 解析
        print("步骤7: 使用 DeepSeek API 解析页面...")
        result = parse_page_with_deepseek(html_content, api_key)
        print("  ✓ 解析完成")
        print()

        # 显示结果
        print("=" * 80)
        print("提取结果")
        print("=" * 80)
        print()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()

        # 保存结果
        output_file = "deepseek_parsed_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✓ 结果已保存到: {output_file}")
        print()

        # 关闭浏览器
        browser.close()
        print("✓ 浏览器已关闭")
        print()

        print("=" * 80)
        print("成功！")
        print("=" * 80)
        print()
        print("💡 优势:")
        print("  - 自动识别页面结构")
        print("  - 提取语义化字段")
        print("  - 不需要写复杂的解析规则")
        print("  - 适应不同网站的页面布局")
        print()
        print("💰 成本（DeepSeek）:")
        print("  - 输入: ¥0.001 / 1K tokens (~20K HTML ≈ ¥0.02)")
        print("  - 输出: ¥0.002 / 1K tokens (~500 tokens ≈ ¥0.001)")
        print("  - 单次解析成本: < ¥0.03")

    except Exception as e:
        print()
        print(f"❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
