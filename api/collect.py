"""
采集任务 API

提供采集任务的创建、查询、取消功能
"""

import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from database.db import get_db
from crawler.task_manager import task_manager
from crawler.collector import TenderCollector

router = APIRouter()

# 从环境变量获取DeepSeek API Key
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")


class CollectRequest(BaseModel):
    """采集请求"""
    source_id: int
    keywords: List[str]
    max_items: int = 10


@router.post("/api/collect")
async def create_collect_task(
    request: CollectRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    创建采集任务

    Args:
        request: 采集请求（source_id, keywords, max_items）

    Returns:
        任务ID和初始状态
    """
    if not DEEPSEEK_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="未配置 DEEPSEEK_API_KEY，请在环境变量或.env文件中设置"
        )

    # 创建采集器
    collector = TenderCollector(
        deepseek_api_key=DEEPSEEK_API_KEY,
        headless=True
    )

    # 创建并启动任务
    try:
        task_id = await task_manager.create_task(
            db=db,
            source_id=request.source_id,
            keywords=request.keywords,
            collector_func=collector.collect,
            max_items=request.max_items
        )

        return {
            "success": True,
            "task_id": task_id,
            "message": "采集任务已创建"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/api/collect/tasks")
async def list_collect_tasks(
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    查询采集任务列表

    Args:
        status: 状态筛选（pending/running/completed/failed/cancelled）
        limit: 最大返回数量

    Returns:
        任务列表
    """
    tasks = await task_manager.list_tasks(db, status=status, limit=limit)

    return {
        "success": True,
        "data": tasks,
        "total": len(tasks)
    }


@router.get("/api/collect/tasks/{task_id}")
async def get_collect_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    查询单个采集任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务详细信息
    """
    task = await task_manager.get_task_status(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "success": True,
        "data": task
    }


@router.post("/api/collect/tasks/{task_id}/cancel")
async def cancel_collect_task(task_id: str):
    """
    取消采集任务

    Args:
        task_id: 任务ID

    Returns:
        是否成功取消
    """
    success = await task_manager.cancel_task(task_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="任务不存在或已完成，无法取消"
        )

    return {
        "success": True,
        "message": "任务已取消"
    }
