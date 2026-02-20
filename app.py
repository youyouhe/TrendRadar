#!/usr/bin/env python3
"""
TrendRadar 招标监控系统 - FastAPI 主应用

完全迁移自 tender-monitor-demo (Go项目)
采用 agent-browser + DeepSeek 智能采集方案
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI

# 加载环境变量
load_dotenv()
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# 配置
DATA_DIR = os.getenv("DATA_DIR", "./data")
TRACES_DIR = os.getenv("TRACES_DIR", "./traces")
STATIC_DIR = os.getenv("STATIC_DIR", "./static")

# 创建FastAPI应用
app = FastAPI(
    title="TrendRadar 招标监控系统",
    description="基于 agent-browser + DeepSeek 的智能招标信息采集系统",
    version="2.0.0",
)

# CORS配置（允许前端跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    from database.db import init_database

    # 确保数据目录存在
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    Path(TRACES_DIR).mkdir(parents=True, exist_ok=True)

    # 初始化数据库
    await init_database()

    print("✅ TrendRadar 启动成功")
    print(f"📊 数据目录: {DATA_DIR}")
    print(f"📁 轨迹目录: {TRACES_DIR}")
    print(f"🌐 API文档: http://localhost:8080/docs")


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    print("👋 TrendRadar 已关闭")


# 健康检查
@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "service": "TrendRadar",
        "version": "2.0.0",
        "data_dir": DATA_DIR,
    }


# 根路由 - 返回前端页面
@app.get("/")
async def root():
    """返回前端首页"""
    index_path = Path(STATIC_DIR) / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse(
        status_code=404,
        content={"error": "前端页面未找到，请先迁移 static/index.html"}
    )


# 挂载静态文件目录（如果存在）
if Path(STATIC_DIR).exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# 注册API路由
try:
    from api import tenders, collect, sources, tags
    app.include_router(tenders.router)
    app.include_router(collect.router)
    app.include_router(sources.router)
    app.include_router(tags.router)
except ImportError as e:
    print(f"警告: 部分API模块未找到: {e}")

# 注册招标推送API（Windows客户端推送）
from api import tender_push
app.include_router(tender_push.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
