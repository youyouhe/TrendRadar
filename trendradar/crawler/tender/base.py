# coding=utf-8
"""
招标数据源抽象基类

定义统一的招标信息采集接口，供各省份实现类继承。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum


class TenderStatus(str, Enum):
    """招标状态枚举"""
    ACTIVE = "进行中"      # 正在进行
    UPCOMING = "即将开始"   # 即将开始
    ENDED = "已结束"        # 已结束
    CANCELLED = "已取消"    # 已取消
    UNKNOWN = "未知"        # 未知状态


@dataclass
class TenderData:
    """
    招标信息数据结构

    对应 TrendRadar 的 NewsData 模式，适配招标领域
    """
    # 核心字段
    title: str                          # 标题
    url: str                            # 详情 URL
    source: str                         # 来源（省份代码）
    source_name: str                    # 来源名称（如"山东省政府采购网"）
    publish_date: Optional[datetime]    # 发布日期
    deadline: Optional[datetime]        # 截止日期

    # 招标特有字段
    project_no: Optional[str] = None    # 项目编号
    amount: Optional[str] = None        # 预算金额
    category: Optional[str] = None      # 采购类别（货物/服务/工程）
    region: Optional[str] = None        # 地区
    purchaser: Optional[str] = None     # 采购单位
    agent: Optional[str] = None         # 代理机构
    contact: Optional[str] = None       # 联系人
    phone: Optional[str] = None         # 联系电话
    status: TenderStatus = TenderStatus.UNKNOWN  # 状态

    # 内容字段
    content: Optional[str] = None       # 详情内容（HTML）
    summary: Optional[str] = None       # 摘要

    # 附件
    attachments: List[Dict[str, str]] = field(default_factory=list)  # [{name, url}]

    # 元数据
    keywords: List[str] = field(default_factory=list)  # 关键词
    tags: List[str] = field(default_factory=list)      # 标签
    raw_data: Dict[str, Any] = field(default_factory=dict)  # 原始数据

    # 采集信息
    crawled_at: datetime = field(default_factory=datetime.now)  # 采集时间
    updated_at: Optional[datetime] = None                       # 更新时间

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "source_name": self.source_name,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "project_no": self.project_no,
            "amount": self.amount,
            "category": self.category,
            "region": self.region,
            "purchaser": self.purchaser,
            "agent": self.agent,
            "contact": self.contact,
            "phone": self.phone,
            "status": self.status.value,
            "content": self.content,
            "summary": self.summary,
            "attachments": self.attachments,
            "keywords": self.keywords,
            "tags": self.tags,
            "raw_data": self.raw_data,
            "crawled_at": self.crawled_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def matches_keywords(self, keywords: List[str], match_mode: str = "any") -> bool:
        """
        检查是否匹配关键词

        Args:
            keywords: 关键词列表
            match_mode: 匹配模式（any=任意匹配, all=全部匹配, exact=精确匹配）

        Returns:
            是否匹配
        """
        if not keywords:
            return True

        title_lower = self.title.lower()
        content_lower = (self.content or "").lower()
        combined = f"{title_lower} {content_lower}"

        if match_mode == "exact":
            # 精确匹配：标题完全等于关键词之一
            return self.title in keywords

        elif match_mode == "all":
            # 全部匹配：所有关键词都必须出现
            return all(kw.lower() in combined for kw in keywords)

        else:  # any (默认)
            # 任意匹配：至少一个关键词出现
            return any(kw.lower() in combined for kw in keywords)


class TenderSource(ABC):
    """
    招标数据源抽象基类

    子类需实现：
    - source_code: 省份代码（如 "shandong"）
    - source_name: 数据源名称（如 "山东省政府采购网"）
    - base_url: 网站基础 URL
    - search(): 搜索招标信息
    - get_detail(): 获取详情页数据
    """

    @property
    @abstractmethod
    def source_code(self) -> str:
        """省份代码（如 shandong）"""
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """数据源名称（如 山东省政府采购网）"""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """网站基础 URL"""
        pass

    @abstractmethod
    def search(
        self,
        keywords: List[str],
        category: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        max_results: int = 100,
    ) -> List[TenderData]:
        """
        搜索招标信息（列表页）

        Args:
            keywords: 搜索关键词列表
            category: 采购类别（货物/服务/工程）
            date_from: 开始日期
            date_to: 结束日期
            max_results: 最大结果数

        Returns:
            招标信息列表（仅包含列表页数据）
        """
        pass

    @abstractmethod
    def get_detail(self, tender: TenderData) -> TenderData:
        """
        获取招标详情（详情页）

        Args:
            tender: 包含 URL 的 TenderData 对象

        Returns:
            完善后的 TenderData 对象（包含详情页数据）
        """
        pass

    def collect(
        self,
        keywords: List[str],
        category: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        max_results: int = 100,
        fetch_detail: bool = True,
    ) -> List[TenderData]:
        """
        完整采集流程（列表 + 详情）

        Args:
            keywords: 搜索关键词列表
            category: 采购类别
            date_from: 开始日期
            date_to: 结束日期
            max_results: 最大结果数
            fetch_detail: 是否获取详情页

        Returns:
            完整的招标信息列表
        """
        # 第一步：搜索列表
        tenders = self.search(
            keywords=keywords,
            category=category,
            date_from=date_from,
            date_to=date_to,
            max_results=max_results,
        )

        # 第二步：获取详情（可选）
        if fetch_detail:
            for i, tender in enumerate(tenders):
                try:
                    tenders[i] = self.get_detail(tender)
                except Exception as e:
                    print(f"[{self.source_name}] 获取详情失败: {tender.url} - {e}")

        return tenders

    def __repr__(self):
        return f"{self.__class__.__name__}(source='{self.source_code}')"
