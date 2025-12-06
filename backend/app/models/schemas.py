"""
Pydantic 数据模式定义
用于 API 请求/响应验证
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """任务基础模式"""
    file_name: str = Field(..., description="文件名")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="任务选项")


class TaskCreate(TaskBase):
    """创建任务模式"""
    pass


class TaskUpdate(BaseModel):
    """更新任务模式"""
    status: Optional[str] = Field(None, description="任务状态")
    progress: Optional[float] = Field(None, ge=0, le=100, description="进度百分比")
    message: Optional[str] = Field(None, description="状态消息")


class AgentStatusSchema(BaseModel):
    """智能体状态模式"""
    agent_name: str = Field(..., description="智能体名称")
    status: str = Field(..., description="状态")
    message: Optional[str] = Field(None, description="状态消息")
    progress: float = Field(0, ge=0, le=100, description="进度百分比")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CodeReviewResult(BaseModel):
    """代码审查结果模式"""
    id: str = Field(..., description="任务ID")
    file_name: str = Field(..., description="文件名")
    original_content: str = Field(..., description="原始代码")
    fixed_content: str = Field(..., description="修复后的代码")
    architect_report: str = Field(..., description="架构分析报告")
    reviewer_report: str = Field(..., description="代码审查报告")
    optimizer_summary: str = Field(..., description="优化总结")
    quality_score: float = Field(..., ge=0, le=10, description="质量评分")
    saved_file_path: str = Field(..., description="保存的文件路径")
    created_at: datetime = Field(default_factory=datetime.now)
    diff_stats: Dict[str, Any] = Field(default_factory=dict, description="差异统计")
    
    class Config:
        from_attributes = True


class TaskResponse(TaskBase):
    """任务响应模式"""
    id: str
    status: str
    progress: float
    quality_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    agent_statuses: List[AgentStatusSchema] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class HealthCheck(BaseModel):
    """健康检查响应"""
    status: str = "healthy"
    service: str = "DeepSeek Code Review"
    version: str = "1.0.0"
    database: Optional[Dict[str, Any]] = None
    redis: Optional[Dict[str, Any]] = None
    environment: str = "development"
    timestamp: datetime = Field(default_factory=datetime.now)