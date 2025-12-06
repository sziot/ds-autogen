"""
WebSocket 管理器
"""

import asyncio
import json
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

from fastapi import WebSocket
from loguru import logger


@dataclass
class WebSocketClient:
    """WebSocket 客户端"""
    websocket: WebSocket
    client_id: str
    subscribed_events: Set[str] = field(default_factory=set)


class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocketClient]] = {}
        self.lock = asyncio.Lock()
    
    async def register_client(
        self, 
        task_id: str, 
        client_id: str, 
        websocket: WebSocket
    ):
        """
        注册 WebSocket 客户端
        
        Args:
            task_id: 任务ID
            client_id: 客户端ID
            websocket: WebSocket 连接
        """
        async with self.lock:
            if task_id not in self.active_connections:
                self.active_connections[task_id] = {}
            
            client = WebSocketClient(
                websocket=websocket,
                client_id=client_id
            )
            self.active_connections[task_id][client_id] = client
    
    async def unregister_client(self, task_id: str, client_id: str):
        """
        注销 WebSocket 客户端
        
        Args:
            task_id: 任务ID
            client_id: 客户端ID
        """
        async with self.lock:
            if task_id in self.active_connections:
                if client_id in self.active_connections[task_id]:
                    del self.active_connections[task_id][client_id]
                
                # 如果该任务没有客户端了，清理任务记录
                if not self.active_connections[task_id]:
                    del self.active_connections[task_id]
    
    async def broadcast_to_task(
        self, 
        task_id: str, 
        message: Dict[str, any]
    ):
        """
        向特定任务的所有客户端广播消息
        
        Args:
            task_id: 任务ID
            message: 消息内容
        """
        async with self.lock:
            if task_id not in self.active_connections:
                return
            
            disconnected_clients = []
            
            for client_id, client in self.active_connections[task_id].items():
                try:
                    await client.websocket.send_json(message)
                except Exception as e:
                    logger.error(f"发送消息到客户端 {client_id} 失败: {str(e)}")
                    disconnected_clients.append(client_id)
            
            # 清理断开连接的客户端
            for client_id in disconnected_clients:
                if task_id in self.active_connections:
                    if client_id in self.active_connections[task_id]:
                        del self.active_connections[task_id][client_id]
    
    async def send_to_client(
        self, 
        task_id: str, 
        client_id: str, 
        message: Dict[str, any]
    ):
        """
        向特定客户端发送消息
        
        Args:
            task_id: 任务ID
            client_id: 客户端ID
            message: 消息内容
        """
        async with self.lock:
            if (task_id not in self.active_connections or 
                client_id not in self.active_connections[task_id]):
                return
            
            try:
                await self.active_connections[task_id][client_id].websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息到客户端 {client_id} 失败: {str(e)}")
                await self.unregister_client(task_id, client_id)
    
    def get_task_clients(self, task_id: str) -> List[str]:
        """
        获取任务的客户端列表
        
        Args:
            task_id: 任务ID
            
        Returns:
            客户端ID列表
        """
        if task_id in self.active_connections:
            return list(self.active_connections[task_id].keys())
        return []
    
    def get_connected_tasks(self) -> List[str]:
        """
        获取有活跃连接的任务列表
        
        Returns:
            任务ID列表
        """
        return list(self.active_connections.keys())
    
    def get_total_connections(self) -> int:
        """
        获取总连接数
        
        Returns:
            总连接数
        """
        total = 0
        for clients in self.active_connections.values():
            total += len(clients)
        return total


# 全局 WebSocket 管理器实例
_websocket_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """
    获取 WebSocket 管理器实例（单例）
    
    Returns:
        WebSocketManager 实例
    """
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager