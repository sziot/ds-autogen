"""
WebSocket 路由
"""

import asyncio
import json
import uuid
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from loguru import logger

from app.api.websocket_manager import get_websocket_manager

router = APIRouter()


@router.websocket("/review/{task_id}")
async def websocket_review(
    websocket: WebSocket,
    task_id: str,
):
    """
    WebSocket 连接，用于实时推送审查进度
    
    Args:
        websocket: WebSocket 连接
        task_id: 任务ID
    """
    ws_manager = get_websocket_manager()
    client_id = str(uuid.uuid4())
    
    try:
        # 接受 WebSocket 连接
        await websocket.accept()
        
        # 注册客户端
        await ws_manager.register_client(task_id, client_id, websocket)
        
        logger.info(f"WebSocket 客户端 {client_id} 已连接，任务: {task_id}")
        
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "data": {
                "client_id": client_id,
                "task_id": task_id,
                "message": "WebSocket 连接成功"
            }
        })
        
        # 保持连接，接收消息
        while True:
            try:
                # 接收消息（支持 ping/pong）
                data = await websocket.receive_text()
                
                # 处理心跳消息
                if data == "ping":
                    await websocket.send_text("pong")
                    continue
                
                # 解析消息
                message = json.loads(data)
                await handle_websocket_message(task_id, client_id, message)
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "无效的JSON格式"}
                })
            except Exception as e:
                logger.error(f"处理WebSocket消息失败: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"处理消息失败: {str(e)}"}
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket 客户端 {client_id} 已断开连接")
    except Exception as e:
        logger.error(f"WebSocket 连接错误: {str(e)}", exc_info=True)
    finally:
        # 注销客户端
        await ws_manager.unregister_client(task_id, client_id)


async def handle_websocket_message(
    task_id: str,
    client_id: str,
    message: Dict[str, Any]
):
    """
    处理 WebSocket 消息
    
    Args:
        task_id: 任务ID
        client_id: 客户端ID
        message: 消息内容
    """
    message_type = message.get("type")
    
    if message_type == "subscribe":
        # 客户端订阅特定事件
        events = message.get("events", [])
        logger.info(f"客户端 {client_id} 订阅事件: {events}")
        
    elif message_type == "unsubscribe":
        # 客户端取消订阅
        events = message.get("events", [])
        logger.info(f"客户端 {client_id} 取消订阅事件: {events}")
        
    elif message_type == "control":
        # 控制消息（暂停、继续等）
        action = message.get("action")
        logger.info(f"客户端 {client_id} 发送控制指令: {action}")
        
    else:
        logger.warning(f"未知的WebSocket消息类型: {message_type}")