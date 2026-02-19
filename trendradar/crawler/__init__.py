# coding=utf-8
"""
爬虫模块 - 数据抓取功能
"""

from trendradar.crawler.fetcher import DataFetcher
from trendradar.crawler.agent_browser import AgentBrowser
from trendradar.crawler.tender import (
    TenderSource,
    TenderData,
    ShandongTenderSource,
    get_tender_source,
)

__all__ = [
    "DataFetcher",
    "AgentBrowser",
    "TenderSource",
    "TenderData",
    "ShandongTenderSource",
    "get_tender_source",
]
