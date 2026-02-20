#!/usr/bin/env python3
"""
测试推送API

用于验证Windows客户端推送功能是否正常工作
"""

import requests
import json
from datetime import datetime

def test_push_api(server_url="http://localhost:8080"):
    """测试推送API"""
    print("=" * 60)
    print("测试招标信息推送API")
    print("=" * 60)
    print()

    # 测试数据
    test_tenders = [
        {
            "title": "[测试] 某区政府信息化建设项目招标公告",
            "url": "http://example.com/tender/123",
            "source": "test",
            "source_name": "测试源",
            "publish_date": datetime.now().isoformat(),
            "deadline": None,
            "project_no": "TEST-2026-001",
            "amount": "500",
            "category": "招标公告",
            "region": "测试区",
            "purchaser": "某区政府办公室",
            "agent": "测试招标代理公司",
            "contact": "张三",
            "phone": "010-12345678",
            "status": "进行中",
            "content": "这是一个测试项目的详细内容...",
            "summary": "测试项目摘要",
            "attachments": [],
            "keywords": ["软件开发", "信息化"],
            "tags": [],
            "raw_data": {},
            "crawled_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "[测试] 智慧城市云平台建设项目",
            "url": "http://example.com/tender/124",
            "source": "test",
            "source_name": "测试源",
            "publish_date": datetime.now().isoformat(),
            "amount": "1200",
            "category": "招标公告",
            "purchaser": "市大数据局",
            "contact": "李四",
            "phone": "010-87654321",
            "keywords": ["云计算", "大数据"],
            "crawled_at": datetime.now().isoformat()
        }
    ]

    push_url = f"{server_url}/api/tenders/push"
    health_url = f"{server_url}/api/tenders/health"

    # 1. 测试健康检查
    print("1. 测试健康检查...")
    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ 服务端正常")
            print(f"   响应: {response.json()}")
        else:
            print(f"   ❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 无法连接到服务端: {server_url}")
        print("   请先启动服务: ./start_api_server.sh")
        return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

    print()

    # 2. 测试推送
    print("2. 测试推送功能...")
    payload = {
        "tenders": test_tenders,
        "client_id": "test_client",
        "keywords": ["软件开发", "信息化", "智慧城市"],
        "auto_inject": True
    }

    try:
        response = requests.post(
            push_url,
            json=payload,
            timeout=30
        )

        print(f"   HTTP状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("   ✅ 推送成功!")
            print(f"   消息: {result.get('message')}")
            print(f"   数据量: {result.get('count')} 条")
            print(f"   保存文件: {result.get('saved_file')}")
            print(f"   已注入HTML: {'是' if result.get('injected') else '否'}")
            return True
        else:
            print(f"   ❌ 推送失败: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    import sys

    server_url = "http://localhost:8080"
    if len(sys.argv) > 1:
        server_url = sys.argv[1]

    print(f"服务端地址: {server_url}")
    print()

    success = test_push_api(server_url)

    print()
    print("=" * 60)
    if success:
        print("✅ 测试通过！")
        print()
        print("下一步:")
        print("1. 查看数据文件: ls -l output/tenders/")
        print("2. 查看HTML报告: output/html/latest/current.html")
        print("3. 启动HTTP服务: cd output/html && python3 -m http.server 8000")
    else:
        print("❌ 测试失败")
        print()
        print("请检查:")
        print("1. API服务是否启动: ./start_api_server.sh")
        print("2. 端口是否正确: 默认8080")
        print("3. 查看服务日志")
    print("=" * 60)


if __name__ == "__main__":
    main()
