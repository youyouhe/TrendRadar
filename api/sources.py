"""
采集源管理 API

提供采集源的查询和管理功能
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from database.db import get_db
from database.models import Source

router = APIRouter()


class SourceCreate(BaseModel):
    """创建采集源请求"""
    name: str
    code: str
    category: str
    base_url: Optional[str] = None
    description: Optional[str] = None


@router.get("/api/sources")
async def list_sources(
    category: Optional[str] = None,
    is_active: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    查询采集源列表

    Args:
        category: 分类筛选（province/national/industry）
        is_active: 是否启用筛选（0/1）

    Returns:
        采集源列表
    """
    query = select(Source)

    if category:
        query = query.where(Source.category == category)
    if is_active is not None:
        query = query.where(Source.is_active == is_active)

    query = query.order_by(Source.created_at.desc())

    result = await db.execute(query)
    sources = result.scalars().all()

    return {
        "success": True,
        "data": [source.to_dict() for source in sources],
        "total": len(sources)
    }


@router.get("/api/sources/{source_id}")
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """查询单个采集源详情"""
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = result.scalar_one_or_none()

    if not source:
        raise HTTPException(status_code=404, detail="采集源不存在")

    return {
        "success": True,
        "data": source.to_dict()
    }


@router.post("/api/sources")
async def create_source(
    request: SourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的采集源

    Args:
        request: 采集源信息

    Returns:
        新创建的采集源
    """
    # 检查code是否已存在
    result = await db.execute(
        select(Source).where(Source.code == request.code)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail=f"采集源代码 {request.code} 已存在")

    # 创建新采集源
    source = Source(
        name=request.name,
        code=request.code,
        category=request.category,
        base_url=request.base_url,
        description=request.description
    )

    db.add(source)
    await db.commit()
    await db.refresh(source)

    return {
        "success": True,
        "data": source.to_dict(),
        "message": "采集源创建成功"
    }


@router.put("/api/sources/{source_id}")
async def update_source(
    source_id: int,
    request: SourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """更新采集源信息"""
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = result.scalar_one_or_none()

    if not source:
        raise HTTPException(status_code=404, detail="采集源不存在")

    # 更新字段
    source.name = request.name
    source.code = request.code
    source.category = request.category
    source.base_url = request.base_url
    source.description = request.description

    await db.commit()

    return {
        "success": True,
        "message": "采集源更新成功"
    }


@router.delete("/api/sources/{source_id}")
async def delete_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除采集源（软删除，设置is_active=0）"""
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = result.scalar_one_or_none()

    if not source:
        raise HTTPException(status_code=404, detail="采集源不存在")

    source.is_active = 0
    await db.commit()

    return {
        "success": True,
        "message": "采集源已禁用"
    }
