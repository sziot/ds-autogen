# main.py
"""
DeepSeek 代码审查系统 - 最小化版本
无需数据库，无需复杂配置
"""

import asyncio
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import config


# 创建应用
app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.VERSION,
    description=config.DESCRIPTION,
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 内存存储 ==========
class MemoryStorage:
    """最简单的内存存储"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.agent_status: Dict[str, List[Dict]] = {}
    
    def create_task(self, file_name: str, file_path: str, file_size: int):
        """创建任务"""
        task_id = str(uuid.uuid4())
        
        task = {
            "id": task_id,
            "file_name": file_name,
            "file_path": file_path,
            "file_size": file_size,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        self.tasks[task_id] = task
        
        # 初始化智能体状态
        self.agent_status[task_id] = [
            {"agent": "Architect", "status": "idle", "progress": 0, "message": "等待中"},
            {"agent": "Reviewer", "status": "idle", "progress": 0, "message": "等待中"},
            {"agent": "Optimizer", "status": "idle", "progress": 0, "message": "等待中"},
            {"agent": "User_Proxy", "status": "idle", "progress": 0, "message": "等待中"},
        ]
        
        print(f"✅ 创建任务: {task_id}")
        return task_id, task
    
    def get_task(self, task_id: str):
        """获取任务"""
        return self.tasks.get(task_id)
    
    def update_task(self, task_id: str, updates: Dict):
        """更新任务"""
        if task_id in self.tasks:
            self.tasks[task_id].update(updates)
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            return True
        return False
    
    def update_agent(self, task_id: str, agent_name: str, updates: Dict):
        """更新智能体状态"""
        if task_id in self.agent_status:
            for agent in self.agent_status[task_id]:
                if agent["agent"] == agent_name:
                    agent.update(updates)
                    return True
        return False
    
    def get_all_tasks(self):
        """获取所有任务"""
        return list(self.tasks.values())


# 全局存储实例
storage = MemoryStorage()


# ========== API 路由 ==========
@app.get("/")
async def root():
    """根目录"""
    return {
        "service": config.PROJECT_NAME,
        "version": config.VERSION,
        "status": "running",
        "docs": "/docs",
        "upload": "POST /upload",
        "start": "POST /start/{task_id}",
        "status": "GET /status/{task_id}",
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    try:
        # 检查文件类型
        filename = file.filename or "unknown"
        ext = Path(filename).suffix.lower()
        
        if ext not in config.ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"不支持的文件类型: {ext}")
        
        # 创建上传目录
        upload_dir = Path(config.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        # 保存文件
        file_path = upload_dir / f"{uuid.uuid4()}_{filename}"
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 创建任务记录
        task_id, task = storage.create_task(
            file_name=filename,
            file_path=str(file_path),
            file_size=len(content)
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "file_name": filename,
            "file_size": len(content),
            "message": "文件上传成功"
        }
        
    except Exception as e:
        raise HTTPException(500, f"上传失败: {str(e)}")


@app.post("/start/{task_id}")
async def start_review(task_id: str, background_tasks: BackgroundTasks):
    """开始代码审查"""
    task = storage.get_task(task_id)
    if not task:
        raise HTTPException(404, f"任务不存在: {task_id}")
    
    # 更新任务状态
    storage.update_task(task_id, {
        "status": "processing",
        "message": "开始代码审查"
    })
    
    # 在后台运行模拟审查
    background_tasks.add_task(simulate_review, task_id)
    
    return {
        "success": True,
        "task_id": task_id,
        "status": "processing",
        "message": "审查已开始"
    }


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """获取任务状态"""
    task = storage.get_task(task_id)
    if not task:
        raise HTTPException(404, f"任务不存在: {task_id}")
    
    agents = storage.agent_status.get(task_id, [])
    
    return {
        "success": True,
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "message": task.get("message", ""),
        "agents": agents,
        "created_at": task["created_at"],
        "updated_at": task["updated_at"]
    }


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """获取审查结果"""
    task = storage.get_task(task_id)
    if not task:
        raise HTTPException(404, f"任务不存在: {task_id}")
    
    if task["status"] != "completed":
        raise HTTPException(400, f"任务尚未完成，当前状态: {task['status']}")
    
    # 模拟结果
    return {
        "success": True,
        "task_id": task_id,
        "file_name": task["file_name"],
        "quality_score": 8.5,
        "summary": "代码审查完成",
        "original_code": "def hello():\n    print('Hello World')",
        "fixed_code": "def hello():\n    '''打印欢迎信息'''\n    print('Hello World')",
        "suggestions": [
            "添加了函数文档字符串",
            "代码结构更清晰"
        ]
    }


@app.get("/tasks")
async def list_tasks():
    """列出所有任务"""
    tasks = storage.get_all_tasks()
    return {
        "success": True,
        "count": len(tasks),
        "tasks": tasks
    }


# ========== 模拟审查逻辑 ==========
async def simulate_review(task_id: str):
    """模拟代码审查流程"""
    print(f"🤖 开始模拟审查: {task_id}")
    
    agents = ["Architect", "Reviewer", "Optimizer", "User_Proxy"]
    
    for i, agent in enumerate(agents):
        # 更新智能体状态
        storage.update_agent(task_id, agent, {
            "status": "processing",
            "progress": 0,
            "message": f"{agent} 正在工作..."
        })
        
        await asyncio.sleep(1)  # 模拟处理时间
        
        # 更新进度
        storage.update_agent(task_id, agent, {
            "status": "processing",
            "progress": 50,
            "message": f"{agent} 分析中..."
        })
        
        await asyncio.sleep(1)
        
        # 完成
        storage.update_agent(task_id, agent, {
            "status": "completed",
            "progress": 100,
            "message": f"{agent} 已完成"
        })
        
        # 更新任务总进度
        progress = (i + 1) * 25
        storage.update_task(task_id, {
            "progress": progress,
            "message": f"{agent} 已完成 ({progress}%)"
        })
    
    # 最终完成
    storage.update_task(task_id, {
        "status": "completed",
        "progress": 100,
        "message": "代码审查完成"
    })
    
    print(f"✅ 模拟审查完成: {task_id}")


# ========== 启动应用 ==========
if __name__ == "__main__":
    # 打印配置
    config.print_config()
    
    # 创建必要的目录
    Path(config.UPLOAD_DIR).mkdir(exist_ok=True)
    Path(config.FIXED_DIR).mkdir(exist_ok=True)
    
    # 启动服务器
    print(f"🚀 启动服务: http://{config.HOST}:{config.PORT}")
    print(f"📚 API 文档: http://{config.HOST}:{config.PORT}/docs")
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )