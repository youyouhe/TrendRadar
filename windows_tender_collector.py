#!/usr/bin/env python3
"""
Windows 招标信息采集客户端

在Windows上运行，采集招标信息并推送到TrendRadar服务端
支持定时采集、断点续传、失败重试
"""

import sys
import json
import time
import requests
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import yaml

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from trendradar.crawler.tender import fetch_tender_data


class WindowsTenderCollector:
    """Windows招标采集客户端"""

    def __init__(
        self,
        server_url: str,
        client_id: str = "windows_client",
        config_file: str = "config/tender_sources.yaml"
    ):
        self.server_url = server_url.rstrip('/')
        self.client_id = client_id
        self.config_file = Path(config_file)

        # 加载配置
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """加载配置文件"""
        if not self.config_file.exists():
            print(f"❌ 配置文件不存在: {self.config_file}")
            sys.exit(1)

        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get_keywords(self) -> List[str]:
        """
        获取关键词列表

        从 frequency_words.txt 读取，如果不存在则使用默认关键词
        """
        keywords_file = Path("config/frequency_words.txt")
        keywords = []

        if keywords_file.exists():
            try:
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('['):
                            keywords.append(line)
                            if len(keywords) >= 5:  # 只取前5个
                                break
            except Exception as e:
                print(f"⚠️  读取关键词文件失败: {e}")

        # 如果没有读到关键词，使用默认值
        if not keywords:
            keywords = ["软件开发", "信息化", "智慧城市"]

        return keywords

    def collect_tenders(self, sources: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        采集招标信息

        Args:
            sources: 采集源列表
            keywords: 关键词列表

        Returns:
            招标信息列表
        """
        max_items = self.config.get('TENDER_SETTINGS', {}).get('MAX_ITEMS_PER_SOURCE', 10)

        print(f"🔍 开始采集...")
        print(f"   采集源: {len(sources)} 个")
        print(f"   关键词: {keywords}")
        print(f"   每源数量: {max_items}")
        print()

        try:
            tenders = fetch_tender_data(
                sources=sources,
                keywords=keywords,
                max_items_per_source=max_items
            )
            return tenders
        except Exception as e:
            print(f"❌ 采集失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def push_to_server(
        self,
        tenders: List[Dict],
        keywords: List[str],
        auto_inject: bool = True
    ) -> bool:
        """
        推送数据到服务端

        Args:
            tenders: 招标信息列表
            keywords: 使用的关键词
            auto_inject: 是否自动注入到HTML

        Returns:
            是否成功
        """
        if not tenders:
            print("⚠️  没有数据需要推送")
            return False

        push_url = f"{self.server_url}/api/tenders/push"
        payload = {
            "tenders": tenders,
            "client_id": self.client_id,
            "keywords": keywords,
            "auto_inject": auto_inject
        }

        print(f"📤 推送到服务端: {push_url}")
        print(f"   数据量: {len(tenders)} 条")

        try:
            response = requests.post(
                push_url,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 推送成功!")
                print(f"   服务端消息: {result.get('message')}")
                print(f"   保存文件: {result.get('saved_file')}")
                if result.get('injected'):
                    print(f"   已触发HTML注入")
                return True
            else:
                print(f"❌ 推送失败: HTTP {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False

        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到服务端: {self.server_url}")
            print(f"   请确保TrendRadar服务正在运行")
            return False
        except Exception as e:
            print(f"❌ 推送异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    def save_local_backup(self, tenders: List[Dict]):
        """保存本地备份（推送失败时使用）"""
        backup_dir = Path("output/tenders_backup")
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = backup_dir / f"backup_{self.client_id}_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tenders, f, ensure_ascii=False, indent=2)

        print(f"💾 本地备份已保存: {filename}")

    def run_once(self, dry_run: bool = False):
        """
        运行一次采集

        Args:
            dry_run: 只采集不推送（测试用）
        """
        print("=" * 60)
        print(f"Windows 招标采集客户端 - {self.client_id}")
        print(f"服务端: {self.server_url}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()

        # 检查服务端连接
        if not dry_run:
            try:
                health_url = f"{self.server_url}/api/tenders/health"
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    print("✅ 服务端连接正常")
                else:
                    print(f"⚠️  服务端健康检查失败: HTTP {response.status_code}")
            except Exception as e:
                print(f"⚠️  无法连接到服务端: {e}")
                print("   将只进行本地保存")
                dry_run = True
            print()

        # 获取启用的采集源
        sources = [
            s for s in self.config.get('TENDER_SOURCES', [])
            if s.get('enabled', False)
        ]

        if not sources:
            print("❌ 没有启用的采集源")
            print("   请编辑 config/tender_sources.yaml 并启用至少一个采集源")
            return

        # 获取关键词
        keywords = self.get_keywords()

        # 采集
        tenders = self.collect_tenders(sources, keywords)

        print()
        print(f"📊 采集结果: {len(tenders)} 条")
        print()

        if not tenders:
            print("⚠️  本次采集未获取到数据")
            return

        # 显示前3条样本
        print("样本数据（前3条）:")
        for i, tender in enumerate(tenders[:3], 1):
            print(f"{i}. {tender.get('title', 'N/A')[:50]}")
            print(f"   来源: {tender.get('source_name', 'N/A')}")
            if tender.get('amount'):
                print(f"   预算: {tender['amount']}万")
        print()

        # 推送或保存
        if dry_run:
            print("🔍 试运行模式，不推送到服务端")
            self.save_local_backup(tenders)
        else:
            success = self.push_to_server(tenders, keywords)
            if not success:
                print("⚠️  推送失败，保存本地备份")
                self.save_local_backup(tenders)

        print()
        print("=" * 60)
        print("✅ 任务完成")
        print("=" * 60)

    def run_scheduled(self, interval_minutes: int = 60):
        """
        定时运行采集

        Args:
            interval_minutes: 采集间隔（分钟）
        """
        print(f"⏰ 定时采集模式")
        print(f"   间隔: {interval_minutes} 分钟")
        print(f"   按 Ctrl+C 停止")
        print()

        while True:
            try:
                self.run_once()
                print(f"⏳ 下次采集时间: {interval_minutes} 分钟后")
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                print("\n👋 用户中断，程序退出")
                break
            except Exception as e:
                print(f"❌ 运行异常: {e}")
                import traceback
                traceback.print_exc()
                print(f"⏳ 60秒后重试...")
                time.sleep(60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Windows招标信息采集客户端",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：

  # 运行一次采集并推送
  python windows_tender_collector.py --server http://192.168.1.100:8080

  # 试运行（不推送）
  python windows_tender_collector.py --server http://localhost:8080 --dry-run

  # 定时采集（每30分钟）
  python windows_tender_collector.py --server http://192.168.1.100:8080 --schedule 30

  # 指定客户端ID
  python windows_tender_collector.py --server http://192.168.1.100:8080 --client-id office_pc
        """
    )

    parser.add_argument(
        '--server',
        default='http://localhost:8080',
        help='TrendRadar服务端地址（默认: http://localhost:8080）'
    )

    parser.add_argument(
        '--client-id',
        default='windows_client',
        help='客户端标识（默认: windows_client）'
    )

    parser.add_argument(
        '--config',
        default='config/tender_sources.yaml',
        help='配置文件路径（默认: config/tender_sources.yaml）'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式（只采集不推送）'
    )

    parser.add_argument(
        '--schedule',
        type=int,
        metavar='MINUTES',
        help='定时采集间隔（分钟），不指定则只运行一次'
    )

    args = parser.parse_args()

    # 创建采集器
    collector = WindowsTenderCollector(
        server_url=args.server,
        client_id=args.client_id,
        config_file=args.config
    )

    # 运行
    if args.schedule:
        collector.run_scheduled(interval_minutes=args.schedule)
    else:
        collector.run_once(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
