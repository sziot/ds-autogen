"""
SQLAlchemy 数据模型定义
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, 
    DateTime, JSON, ForeignKey, Index, UniqueConstraint,
    text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

# 声明基类
Base = declarative_base()


class Task(Base):
    """任务表"""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # 状态相关
    status = Column(String(50), nullable=False, default="pending")
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
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
                       onupdate=text("CURRENT_TIMESTAMP"))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # 关系
    agent_statuses = relationship("AgentStatus", back_populates="task", 
                                 cascade="all, delete-orphan", lazy="selectin")
    code_files = relationship("CodeFile", back_populates="task", 
                             cascade="all, delete-orphan", lazy="selectin")
    
    # 索引
    __table_args__ = (
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_created_at", "created_at"),
        Index("idx_tasks_completed_at", "completed_at"),
        Index("idx_tasks_file_name", "file_name"),
        Index("idx_tasks_quality_score", "quality_score"),
    )
    
    def __repr__(self):
        return f"<Task(id={self.id}, file={self.file_name}, status={self.status})>"


class AgentStatus(Base):
    """智能体状态表"""
    __tablename__ = "agent_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String(50), nullable=False)
    
    # 状态信息
    status = Column(String(50), nullable=False, default="idle")
    message = Column(Text, nullable=True)
    progress = Column(Float, default=0.0)
    result = Column(JSON, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
                       onupdate=text("CURRENT_TIMESTAMP"))
    
    # 关系
    task = relationship("Task", back_populates="agent_statuses")
    
    # 索引和约束
    __table_args__ = (
        Index("idx_agent_status_task_id", "task_id"),
        Index("idx_agent_status_agent_name", "agent_name"),
        Index("idx_agent_status_created_at", "created_at"),
        UniqueConstraint("task_id", "agent_name", name="uq_task_agent"),
    )
    
    def __repr__(self):
        return f"<AgentStatus(task={self.task_id}, agent={self.agent_name}, status={self.status})>"


class CodeFile(Base):
    """代码文件表"""
    __tablename__ = "code_files"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    
    # 文件信息
    file_type = Column(String(10), nullable=False)  # original, fixed
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    file_size = Column(Integer, nullable=False)
    line_count = Column(Integer, nullable=True)
    
    # 代码信息
    language = Column(String(50), nullable=True)
    complexity = Column(Float, nullable=True)
    vulnerability_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
                       onupdate=text("CURRENT_TIMESTAMP"))
    
    # 关系
    task = relationship("Task", back_populates="code_files")
    
    # 索引
    __table_args__ = (
        Index("idx_code_files_task_id", "task_id"),
        Index("idx_code_files_file_type", "file_type"),
        Index("idx_code_files_file_hash", "file_hash"),
        Index("idx_code_files_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<CodeFile(name={self.file_name}, type={self.file_type})>"


class ReviewHistory(Base):
    """审查历史表"""
    __tablename__ = "review_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), nullable=True)
    
    # 审查统计
    review_duration = Column(Float, nullable=True)
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
    reviewed_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    
    # 关系
    task = relationship("Task", foreign_keys=[task_id])
    
    # 索引
    __table_args__ = (
        Index("idx_review_history_task_id", "task_id"),
        Index("idx_review_history_reviewed_at", "reviewed_at"),
        Index("idx_review_history_overall_score", "overall_score"),
    )
    
    def __repr__(self):
        return f"<ReviewHistory(task={self.task_id}, score={self.overall_score})>"