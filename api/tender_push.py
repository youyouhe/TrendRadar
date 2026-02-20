#!/usr/bin/env python3
"""
招标信息推送接收端API

Windows客户端采集的招标信息可以推送到此API，自动保存并触发HTML重新生成
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import subprocess

router = APIRouter(prefix="/api/tenders", tags=["招标推送"])


class TenderItem(BaseModel):
    """招标信息模型"""
    title: str
    url: str
    source: str
    source_name: str
    publish_date: Optional[str] = None
    deadline: Optional[str] = None
    project_no: Optional[str] = None
    amount: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    purchaser: Optional[str] = None
    agent: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    status: str = "未知"
    content: Optional[str] = None
    summary: Optional[str] = None
    attachments: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    raw_data: Dict = Field(default_factory=dict)
    crawled_at: Optional[str] = None
    updated_at: Optional[str] = None


class TenderPushRequest(BaseModel):
    """推送请求模型"""
    tenders: List[TenderItem]
    client_id: Optional[str] = None  # 客户端标识（如 windows_client_1）
    keywords: Optional[List[str]] = None  # 使用的关键词
    auto_inject: bool = True  # 是否自动注入到HTML


class TenderPushResponse(BaseModel):
    """推送响应模型"""
    success: bool
    message: str
    saved_file: Optional[str] = None
    count: int
    injected: bool = False


def save_tender_data(tenders: List[Dict], client_id: Optional[str] = None) -> Path:
    """保存招标数据到JSON文件"""
    output_dir = Path("output/tenders")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 文件名包含客户端ID（如果有）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if client_id:
        filename = output_dir / f"tenders_{client_id}_{timestamp}.json"
    else:
        filename = output_dir / f"tenders_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tenders, f, ensure_ascii=False, indent=2)

    return filename


def inject_to_html_background():
    """后台任务：注入招标信息到HTML"""
    try:
        result = subprocess.run(
            ["python3", "inject_tenders_to_html.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"[推送API] HTML注入成功: {result.stdout}")
        else:
            print(f"[推送API] HTML注入失败: {result.stderr}")
    except Exception as e:
        print(f"[推送API] HTML注入异常: {e}")


@router.post("/push", response_model=TenderPushResponse)
async def push_tenders(
    request: TenderPushRequest,
    background_tasks: BackgroundTasks
):
    """
    接收招标信息推送

    Windows客户端采集完成后，调用此API推送数据到服务端
    """
    if not request.tenders:
        raise HTTPException(status_code=400, detail="招标数据为空")

    # 转换为字典列表
    tenders_data = [tender.model_dump() for tender in request.tenders]

    # 保存到文件
    try:
        saved_file = save_tender_data(
            tenders_data,
            client_id=request.client_id
        )
        print(f"[推送API] 收到推送: {len(tenders_data)} 条，来自客户端 {request.client_id or '未知'}")
        print(f"[推送API] 数据已保存: {saved_file}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")

    # 自动注入到HTML（后台任务）
    injected = False
    if request.auto_inject:
        background_tasks.add_task(inject_to_html_background)
        injected = True

    return TenderPushResponse(
        success=True,
        message=f"成功接收 {len(tenders_data)} 条招标信息",
        saved_file=str(saved_file),
        count=len(tenders_data),
        injected=injected
    )


@router.get("/latest")
async def get_latest_tenders(limit: int = 20):
    """
    获取最新的招标数据

    返回最近保存的招标信息
    """
    tender_dir = Path("output/tenders")
    if not tender_dir.exists():
        return {"tenders": [], "count": 0}

    # 找到最新的JSON文件
    tender_files = sorted(tender_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not tender_files:
        return {"tenders": [], "count": 0}

    # 读取最新文件
    with open(tender_files[0], 'r', encoding='utf-8') as f:
        tenders = json.load(f)

    return {
        "tenders": tenders[:limit],
        "count": len(tenders),
        "file": str(tender_files[0]),
        "updated_at": datetime.fromtimestamp(tender_files[0].stat().st_mtime).isoformat()
    }


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "tender_push_api",
        "timestamp": datetime.now().isoformat()
    }
