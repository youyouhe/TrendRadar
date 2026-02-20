"""
招标信息采集器 - TrendRadar 扩展模块

将招标信息整合到TrendRadar框架中，作为独立信息源展示
"""

import os
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# 导入agent_browser和DeepSeek解析器
from .agent_browser import AgentBrowser


class TenderCollector:
    """招标信息采集器（整合到TrendRadar）"""

    def __init__(self, deepseek_api_key: str, headless: bool = True):
        """
        初始化采集器

        Args:
            deepseek_api_key: DeepSeek API密钥
            headless: 是否无头模式
        """
        self.api_key = deepseek_api_key
        self.headless = headless
        self.browser = None

        # 导入DeepSeek解析器
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
        except ImportError:
            print("[招标] 警告：未安装openai库，无法使用DeepSeek解析")
            self.client = None

    def _init_browser(self):
        """初始化浏览器"""
        if not self.browser:
            self.browser = AgentBrowser(
                session_name=f"tender_{int(time.time())}",
                headless=self.headless,
                timeout=60000
            )
            # 预热
            self.browser.goto("https://example.com/")
            self.browser.wait(1000)

    def _close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            self.browser = None

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

            import json
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"[招标] DeepSeek解析失败: {e}")
            return {} if is_list else None

    def collect_tenders(
        self,
        source_name: str,
        base_url: str,
        keywords: List[str],
        max_items: int = 10
    ) -> List[Dict]:
        """
        采集招标信息

        Args:
            source_name: 采集源名称（如：北京市政府采购网）
            base_url: 采集源基础URL
            keywords: 关键词列表
            max_items: 最多采集数量

        Returns:
            招标信息列表
        """
        results = []

        try:
            print(f"[招标] 开始采集：{source_name}")

            self._init_browser()

            # 访问采集源
            self.browser.goto(base_url)
            self.browser.wait(2000)

            # 搜索关键词
            keyword = keywords[0] if keywords else ""
            self.browser._run("fill", '[placeholder="请输入搜索内容"]', keyword, capture_output=False)
            self.browser.press("Enter")
            self.browser.wait(3000)

            # 获取搜索结果HTML
            search_html = self.browser.get_content()

            # 使用DeepSeek解析列表
            list_result = self._parse_with_deepseek(search_html, is_list=True)
            projects = list_result if isinstance(list_result, list) else list_result.get('projects', [])

            print(f"[招标] 找到 {len(projects)} 个项目")

            # 限制采集数量
            projects_to_collect = projects[:max_items]

            # 逐个采集详情
            for i, project in enumerate(projects_to_collect):
                try:
                    title = project.get('title', 'Unknown')
                    detail_url = project.get('detail_url', '')

                    if not detail_url:
                        continue

                    print(f"[招标] [{i+1}/{len(projects_to_collect)}] {title[:50]}...")

                    # 访问详情页
                    self.browser.goto(detail_url)
                    self.browser.wait(3000)

                    # 获取详情页HTML
                    detail_html = self.browser.get_content()

                    # 使用DeepSeek解析详情
                    detail = self._parse_with_deepseek(detail_html, is_list=False)

                    if detail:
                        # 合并数据
                        tender_data = {
                            **project,
                            **detail,
                            'source': source_name,
                            'url': detail_url,
                            'collected_at': datetime.now().isoformat(),
                        }
                        results.append(tender_data)

                    # 短暂休息
                    time.sleep(1)

                except Exception as e:
                    print(f"[招标] 详情采集失败 {title}: {e}")

            print(f"[招标] 采集完成：成功 {len(results)} 个")

        except Exception as e:
            print(f"[招标] 采集失败: {e}")

        finally:
            self._close_browser()

        return results


def fetch_tender_data(
    sources: List[Dict],
    keywords: List[str],
    max_items_per_source: int = 10,
    deepseek_api_key: Optional[str] = None
) -> List[Dict]:
    """
    采集招标信息的主函数（供TrendRadar调用）

    Args:
        sources: 采集源列表 [{"name": "北京市政府采购网", "url": "..."}]
        keywords: 关键词列表
        max_items_per_source: 每个源最多采集数量
        deepseek_api_key: DeepSeek API密钥

    Returns:
        招标信息列表
    """
    if not deepseek_api_key:
        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "")

    if not deepseek_api_key:
        print("[招标] 未配置DEEPSEEK_API_KEY，跳过招标采集")
        return []

    if not sources:
        print("[招标] 未配置招标采集源")
        return []

    all_tenders = []

    for source in sources:
        if not source.get('enabled', True):
            continue

        collector = TenderCollector(
            deepseek_api_key=deepseek_api_key,
            headless=True
        )

        tenders = collector.collect_tenders(
            source_name=source['name'],
            base_url=source['url'],
            keywords=keywords,
            max_items=max_items_per_source
        )

        all_tenders.extend(tenders)

    return all_tenders
