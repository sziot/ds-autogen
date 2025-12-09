#!/bin/bash

# 后端启动脚本

echo "启动AI代码审查系统后端服务..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "警告: 未找到 .env 文件，请创建并配置 DEEPSEEK_API_KEY"
    echo "可以复制 .env.example 作为模板"
fi

# 启动服务
echo "启动FastAPI服务..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

