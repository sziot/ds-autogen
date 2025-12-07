# app/services/task_service_memory.py
"""
基于内存存储的任务服务
"""

from typing import Dict, List, Optional, Any
from app.memory_store import memory_store


class TaskService:
    """任务服务（内存版本）"""
    
    def __init__(self):
        self.store = memory_store
    
    async def create_task(
        self,
        file_name: str,
        file_path: str,
        file_size: int,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """创建任务"""
        task_data = {
            "file_name": file_name,
            "file_path": file_path,
            "file_size": file_size,
            "options": options or {}
        }
        
        task = await self.store.create_task(task_data)
        return task.to_dict()
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务"""
        task = await self.store.get_task(task_id)
        return task.to_dict() if task else None
    
    async def update_task_status(
        self,
        task_id: str,
        status: str,
        message: Optional[str] = None,
        progress: Optional[float] = None
    ) -> bool:
        """更新任务状态"""
        updates = {"status": status}
        
        if message:
            updates["message"] = message
        if progress is not None:
            updates["progress"] = progress
        
        return await self.store.update_task(task_id, updates)
    
    async def update_task_result(
        self,
        task_id: str,
        result: Dict[str, Any]
    ) -> bool:
        """更新任务结果"""
        return await self.store.update_task(task_id, result)
    
    async def update_agent_status(
        self,
        task_id: str,
        agent_name: str,
        status: str,
        message: str = "",
        progress: float = 0.0
    ) -> bool:
        """更新智能体状态"""
        return await self.store.update_agent_status(
            task_id, agent_name, status, message, progress
        )
    
    async def get_agent_status(self, task_id: str) -> List[Dict[str, Any]]:
        """获取智能体状态"""
        return await self.store.get_agent_statuses(task_id)
    
    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取任务列表"""
        all_tasks = await self.store.get_all_tasks(limit + skip)
        return all_tasks[skip:skip + limit]
    
    async def get_task_count(self) -> int:
        """获取任务数量"""
        all_tasks = await self.store.get_all_tasks(1000)  # 获取足够多的任务
        return len(all_tasks)
    
    async def cleanup_old_tasks(self, days: int = 1) -> int:
        """清理旧任务（内存版本只保留最近的任务）"""
        # 内存版本简单实现：保留最多100个任务
        all_tasks = await self.store.get_all_tasks(1000)
        if len(all_tasks) > 100:
            tasks_to_keep = all_tasks[:100]
            # 清空并重新添加
            await self.store.clear_all()
            for task_dict in tasks_to_keep:
                await self.store.create_task(task_dict)
            
            return len(all_tasks) - 100
        return 0