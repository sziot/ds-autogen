# app/config.py
"""
极简配置管理 - 不使用 BaseSettings
"""

import os
from typing import List


class Config:
    """纯 Python 类配置管理"""
    
    # 项目信息
    PROJECT_NAME = "DeepSeek Code Review"
    VERSION = "1.0.0"
    DESCRIPTION = "基于 AI 的智能代码审查系统"
    
    # 服务器配置
    HOST = "0.0.0.0"
    PORT = 8000
    
    # 环境配置
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS 配置
    BACKEND_CORS_ORIGINS = ["*"]  # 开发环境允许所有来源
    
    # 文件存储
    UPLOAD_DIR = "uploads"
    FIXED_DIR = "fixed"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rb"]
    
    # API 配置
    API_V1_STR = "/api/v1"
    
    # AI 配置（可选）
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    # 日志配置
    LOG_LEVEL = "INFO"
    
    @classmethod
    def print_config(cls):
        """打印当前配置"""
        print("=" * 50)
        print(f"{cls.PROJECT_NAME} - v{cls.VERSION}")
        print("=" * 50)
        
        config_items = {
            "服务器": f"{cls.HOST}:{cls.PORT}",
            "环境": cls.ENVIRONMENT,
            "调试模式": cls.DEBUG,
            "文件上传目录": cls.UPLOAD_DIR,
            "API前缀": cls.API_V1_STR,
            "DeepSeek API": "已配置" if cls.DEEPSEEK_API_KEY else "未配置"
        }
        
        for key, value in config_items.items():
            print(f"{key:15} : {value}")
        
        print("=" * 50)


# 全局配置实例
config = Config()