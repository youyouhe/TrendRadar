"""
招标信息查询 API

提供招标信息的查询、筛选、更新、导出功能
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from pydantic import BaseModel
import csv
import io

from database.db import get_db
from database.models import Tender, Source

router = APIRouter()


class TenderUpdate(BaseModel):
    """招标信息更新请求"""
    status: Optional[str] = None
    tags: Optional[str] = None
    note: Optional[str] = None


@router.get("/api/tenders")
async def get_tenders(
    source_id: Optional[int] = Query(None, description="采集源ID"),
    keyword: Optional[str] = Query(None, description="关键词"),
    match_mode: str = Query("any", description="关键词匹配模式: any/all/exact"),
    status: Optional[str] = Query(None, description="状态筛选: active/archived"),
    date_from: Optional[str] = Query(None, description="起始日期 YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    tags: Optional[str] = Query(None, description="标签筛选（逗号分隔）"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    查询招标信息列表

    支持多种筛选条件和分页
    """
    # 构建查询
    query = select(Tender)

    # 采集源筛选
    if source_id:
        query = query.where(Tender.source_id == source_id)

    # 状态筛选
    if status:
        query = query.where(Tender.status == status)

    # 日期范围筛选
    if date_from:
        query = query.where(Tender.publish_date >= date_from)
    if date_to:
        query = query.where(Tender.publish_date <= date_to)

    # 标签筛选
    if tags:
        tag_list = tags.split(',')
        tag_conditions = [Tender.tags.like(f'%{tag}%') for tag in tag_list]
        query = query.where(or_(*tag_conditions))

    # 关键词筛选
    if keyword:
        keywords = keyword.split()

        if match_mode == "exact":
            # 精确匹配：整个关键词字符串
            query = query.where(
                or_(
                    Tender.title.like(f'%{keyword}%'),
                    Tender.content.like(f'%{keyword}%')
                )
            )
        elif match_mode == "all":
            # 全部匹配：包含所有关键词
            for kw in keywords:
                query = query.where(
                    or_(
                        Tender.title.like(f'%{kw}%'),
                        Tender.content.like(f'%{kw}%')
                    )
                )
        else:  # any
            # 任意匹配：包含任一关键词
            conditions = []
            for kw in keywords:
                conditions.extend([
                    Tender.title.like(f'%{kw}%'),
                    Tender.content.like(f'%{kw}%')
                ])
            query = query.where(or_(*conditions))

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()

    # 分页
    offset = (page - 1) * limit
    query = query.order_by(Tender.publish_date.desc()).offset(offset).limit(limit)

    # 执行查询
    result = await db.execute(query)
    tenders = result.scalars().all()

    # 计算总页数
    total_pages = (total + limit - 1) // limit

    return {
        "data": [tender.to_dict() for tender in tenders],
        "total": total,
        "page": page,
        "page_size": limit,
        "total_pages": total_pages,
    }


@router.get("/api/tenders/{tender_id}")
async def get_tender_detail(
    tender_id: int,
    db: AsyncSession = Depends(get_db)
):
    """查询单个招标信息详情"""
    result = await db.execute(
        select(Tender).where(Tender.id == tender_id)
    )
    tender = result.scalar_one_or_none()

    if not tender:
        raise HTTPException(status_code=404, detail="招标信息不存在")

    return tender.to_dict()


@router.post("/api/tenders/{tender_id}")
async def update_tender(
    tender_id: int,
    update_data: TenderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新招标信息

    支持更新状态、标签、备注
    """
    result = await db.execute(
        select(Tender).where(Tender.id == tender_id)
    )
    tender = result.scalar_one_or_none()

    if not tender:
        raise HTTPException(status_code=404, detail="招标信息不存在")

    # 更新字段
    if update_data.status is not None:
        tender.status = update_data.status
    if update_data.tags is not None:
        tender.tags = update_data.tags
    if update_data.note is not None:
        tender.note = update_data.note

    await db.commit()

    return {"success": True, "message": "更新成功"}


@router.get("/api/tenders/export")
async def export_tenders(
    source_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    导出招标信息为CSV

    使用与查询相同的筛选条件
    """
    # 构建查询（与get_tenders类似，但不分页）
    query = select(Tender)

    if source_id:
        query = query.where(Tender.source_id == source_id)
    if status:
        query = query.where(Tender.status == status)
    if date_from:
        query = query.where(Tender.publish_date >= date_from)
    if date_to:
        query = query.where(Tender.publish_date <= date_to)
    if keyword:
        query = query.where(
            or_(
                Tender.title.like(f'%{keyword}%'),
                Tender.content.like(f'%{keyword}%')
            )
        )

    query = query.order_by(Tender.publish_date.desc())

    result = await db.execute(query)
    tenders = result.scalars().all()

    # 生成CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # 写入表头
    writer.writerow([
        'ID', '标题', '金额', '发布日期', '截止日期',
        '联系人', '电话', '状态', '标签', '备注', 'URL'
    ])

    # 写入数据
    for tender in tenders:
        writer.writerow([
            tender.id,
            tender.title,
            tender.amount,
            tender.publish_date,
            tender.deadline,
            tender.contact,
            tender.phone,
            tender.status,
            tender.tags,
            tender.note,
            tender.url
        ])

    # 返回CSV文件
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),  # BOM for Excel
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=tenders_export.csv"
        }
    )
