"""
WebSocket 路由
"""

import asyncio
import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.websocket_manager import get_websocket_manager

router = APIRouter()


@router.websocket("/ws/review/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket 端点"""
    ws_manager = get_websocket_manager()
    client_id = str(uuid.uuid4())
    
    try:
        # 连接客户端
        await ws_manager.connect(websocket, task_id, client_id)
        
        # 保持连接活跃
        while True:
            try:
                # 接收消息（支持心跳）
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                
                if data == "ping":
                    await websocket.send_text("pong")
                    continue
                
                # 处理其他消息
                try:
                    message = json.loads(data)
                    await handle_websocket_message(task_id, client_id, message)
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "无效的JSON格式"}
                    })
                    
            except asyncio.TimeoutError:
                # 发送心跳
                await websocket.send_json({
                    "type": "ping",
                    "data": {"timestamp": asyncio.get_event_loop().time()}
                })
                
    except WebSocketDisconnect:
        print(f"WebSocket 断开: {client_id}")
    except Exception as e:
        print(f"WebSocket 错误: {e}")
    finally:
        # 清理连接
        await ws_manager.disconnect(task_id, client_id)


async def handle_websocket_message(task_id: str, client_id: str, message: dict):
    """处理 WebSocket 消息"""
    message_type = message.get("type")
    
    if message_type == "subscribe":
        # 客户端订阅更新
        print(f"客户端 {client_id} 订阅任务 {task_id}")
        
    elif message_type == "control":
        # 控制消息（暂停、继续等）
        action = message.get("action")
        print(f"客户端 {client_id} 控制: {action}")
        
    else:
        print(f"未知消息类型: {message_type}")