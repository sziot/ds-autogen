"""
FastAPI 后端主服务
提供代码审查API和WebSocket支持
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from loguru import logger
from dotenv import load_dotenv

from autogen_reviewer import CodeReviewSystem

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="AI代码审查系统",
    description="基于DeepSeek和AutoGen的智能代码审查系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
review_system: Optional[CodeReviewSystem] = None


class CodeReviewRequest(BaseModel):
    """代码审查请求模型"""
    code: str = Field(..., description="代码内容")
    file_name: str = Field(..., description="文件名")
    file_path: Optional[str] = Field(None, description="文件路径")


class CodeReviewResponse(BaseModel):
    """代码审查响应模型"""
    success: bool
    architect_report: Optional[str] = None
    reviewer_report: Optional[str] = None
    optimizer_report: Optional[str] = None
    fixed_code: Optional[str] = None
    save_result: Optional[Dict[str, Any]] = None
    file_name: Optional[str] = None
    message: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global review_system
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    
    if not api_key:
        logger.warning("未找到 DEEPSEEK_API_KEY，请设置环境变量")
        return
    
    try:
        review_system = CodeReviewSystem(api_key, base_url)
        logger.info("代码审查系统初始化成功")
    except Exception as e:
        logger.error(f"初始化代码审查系统失败: {str(e)}")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI代码审查系统API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "review_system_ready": review_system is not None
    }


@app.post("/api/review", response_model=CodeReviewResponse)
@app.post("/review", response_model=CodeReviewResponse)  # 兼容未加 /api 前缀的调用
async def review_code(request: CodeReviewRequest):
    """
    代码审查接口
    
    接收代码内容，返回审查结果和修复后的代码
    """
    if not review_system:
        raise HTTPException(
            status_code=503,
            detail="代码审查系统未初始化，请检查配置"
        )
    
    try:
        logger.info(f"收到代码审查请求: {request.file_name}")
        
        # 执行代码审查
        result = review_system.review_code(
            code_content=request.code,
            file_name=request.file_name,
            file_path=request.file_path or request.file_name
        )
        
        return CodeReviewResponse(
            success=True,
            architect_report=result.get("architect_report"),
            reviewer_report=result.get("reviewer_report"),
            optimizer_report=result.get("optimizer_report"),
            fixed_code=result.get("fixed_code"),
            save_result=result.get("save_result"),
            file_name=result.get("file_name"),
            message="代码审查完成"
        )
        
    except Exception as e:
        logger.error(f"代码审查失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"代码审查失败: {str(e)}"
        )


def _build_upload_router_path(path: str):
    """
    Helper to register both /api/review/upload and /review/upload
    to avoid 404 when前端未带 /api 前缀
    """
    return path


@app.post("/api/review/upload")
@app.post("/review/upload")  # 兼容未加 /api 前缀的调用
async def review_uploaded_file(file: UploadFile = File(...)):
    """
    上传文件进行代码审查
    """
    if not review_system:
        raise HTTPException(
            status_code=503,
            detail="代码审查系统未初始化"
        )
    
    try:
        # 读取文件内容
        content = await file.read()
        code_content = content.decode('utf-8')
        logger.info(f"收到上传文件: {file.filename}, 大小: {len(code_content)} 字节")
        
        # 执行审查
        result = review_system.review_code(
            code_content=code_content,
            file_name=file.filename,
            file_path=file.filename
        )
        
        return CodeReviewResponse(
            success=True,
            architect_report=result.get("architect_report"),
            reviewer_report=result.get("reviewer_report"),
            optimizer_report=result.get("optimizer_report"),
            fixed_code=result.get("fixed_code"),
            save_result=result.get("save_result"),
            file_name=result.get("file_name"),
            message="文件审查完成"
        )
        
    except Exception as e:
        logger.error(f"文件审查失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"文件审查失败: {str(e)}"
        )


@app.get("/api/download/{filename}")
async def download_fixed_file(filename: str):
    """
    下载修复后的文件
    """
    fixed_file_path = Path("fixed") / filename
    
    if not fixed_file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"文件 {filename} 不存在"
        )
    
    return FileResponse(
        path=str(fixed_file_path),
        filename=filename,
        media_type="text/plain"
    )


@app.get("/api/files")
async def list_fixed_files():
    """
    列出所有修复后的文件
    """
    fixed_dir = Path("fixed")
    
    if not fixed_dir.exists():
        return {"files": []}
    
    files = [
        {
            "name": f.name,
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime
        }
        for f in fixed_dir.iterdir()
        if f.is_file()
    ]
    
    return {"files": files}


@app.websocket("/ws/review")
async def websocket_review(websocket: WebSocket):
    """
    WebSocket接口，支持实时代码审查
    """
    await websocket.accept()
    
    if not review_system:
        await websocket.send_json({
            "error": "代码审查系统未初始化"
        })
        await websocket.close()
        return
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            
            if data.get("type") == "review":
                code_content = data.get("code", "")
                file_name = data.get("file_name", "unknown.py")
                file_path = data.get("file_path", file_name)
                
                # 发送开始消息
                await websocket.send_json({
                    "type": "status",
                    "message": "开始审查代码..."
                })
                
                # 执行审查（这里可以分步骤发送进度）
                result = review_system.review_code(
                    code_content=code_content,
                    file_name=file_name,
                    file_path=file_path
                )
                
                # 发送结果
                await websocket.send_json({
                    "type": "result",
                    "success": True,
                    "data": result
                })
            
            elif data.get("type") == "close":
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket连接断开")
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

