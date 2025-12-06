#!/bin/bash

# 生产环境部署脚本

set -e  # 出错时退出

echo "🚀 开始部署 DeepSeek 代码审查系统..."

# 检查环境变量
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "错误: 需要设置 DEEPSEEK_API_KEY 环境变量"
    exit 1
fi

# 构建 Docker 镜像
echo "构建 Docker 镜像..."
docker-compose build

# 停止旧容器
echo "停止旧容器..."
docker-compose down

# 启动新容器
echo "启动新容器..."
docker-compose up -d

# 运行数据库迁移
echo "运行数据库迁移..."
docker-compose exec backend alembic upgrade head

# 检查服务状态
echo "检查服务状态..."
sleep 10

# 检查后端健康
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HEALTH_STATUS" = "200" ]; then
    echo "✅ 后端服务健康"
else
    echo "❌ 后端服务异常"
    exit 1
fi

echo "🎉 部署完成！"
echo ""
echo "服务地址:"
echo "- 后端 API: http://localhost:8000"
echo "- API 文档: http://localhost:8000/docs"
echo "- Flower 监控: http://localhost:5555"
echo ""
echo "查看日志: docker-compose logs -f"