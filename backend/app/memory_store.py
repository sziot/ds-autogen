# app/memory_store.py
"""
基于内存的数据存储
使用字典和列表存储数据，重启后数据会丢失
"""

import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class TaskData:
    """任务数据类"""
    id: str
    file_name: str
    file_path: str
    file_size: int
    status: str = "pending"  # pending, processing, completed, failed
    progress: float = 0.0
    message: Optional[str] = None
    original_content: Optional[str] = None
    fixed_content: Optional[str] = None
    architect_report: Optional[str] = None
    reviewer_report: Optional[str] = None
    optimizer_summary: Optional[str] = None
    quality_score: Optional[float] = None
    saved_file_path: Optional[str] = None
    diff_stats: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    
    def to_dict(self):
        """转换为字典"""
        data = asdict(self)
        # 转换 datetime 为字符串
        for key in ['created_at', 'updated_at', 'started_at', 'completed_at', 'failed_at']:
            if data[key]:
                data[key] = data[key].isoformat()
        return data


@dataclass
class AgentStatusData:
    """智能体状态数据类"""
    id: int
    task_id: str
    agent_name: str  # Architect, Reviewer, Optimizer, User_Proxy
    status: str = "idle"  # idle, processing, completed, error
    message: Optional[str] = None
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class MemoryStore:
    """内存数据存储管理器"""
    
    def __init__(self):
        # 使用字典存储数据
        self.tasks: Dict[str, TaskData] = {}
        self.agent_statuses: List[AgentStatusData] = []
        self._lock = asyncio.Lock()  # 用于并发控制
        self._agent_counter = 0
    
    async def create_task(self, task_data: Dict[str, Any]) -> TaskData:
        """创建任务"""
        async with self._lock:
            task_id = str(uuid.uuid4())
            task = TaskData(
                id=task_id,
                file_name=task_data["file_name"],
                file_path=task_data["file_path"],
                file_size=task_data["file_size"],
                options=task_data.get("options", {})
            )
            
            self.tasks[task_id] = task
            
            # 初始化智能体状态
            for agent_name in ["Architect", "Reviewer", "Optimizer", "User_Proxy"]:
                self._agent_counter += 1
                agent_status = AgentStatusData(
                    id=self._agent_counter,
                    task_id=task_id,
                    agent_name=agent_name,
                    status="idle"
                )
                self.agent_statuses.append(agent_status)
            
            print(f"✅ 创建任务: {task_id} - {task.file_name}")
            return task
    
    async def get_task(self, task_id: str) -> Optional[TaskData]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """更新任务"""
        async with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            
            # 更新字段
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            task.updated_at = datetime.now()
            
            # 如果是状态变更，更新时间戳
            if "status" in updates:
                if updates["status"] == "processing" and not task.started_at:
                    task.started_at = datetime.now()
                elif updates["status"] == "completed" and not task.completed_at:
                    task.completed_at = datetime.now()
                elif updates["status"] == "failed" and not task.failed_at:
                    task.failed_at = datetime.now()
            
            print(f"📝 更新任务: {task_id} - 状态: {updates.get('status', '未变')}")
            return True
    
    async def update_agent_status(self, task_id: str, agent_name: str, 
                                 status: str, message: str = "", 
                                 progress: float = 0.0) -> bool:
        """更新智能体状态"""
        async with self._lock:
            for agent in self.agent_statuses:
                if agent.task_id == task_id and agent.agent_name == agent_name:
                    agent.status = status
                    agent.message = message
                    agent.progress = progress
                    agent.updated_at = datetime.now()
                    
                    print(f"🤖 智能体状态更新: {agent_name} - {status}")
                    return True
            
            # 如果没找到，创建新的状态
            self._agent_counter += 1
            new_agent = AgentStatusData(
                id=self._agent_counter,
                task_id=task_id,
                agent_name=agent_name,
                status=status,
                message=message,
                progress=progress
            )
            self.agent_statuses.append(new_agent)
            return True
    
    async def get_agent_statuses(self, task_id: str) -> List[Dict[str, Any]]:
        """获取任务的智能体状态"""
        agents = []
        for agent in self.agent_statuses:
            if agent.task_id == task_id:
                agents.append({
                    "agent_name": agent.agent_name,
                    "status": agent.status,
                    "message": agent.message,
                    "progress": agent.progress,
                    "created_at": agent.created_at.isoformat(),
                    "updated_at": agent.updated_at.isoformat()
                })
        
        # 确保四个智能体都存在
        agent_names = {a["agent_name"] for a in agents}
        for required_agent in ["Architect", "Reviewer", "Optimizer", "User_Proxy"]:
            if required_agent not in agent_names:
                await self.update_agent_status(task_id, required_agent, "idle", "等待启动")
        
        return await self.get_agent_statuses(task_id)  # 重新获取
    
    async def get_all_tasks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取所有任务"""
        tasks = list(self.tasks.values())
        # 按创建时间倒序排序
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        return [task.to_dict() for task in tasks[:limit]]
    
    async def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        async with self._lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                # 删除相关的智能体状态
                self.agent_statuses = [
                    a for a in self.agent_statuses 
                    if a.task_id != task_id
                ]
                print(f"🗑️ 删除任务: {task_id}")
                return True
            return False
    
    async def clear_all(self):
        """清空所有数据"""
        async with self._lock:
            self.tasks.clear()
            self.agent_statuses.clear()
            self._agent_counter = 0
            print("🧹 已清空所有数据")


# 全局内存存储实例
memory_store = MemoryStore()