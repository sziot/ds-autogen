"""
数据库模型
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, 
    DateTime, JSON, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Task(Base):
    """任务表"""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # 状态相关
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    message = Column(Text, nullable=True)
    
    # 审查结果
    original_content = Column(Text, nullable=True)
    fixed_content = Column(Text, nullable=True)
    architect_report = Column(Text, nullable=True)
    reviewer_report = Column(Text, nullable=True)
    optimizer_summary = Column(Text, nullable=True)
    quality_score = Column(Float, nullable=True)
    saved_file_path = Column(String(500), nullable=True)
    diff_stats = Column(JSON, nullable=True)
    
    # 选项和元数据
    options = Column(JSON, nullable=True, default=dict)
    metadata = Column(JSON, nullable=True, default=dict)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # 关系
    agent_statuses = relationship("AgentStatus", back_populates="task", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_created_at", "created_at"),
        Index("idx_tasks_completed_at", "completed_at"),
        Index("idx_tasks_file_name", "file_name"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "quality_score": self.quality_score,
            "saved_file_path": self.saved_file_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class AgentStatus(Base):
    """智能体状态表"""
    __tablename__ = "agent_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String(50), nullable=False)  # Architect, Reviewer, Optimizer, User_Proxy
    
    # 状态信息
    status = Column(String(50), nullable=False)  # idle, processing, completed, error
    message = Column(Text, nullable=True)
    progress = Column(Float, default=0.0)
    result = Column(JSON, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    task = relationship("Task", back_populates="agent_statuses")
    
    # 索引和约束
    __table_args__ = (
        Index("idx_agent_status_task_id", "task_id"),
        Index("idx_agent_status_agent_name", "agent_name"),
        Index("idx_agent_status_created_at", "created_at"),
        UniqueConstraint("task_id", "agent_name", name="uq_task_agent"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "status": self.status,
            "message": self.message,
            "progress": self.progress,
            "result": self.result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CodeFile(Base):
    """代码文件表"""
    __tablename__ = "code_files"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    
    # 文件信息
    file_type = Column(String(10), nullable=False)  # original, fixed
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)  # MD5 hash
    file_size = Column(Integer, nullable=False)
    line_count = Column(Integer, nullable=True)
    
    # 代码信息
    language = Column(String(50), nullable=True)
    complexity = Column(Float, nullable=True)
    vulnerability_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    task = relationship("Task", foreign_keys=[task_id])
    
    # 索引
    __table_args__ = (
        Index("idx_code_files_task_id", "task_id"),
        Index("idx_code_files_file_type", "file_type"),
        Index("idx_code_files_file_hash", "file_hash"),
        Index("idx_code_files_created_at", "created_at"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "file_type": self.file_type,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "line_count": self.line_count,
            "language": self.language,
            "complexity": self.complexity,
            "vulnerability_score": self.vulnerability_score,
            "quality_score": self.quality_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ReviewHistory(Base):
    """审查历史表"""
    __tablename__ = "review_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), nullable=True)  # 未来支持多用户
    
    # 审查统计
    review_duration = Column(Float, nullable=True)  # 秒
    total_issues = Column(Integer, nullable=True)
    critical_issues = Column(Integer, nullable=True)
    security_issues = Column(Integer, nullable=True)
    performance_issues = Column(Integer, nullable=True)
    
    # 评分
    overall_score = Column(Float, nullable=True)
    architecture_score = Column(Float, nullable=True)
    security_score = Column(Float, nullable=True)
    performance_score = Column(Float, nullable=True)
    readability_score = Column(Float, nullable=True)
    
    # 时间戳
    reviewed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    task = relationship("Task", foreign_keys=[task_id])
    
    # 索引
    __table_args__ = (
        Index("idx_review_history_task_id", "task_id"),
        Index("idx_review_history_reviewed_at", "reviewed_at"),
        Index("idx_review_history_overall_score", "overall_score"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "review_duration": self.review_duration,
            "total_issues": self.total_issues,
            "critical_issues": self.critical_issues,
            "security_issues": self.security_issues,
            "performance_issues": self.performance_issues,
            "overall_score": self.overall_score,
            "architecture_score": self.architecture_score,
            "security_score": self.security_score,
            "performance_score": self.performance_score,
            "readability_score": self.readability_score,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }