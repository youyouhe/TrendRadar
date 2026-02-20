#!/usr/bin/env python3
"""
TrendRadar + 招标信息整合版

在TrendRadar主流程中添加招标信息采集，在HTML报告中展示
"""

import os
import sys
from pathlib import Path
import yaml

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# 导入TrendRadar主程序
from trendradar.__main__ import NewsAnalyzer, main as trendradar_main
from trendradar.crawler.tender import fetch_tender_data


def load_tender_config():
    """加载招标配置"""
    config_path = Path("config/tender_sources.yaml")
    if not config_path.exists():
        print("[招标] 未找到配置文件: config/tender_sources.yaml")
        return None

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def collect_tenders(tender_config, frequency_words):
    """采集招标信息"""
    if not tender_config or not tender_config.get('TENDER_ENABLED', False):
        print("[招标] 招标采集未启用")
        return []

    sources = tender_config.get('TENDER_SOURCES', [])
    settings = tender_config.get('TENDER_SETTINGS', {})

    # 启用的源
    enabled_sources = [s for s in sources if s.get('enabled', True)]

    if not enabled_sources:
        print("[招标] 没有启用的采集源")
        return []

    # 关键词（从 frequency_words 提取）
    keywords = []
    if settings.get('USE_KEYWORD_FILTER', True) and frequency_words:
        # 提取第一组关键词
        for group in frequency_words:
            if isinstance(group, dict) and 'keywords' in group:
                keywords.extend(group['keywords'][:3])  # 取前3个
                break

    if not keywords:
        keywords = ["软件开发", "信息化"]  # 默认关键词

    print(f"[招标] 使用关键词: {keywords}")

    # 采集
    tenders = fetch_tender_data(
        sources=enabled_sources,
        keywords=keywords,
        max_items_per_source=settings.get('MAX_ITEMS_PER_SOURCE', 10)
    )

    return tenders


def integrate_tenders_into_standalone(standalone_data, tenders, tender_config):
    """将招标信息整合到独立展示区数据"""
    if not tenders:
        return standalone_data

    if standalone_data is None:
        standalone_data = {
            "platforms": [],
            "rss_feeds": [],
            "tenders": []
        }

    # 添加招标数据
    display_settings = tender_config.get('TENDER_DISPLAY', {})
    max_items = display_settings.get('MAX_DISPLAY_ITEMS', 20)

    tender_items = []
    for tender in tenders[:max_items]:
        # 直接传递原始数据，HTML生成器会处理
        tender_items.append(tender)

    standalone_data["tenders"] = tender_items

    return standalone_data


def run_with_tenders():
    """运行TrendRadar + 招标信息"""
    print("=" * 60)
    print("TrendRadar + 招标信息整合版")
    print("=" * 60)
    print()

    # 加载招标配置
    tender_config = load_tender_config()

    # 加载关键词（用于过滤招标）
    try:
        with open('config/frequency_words.txt', 'r', encoding='utf-8') as f:
            # 简单解析（提取关键词组）
            frequency_words = []
            current_group = None
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('['):
                    if current_group:
                        frequency_words.append(current_group)
                    current_group = {"keywords": []}
                elif current_group is not None:
                    current_group["keywords"].append(line)
            if current_group:
                frequency_words.append(current_group)
    except:
        frequency_words = []

    # 采集招标信息
    tenders = []
    if tender_config and tender_config.get('TENDER_ENABLED', False):
        tenders = collect_tenders(tender_config, frequency_words)
        print(f"[招标] 采集完成：{len(tenders)} 条")

    if tenders:
        # 保存到文件
        import json
        output_dir = Path("output/tenders")
        output_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        filename = output_dir / f"tenders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tenders, f, ensure_ascii=False, indent=2)

        print(f"[招标] 数据已保存: {filename}")

        # 将招标数据保存到环境变量，供TrendRadar使用
        import os
        os.environ['TRENDRADAR_TENDER_DATA'] = str(filename)
        print(f"[招标] 数据路径已设置为环境变量")

    # 运行TrendRadar主程序
    print("\n正在运行TrendRadar主程序...")
    print("=" * 60)
    trendradar_main()

    # 自动注入招标信息到HTML报告
    if tenders:
        print("\n" + "=" * 60)
        print("正在注入招标信息到HTML报告...")
        print("=" * 60)
        try:
            from inject_tenders_to_html import inject_tenders_to_html
            from pathlib import Path

            html_file = Path("output/html/latest/current.html")
            if html_file.exists():
                success = inject_tenders_to_html(html_file, tenders)
                if success:
                    print(f"[招标] ✅ 已自动注入到HTML报告")
                else:
                    print(f"[招标] ⚠️  注入失败，但不影响主流程")
            else:
                print(f"[招标] ⚠️  HTML报告不存在: {html_file}")
        except Exception as e:
            print(f"[招标] ⚠️  自动注入异常: {e}")
            print(f"[招标] 您可以手动运行: python3 inject_tenders_to_html.py")

    print("\n" + "=" * 60)
    print("✅ 全部完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_with_tenders()
