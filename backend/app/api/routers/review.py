"""
代码审查路由
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.task_service import TaskService
from app.services.file_service import FileService
from app.api.websocket_manager import get_websocket_manager
from app.models.schemas import CodeReviewResult, TaskStatus
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter()


class UploadResponse(BaseModel):
    """上传响应模型"""
    task_id: str = Field(..., description="任务ID")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    status: str = Field("pending", description="任务状态")


class ReviewRequest(BaseModel):
    """开始审查请求模型"""
    task_id: str = Field(..., description="任务ID")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="审查选项"
    )


class ReviewResponse(BaseModel):
    """审查响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="消息")


@router.post("/upload", response_model=UploadResponse)
async def upload_code_file(
    file: UploadFile = File(..., description="代码文件"),
    file_service: FileService = Depends(FileService),
) -> UploadResponse:
    """
    上传代码文件
    
    Args:
        file: 上传的代码文件
        
    Returns:
        上传响应
    """
    try:
        # 验证文件扩展名
        file_extension = Path(file.filename or "").suffix.lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_extension}。支持的类型: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 保存文件
        saved_path = await file_service.save_upload_file(task_id, file)
        
        # 创建任务记录
        task_service = TaskService()
        await task_service.create_task(
            task_id=task_id,
            file_name=file.filename or "unknown",
            file_path=str(saved_path),
            file_size=file.size or 0
        )
        
        # 发送WebSocket通知
        ws_manager = get_websocket_manager()
        await ws_manager.broadcast_to_task(
            task_id,
            {
                "type": "upload_complete",
                "data": {
                    "task_id": task_id,
                    "file_name": file.filename,
                    "file_size": file.size
                }
            }
        )
        
        return UploadResponse(
            task_id=task_id,
            file_name=file.filename or "unknown",
            file_size=file.size or 0,
            status="pending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )


@router.post("/start", response_model=ReviewResponse)
async def start_code_review(
    request: ReviewRequest,
    background_tasks: BackgroundTasks,
    task_service: TaskService = Depends(TaskService),
) -> ReviewResponse:
    """
    开始代码审查
    
    Args:
        request: 审查请求
        
    Returns:
        审查响应
    """
    try:
        # 获取任务
        task = await task_service.get_task(request.task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"任务 {request.task_id} 不存在"
            )
        
        # 检查任务状态
        if task.status != TaskStatus.PENDING.value:
            raise HTTPException(
                status_code=400,
                detail=f"任务状态为 {task.status}，无法开始审查"
            )
        
        # 更新任务状态
        await task_service.update_task_status(
            task_id=request.task_id,
            status=TaskStatus.PROCESSING,
            message="开始代码审查"
        )
        
        # 在后台启动审查流程
        background_tasks.add_task(
            run_code_review_pipeline,
            request.task_id,
            request.options
        )
        
        return ReviewResponse(
            task_id=request.task_id,
            status=TaskStatus.PROCESSING.value,
            message="代码审查已开始"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # 更新任务状态为失败
        try:
            await task_service.update_task_status(
                task_id=request.task_id,
                status=TaskStatus.FAILED,
                message=f"启动失败: {str(e)}"
            )
        except:
            pass
        
        raise HTTPException(
            status_code=500,
            detail=f"启动审查失败: {str(e)}"
        )


@router.get("/result/{task_id}", response_model=CodeReviewResult)
async def get_review_result(
    task_id: str,
    task_service: TaskService = Depends(TaskService),
) -> CodeReviewResult:
    """
    获取审查结果
    
    Args:
        task_id: 任务ID
        
    Returns:
        审查结果
    """
    try:
        # 获取任务
        task = await task_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"任务 {task_id} 不存在"
            )
        
        # 检查任务是否完成
        if task.status not in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
            raise HTTPException(
                status_code=400,
                detail=f"任务尚未完成，当前状态: {task.status}"
            )
        
        # 返回结果
        result = CodeReviewResult(
            id=task_id,
            file_name=task.file_name,
            original_content=task.original_content or "",
            fixed_content=task.fixed_content or "",
            architect_report=task.architect_report or "",
            reviewer_report=task.reviewer_report or "",
            optimizer_summary=task.optimizer_summary or "",
            quality_score=task.quality_score or 0.0,
            saved_file_path=task.saved_file_path or "",
            created_at=task.created_at,
            diff_stats=task.diff_stats or {}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取结果失败: {str(e)}"
        )


@router.get("/status/{task_id}")
async def get_review_status(
    task_id: str,
    task_service: TaskService = Depends(TaskService),
) -> Dict[str, Any]:
    """
    获取审查状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        审查状态
    """
    try:
        # 获取任务
        task = await task_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"任务 {task_id} 不存在"
            )
        
        # 获取智能体状态
        agent_status = await task_service.get_agent_status(task_id)
        
        return {
            "task_id": task_id,
            "status": task.status,
            "progress": task.progress or 0,
            "message": task.message or "",
            "agents": agent_status,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取状态失败: {str(e)}"
        )


@router.get("/history")
async def get_review_history(
    skip: int = 0,
    limit: int = 20,
    task_service: TaskService = Depends(TaskService),
) -> Dict[str, Any]:
    """
    获取审查历史
    
    Args:
        skip: 跳过记录数
        limit: 限制记录数
        
    Returns:
        审查历史
    """
    try:
        tasks = await task_service.get_tasks(skip=skip, limit=limit)
        total = await task_service.get_task_count()
        
        return {
            "tasks": [
                {
                    "id": task.id,
                    "file_name": task.file_name,
                    "status": task.status,
                    "progress": task.progress,
                    "quality_score": task.quality_score,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                }
                for task in tasks
            ],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
                "has_more": skip + limit < total
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取历史失败: {str(e)}"
        )


async def run_code_review_pipeline(task_id: str, options: Dict[str, Any]):
    """
    运行代码审查管道
    
    Args:
        task_id: 任务ID
        options: 审查选项
    """
    task_service = TaskService()
    ws_manager = get_websocket_manager()
    
    try:
        # 获取任务信息
        task = await task_service.get_task(task_id)
        if not task:
            raise ValueError(f"任务 {task_id} 不存在")
        
        # 读取文件内容
        file_service = FileService()
        file_content = await file_service.read_file(task.file_path)
        
        # 初始化智能体编排器
        orchestrator = AgentOrchestrator(task_id)
        
        # 运行审查流程
        result = await orchestrator.review_code(
            file_content=file_content,
            file_name=task.file_name,
            options=options
        )
        
        # 更新任务结果
        await task_service.update_task_result(
            task_id=task_id,
            result=result,
            status=TaskStatus.COMPLETED
        )
        
        # 发送完成通知
        await ws_manager.broadcast_to_task(
            task_id,
            {
                "type": "result",
                "data": result.dict()
            }
        )
        
    except Exception as e:
        logger.error(f"代码审查失败: {str(e)}", exc_info=True)
        
        # 更新任务状态为失败
        await task_service.update_task_status(
            task_id=task_id,
            status=TaskStatus.FAILED,
            message=f"审查失败: {str(e)}"
        )
        
        # 发送错误通知
        await ws_manager.broadcast_to_task(
            task_id,
            {
                "type": "error",
                "data": {
                    "task_id": task_id,
                    "message": str(e)
                }
            }
        )