# coding=utf-8
"""
招标信息采集模块

支持多省份政府采购网站的招标信息采集，使用 agent-browser 进行语义化自动化。
"""

from trendradar.crawler.tender.base import TenderSource, TenderData, TenderStatus
from trendradar.crawler.tender.shandong import ShandongTenderSource

__all__ = [
    "TenderSource",
    "TenderData",
    "TenderStatus",
    "ShandongTenderSource",
]


# 省份代码映射
PROVINCE_SOURCES = {
    "shandong": ShandongTenderSource,
    # 未来扩展：
    # "guangdong": GuangdongTenderSource,
    # "zhejiang": ZhejiangTenderSource,
}


def get_tender_source(province: str) -> TenderSource:
    """
    获取指定省份的招标数据源

    Args:
        province: 省份代码（如 shandong, guangdong）

    Returns:
        TenderSource 实例

    Raises:
        ValueError: 不支持的省份
    """
    source_class = PROVINCE_SOURCES.get(province.lower())
    if not source_class:
        raise ValueError(
            f"不支持的省份: {province}，"
            f"支持的省份: {', '.join(PROVINCE_SOURCES.keys())}"
        )

    return source_class()
