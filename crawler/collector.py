"""
招标信息采集协调器

协调 agent-browser 和 DeepSeek 解析器，完成完整的采集流程
"""

import time
from datetime import datetime
from typing import List, Dict, Optional, Callable
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from trendradar.crawler.agent_browser import AgentBrowser
from crawler.parsers.deepseek_parser import DeepSeekParser


class CollectResult:
    """采集结果"""

    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
        self.data = []
        self.errors = []

    def add_success(self, item: Dict):
        self.data.append(item)
        self.success += 1
        self.total += 1

    def add_failure(self, error: str):
        self.errors.append(error)
        self.failed += 1
        self.total += 1

    def to_dict(self):
        return {
            "total": self.total,
            "success": self.success,
            "failed": self.failed,
            "data": self.data,
            "errors": self.errors,
        }


class TenderCollector:
    """招标信息采集器"""

    def __init__(
        self,
        deepseek_api_key: str,
        headless: bool = True,
        timeout: int = 60000
    ):
        """
        初始化采集器

        Args:
            deepseek_api_key: DeepSeek API密钥
            headless: 是否无头模式
            timeout: 浏览器超时时间（毫秒）
        """
        self.parser = DeepSeekParser(deepseek_api_key)
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[AgentBrowser] = None

    def _init_browser(self, session_name: str):
        """初始化浏览器"""
        if not self.browser:
            self.browser = AgentBrowser(
                session_name=session_name,
                headless=self.headless,
                timeout=self.timeout
            )
            # 预热浏览器
            self.browser.goto("https://example.com/")
            self.browser.wait(1000)

    def _close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            self.browser = None

    async def collect(
        self,
        source_name: str,
        base_url: str,
        keywords: List[str],
        max_items: int = 10,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> CollectResult:
        """
        完整采集流程

        Args:
            source_name: 采集源名称
            base_url: 采集源基础URL
            keywords: 关键词列表
            max_items: 最多采集多少个项目
            progress_callback: 进度回调函数 callback(progress: int, message: str)

        Returns:
            采集结果
        """
        result = CollectResult()
        session_name = f"collect_{source_name}_{int(time.time())}"

        try:
            # 初始化浏览器
            if progress_callback:
                progress_callback(5, "正在初始化浏览器...")

            self._init_browser(session_name)

            # 访问采集源
            if progress_callback:
                progress_callback(10, f"正在访问 {source_name}...")

            self.browser.goto(base_url)
            self.browser.wait(2000)

            # 搜索关键词（使用第一个关键词）
            keyword = keywords[0] if keywords else ""

            if progress_callback:
                progress_callback(20, f"正在搜索关键词: {keyword}...")

            # 查找搜索框并输入
            self.browser._run("fill", '[placeholder="请输入搜索内容"]', keyword, capture_output=False)
            self.browser.press("Enter")
            self.browser.wait(3000)

            # 获取搜索结果HTML
            if progress_callback:
                progress_callback(30, "正在解析搜索结果...")

            search_html = self.browser.get_content()

            # 使用DeepSeek解析列表
            projects = await self.parser.parse_search_results(search_html, base_url)

            if progress_callback:
                progress_callback(40, f"找到 {len(projects)} 个项目，开始采集详情...")

            # 限制采集数量
            projects_to_collect = projects[:max_items]

            # 逐个采集详情
            for i, project in enumerate(projects_to_collect):
                try:
                    title = project.get('title', 'Unknown')
                    detail_url = project.get('detail_url', '')

                    if not detail_url:
                        result.add_failure(f"项目无详情页URL: {title}")
                        continue

                    # 计算进度 (40-90区间)
                    progress = 40 + int((i + 1) / len(projects_to_collect) * 50)

                    if progress_callback:
                        progress_callback(progress, f"采集 [{i+1}/{len(projects_to_collect)}]: {title[:30]}...")

                    # 访问详情页
                    self.browser.goto(detail_url)
                    self.browser.wait(3000)

                    # 获取详情页HTML
                    detail_html = self.browser.get_content()

                    # 使用DeepSeek解析详情
                    detail = await self.parser.parse_project_detail(detail_html)

                    # 合并列表信息和详情信息
                    tender_data = {
                        **project,
                        **detail,
                        'source': source_name,
                        'collected_at': datetime.now().isoformat(),
                        'url': detail_url,  # 确保有URL字段（用于去重）
                    }

                    result.add_success(tender_data)

                    # 短暂休息
                    time.sleep(1)

                except Exception as e:
                    result.add_failure(f"采集失败 {title}: {str(e)}")

            # 完成
            if progress_callback:
                progress_callback(100, f"采集完成：成功 {result.success} 个")

        except Exception as e:
            if progress_callback:
                progress_callback(0, f"采集失败: {str(e)}")
            raise

        finally:
            self._close_browser()

        return result

    async def collect_by_source_code(
        self,
        source_code: str,
        keywords: List[str],
        max_items: int = 10,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> CollectResult:
        """
        根据采集源代码采集（内置省份配置）

        Args:
            source_code: 采集源代码（beijing/guangdong/shandong等）
            keywords: 关键词列表
            max_items: 最多采集数量
            progress_callback: 进度回调

        Returns:
            采集结果
        """
        # 内置省份配置
        source_configs = {
            "beijing": {
                "name": "北京市政府采购网",
                "base_url": "http://www.ccgp-beijing.gov.cn/"
            },
            "guangdong": {
                "name": "广东省政府采购网",
                "base_url": "https://gdgpo.czt.gd.gov.cn"
            },
            "shandong": {
                "name": "山东省政府采购网",
                "base_url": "https://www.ccgp-shandong.gov.cn"
            },
        }

        if source_code not in source_configs:
            raise ValueError(f"不支持的采集源: {source_code}")

        config = source_configs[source_code]

        return await self.collect(
            source_name=config["name"],
            base_url=config["base_url"],
            keywords=keywords,
            max_items=max_items,
            progress_callback=progress_callback
        )
