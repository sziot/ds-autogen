#!/bin/bash

# 前端启动脚本

echo "启动AI代码审查系统前端服务..."

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    npm install
fi

# 启动开发服务器
echo "启动Vite开发服务器..."
npm run dev

