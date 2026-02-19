# coding=utf-8
"""
山东省政府采购网招标信息采集

网站: http://ggzy.shandong.gov.cn/
技术栈: agent-browser (语义化定位)
"""

import re
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from trendradar.crawler.agent_browser import AgentBrowser, AgentBrowserError
from trendradar.crawler.tender.base import TenderSource, TenderData, TenderStatus


class ShandongTenderSource(TenderSource):
    """
    山东省政府采购网数据源

    特点：
    - 需要处理验证码（集成 captcha-service）
    - 使用 agent-browser 语义化定位
    - 支持货物/服务/工程三类采购
    """

    @property
    def source_code(self) -> str:
        return "shandong"

    @property
    def source_name(self) -> str:
        return "山东省政府采购网"

    @property
    def base_url(self) -> str:
        return "http://ggzy.shandong.gov.cn/"

    def __init__(self, captcha_service: str = "http://localhost:5000"):
        """
        初始化山东数据源

        Args:
            captcha_service: 验证码识别服务地址
        """
        self.captcha_service = captcha_service

    def search(
        self,
        keywords: List[str],
        category: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        max_results: int = 100,
    ) -> List[TenderData]:
        """
        搜索山东省招标信息

        Args:
            keywords: 关键词列表
            category: 采购类别（货物/服务/工程）
            date_from: 开始日期（暂不支持）
            date_to: 结束日期（暂不支持）
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
        2. 选择采购类别（如果指定）
        3. 输入关键词
        4. 识别并输入验证码
        5. 点击查询
        6. 提取列表结果
        """
        session_name = f"shandong_{keyword}_{int(time.time())}"

        with AgentBrowser(session_name=session_name, headless=True) as browser:
            # 步骤1：打开网站
            print(f"[{self.source_name}] 访问 {self.base_url}")
            browser.goto(self.base_url)
            browser.wait(2000)

            # 获取初始快照
            snapshot = browser.snapshot(interactive_only=True)

            # 步骤2：选择采购类别（如果指定）
            if category:
                category_map = {
                    "货物": "货物类",
                    "服务": "服务类",
                    "工程": "工程类",
                }
                category_text = category_map.get(category)
                if category_text:
                    try:
                        print(f"[{self.source_name}] 选择类别: {category_text}")
                        browser.click(text=category_text, wait_ms=1000)
                    except AgentBrowserError as e:
                        print(f"[{self.source_name}] 选择类别失败: {e}")

            # 步骤3：输入关键词
            print(f"[{self.source_name}] 输入关键词: {keyword}")

            # 查找关键词输入框（尝试多种定位方式）
            snapshot = browser.snapshot(interactive_only=True)
            keyword_input = self._find_keyword_input(snapshot)

            if keyword_input:
                ref = keyword_input.get("ref")
                browser.fill(ref=ref, value=keyword, wait_ms=500)
            else:
                # 回退到占位符匹配
                browser.fill(placeholder="公告标题", value=keyword, wait_ms=500)

            # 步骤4：处理验证码
            captcha_text = self._handle_captcha(browser)
            if captcha_text:
                print(f"[{self.source_name}] 验证码识别: {captcha_text}")

                # 查找验证码输入框
                snapshot = browser.snapshot(interactive_only=True)
                captcha_input = self._find_captcha_input(snapshot)

                if captcha_input:
                    ref = captcha_input.get("ref")
                    browser.fill(ref=ref, value=captcha_text, wait_ms=500)
                else:
                    browser.fill(placeholder="验证码", value=captcha_text, wait_ms=500)

            # 步骤5：点击查询按钮
            print(f"[{self.source_name}] 点击查询按钮")
            try:
                browser.click(role="button", name="查询", wait_ms=2000)
            except AgentBrowserError:
                # 尝试其他可能的按钮文本
                try:
                    browser.click(text="查询", wait_ms=2000)
                except AgentBrowserError as e:
                    print(f"[{self.source_name}] 点击查询失败: {e}")
                    return []

            # 步骤6：提取列表结果
            print(f"[{self.source_name}] 提取列表数据")
            browser.wait(2000)  # 等待结果加载

            snapshot = browser.snapshot(interactive_only=True)
            tenders = self._extract_list_data(snapshot, keyword)

            print(f"[{self.source_name}] 找到 {len(tenders)} 条结果")
            return tenders[:max_results]

    def _find_keyword_input(self, snapshot: Dict) -> Optional[Dict]:
        """
        查找关键词输入框

        查找策略：
        - placeholder 包含 "标题"、"关键词"
        - name 包含 "标题"
        - role="textbox"
        """
        for elem in snapshot.get("elements", []):
            role = elem.get("role", "")
            name = elem.get("name", "").lower()
            placeholder = elem.get("placeholder", "").lower()

            if role == "textbox":
                if "标题" in placeholder or "关键" in placeholder:
                    return elem
                if "标题" in name:
                    return elem

        return None

    def _find_captcha_input(self, snapshot: Dict) -> Optional[Dict]:
        """
        查找验证码输入框

        查找策略：
        - placeholder 包含 "验证码"
        - name 包含 "验证码"
        """
        for elem in snapshot.get("elements", []):
            name = elem.get("name", "").lower()
            placeholder = elem.get("placeholder", "").lower()

            if "验证" in placeholder or "验证" in name:
                return elem

        return None

    def _handle_captcha(self, browser: AgentBrowser) -> Optional[str]:
        """
        识别并返回验证码文本

        步骤：
        1. 截图当前页面
        2. 发送到 captcha-service 识别
        3. 返回识别结果

        Returns:
            验证码文本，失败返回 None
        """
        try:
            # 截图
            screenshot_path = f"/tmp/captcha_{int(time.time())}.png"
            browser.screenshot(screenshot_path, fullpage=False)

            # 调用验证码服务
            with open(screenshot_path, "rb") as f:
                response = requests.post(
                    f"{self.captcha_service}/ocr",
                    files={"image": f},
                    timeout=10
                )

            if response.status_code == 200:
                data = response.json()
                return data.get("text", "").strip()
            else:
                print(f"[{self.source_name}] 验证码识别失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"[{self.source_name}] 验证码识别异常: {e}")
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
            if role == "link" and name:
                # 如果已有 current_item，保存它
                if current_item.get("title"):
                    tenders.append(self._create_tender_from_item(current_item, keyword))
                    current_item = {}

                current_item["title"] = name
                current_item["ref"] = ref

            # 提取日期（匹配 YYYY-MM-DD 格式）
            if name and re.match(r"\d{4}-\d{2}-\d{2}", name):
                current_item["publish_date"] = name

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
        # 实际 URL 在 get_detail() 中获取
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
        session_name = f"shandong_detail_{int(time.time())}"

        try:
            with AgentBrowser(session_name=session_name, headless=True) as browser:
                # 从 URL 提取 ref
                ref = self._extract_ref_from_url(tender.url)
                if not ref:
                    print(f"[{self.source_name}] 无法提取 ref: {tender.url}")
                    return tender

                # 返回列表页并点击链接
                print(f"[{self.source_name}] 获取详情: {tender.title}")

                # TODO: 这里需要重新执行搜索并点击对应的 ref
                # 简化版本：直接尝试导航到详情页（需要具体 URL 规则）

                # 暂时返回原始数据（详情页采集需要完整的导航流程）
                return tender

        except Exception as e:
            print(f"[{self.source_name}] 获取详情失败: {tender.title} - {e}")
            return tender

    def _extract_ref_from_url(self, url: str) -> Optional[str]:
        """
        从 URL 提取元素引用

        Args:
            url: URL 字符串（如 http://...?ref=@e5）

        Returns:
            ref 字符串（如 @e5），失败返回 None
        """
        match = re.search(r"ref=(@e\d+)", url)
        if match:
            return match.group(1)
        return None
