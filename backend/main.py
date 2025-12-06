"""
DeepSeek 代码审查系统 - 主应用入口
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routers import api_router
from app.api.websocket_manager import WebSocketManager
from app.services.cache_service import get_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时
    logger.info("🚀 启动 DeepSeek 代码审查系统...")
    
    # 初始化 Redis 连接
    redis_client = get_redis_client()
    await redis_client.ping()
    logger.info("✅ Redis 连接成功")
    
    # 初始化 WebSocket 管理器
    app.state.websocket_manager = WebSocketManager()
    logger.info("✅ WebSocket 管理器初始化完成")
    
    yield
    
    # 关闭时
    logger.info("🛑 关闭应用...")
    await redis_client.close()
    logger.info("✅ Redis 连接已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="基于 AutoGen 的智能代码审查系统 API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# 设置日志
setup_logging()

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)

# 添加全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    请求验证异常处理
    """
    logger.warning(f"请求验证失败: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "参数验证失败",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理
    """
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else "Internal server error",
        },
    )


# 健康检查端点
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 添加 Prometheus 指标端点（如果启用）
if settings.MONITORING_ENABLED:
    from prometheus_client import make_asgi_app
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.ACCESS_LOG,
    )