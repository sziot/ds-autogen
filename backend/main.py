# main.py - 简化版本
"""
DeepSeek 代码审查系统 - 无数据库版本
"""

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.api.routers import review_simple
from app.api.websocket_manager import WebSocketManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理 - 简化版
    """
    # 启动时
    logger.info("🚀 启动 DeepSeek 代码审查系统（内存版）...")
    
    # 创建必要的目录
    import os
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("fixed", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 初始化 WebSocket 管理器
    app.state.websocket_manager = WebSocketManager()
    logger.info("✅ WebSocket 管理器初始化完成")
    
    yield
    
    # 关闭时
    logger.info("🛑 关闭应用...")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)


# 异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "参数验证失败",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "服务器内部错误",
            "detail": str(exc),
        },
    )


# 健康检查端点
@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "database": "memory_storage",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "storage": "memory",
        "timestamp": asyncio.get_event_loop().time()
    }


# API 文档信息
@app.get("/api-info")
async def api_info():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "endpoints": {
            "upload": "POST /api/v1/review",
            "start_review": "POST /api/v1/review/start?task_id={task_id}",
            "get_status": "GET /api/v1/review/status/{task_id}",
            "get_result": "GET /api/v1/review/result/{task_id}",
            "get_history": "GET /api/v1/review/history",
            "websocket": "WS /ws/review/{task_id}"
        }
    }


# 注册路由
app.include_router(
    review_simple.router,
    prefix="/api/v1/review",
    tags=["代码审查"]
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info",
        access_log=True,
    )