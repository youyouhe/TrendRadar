# coding=utf-8
"""
招标信息采集模块

支持多省份政府采购网站的招标信息采集，使用 agent-browser 进行语义化自动化。
"""

from typing import List, Dict, Optional

from trendradar.crawler.tender.base import TenderSource, TenderData, TenderStatus
from trendradar.crawler.tender.shandong import ShandongTenderSource
from trendradar.crawler.tender.guangdong import GuangdongTenderSource
from trendradar.crawler.tender.beijing import BeijingTenderSource

__all__ = [
    "TenderSource",
    "TenderData",
    "TenderStatus",
    "ShandongTenderSource",
    "GuangdongTenderSource",
    "BeijingTenderSource",
    "get_tender_source",
    "fetch_tender_data",
]


# 省份代码映射
PROVINCE_SOURCES = {
    "shandong": ShandongTenderSource,
    "guangdong": GuangdongTenderSource,
    "beijing": BeijingTenderSource,
}


def get_tender_source(province: str) -> TenderSource:
    """
    获取指定省份的招标数据源

    Args:
        province: 省份代码（如 shandong, guangdong, beijing）

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


def fetch_tender_data(
    sources: List[Dict],
    keywords: List[str],
    max_items_per_source: int = 10,
    deepseek_api_key: Optional[str] = None
) -> List[Dict]:
    """
    采集招标信息的主函数（供TrendRadar调用）

    Args:
        sources: 采集源列表 [{"id": "beijing", "name": "...", "url": "...", "enabled": true}]
        keywords: 关键词列表
        max_items_per_source: 每个源最多采集数量
        deepseek_api_key: DeepSeek API密钥（可选，会从环境变量读取）

    Returns:
        招标信息列表（字典格式）
    """
    all_tenders = []

    for source_config in sources:
        if not source_config.get('enabled', True):
            continue

        source_id = source_config.get('id', '')

        try:
            # 获取对应的采集器
            source = get_tender_source(source_id)

            # 采集数据
            tenders = source.collect(
                keywords=keywords,
                max_results=max_items_per_source,
                fetch_detail=True
            )

            # 转换为字典格式
            for tender in tenders:
                all_tenders.append(tender.to_dict())

        except ValueError as e:
            print(f"[招标] 不支持的采集源: {source_id} - {e}")
        except Exception as e:
            print(f"[招标] 采集失败 {source_id}: {e}")

    return all_tenders
