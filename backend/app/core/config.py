# app/core/config.py
"""
简化的配置管理 - 数据库版本
"""

import secrets
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用设置 - 数据库版本
    """

    # model_config 替代 v1 的 class Config
    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env", case_sensitive=True)

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
    # 注：类型允许原始字符串以便从 .env 中安全读取，后续由 field_validator 处理
    BACKEND_CORS_ORIGINS: Union[List[Union[str, AnyHttpUrl]], str] = [
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
        "*"  # 开发环境允许所有来源
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v):
        """
        兼容从 .env 中读取的多种格式：
        - 如果是字符串且不以 [ 开头，按逗号分割： "a,b,c"
        - 如果是 JSON 数组样式（以 [ 开头），交给 pydantic 解析（这里直接返回原始，让后续解析处理）
        - 如果已经是 list/tuple，直接返回 list
        """
        # 如果原始是 None 或空，直接返回默认（由 pydantic 处理默认值）
        if v is None:
            return v

        # 当 .env 中为逗号分隔字符串时（最常见）
        if isinstance(v, str) and not v.strip().startswith("["):
            # 空字符串 -> 空列表
            if v.strip() == "":
                return []
            return [i.strip() for i in v.split(",")]

        # 如果已经是序列（list/tuple），确保返回 list
        if isinstance(v, (list, tuple)):
            return list(v)

        # 其余情况（例如文本 JSON 数组或其它），直接返回原始值，交给 pydantic 后续解析或抛出更明确错误
        return v

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


# 全局设置实例
settings = Settings()