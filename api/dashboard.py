#!/usr/bin/env python3
"""
TrendRadar Web Dashboard API

提供统一的Web界面浏览所有信息：
- 最新报告展示
- 历史报告列表
- 招标信息查询
- 数据统计分析
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import APIRouter, Query
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


class ReportInfo(BaseModel):
    """报告信息"""
    filename: str
    date: str
    time: str
    file_path: str
    size: int
    created_at: str


class TenderInfo(BaseModel):
    """招标信息摘要"""
    title: str
    source_name: str
    publish_date: Optional[str]
    amount: Optional[str]
    url: str


class DashboardStats(BaseModel):
    """Dashboard统计数据"""
    total_reports: int
    total_tenders: int
    latest_report_time: Optional[str]
    latest_tender_time: Optional[str]
    reports_last_7days: int
    tenders_last_7days: int


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """获取Dashboard统计数据"""
    output_dir = Path("output")

    # 统计报告数量
    html_dir = output_dir / "html"
    html_files = list(html_dir.rglob("*.html")) if html_dir.exists() else []

    # 统计招标数量
    tender_dir = output_dir / "tenders"
    total_tenders = 0
    latest_tender_time = None
    tenders_last_7days = 0

    if tender_dir.exists():
        tender_files = sorted(tender_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        for tender_file in tender_files:
            try:
                with open(tender_file, 'r', encoding='utf-8') as f:
                    tenders = json.load(f)
                    total_tenders += len(tenders)

                    # 最新时间
                    if not latest_tender_time:
                        latest_tender_time = datetime.fromtimestamp(tender_file.stat().st_mtime).isoformat()

                    # 7天内数量
                    file_time = datetime.fromtimestamp(tender_file.stat().st_mtime)
                    if datetime.now() - file_time < timedelta(days=7):
                        tenders_last_7days += len(tenders)
            except:
                pass

    # 最新报告时间
    latest_report_time = None
    if html_files:
        latest_file = max(html_files, key=lambda x: x.stat().st_mtime)
        latest_report_time = datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()

    # 7天内报告数量
    reports_last_7days = 0
    for f in html_files:
        file_time = datetime.fromtimestamp(f.stat().st_mtime)
        if datetime.now() - file_time < timedelta(days=7):
            reports_last_7days += 1

    return DashboardStats(
        total_reports=len(html_files),
        total_tenders=total_tenders,
        latest_report_time=latest_report_time,
        latest_tender_time=latest_tender_time,
        reports_last_7days=reports_last_7days,
        tenders_last_7days=tenders_last_7days
    )


@router.get("/reports", response_model=List[ReportInfo])
async def list_reports(
    limit: int = Query(default=50, ge=1, le=200),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """
    获取报告列表

    Args:
        limit: 返回数量限制
        date_from: 开始日期 (YYYY-MM-DD)
        date_to: 结束日期 (YYYY-MM-DD)
    """
    html_dir = Path("output/html")
    if not html_dir.exists():
        return []

    # 收集所有HTML文件
    html_files = []
    for html_file in html_dir.rglob("*.html"):
        if html_file.name == "index.html":  # 跳过索引文件
            continue

        stat = html_file.stat()
        created_time = datetime.fromtimestamp(stat.st_mtime)

        # 日期过滤
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from)
            if created_time < date_from_dt:
                continue

        if date_to:
            date_to_dt = datetime.fromisoformat(date_to) + timedelta(days=1)
            if created_time > date_to_dt:
                continue

        # 从路径解析日期和时间
        parts = html_file.parts
        date_str = parts[-2] if len(parts) > 1 and parts[-2] != "html" else "unknown"
        time_str = html_file.stem

        # 安全处理文件路径
        try:
            # 尝试获取相对于当前目录的路径
            rel_path = html_file.relative_to(Path.cwd())
            file_path_str = str(rel_path)
        except ValueError:
            # 如果失败，使用绝对路径
            file_path_str = str(html_file.absolute())

        html_files.append(ReportInfo(
            filename=html_file.name,
            date=date_str,
            time=time_str,
            file_path=file_path_str,
            size=stat.st_size,
            created_at=created_time.isoformat()
        ))

    # 按时间倒序排序
    html_files.sort(key=lambda x: x.created_at, reverse=True)

    return html_files[:limit]


@router.get("/reports/latest")
async def get_latest_report():
    """获取最新报告（返回HTML内容）"""
    latest_file = Path("output/html/latest/current.html")

    if latest_file.exists():
        return FileResponse(
            latest_file,
            media_type="text/html",
            headers={"Cache-Control": "no-cache"}
        )

    # 如果latest不存在，找最新的报告
    html_dir = Path("output/html")
    if html_dir.exists():
        html_files = [f for f in html_dir.rglob("*.html") if f.name != "index.html"]
        if html_files:
            latest = max(html_files, key=lambda x: x.stat().st_mtime)
            return FileResponse(
                latest,
                media_type="text/html",
                headers={"Cache-Control": "no-cache"}
            )

    return HTMLResponse(
        content="<h1>暂无报告</h1><p>请先运行 TrendRadar 生成报告</p>",
        status_code=404
    )


@router.get("/reports/file")
async def get_report_file(file_path: str):
    """
    获取指定报告文件

    Args:
        file_path: 相对路径，如 output/html/2026-02-20/14-01.html
    """
    report_file = Path(file_path)

    # 安全检查：必须在output目录下
    try:
        report_file = report_file.resolve()
        output_dir = Path("output").resolve()
        if not str(report_file).startswith(str(output_dir)):
            return HTMLResponse(content="<h1>非法路径</h1>", status_code=403)
    except:
        return HTMLResponse(content="<h1>路径错误</h1>", status_code=400)

    if report_file.exists():
        return FileResponse(
            report_file,
            media_type="text/html",
            headers={"Cache-Control": "no-cache"}
        )

    return HTMLResponse(
        content=f"<h1>报告未找到</h1><p>{file_path}</p>",
        status_code=404
    )


@router.get("/tenders/recent", response_model=List[TenderInfo])
async def get_recent_tenders(limit: int = Query(default=20, ge=1, le=100)):
    """获取最近的招标信息"""
    tender_dir = Path("output/tenders")
    if not tender_dir.exists():
        return []

    # 找最新的文件
    tender_files = sorted(tender_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not tender_files:
        return []

    # 读取最新文件
    tenders = []
    for tender_file in tender_files[:3]:  # 读取最近3个文件
        try:
            with open(tender_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if len(tenders) >= limit:
                        break

                    tenders.append(TenderInfo(
                        title=item.get('title', ''),
                        source_name=item.get('source_name', ''),
                        publish_date=item.get('publish_date'),
                        amount=item.get('amount'),
                        url=item.get('url', '')
                    ))

            if len(tenders) >= limit:
                break
        except:
            continue

    return tenders[:limit]


@router.get("/tenders/search")
async def search_tenders(
    keyword: str = Query(default="", min_length=1),
    source: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200)
):
    """
    搜索招标信息

    Args:
        keyword: 搜索关键词
        source: 来源筛选
        limit: 返回数量
    """
    tender_dir = Path("output/tenders")
    if not tender_dir.exists():
        return {"tenders": [], "count": 0}

    results = []
    tender_files = sorted(tender_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

    for tender_file in tender_files:
        try:
            with open(tender_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    # 关键词过滤
                    if keyword and keyword.lower() not in item.get('title', '').lower():
                        continue

                    # 来源过滤
                    if source and item.get('source') != source:
                        continue

                    results.append(TenderInfo(
                        title=item.get('title', ''),
                        source_name=item.get('source_name', ''),
                        publish_date=item.get('publish_date'),
                        amount=item.get('amount'),
                        url=item.get('url', '')
                    ))

                    if len(results) >= limit:
                        break

            if len(results) >= limit:
                break
        except:
            continue

    return {
        "tenders": results,
        "count": len(results),
        "keyword": keyword,
        "source": source
    }
