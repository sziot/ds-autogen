"""
应用配置管理
"""

import secrets
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, validator, Field


class Settings(BaseSettings):
    """应用设置"""
    
    # 项目信息
    PROJECT_NAME: str = "DeepSeek Code Review System"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "基于 AutoGen 的智能代码审查系统"
    
    # 环境配置
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # API 配置
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 安全配置
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    ALGORITHM: str = "HS256"
    
    # CORS 配置
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """组装 CORS 源"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/code_review"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    
    # Celery 配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # LLM 配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-coder"
    
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # AI 配置
    AI_TEMPERATURE: float = 0.1
    AI_MAX_TOKENS: int = 4000
    AI_TIMEOUT: int = 120
    
    # 文件存储
    UPLOAD_DIR: str = "uploads"
    FIXED_DIR: str = "fixed"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".rb"
    ]
    
    # 监控配置
    MONITORING_ENABLED: bool = False
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    ACCESS_LOG: bool = True
    
    # 限流配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # WebSocket 配置
    WEBSOCKET_PING_INTERVAL: int = 20
    WEBSOCKET_PING_TIMEOUT: int = 20
    WEBSOCKET_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局设置实例
settings = Settings()