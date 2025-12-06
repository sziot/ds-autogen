"""
数据库连接和会话管理
"""

import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

# 全局引擎和会话工厂
_async_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker] = None


def get_async_engine() -> AsyncEngine:
    """
    获取异步数据库引擎（单例模式）
    
    Returns:
        AsyncEngine: 异步数据库引擎
    """
    global _async_engine
    
    if _async_engine is None:
        try:
            # 根据环境配置连接池
            if settings.ENVIRONMENT == "test":
                # 测试环境使用无连接池
                poolclass = NullPool
            else:
                # 生产/开发环境使用连接池
                poolclass = QueuePool
            
            # 创建异步引擎
            _async_engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DEBUG,  # 调试模式下显示SQL
                echo_pool=settings.DEBUG,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_pre_ping=True,  # 连接前检查
                pool_recycle=3600,  # 1小时回收连接
                pool_timeout=30,  # 连接超时30秒
                poolclass=poolclass,
                connect_args={
                    "server_settings": {
                        "application_name": settings.PROJECT_NAME,
                        "timezone": "UTC"
                    }
                }
            )
            
            logger.info(f"✅ 数据库引擎初始化成功: {settings.DATABASE_URL[:30]}...")
            
        except Exception as e:
            logger.error(f"❌ 数据库引擎初始化失败: {str(e)}")
            raise
    
    return _async_engine


def get_async_session_factory() -> async_sessionmaker:
    """
    获取异步会话工厂（单例模式）
    
    Returns:
        async_sessionmaker: 异步会话工厂
    """
    global _async_session_factory
    
    if _async_session_factory is None:
        engine = get_async_engine()
        
        _async_session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,  # 提交后不使实例过期
            autoflush=True,  # 自动刷新
            autocommit=False  # 手动提交
        )
        
        logger.info("✅ 数据库会话工厂初始化成功")
    
    return _async_session_factory


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的上下文管理器
    
    Yields:
        AsyncSession: 异步数据库会话
    
    Raises:
        SQLAlchemyError: 数据库操作错误
    """
    session_factory = get_async_session_factory()
    session: AsyncSession = session_factory()
    
    try:
        yield session
        await session.commit()
        logger.debug("✅ 数据库会话提交成功")
        
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"❌ 数据库操作失败，已回滚: {str(e)}")
        raise
        
    finally:
        await session.close()
        logger.debug("✅ 数据库会话已关闭")


async def init_database() -> None:
    """
    初始化数据库连接
    
    Raises:
        Exception: 初始化失败
    """
    try:
        # 获取引擎以测试连接
        engine = get_async_engine()
        
        # 测试连接
        async with engine.connect() as conn:
            # 执行简单的查询测试
            result = await conn.execute("SELECT 1")
            test_result = result.scalar()
            
            if test_result == 1:
                logger.info("✅ 数据库连接测试成功")
            else:
                raise Exception("数据库连接测试失败")
                
        logger.info("✅ 数据库初始化完成")
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {str(e)}")
        raise


async def close_database() -> None:
    """
    关闭数据库连接
    """
    global _async_engine, _async_session_factory
    
    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None
        logger.info("✅ 数据库引擎已关闭")
    
    _async_session_factory = None


# 便捷的依赖注入函数
async def get_db():
    """
    用于 FastAPI 依赖注入的数据库会话获取器
    """
    async with get_db_session() as session:
        yield session


# 同步兼容性函数（如果需要）
def get_sync_session_factory():
    """
    获取同步会话工厂（用于 Alembic 迁移等）
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 将异步URL转换为同步URL
    sync_url = settings.DATABASE_URL.replace("asyncpg", "psycopg2")
    
    engine = create_engine(
        sync_url,
        echo=settings.DEBUG,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW
    )
    
    return sessionmaker(bind=engine, expire_on_commit=False)


# 数据库健康检查
async def check_database_health() -> dict:
    """
    检查数据库健康状态
    
    Returns:
        dict: 健康状态信息
    """
    try:
        engine = get_async_engine()
        
        async with engine.connect() as conn:
            # 检查连接
            start_time = asyncio.get_event_loop().time()
            result = await conn.execute("SELECT 1")
            latency = asyncio.get_event_loop().time() - start_time
            
            # 获取数据库信息
            db_info = await conn.execute(
                "SELECT version(), current_database(), current_user"
            )
            version, db_name, db_user = db_info.first()
            
            # 获取连接池状态
            pool = engine.pool
            pool_status = {
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "size": pool.size(),
                "checked_in": pool.checkedin()
            }
            
            return {
                "status": "healthy",
                "latency_ms": round(latency * 1000, 2),
                "database": db_name,
                "user": db_user,
                "version": version,
                "pool": pool_status,
                "message": "数据库连接正常"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "数据库连接失败"
        }


# 导入 asyncio（在文件顶部已导入，这里确保可用）
import asyncio