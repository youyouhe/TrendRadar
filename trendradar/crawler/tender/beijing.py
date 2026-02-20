# coding=utf-8
"""
北京市政府采购网招标信息采集器

基于 agent-browser + DeepSeek 智能解析
"""

import os
import json
from typing import List, Optional
from datetime import datetime
from openai import OpenAI

from trendradar.crawler.agent_browser import AgentBrowser
from trendradar.crawler.tender.base import TenderSource, TenderData, TenderStatus


class BeijingTenderSource(TenderSource):
    """北京市政府采购网数据源"""

    @property
    def source_code(self) -> str:
        return "beijing"

    @property
    def source_name(self) -> str:
        return "北京市政府采购网"

    @property
    def base_url(self) -> str:
        return "http://www.ccgp-beijing.gov.cn/"

    def __init__(self):
        self.deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if self.deepseek_api_key:
            self.client = OpenAI(
                api_key=self.deepseek_api_key,
                base_url="https://api.deepseek.com"
            )
        else:
            self.client = None
            print(f"[{self.source_name}] 警告：未配置DEEPSEEK_API_KEY")

    def _parse_with_deepseek(self, html: str, is_list: bool = True) -> dict:
        """使用DeepSeek解析HTML"""
        if not self.client:
            return {} if is_list else None

        if is_list:
            prompt = f"""
请从以下招标搜索结果页面HTML中提取项目列表，以JSON格式输出。

要提取的字段（数组，每个项目包含）：
- title: 项目完整标题
- category: 公告类型（从标题中提取）
- detail_url: 项目详情页URL（完整URL）

只返回JSON数组，不要其他说明。提取前10个项目。

HTML内容：
{html[:30000]}
"""
        else:
            prompt = f"""
请从以下招标公告详情页HTML中提取信息，以JSON格式输出。

要提取的字段：
- title: 项目标题
- budget: 预算金额（万元，纯数字）
- publish_date: 发布日期（YYYY-MM-DD）
- deadline: 截止日期（YYYY-MM-DD HH:MM）
- contact_person: 联系人姓名
- contact_phone: 联系电话
- purchaser: 采购人单位名称

如果某个字段找不到，设为 null。只返回JSON对象。

HTML内容：
{html[:30000]}
"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是专业的政府采购信息提取助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"[{self.source_name}] DeepSeek解析失败: {e}")
            return {} if is_list else None

    def search(
        self,
        keywords: List[str],
        category: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        max_results: int = 100,
    ) -> List[TenderData]:
        """搜索招标信息"""
        browser = None
        results = []

        try:
            # 初始化浏览器
            browser = AgentBrowser(
                session_name=f"beijing_tender_{int(datetime.now().timestamp())}",
                headless=True,
                timeout=60000
            )

            # 预热
            browser.goto("https://example.com/")
            browser.wait(1000)

            # 访问北京政府采购网
            browser.goto(self.base_url)
            browser.wait(2000)

            # 搜索关键词
            keyword = keywords[0] if keywords else ""
            browser._run("fill", '[placeholder="请输入搜索内容"]', keyword, capture_output=False)
            browser.press("Enter")
            browser.wait(3000)

            # 获取搜索结果HTML
            search_html = browser.get_content()

            # 使用DeepSeek解析列表
            list_result = self._parse_with_deepseek(search_html, is_list=True)
            projects = list_result if isinstance(list_result, list) else list_result.get('projects', [])

            print(f"[{self.source_name}] 找到 {len(projects)} 个项目")

            # 转换为TenderData格式
            for project in projects[:max_results]:
                tender = TenderData(
                    title=project.get('title', ''),
                    url=project.get('detail_url', ''),
                    source=self.source_code,
                    source_name=self.source_name,
                    publish_date=None,  # 详情页获取
                    deadline=None,
                    category=project.get('category'),
                )
                results.append(tender)

        except Exception as e:
            print(f"[{self.source_name}] 搜索失败: {e}")

        finally:
            if browser:
                browser.close()

        return results

    def get_detail(self, tender: TenderData, max_retries: int = 2) -> TenderData:
        """
        获取招标详情

        Args:
            tender: 招标基本信息
            max_retries: 最大重试次数

        Returns:
            更新后的招标信息
        """
        browser = None
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                # 初始化浏览器
                browser = AgentBrowser(
                    session_name=f"beijing_detail_{int(datetime.now().timestamp())}",
                    headless=True,
                    timeout=30000  # 减少超时时间到30秒
                )

                # 访问详情页（带重试）
                try:
                    browser.goto(tender.url)
                    browser.wait(2000)  # 减少等待时间
                except Exception as goto_error:
                    # goto失败，可能是网络问题或防爬
                    if "ERR_CONNECTION_RESET" in str(goto_error):
                        print(f"[{self.source_name}] 连接重置，可能被防爬限制")
                        if attempt < max_retries:
                            print(f"[{self.source_name}] 等待5秒后重试... ({attempt + 1}/{max_retries})")
                            import time
                            time.sleep(5)
                            continue
                    raise goto_error

                # 获取详情页HTML
                detail_html = browser.get_content()

                # 检查是否真的加载了内容
                if not detail_html or len(detail_html) < 100:
                    raise Exception("详情页内容为空或过短")

                # 使用DeepSeek解析详情
                detail = self._parse_with_deepseek(detail_html, is_list=False)

                if detail:
                    # 更新字段
                    tender.amount = detail.get('budget')
                    tender.contact = detail.get('contact_person')
                    tender.phone = detail.get('contact_phone')
                    tender.purchaser = detail.get('purchaser')

                    # 解析日期
                    if detail.get('publish_date'):
                        try:
                            tender.publish_date = datetime.fromisoformat(detail['publish_date'])
                        except:
                            pass

                    if detail.get('deadline'):
                        try:
                            tender.deadline = datetime.fromisoformat(detail['deadline'])
                        except:
                            pass

                # 成功获取，跳出重试循环
                break

            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    print(f"[{self.source_name}] 获取详情失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
                    import time
                    time.sleep(3)  # 重试前等待
                else:
                    print(f"[{self.source_name}] 获取详情失败（已重试{max_retries}次）: {e}")

            finally:
                if browser:
                    try:
                        browser.close()
                    except:
                        pass
                browser = None

        return tender
