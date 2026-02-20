"""
标签管理 API

提供标签的查询和管理功能
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from database.db import get_db
from database.models import TagDefinition

router = APIRouter()


class TagCreate(BaseModel):
    """创建标签请求"""
    name: str
    color: Optional[str] = None
    sort_order: Optional[int] = 0


@router.get("/api/tags")
async def list_tags(db: AsyncSession = Depends(get_db)):
    """
    查询标签列表

    Returns:
        标签列表（按sort_order排序）
    """
    query = select(TagDefinition).order_by(TagDefinition.sort_order)

    result = await db.execute(query)
    tags = result.scalars().all()

    return {
        "success": True,
        "data": [tag.to_dict() for tag in tags],
        "total": len(tags)
    }


@router.get("/api/tags/{tag_id}")
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db)
):
    """查询单个标签详情"""
    result = await db.execute(
        select(TagDefinition).where(TagDefinition.id == tag_id)
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    return {
        "success": True,
        "data": tag.to_dict()
    }


@router.post("/api/tags")
async def create_tag(
    request: TagCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新标签

    Args:
        request: 标签信息

    Returns:
        新创建的标签
    """
    # 检查名称是否已存在
    result = await db.execute(
        select(TagDefinition).where(TagDefinition.name == request.name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail=f"标签 {request.name} 已存在")

    # 创建新标签
    tag = TagDefinition(
        name=request.name,
        color=request.color,
        sort_order=request.sort_order
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return {
        "success": True,
        "data": tag.to_dict(),
        "message": "标签创建成功"
    }


@router.put("/api/tags/{tag_id}")
async def update_tag(
    tag_id: int,
    request: TagCreate,
    db: AsyncSession = Depends(get_db)
):
    """更新标签信息"""
    result = await db.execute(
        select(TagDefinition).where(TagDefinition.id == tag_id)
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 更新字段
    tag.name = request.name
    tag.color = request.color
    tag.sort_order = request.sort_order

    await db.commit()

    return {
        "success": True,
        "message": "标签更新成功"
    }


@router.delete("/api/tags/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除标签"""
    result = await db.execute(
        select(TagDefinition).where(TagDefinition.id == tag_id)
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    await db.delete(tag)
    await db.commit()

    return {
        "success": True,
        "message": "标签已删除"
    }
