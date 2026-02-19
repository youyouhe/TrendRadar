# coding=utf-8
"""
广东省政府采购网招标信息采集

网站: https://gdgpo.czt.gd.gov.cn/
特点: 对 Linux 浏览器友好，无验证码
技术栈: agent-browser (语义化定位)
"""

import re
import time
from datetime import datetime
from typing import List, Dict, Optional

from trendradar.crawler.agent_browser import AgentBrowser, AgentBrowserError
from trendradar.crawler.tender.base import TenderSource, TenderData, TenderStatus


class GuangdongTenderSource(TenderSource):
    """
    广东省政府采购网数据源

    特点：
    - 对 Linux 友好，无需特殊处理
    - 无验证码
    - 使用 agent-browser 语义化定位
    - 支持货物/服务/工程三类采购
    """

    @property
    def source_code(self) -> str:
        return "guangdong"

    @property
    def source_name(self) -> str:
        return "广东省政府采购网"

    @property
    def base_url(self) -> str:
        return "https://gdgpo.czt.gd.gov.cn/"

    def search(
        self,
        keywords: List[str],
        category: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        max_results: int = 100,
    ) -> List[TenderData]:
        """
        搜索广东省招标信息

        Args:
            keywords: 关键词列表
            category: 采购类别（货物/服务/工程）
            date_from: 开始日期
            date_to: 结束日期
            max_results: 最大结果数

        Returns:
            招标信息列表
        """
        results = []

        # 对每个关键词执行搜索
        for keyword in keywords:
            try:
                batch = self._search_single_keyword(keyword, category, max_results)
                results.extend(batch)

                # 检查是否达到最大结果数
                if len(results) >= max_results:
                    results = results[:max_results]
                    break

            except Exception as e:
                print(f"[{self.source_name}] 搜索关键词 '{keyword}' 失败: {e}")

        return results

    def _search_single_keyword(
        self,
        keyword: str,
        category: Optional[str],
        max_results: int
    ) -> List[TenderData]:
        """
        执行单个关键词的搜索

        流程：
        1. 打开网站
        2. 找到搜索入口（通常在首页）
        3. 输入关键词
        4. 点击搜索
        5. 提取列表结果
        """
        session_name = f"guangdong_{keyword}_{int(time.time())}"

        with AgentBrowser(session_name=session_name, headless=True) as browser:
            # 步骤1：打开网站
            print(f"[{self.source_name}] 访问 {self.base_url}")
            browser.goto(self.base_url)
            browser.wait(3000)  # 等待页面加载

            # 获取初始快照
            snapshot = browser.snapshot(interactive_only=True)
            print(f"[{self.source_name}] 页面加载完成，找到 {len(snapshot.get('elements', []))} 个可交互元素")

            # 步骤2：查找并点击高级搜索或综合搜索入口
            try:
                # 尝试多种可能的搜索入口
                search_triggers = [
                    {"text": "综合搜索"},
                    {"text": "高级搜索"},
                    {"text": "信息搜索"},
                    {"role": "link", "name": "搜索"},
                ]

                search_clicked = False
                for trigger in search_triggers:
                    try:
                        if "text" in trigger:
                            browser.click(text=trigger["text"], wait_ms=1500)
                        else:
                            browser.click(**trigger, wait_ms=1500)
                        search_clicked = True
                        print(f"[{self.source_name}] 点击搜索入口成功")
                        break
                    except AgentBrowserError:
                        continue

                if not search_clicked:
                    print(f"[{self.source_name}] 未找到搜索入口，尝试直接在首页搜索")

            except Exception as e:
                print(f"[{self.source_name}] 搜索入口处理异常: {e}")

            # 步骤3：输入关键词
            print(f"[{self.source_name}] 输入关键词: {keyword}")
            browser.wait(1000)

            # 获取新快照
            snapshot = browser.snapshot(interactive_only=True)

            # 查找关键词输入框
            keyword_input = self._find_keyword_input(snapshot)

            if keyword_input:
                ref = keyword_input.get("ref")
                print(f"[{self.source_name}] 找到关键词输入框: {ref}")
                browser.fill(ref=ref, value=keyword, wait_ms=800)
            else:
                # 回退：尝试常见的占位符
                try:
                    browser.fill(placeholder="请输入关键词", value=keyword, wait_ms=800)
                except AgentBrowserError:
                    try:
                        browser.fill(placeholder="关键词", value=keyword, wait_ms=800)
                    except AgentBrowserError:
                        print(f"[{self.source_name}] 无法找到关键词输入框")
                        return []

            # 步骤4：点击搜索按钮
            print(f"[{self.source_name}] 点击搜索按钮")
            try:
                # 尝试多种可能的按钮
                search_buttons = [
                    {"role": "button", "name": "搜索"},
                    {"role": "button", "name": "查询"},
                    {"text": "搜索"},
                    {"text": "查询"},
                ]

                search_executed = False
                for btn in search_buttons:
                    try:
                        if "text" in btn:
                            browser.click(text=btn["text"], wait_ms=2000)
                        else:
                            browser.click(**btn, wait_ms=2000)
                        search_executed = True
                        print(f"[{self.source_name}] 搜索执行成功")
                        break
                    except AgentBrowserError:
                        continue

                if not search_executed:
                    # 尝试按回车键
                    print(f"[{self.source_name}] 尝试按回车键搜索")
                    browser.press("Enter", wait_ms=2000)

            except Exception as e:
                print(f"[{self.source_name}] 搜索执行失败: {e}")
                return []

            # 步骤5：提取列表结果
            print(f"[{self.source_name}] 等待结果加载...")
            browser.wait(2000)

            snapshot = browser.snapshot(interactive_only=True)
            tenders = self._extract_list_data(snapshot, keyword)

            print(f"[{self.source_name}] 找到 {len(tenders)} 条结果")
            return tenders[:max_results]

    def _find_keyword_input(self, snapshot: Dict) -> Optional[Dict]:
        """
        查找关键词输入框

        查找策略：
        - placeholder 包含 "关键词"、"标题"、"搜索"
        - name 包含 "关键词"、"keyword"
        - role="textbox"
        """
        for elem in snapshot.get("elements", []):
            role = elem.get("role", "")
            name = elem.get("name", "").lower()
            placeholder = elem.get("placeholder", "").lower()

            if role == "textbox" or role == "searchbox":
                # 优先匹配包含"关键"的
                if "关键" in placeholder or "关键" in name:
                    return elem
                # 其次匹配包含"搜索"的
                if "搜索" in placeholder or "search" in name.lower():
                    return elem
                # 再次匹配包含"标题"的
                if "标题" in placeholder or "标题" in name:
                    return elem

        # 如果没找到明确的，返回第一个 textbox
        for elem in snapshot.get("elements", []):
            if elem.get("role") in ["textbox", "searchbox"]:
                return elem

        return None

    def _extract_list_data(self, snapshot: Dict, keyword: str) -> List[TenderData]:
        """
        从列表页快照提取招标信息

        提取字段：
        - 标题（link role）
        - URL（从 ref 推断）
        - 发布日期（日期格式文本）

        Returns:
            TenderData 列表
        """
        tenders = []
        current_item = {}

        for elem in snapshot.get("elements", []):
            role = elem.get("role", "")
            name = elem.get("name", "")
            ref = elem.get("ref", "")

            # 提取标题（link）
            if role == "link" and name and len(name) > 10:  # 标题通常较长
                # 如果已有 current_item，保存它
                if current_item.get("title"):
                    tenders.append(self._create_tender_from_item(current_item, keyword))
                    current_item = {}

                current_item["title"] = name
                current_item["ref"] = ref

            # 提取日期（匹配 YYYY-MM-DD 或 YYYY/MM/DD 格式）
            if name:
                date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', name)
                if date_match:
                    current_item["publish_date"] = date_match.group(1).replace('/', '-')

        # 保存最后一个 item
        if current_item.get("title"):
            tenders.append(self._create_tender_from_item(current_item, keyword))

        return tenders

    def _create_tender_from_item(self, item: Dict, keyword: str) -> TenderData:
        """
        从列表项创建 TenderData 对象

        Args:
            item: 包含 title, ref, publish_date 的字典
            keyword: 搜索关键词

        Returns:
            TenderData 对象
        """
        title = item.get("title", "")
        ref = item.get("ref", "")

        # URL 需要根据 ref 点击后获取（暂时使用占位符）
        url = f"{self.base_url}?ref={ref}"

        # 解析发布日期
        publish_date = None
        date_str = item.get("publish_date")
        if date_str:
            try:
                publish_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                pass

        return TenderData(
            title=title,
            url=url,
            source=self.source_code,
            source_name=self.source_name,
            publish_date=publish_date,
            deadline=None,
            keywords=[keyword],
            raw_data=item,
        )

    def get_detail(self, tender: TenderData) -> TenderData:
        """
        获取招标详情页数据

        流程：
        1. 点击标题链接（使用 ref）
        2. 等待详情页加载
        3. 提取详情字段（金额、联系人、电话等）
        4. 返回完善的 TenderData

        Args:
            tender: 包含 URL 和 ref 的 TenderData

        Returns:
            完善后的 TenderData
        """
        # 暂时返回原始数据，详情页采集待实现
        print(f"[{self.source_name}] 详情页采集功能待实现")
        return tender
