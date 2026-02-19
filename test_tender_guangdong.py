#!/usr/bin/env python3
# coding=utf-8
"""
广东省招标信息采集测试脚本

优点：对 Linux 友好，无验证码

用法:
    python3 test_tender_guangdong.py
"""

import sys
from datetime import datetime
from trendradar.crawler.tender import get_tender_source


def main():
    """测试广东省招标信息采集"""
    print("=" * 60)
    print("广东省招标信息采集测试")
    print("=" * 60)

    # 获取广东数据源
    try:
        source = get_tender_source("guangdong")
        print(f"\n✓ 数据源: {source.source_name}")
        print(f"  代码: {source.source_code}")
        print(f"  网站: {source.base_url}")
        print(f"  特点: 对 Linux 友好，无验证码")
    except Exception as e:
        print(f"\n✗ 获取数据源失败: {e}")
        return 1

    # 测试搜索功能
    keywords = ["软件开发", "信息化"]
    category = "服务"  # 服务类采购

    print(f"\n搜索参数:")
    print(f"  关键词: {keywords}")
    print(f"  类别: {category}")
    print(f"  最大结果: 10")

    print("\n开始搜索...")
    print("-" * 60)

    try:
        results = source.search(
            keywords=keywords,
            category=category,
            max_results=10
        )

        print(f"\n✓ 搜索完成，找到 {len(results)} 条结果\n")

        # 显示结果
        for i, tender in enumerate(results, 1):
            print(f"{i}. {tender.title}")
            print(f"   发布日期: {tender.publish_date or '未知'}")
            print(f"   URL: {tender.url}")
            print(f"   关键词: {', '.join(tender.keywords)}")
            print()

        # 测试详情获取（仅第一条）
        if results:
            print("-" * 60)
            print("测试详情获取（第一条）...")
            print("-" * 60)

            detail = source.get_detail(results[0])
            print(f"\n标题: {detail.title}")
            print(f"金额: {detail.amount or '未获取'}")
            print(f"联系人: {detail.contact or '未获取'}")
            print(f"电话: {detail.phone or '未获取'}")

    except Exception as e:
        print(f"\n✗ 搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
