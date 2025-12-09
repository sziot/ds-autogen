# app/api/routers/review_simple.py
"""
简化的代码审查路由 - 无数据库版本
"""

import asyncio
import uuid
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from app.core.config import settings
from app.services.task_service_memory import TaskService
from app.api.websocket_manager import get_websocket_manager

router = APIRouter()


@router.post("/upload")
async def upload_code_file(
    file: UploadFile = File(..., description="代码文件")
):
    """上传代码文件（简化版）"""
    try:
        # 验证文件扩展名
        file_extension = Path(file.filename or "").suffix.lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_extension}"
            )
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 保存文件（简化版，直接保存到 uploads 目录）
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / f"{task_id}_{file.filename}"
        
        # 读取文件内容
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # 创建任务
        task_service = TaskService()
        task = await task_service.create_task(
            file_name=file.filename or "unknown",
            file_path=str(file_path),
            file_size=file.size or len(content)
        )
        
        # 发送WebSocket通知
        ws_manager = get_websocket_manager()
        await ws_manager.send_to_task(
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
        
        return {
            "success": True,
            "task_id": task_id,
            "file_name": file.filename,
            "file_size": file.size,
            "message": "文件上传成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )


@router.post("/start")
async def start_code_review(
    task_id: str,
    background_tasks: BackgroundTasks
):
    """开始代码审查（简化版）"""
    try:
        task_service = TaskService()
        
        # 获取任务
        task = await task_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"任务 {task_id} 不存在"
            )
        
        # 更新任务状态
        await task_service.update_task_status(
            task_id=task_id,
            status="processing",
            message="开始代码审查"
        )
        
        # 在后台启动模拟的审查流程
        background_tasks.add_task(
            mock_code_review_pipeline,
            task_id
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "status": "processing",
            "message": "代码审查已开始"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"启动失败: {str(e)}"
        )


@router.get("/result/{task_id}")
async def get_review_result(task_id: str):
    """获取审查结果（简化版）"""
    try:
        task_service = TaskService()
        
        # 获取任务
        task = await task_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"任务 {task_id} 不存在"
            )
        
        # 检查任务是否完成
        if task.get("status") not in ["completed", "failed"]:
            raise HTTPException(
                status_code=400,
                detail=f"任务尚未完成，当前状态: {task.get('status')}"
            )
        
        # 返回模拟结果
        result = {
            "id": task_id,
            "file_name": task["file_name"],
            "original_content": "def hello():\n    print('Hello World')",
            "fixed_content": "def hello():\n    '''打印欢迎信息'''\n    print('Hello World')",
            "architect_report": "## 架构评估报告\n\n**优点**:\n- 函数结构清晰\n- 功能单一明确\n\n**建议**:\n- 添加函数文档字符串\n- 考虑错误处理机制",
            "reviewer_report": "## 代码审查报告\n\n**问题发现**:\n- 缺少函数文档\n- 没有类型注解\n\n**建议**:\n1. 添加 docstring\n2. 添加类型注解",
            "optimizer_summary": "## 优化总结\n\n已修复以下问题:\n1. 添加了函数文档字符串\n2. 代码结构更清晰\n\n质量评分: 8.5/10",
            "quality_score": 8.5,
            "saved_file_path": f"fixed/{task_id}_fixed.py",
            "created_at": task["created_at"],
            "diff_stats": {
                "additions": 2,
                "deletions": 0,
                "changes": 2
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取结果失败: {str(e)}"
        )


@router.get("/status/{task_id}")
async def get_review_status(task_id: str):
    """获取审查状态（简化版）"""
    try:
        task_service = TaskService()
        
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
            "success": True,
            "task_id": task_id,
            "status": task.get("status", "unknown"),
            "progress": task.get("progress", 0),
            "message": task.get("message", ""),
            "agents": agent_status,
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取状态失败: {str(e)}"
        )


@router.get("/history")
async def get_review_history(limit: int = 10):
    """获取审查历史（简化版）"""
    try:
        task_service = TaskService()
        
        tasks = await task_service.get_tasks(limit=limit)
        
        return {
            "success": True,
            "tasks": tasks,
            "total": len(tasks)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取历史失败: {str(e)}"
        )


async def mock_code_review_pipeline(task_id: str):
    """模拟代码审查流程"""
    task_service = TaskService()
    ws_manager = get_websocket_manager()
    
    try:
        # 模拟审查过程
        agents = ["Architect", "Reviewer", "Optimizer", "User_Proxy"]
        
        for i, agent in enumerate(agents):
            # 更新智能体状态
            await task_service.update_agent_status(
                task_id=task_id,
                agent_name=agent,
                status="processing",
                message=f"{agent} 正在工作...",
                progress=25 * i
            )
            
            # 发送WebSocket通知
            await ws_manager.send_to_task(
                task_id,
                {
                    "type": "agent_update",
                    "data": {
                        "agent": agent,
                        "status": "processing",
                        "message": f"{agent} 正在分析代码",
                        "progress": 25 * (i + 1)
                    }
                }
            )
            
            # 模拟处理时间
            await asyncio.sleep(2)
            
            # 完成该智能体
            await task_service.update_agent_status(
                task_id=task_id,
                agent_name=agent,
                status="completed",
                message=f"{agent} 已完成",
                progress=25 * (i + 1)
            )
        
        # 更新总体进度
        await task_service.update_task_status(
            task_id=task_id,
            status="completed",
            progress=100,
            message="代码审查完成"
        )
        
        # 生成模拟结果
        result = {
            "original_content": "def hello():\n    print('Hello World')",
            "fixed_content": "def hello():\n    '''打印欢迎信息'''\n    print('Hello World')",
            "architect_report": "架构分析完成",
            "reviewer_report": "代码审查完成",
            "optimizer_summary": "代码优化完成",
            "quality_score": 8.5,
            "saved_file_path": f"fixed/{task_id}_fixed.py",
            "diff_stats": {"additions": 2, "deletions": 0, "changes": 2}
        }
        
        await task_service.update_task_result(task_id, result)
        
        # 发送完成通知
        await ws_manager.send_to_task(
            task_id,
            {
                "type": "result",
                "data": {
                    "id": task_id,
                    "file_name": "example.py",
                    **result
                }
            }
        )
        
    except Exception as e:
        print(f"模拟审查失败: {e}")
        
        await task_service.update_task_status(
            task_id=task_id,
            status="failed",
            message=f"审查失败: {str(e)}"
        )
        
        await ws_manager.send_to_task(
            task_id,
            {
                "type": "error",
                "data": {
                    "task_id": task_id,
                    "message": str(e)
                }
            }
        )
