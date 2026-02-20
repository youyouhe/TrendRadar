"""
数据库连接和初始化

提供数据库会话管理、表创建、初始数据导入等功能
"""

import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, text
from .models import Base, Source, TagDefinition

# 配置
DATA_DIR = os.getenv("DATA_DIR", "./data")
DB_PATH = Path(DATA_DIR) / "tenders.db"

# 创建异步引擎
# 使用 aiosqlite 驱动
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 生产环境设为False
    future=True,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """
    FastAPI依赖注入函数

    使用方式：
        @router.get("/api/tenders")
        async def get_tenders(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Tender))
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_database():
    """初始化数据库：创建表、索引、默认数据"""
    print("🔧 正在初始化数据库...")

    # 确保数据目录存在
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建索引（SQLite特定）
    async with AsyncSessionLocal() as session:
        # tenders表索引
        await session.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_source_id ON tenders(source_id)"
        ))
        await session.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_publish_date ON tenders(publish_date)"
        ))
        await session.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_status ON tenders(status)"
        ))

        # collect_tasks表索引
        await session.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_task_status ON collect_tasks(status)"
        ))
        await session.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_task_created ON collect_tasks(created_at)"
        ))

        await session.commit()

    # 初始化默认数据
    await init_default_sources()
    await init_default_tags()

    print(f"✅ 数据库初始化成功: {DB_PATH}")


async def init_default_sources():
    """初始化默认采集源"""
    default_sources = [
        {
            "name": "北京市政府采购网",
            "code": "beijing",
            "category": "province",
            "base_url": "http://www.ccgp-beijing.gov.cn/",
            "description": "北京市政府采购官方网站",
        },
        {
            "name": "广东省政府采购网",
            "code": "guangdong",
            "category": "province",
            "base_url": "https://gdgpo.czt.gd.gov.cn",
            "description": "广东省政府采购官方网站",
        },
        {
            "name": "山东省政府采购网",
            "code": "shandong",
            "category": "province",
            "base_url": "https://www.ccgp-shandong.gov.cn",
            "description": "山东省政府采购官方网站",
        },
        {
            "name": "中国政府采购网",
            "code": "govcn",
            "category": "national",
            "base_url": "http://www.ccgp.gov.cn",
            "description": "中国政府采购网全国平台",
        },
        {
            "name": "中国招标投标网",
            "code": "bidcenter",
            "category": "industry",
            "base_url": "https://www.cec.gov.cn",
            "description": "中国招标投标公共服务平台",
        },
    ]

    async with AsyncSessionLocal() as session:
        for source_data in default_sources:
            # 检查是否已存在
            result = await session.execute(
                select(Source).where(Source.code == source_data["code"])
            )
            existing = result.scalar_one_or_none()

            if not existing:
                source = Source(**source_data)
                session.add(source)

        await session.commit()

    print(f"  ✓ 初始化 {len(default_sources)} 个默认采集源")


async def init_default_tags():
    """初始化默认标签"""
    default_tags = [
        {"name": "重点关注", "color": "#ff4444", "sort_order": 1},
        {"name": "待跟进", "color": "#ff9900", "sort_order": 2},
        {"name": "已投标", "color": "#00cc66", "sort_order": 3},
        {"name": "已中标", "color": "#0099ff", "sort_order": 4},
        {"name": "已归档", "color": "#999999", "sort_order": 5},
    ]

    async with AsyncSessionLocal() as session:
        for tag_data in default_tags:
            # 检查是否已存在
            result = await session.execute(
                select(TagDefinition).where(TagDefinition.name == tag_data["name"])
            )
            existing = result.scalar_one_or_none()

            if not existing:
                tag = TagDefinition(**tag_data)
                session.add(tag)

        await session.commit()

    print(f"  ✓ 初始化 {len(default_tags)} 个默认标签")


async def close_database():
    """关闭数据库连接"""
    await engine.dispose()
    print("🔒 数据库连接已关闭")
