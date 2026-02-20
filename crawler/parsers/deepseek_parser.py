"""
DeepSeek 智能解析器

使用 DeepSeek API 解析招标信息列表和详情页
"""

import os
import json
from typing import Dict, List, Optional
from openai import OpenAI

# DeepSeek API配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"


# 搜索结果列表提取提示词
LIST_PROMPT_TEMPLATE = """
请从以下招标搜索结果页面HTML中提取项目列表，以JSON格式输出。

要提取的字段（数组，每个项目包含）：
- title: 项目完整标题
- category: 公告类型（从标题中提取，如：公开招标、中标公告、合同公告等）
- region: 所属地区（从标题中提取，如有，如"石景山区"）
- detail_url: 项目详情页的完整URL（从HTML的<a>标签href属性中提取，必须是完整的URL）

**重要**: detail_url 必须是完整的可访问URL，如果是相对路径需要补全为完整URL。
例如：如果base_url是 http://www.ccgp-beijing.gov.cn/，相对路径 /detail/123 应该转换为 http://www.ccgp-beijing.gov.cn/detail/123

只返回JSON数组，不要其他说明文字。提取前10个项目。

HTML内容：
{html_content}
"""


# 详情页提取提示词
DETAIL_PROMPT_TEMPLATE = """
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


class DeepSeekParser:
    """DeepSeek智能解析器"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化解析器

        Args:
            api_key: DeepSeek API密钥，如不提供则从环境变量读取
        """
        self.api_key = api_key or DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("未找到 DEEPSEEK_API_KEY，请在环境变量或.env文件中配置")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=DEEPSEEK_BASE_URL
        )

    async def parse_search_results(
        self,
        html_content: str,
        base_url: Optional[str] = None
    ) -> List[Dict]:
        """
        解析搜索结果列表页

        Args:
            html_content: 搜索结果页HTML
            base_url: 基础URL，用于补全相对路径

        Returns:
            项目列表，每项包含 title, category, region, detail_url
        """
        # 截取前30000字符（避免超过API限制）
        truncated_html = html_content[:30000]

        # 构造提示词
        prompt = LIST_PROMPT_TEMPLATE.format(html_content=truncated_html)

        # 调用DeepSeek API
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是专业的政府采购信息提取助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        result = json.loads(result_text)

        # 处理返回格式（可能是数组或包含projects字段的对象）
        projects = result if isinstance(result, list) else result.get('projects', [])

        # 补全相对路径URL
        if base_url:
            for project in projects:
                detail_url = project.get('detail_url', '')
                if detail_url and not detail_url.startswith('http'):
                    # 补全相对路径
                    if detail_url.startswith('/'):
                        project['detail_url'] = base_url.rstrip('/') + detail_url
                    else:
                        project['detail_url'] = base_url.rstrip('/') + '/' + detail_url

        return projects

    async def parse_project_detail(self, html_content: str) -> Dict:
        """
        解析项目详情页

        Args:
            html_content: 详情页HTML

        Returns:
            项目详情字典，包含预算、联系人等字段
        """
        # 截取前30000字符
        truncated_html = html_content[:30000]

        # 构造提示词
        prompt = DETAIL_PROMPT_TEMPLATE.format(html_content=truncated_html)

        # 调用DeepSeek API
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是专业的政府采购信息提取助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        detail = json.loads(result_text)

        return detail

    def estimate_cost(self, list_count: int, detail_count: int) -> float:
        """
        估算解析成本

        Args:
            list_count: 列表页解析次数
            detail_count: 详情页解析次数

        Returns:
            估算成本（元）
        """
        # 根据实测数据估算
        list_cost = list_count * 0.02  # 每次列表解析约¥0.02
        detail_cost = detail_count * 0.03  # 每次详情解析约¥0.03
        return list_cost + detail_cost
