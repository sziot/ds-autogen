#!/bin/bash

echo "🚀 启动 DeepSeek 代码审查系统开发环境..."

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version)
echo "Python 版本: $PYTHON_VERSION"

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 创建环境变量文件
if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
    echo "请编辑 .env 文件配置环境变量"
fi

# 创建数据库目录
mkdir -p uploads fixed logs

# 启动数据库服务
echo "启动 PostgreSQL 和 Redis..."
docker-compose up -d postgres redis

# 等待数据库就绪
echo "等待数据库就绪..."
sleep 10

# 运行数据库迁移
echo "运行数据库迁移..."
alembic upgrade head

# 启动后端服务
echo "启动后端服务..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level info