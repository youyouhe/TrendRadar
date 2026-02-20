#!/usr/bin/env python3
"""
测试各省份招标信息采集器

用法：
  python3 test_province_tenders.py shanghai 软件开发
  python3 test_province_tenders.py beijing 信息化 --max 5
  python3 test_province_tenders.py --list
"""

import sys
import json
import argparse
from pathlib import Path

from trendradar.crawler.tender import PROVINCE_SOURCES, get_tender_source


def list_provinces():
    """列出所有支持的省份"""
    print("=" * 60)
    print("支持的省份采集器（共 {} 个）".format(len(PROVINCE_SOURCES)))
    print("=" * 60)
    print()

    regions = {
        "国家级平台": ["china"],
        "华北地区": ["beijing", "tianjin", "hebei", "shanxi", "neimenggu"],
        "东北地区": ["liaoning", "jilin", "heilongjiang"],
        "华东地区": ["shanghai", "jiangsu", "zhejiang", "anhui", "fujian", "jiangxi", "shandong"],
        "华中地区": ["henan", "hubei", "hunan"],
        "华南地区": ["guangdong", "guangxi", "hainan"],
        "西南地区": ["chongqing", "sichuan", "guizhou", "yunnan", "xizang"],
        "西北地区": ["shaanxi", "gansu", "qinghai", "ningxia", "xinjiang"],
    }

    for region_name, codes in regions.items():
        print(f"【{region_name}】")
        for code in codes:
            if code in PROVINCE_SOURCES:
                source = get_tender_source(code)
                print(f"  {code:15s} - {source.source_name}")
        print()


def test_province(province: str, keywords: list, max_results: int = 5, save: bool = False):
    """测试指定省份的采集器"""
    print("=" * 60)
    print(f"测试省份: {province}")
    print(f"关键词: {', '.join(keywords)}")
    print(f"最大结果数: {max_results}")
    print("=" * 60)
    print()

    try:
        # 获取采集器
        source = get_tender_source(province)
        print(f"✅ 采集器: {source.source_name}")
        print(f"   URL: {source.base_url}")
        print()

        # 采集数据
        print("🔍 开始采集...")
        tenders = source.collect(
            keywords=keywords,
            max_results=max_results,
            fetch_detail=True  # 获取详情页
        )

        print()
        print(f"📊 采集结果: {len(tenders)} 条")
        print()

        if not tenders:
            print("⚠️  未采集到数据")
            return

        # 显示结果
        for i, tender in enumerate(tenders, 1):
            print(f"【{i}】{tender.title}")
            print(f"    来源: {tender.source_name}")
            print(f"    URL: {tender.url}")

            if tender.amount:
                print(f"    💰 预算: {tender.amount}万元")

            if tender.publish_date:
                print(f"    📅 发布日期: {tender.publish_date.strftime('%Y-%m-%d')}")

            if tender.deadline:
                print(f"    ⏰ 截止日期: {tender.deadline.strftime('%Y-%m-%d %H:%M')}")

            if tender.purchaser:
                print(f"    🏢 采购人: {tender.purchaser}")

            if tender.contact:
                print(f"    📞 联系人: {tender.contact}")
                if tender.phone:
                    print(f"       电话: {tender.phone}")

            print()

        # 保存结果
        if save:
            output_dir = Path("output/test_tenders")
            output_dir.mkdir(parents=True, exist_ok=True)

            from datetime import datetime
            filename = output_dir / f"test_{province}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            data = [tender.to_dict() for tender in tenders]
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"💾 结果已保存: {filename}")
            print()

    except ValueError as e:
        print(f"❌ 错误: {e}")
    except Exception as e:
        print(f"❌ 采集失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(
        description="测试各省份招标信息采集器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：

  # 列出所有支持的省份
  python3 test_province_tenders.py --list

  # 测试上海市采集器
  python3 test_province_tenders.py shanghai 软件开发

  # 测试北京市采集器，最多5条结果
  python3 test_province_tenders.py beijing 信息化建设 --max 5

  # 测试并保存结果
  python3 test_province_tenders.py shanghai 云计算 --save

  # 测试多个关键词
  python3 test_province_tenders.py guangdong 软件开发 信息化 --max 10
        """
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出所有支持的省份'
    )

    parser.add_argument(
        'province',
        nargs='?',
        help='省份代码（如 shanghai, beijing, guangdong）'
    )

    parser.add_argument(
        'keywords',
        nargs='*',
        help='搜索关键词（可以多个）'
    )

    parser.add_argument(
        '--max', '-m',
        type=int,
        default=5,
        help='最大结果数（默认: 5）'
    )

    parser.add_argument(
        '--save', '-s',
        action='store_true',
        help='保存结果到文件'
    )

    args = parser.parse_args()

    # 列出省份
    if args.list:
        list_provinces()
        return

    # 测试省份
    if not args.province:
        parser.print_help()
        return

    if not args.keywords:
        print("❌ 错误: 请提供至少一个关键词")
        print()
        parser.print_help()
        return

    test_province(
        province=args.province,
        keywords=args.keywords,
        max_results=args.max,
        save=args.save
    )


if __name__ == "__main__":
    main()
