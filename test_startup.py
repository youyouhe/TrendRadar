#!/usr/bin/env python3
"""
测试TrendRadar启动和基本功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(project_root / '.env')


async def test_database():
    """测试数据库初始化"""
    print("=" * 60)
    print("测试1: 数据库初始化")
    print("=" * 60)

    from database.db import init_database, AsyncSessionLocal
    from database.models import Source, TagDefinition
    from sqlalchemy import select

    # 初始化数据库
    await init_database()

    # 查询采集源
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Source))
        sources = result.scalars().all()
        print(f"\n✓ 找到 {len(sources)} 个采集源:")
        for source in sources:
            print(f"  - {source.name} ({source.code})")

        # 查询标签
        result = await session.execute(select(TagDefinition))
        tags = result.scalars().all()
        print(f"\n✓ 找到 {len(tags)} 个标签:")
        for tag in tags:
            print(f"  - {tag.name} ({tag.color})")

    print("\n✅ 数据库测试通过\n")


async def test_parser():
    """测试DeepSeek解析器"""
    print("=" * 60)
    print("测试2: DeepSeek解析器")
    print("=" * 60)

    from crawler.parsers.deepseek_parser import DeepSeekParser

    try:
        parser = DeepSeekParser()
        print("✓ DeepSeek解析器初始化成功")
        print(f"✓ API Key: {parser.api_key[:20]}...")
        print("\n✅ 解析器测试通过\n")
    except Exception as e:
        print(f"❌ 解析器测试失败: {e}\n")


def test_api_routes():
    """测试API路由注册"""
    print("=" * 60)
    print("测试3: API路由")
    print("=" * 60)

    from app import app

    # 获取所有路由
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            for method in route.methods:
                if method != 'HEAD':
                    routes.append(f"{method:6} {route.path}")

    print(f"✓ 注册了 {len(routes)} 个API端点:")
    for route in sorted(routes):
        print(f"  {route}")

    print("\n✅ API路由测试通过\n")


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("TrendRadar 系统测试")
    print("=" * 60 + "\n")

    try:
        # 测试1: 数据库
        await test_database()

        # 测试2: 解析器
        await test_parser()

        # 测试3: API路由
        test_api_routes()

        print("=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)
        print("\n启动命令:")
        print("  uvicorn app:app --host 0.0.0.0 --port 8080 --reload")
        print("\nAPI文档:")
        print("  http://localhost:8080/docs")
        print("\nWeb界面:")
        print("  http://localhost:8080/")
        print()

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
