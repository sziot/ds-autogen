"""
WebSocket 连接管理器 - 完整实现
"""

import asyncio
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

from fastapi import WebSocket


@dataclass
class WebSocketClient:
    """WebSocket 客户端信息"""
    websocket: WebSocket
    client_id: str
    connected_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)


class WebSocketManager:
    """WebSocket 管理器"""
    
    def __init__(self):
        # task_id -> {client_id -> WebSocketClient}
        self.active_connections: Dict[str, Dict[str, WebSocketClient]] = {}
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, task_id: str, client_id: str):
        """连接 WebSocket"""
        await websocket.accept()
        
        async with self.lock:
            if task_id not in self.active_connections:
                self.active_connections[task_id] = {}
            
            client = WebSocketClient(
                websocket=websocket,
                client_id=client_id
            )
            self.active_connections[task_id][client_id] = client
        
        print(f"✅ WebSocket 连接: {client_id} -> 任务 {task_id}")
        
        # 发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "data": {
                "client_id": client_id,
                "task_id": task_id,
                "message": "WebSocket 连接成功",
                "timestamp": datetime.now().isoformat()
            }
        })
    
    async def disconnect(self, task_id: str, client_id: str):
        """断开 WebSocket 连接"""
        async with self.lock:
            if task_id in self.active_connections:
                if client_id in self.active_connections[task_id]:
                    del self.active_connections[task_id][client_id]
                    print(f"❌ WebSocket 断开: {client_id}")
                
                # 清理空的任务连接
                if not self.active_connections[task_id]:
                    del self.active_connections[task_id]
    
    async def send_to_task(self, task_id: str, message: dict):
        """发送消息到特定任务的所有客户端"""
        async with self.lock:
            if task_id not in self.active_connections:
                return
            
            disconnected_clients = []
            
            for client_id, client in self.active_connections[task_id].items():
                try:
                    await client.websocket.send_json(message)
                    client.last_active = datetime.now()
                except Exception as e:
                    print(f"发送消息失败 {client_id}: {e}")
                    disconnected_clients.append(client_id)
            
            # 清理断开连接的客户端
            for client_id in disconnected_clients:
                await self.disconnect(task_id, client_id)
    
    async def send_to_client(self, task_id: str, client_id: str, message: dict):
        """发送消息到特定客户端"""
        async with self.lock:
            if (task_id not in self.active_connections or 
                client_id not in self.active_connections[task_id]):
                return
            
            try:
                await self.active_connections[task_id][client_id].websocket.send_json(message)
                self.active_connections[task_id][client_id].last_active = datetime.now()
            except Exception as e:
                print(f"发送到客户端失败 {client_id}: {e}")
                await self.disconnect(task_id, client_id)
    
    async def broadcast(self, message: dict):
        """广播消息到所有客户端"""
        async with self.lock:
            for task_id in list(self.active_connections.keys()):
                await self.send_to_task(task_id, message)
    
    def get_task_clients(self, task_id: str) -> List[str]:
        """获取任务的客户端列表"""
        if task_id in self.active_connections:
            return list(self.active_connections[task_id].keys())
        return []
    
    def get_connected_tasks(self) -> List[str]:
        """获取有连接的任务列表"""
        return list(self.active_connections.keys())
    
    def get_total_connections(self) -> int:
        """获取总连接数"""
        total = 0
        for clients in self.active_connections.values():
            total += len(clients)
        return total
    
    async def cleanup_inactive(self, timeout_seconds: int = 300):
        """清理不活跃的连接"""
        async with self.lock:
            now = datetime.now()
            to_remove = []
            
            for task_id, clients in self.active_connections.items():
                for client_id, client in clients.items():
                    inactive_time = (now - client.last_active).total_seconds()
                    if inactive_time > timeout_seconds:
                        to_remove.append((task_id, client_id))
            
            for task_id, client_id in to_remove:
                await self.disconnect(task_id, client_id)
            
            if to_remove:
                print(f"🧹 清理了 {len(to_remove)} 个不活跃连接")


# 全局 WebSocket 管理器实例
_websocket_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """获取 WebSocket 管理器单例"""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager