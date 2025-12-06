"""
任务服务
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc

from app.models.database import get_db_session
from app.models.models import Task, AgentStatus
from app.models.schemas import TaskStatus, CodeReviewResult
from app.services.cache_service import get_redis_client


class TaskService:
    """任务服务"""
    
    def __init__(self):
        self.redis_client = get_redis_client()
    
    async def create_task(
        self,
        task_id: str,
        file_name: str,
        file_path: str,
        file_size: int,
        options: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        创建任务
        
        Args:
            task_id: 任务ID
            file_name: 文件名
            file_path: 文件路径
            file_size: 文件大小
            options: 任务选项
            
        Returns:
            任务对象
        """
        async with get_db_session() as session:
            try:
                # 创建任务记录
                task = Task(
                    id=task_id,
                    file_name=file_name,
                    file_path=file_path,
                    file_size=file_size,
                    status=TaskStatus.PENDING.value,
                    progress=0,
                    options=options or {},
                    created_at=datetime.utcnow()
                )
                
                session.add(task)
                await session.commit()
                await session.refresh(task)
                
                # 缓存任务信息
                await self._cache_task(task)
                
                logger.info(f"创建任务成功: {task_id}")
                return task
                
            except Exception as e:
                await session.rollback()
                logger.error(f"创建任务失败: {str(e)}")
                raise
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务对象
        """
        # 尝试从缓存获取
        cached_task = await self._get_cached_task(task_id)
        if cached_task:
            return cached_task
        
        # 从数据库获取
        async with get_db_session() as session:
            try:
                stmt = select(Task).where(Task.id == task_id)
                result = await session.execute(stmt)
                task = result.scalar_one_or_none()
                
                if task:
                    await self._cache_task(task)
                
                return task
                
            except Exception as e:
                logger.error(f"获取任务失败: {str(e)}")
                return None
    
    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        message: Optional[str] = None,
        progress: Optional[float] = None
    ) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 任务状态
            message: 状态消息
            progress: 进度百分比
            
        Returns:
            是否成功
        """
        async with get_db_session() as session:
            try:
                update_data = {
                    "status": status.value,
                    "updated_at": datetime.utcnow()
                }
                
                if message:
                    update_data["message"] = message
                
                if progress is not None:
                    update_data["progress"] = progress
                
                if status == TaskStatus.COMPLETED:
                    update_data["completed_at"] = datetime.utcnow()
                elif status == TaskStatus.FAILED:
                    update_data["failed_at"] = datetime.utcnow()
                
                stmt = (
                    update(Task)
                    .where(Task.id == task_id)
                    .values(**update_data)
                )
                
                result = await session.execute(stmt)
                await session.commit()
                
                # 清理缓存
                await self._clear_task_cache(task_id)
                
                return result.rowcount > 0
                
            except Exception as e:
                await session.rollback()
                logger.error(f"更新任务状态失败: {str(e)}")
                return False
    
    async def update_task_result(
        self,
        task_id: str,
        result: CodeReviewResult,
        status: TaskStatus = TaskStatus.COMPLETED
    ) -> bool:
        """
        更新任务结果
        
        Args:
            task_id: 任务ID
            result: 审查结果
            status: 任务状态
            
        Returns:
            是否成功
        """
        async with get_db_session() as session:
            try:
                update_data = {
                    "status": status.value,
                    "progress": 100,
                    "original_content": result.original_content,
                    "fixed_content": result.fixed_content,
                    "architect_report": result.architect_report,
                    "reviewer_report": result.reviewer_report,
                    "optimizer_summary": result.optimizer_summary,
                    "quality_score": result.quality_score,
                    "saved_file_path": result.saved_file_path,
                    "diff_stats": result.diff_stats,
                    "updated_at": datetime.utcnow(),
                    "completed_at": datetime.utcnow()
                }
                
                stmt = (
                    update(Task)
                    .where(Task.id == task_id)
                    .values(**update_data)
                )
                
                result = await session.execute(stmt)
                await session.commit()
                
                # 清理缓存
                await self._clear_task_cache(task_id)
                
                return result.rowcount > 0
                
            except Exception as e:
                await session.rollback()
                logger.error(f"更新任务结果失败: {str(e)}")
                return False
    
    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[TaskStatus] = None,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> List[Task]:
        """
        获取任务列表
        
        Args:
            skip: 跳过记录数
            limit: 限制记录数
            status: 任务状态筛选
            order_by: 排序字段
            order_desc: 是否降序
            
        Returns:
            任务列表
        """
        async with get_db_session() as session:
            try:
                stmt = select(Task)
                
                if status:
                    stmt = stmt.where(Task.status == status.value)
                
                # 排序
                order_column = getattr(Task, order_by, Task.created_at)
                if order_desc:
                    stmt = stmt.order_by(desc(order_column))
                else:
                    stmt = stmt.order_by(order_column)
                
                # 分页
                stmt = stmt.offset(skip).limit(limit)
                
                result = await session.execute(stmt)
                tasks = result.scalars().all()
                
                return tasks
                
            except Exception as e:
                logger.error(f"获取任务列表失败: {str(e)}")
                return []
    
    async def get_task_count(
        self,
        status: Optional[TaskStatus] = None
    ) -> int:
        """
        获取任务数量
        
        Args:
            status: 任务状态筛选
            
        Returns:
            任务数量
        """
        async with get_db_session() as session:
            try:
                stmt = select(func.count(Task.id))
                
                if status:
                    stmt = stmt.where(Task.status == status.value)
                
                result = await session.execute(stmt)
                count = result.scalar()
                
                return count or 0
                
            except Exception as e:
                logger.error(f"获取任务数量失败: {str(e)}")
                return 0
    
    async def update_agent_status(
        self,
        task_id: str,
        agent_name: str,
        status: str,
        message: str,
        progress: float = 0.0
    ) -> bool:
        """
        更新智能体状态
        
        Args:
            task_id: 任务ID
            agent_name: 智能体名称
            status: 状态
            message: 状态消息
            progress: 进度百分比
            
        Returns:
            是否成功
        """
        async with get_db_session() as session:
            try:
                # 查找现有状态
                stmt = select(AgentStatus).where(
                    (AgentStatus.task_id == task_id) &
                    (AgentStatus.agent_name == agent_name)
                )
                
                result = await session.execute(stmt)
                agent_status = result.scalar_one_or_none()
                
                if agent_status:
                    # 更新现有状态
                    agent_status.status = status
                    agent_status.message = message
                    agent_status.progress = progress
                    agent_status.updated_at = datetime.utcnow()
                else:
                    # 创建新状态
                    agent_status = AgentStatus(
                        task_id=task_id,
                        agent_name=agent_name,
                        status=status,
                        message=message,
                        progress=progress,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(agent_status)
                
                await session.commit()
                
                # 更新缓存
                await self._cache_agent_status(task_id, agent_status)
                
                return True
                
            except Exception as e:
                await session.rollback()
                logger.error(f"更新智能体状态失败: {str(e)}")
                return False
    
    async def get_agent_status(self, task_id: str) -> List[Dict[str, Any]]:
        """
        获取智能体状态列表
        
        Args:
            task_id: 任务ID
            
        Returns:
            智能体状态列表
        """
        async with get_db_session() as session:
            try:
                stmt = select(AgentStatus).where(
                    AgentStatus.task_id == task_id
                ).order_by(AgentStatus.created_at)
                
                result = await session.execute(stmt)
                agents = result.scalars().all()
                
                return [
                    {
                        "agent_name": agent.agent_name,
                        "status": agent.status,
                        "message": agent.message,
                        "progress": agent.progress,
                        "created_at": agent.created_at.isoformat() if agent.created_at else None,
                        "updated_at": agent.updated_at.isoformat() if agent.updated_at else None
                    }
                    for agent in agents
                ]
                
            except Exception as e:
                logger.error(f"获取智能体状态失败: {str(e)}")
                return []
    
    async def cleanup_old_tasks(self, days: int = 30) -> int:
        """
        清理旧任务
        
        Args:
            days: 保留天数
            
        Returns:
            清理的任务数量
        """
        async with get_db_session() as session:
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                # 删除智能体状态
                stmt_agents = delete(AgentStatus).where(
                    AgentStatus.task_id.in_(
                        select(Task.id).where(Task.created_at < cutoff_date)
                    )
                )
                await session.execute(stmt_agents)
                
                # 删除任务
                stmt_tasks = delete(Task).where(Task.created_at < cutoff_date)
                result = await session.execute(stmt_tasks)
                
                await session.commit()
                
                cleaned_count = result.rowcount
                logger.info(f"清理了 {cleaned_count} 个旧任务")
                
                return cleaned_count
                
            except Exception as e:
                await session.rollback()
                logger.error(f"清理旧任务失败: {str(e)}")
                return 0
    
    # 缓存相关方法
    
    async def _cache_task(self, task: Task) -> None:
        """缓存任务"""
        try:
            cache_key = f"task:{task.id}"
            cache_data = {
                "id": task.id,
                "file_name": task.file_name,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            }
            
            await self.redis_client.set(
                cache_key,
                json.dumps(cache_data),
                ex=300  # 5分钟过期
            )
            
        except Exception as e:
            logger.warning(f"缓存任务失败: {str(e)}")
    
    async def _get_cached_task(self, task_id: str) -> Optional[Task]:
        """获取缓存的任务"""
        try:
            cache_key = f"task:{task_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                
                # 转换为 Task 对象
                task = Task(
                    id=data["id"],
                    file_name=data["file_name"],
                    status=data["status"],
                    progress=data["progress"],
                    created_at=datetime.fromisoformat(data["created_at"]) if data["created_at"] else None,
                    updated_at=datetime.fromisoformat(data["updated_at"]) if data["updated_at"] else None
                )
                
                return task
                
        except Exception as e:
            logger.warning(f"获取缓存任务失败: {str(e)}")
        
        return None
    
    async def _clear_task_cache(self, task_id: str) -> None:
        """清理任务缓存"""
        try:
            cache_key = f"task:{task_id}"
            await self.redis_client.delete(cache_key)
        except Exception as e:
            logger.warning(f"清理任务缓存失败: {str(e)}")
    
    async def _cache_agent_status(
        self, 
        task_id: str, 
        agent_status: AgentStatus
    ) -> None:
        """缓存智能体状态"""
        try:
            cache_key = f"agent_status:{task_id}:{agent_status.agent_name}"
            cache_data = {
                "agent_name": agent_status.agent_name,
                "status": agent_status.status,
                "message": agent_status.message,
                "progress": agent_status.progress,
                "updated_at": agent_status.updated_at.isoformat() if agent_status.updated_at else None
            }
            
            await self.redis_client.set(
                cache_key,
                json.dumps(cache_data),
                ex=60  # 1分钟过期
            )
            
        except Exception as e:
            logger.warning(f"缓存智能体状态失败: {str(e)}")