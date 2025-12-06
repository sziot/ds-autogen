# 替代方案 - 使用 BaseModel
from typing import List, Optional, Union
from pydantic import BaseModel, Field, AnyHttpUrl, validator
import os


class Settings(BaseModel):
    """使用 BaseModel 的配置类"""
    
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
    
    # ... 其他配置字段 ...
    
    @classmethod
    def from_env(cls):
        """从环境变量加载配置"""
        # 手动加载 .env 文件
        from dotenv import load_dotenv
        load_dotenv()
        
        return cls(
            PROJECT_NAME=os.getenv("PROJECT_NAME", "DeepSeek Code Review System"),
            VERSION=os.getenv("VERSION", "1.0.0"),
            ENVIRONMENT=os.getenv("ENVIRONMENT", "development"),
            DEBUG=os.getenv("DEBUG", "False").lower() == "true",
            # ... 加载其他环境变量
        )


# 创建配置实例
settings = Settings.from_env()