"""
日志配置
"""

import sys
from pathlib import Path

from loguru import logger


def setup_logging():
    """
    配置 Loguru 日志
    """
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出（开发环境）
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level="INFO",
        colorize=True,
    )
    
    # 文件输出（所有日志）
    log_file = Path("logs/app.log")
    log_file.parent.mkdir(exist_ok=True)
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )
    
    # 错误日志单独文件
    error_log_file = Path("logs/error.log")
    logger.add(
        error_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )
    
    # 拦截标准日志
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # 获取对应的 Loguru 级别
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            # 找到调用者
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    # 配置标准库日志
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    return logger