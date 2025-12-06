"""
API 路由器
"""

from fastapi import APIRouter

from app.api.routers import review, files, ws, health

api_router = APIRouter()

# 注册路由
api_router.include_router(health.router, tags=["健康检查"])
api_router.include_router(review.router, prefix="/review", tags=["代码审查"])
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])
api_router.include_router(ws.router, prefix="/ws", tags=["WebSocket"])