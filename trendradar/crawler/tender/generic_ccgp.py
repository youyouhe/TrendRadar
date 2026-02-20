# coding=utf-8
"""
通用政府采购网招标信息采集器

适用于全国各省市政府采购网（基于中国政府采购网统一平台）
使用 agent-browser + DeepSeek 智能解析，自适应不同省份网站结构
"""

import os
import json
import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from openai import OpenAI

from trendradar.crawler.agent_browser import AgentBrowser
from trendradar.crawler.tender.base import TenderSource, TenderData, TenderStatus


class GenericCCGPSource(TenderSource):
    """
    通用政府采购网数据源

    适用于大部分省份的政府采购网站（www.ccgp-XXX.gov.cn）
    使用DeepSeek智能解析，无需硬编码CSS选择器
    """

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

    def _parse_list_with_deepseek(self, html: str) -> List[Dict[str, Any]]:
        """使用DeepSeek解析列表页HTML"""
        if not self.client:
            return []

        prompt = f"""
请从以下政府采购搜索结果页面HTML中提取项目列表，以JSON格式输出。

要提取的字段（数组，每个项目包含）：
- title: 项目完整标题
- category: 公告类型（如：招标公告、中标公告、采购公告等）
- detail_url: 项目详情页URL（完整URL，如果是相对路径请补全）
- publish_date: 发布日期（YYYY-MM-DD格式，如果能找到）

只返回JSON数组格式，不要其他说明。提取前15个有效项目。

HTML内容：
{html[:40000]}
"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是专业的政府采购信息提取助手，擅长从HTML中提取结构化数据。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # 处理不同的返回格式
            if isinstance(result, list):
                return result
            elif isinstance(result, dict):
                # 可能是 {"projects": [...]} 或 {"items": [...]}
                for key in ['projects', 'items', 'list', 'data', 'tenders']:
                    if key in result and isinstance(result[key], list):
                        return result[key]
                # 如果没有找到数组，尝试返回整个字典作为单个项目
                return [result] if result else []
            else:
                return []

        except Exception as e:
            print(f"[{self.source_name}] DeepSeek列表解析失败: {e}")
            return []

    def _parse_detail_with_deepseek(self, html: str) -> Optional[Dict[str, Any]]:
        """使用DeepSeek解析详情页HTML"""
        if not self.client:
            return None

        prompt = f"""
请从以下招标公告详情页HTML中提取信息，以JSON格式输出。

要提取的字段：
- title: 项目标题
- project_no: 项目编号/采购项目编号
- budget: 预算金额（只提取数字，单位万元）
- publish_date: 发布日期（YYYY-MM-DD）
- deadline: 截止日期（YYYY-MM-DD HH:MM）
- contact_person: 联系人姓名
- contact_phone: 联系电话
- purchaser: 采购人/采购单位名称
- agent: 代理机构名称
- region: 行政区域/地区

如果某个字段找不到，设为 null。只返回JSON对象，不要其他说明。

HTML内容：
{html[:40000]}
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
            print(f"[{self.source_name}] DeepSeek详情解析失败: {e}")
            return None

    def _fix_url(self, url: str) -> str:
        """修复URL（补全相对路径）"""
        if not url:
            return ""

        if url.startswith("http://") or url.startswith("https://"):
            return url

        # 补全相对路径
        if url.startswith("/"):
            # 绝对路径，补全域名
            base = self.base_url.rstrip('/')
            return base + url
        else:
            # 相对路径，补全完整路径
            base = self.base_url.rstrip('/')
            return f"{base}/{url}"

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
                session_name=f"{self.source_code}_tender_{int(datetime.now().timestamp())}",
                headless=True,
                timeout=60000
            )

            # 预热
            print(f"[{self.source_name}] 正在访问网站...")
            browser.goto("https://example.com/")
            browser.wait(1000)

            # 访问政府采购网
            browser.goto(self.base_url)
            browser.wait(3000)

            # 搜索关键词
            keyword = keywords[0] if keywords else ""
            print(f"[{self.source_name}] 搜索关键词: {keyword}")

            # 尝试常见的搜索框选择器
            search_selectors = [
                'input[name="wd"]',
                'input[name="keyword"]',
                'input[name="searchWord"]',
                'input[placeholder*="搜索"]',
                'input[placeholder*="关键"]',
                'input[type="text"]',
            ]

            search_success = False
            for selector in search_selectors:
                try:
                    browser._run("fill", selector, keyword, capture_output=False)
                    browser.press("Enter")
                    search_success = True
                    break
                except:
                    continue

            if not search_success:
                print(f"[{self.source_name}] 未找到搜索框，尝试直接获取列表")

            browser.wait(3000)

            # 获取搜索结果HTML
            search_html = browser.get_content()

            # 使用DeepSeek解析列表
            projects = self._parse_list_with_deepseek(search_html)
            print(f"[{self.source_name}] 找到 {len(projects)} 个项目")

            # 转换为TenderData格式
            for project in projects[:max_results]:
                # 修复URL
                detail_url = self._fix_url(project.get('detail_url', ''))

                tender = TenderData(
                    title=project.get('title', ''),
                    url=detail_url,
                    source=self.source_code,
                    source_name=self.source_name,
                    publish_date=None,  # 详情页获取
                    deadline=None,
                    category=project.get('category'),
                )

                # 如果列表页已有发布日期
                if project.get('publish_date'):
                    try:
                        tender.publish_date = datetime.fromisoformat(project['publish_date'])
                    except:
                        pass

                results.append(tender)

        except Exception as e:
            print(f"[{self.source_name}] 搜索失败: {e}")
            import traceback
            traceback.print_exc()

        finally:
            if browser:
                try:
                    browser.close()
                except:
                    pass

        return results

    def get_detail(self, tender: TenderData, max_retries: int = 2) -> TenderData:
        """获取招标详情"""
        browser = None
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                # 初始化浏览器
                browser = AgentBrowser(
                    session_name=f"{self.source_code}_detail_{int(datetime.now().timestamp())}",
                    headless=True,
                    timeout=30000
                )

                # 访问详情页
                print(f"[{self.source_name}] 获取详情: {tender.title[:30]}...")
                browser.goto(tender.url)
                browser.wait(2000)

                # 获取详情页HTML
                detail_html = browser.get_content()

                # 检查内容
                if not detail_html or len(detail_html) < 100:
                    raise Exception("详情页内容为空或过短")

                # 使用DeepSeek解析详情
                detail = self._parse_detail_with_deepseek(detail_html)

                if detail:
                    # 更新字段
                    tender.project_no = detail.get('project_no')
                    tender.amount = detail.get('budget')
                    tender.contact = detail.get('contact_person')
                    tender.phone = detail.get('contact_phone')
                    tender.purchaser = detail.get('purchaser')
                    tender.agent = detail.get('agent')
                    tender.region = detail.get('region')

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
                    time.sleep(3)
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
