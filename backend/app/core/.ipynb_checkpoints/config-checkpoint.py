# app/core/config.py
"""
简化的配置管理 - 无数据库版本
"""

import secrets
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, Field, validator


class Settings(BaseSettings):
    """应用设置 - 无数据库版本"""
    
    # 项目信息
    PROJECT_NAME: str = "DeepSeek Code Review System"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "基于 AutoGen 的智能代码审查系统（内存版）"
    
    # 环境配置
    ENVIRONMENT: str = "development"
    DEBUG: bool = True  # 开发模式默认开启调试
    
    # API 配置
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS 配置
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
        "*"  # 开发环境允许所有来源
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """组装 CORS 源"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # LLM 配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-coder"
    
    # 文件存储
    UPLOAD_DIR: str = "uploads"
    FIXED_DIR: str = "fixed"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".rb"
    ]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # 内存存储配置
    MEMORY_STORE_MAX_TASKS: int = 100  # 内存中最大任务数
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局设置实例
settings = Settings()