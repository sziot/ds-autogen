#!/bin/bash

# 开发环境启动脚本
echo "启动 DeepSeek 代码审查系统开发环境..."

# 检查 Node.js 版本
NODE_VERSION=$(node -v)
if [[ $NODE_VERSION != v18.* ]] && [[ $NODE_VERSION != v20.* ]]; then
    echo "错误: 需要 Node.js 18 或 20，当前版本: $NODE_VERSION"
    exit 1
fi

# 检查包管理器
if [ -f "package-lock.json" ]; then
    echo "使用 npm..."
    PM="npm"
elif [ -f "yarn.lock" ]; then
    echo "使用 yarn..."
    PM="yarn"
elif [ -f "pnpm-lock.yaml" ]; then
    echo "使用 pnpm..."
    PM="pnpm"
else
    echo "使用 npm..."
    PM="npm"
fi

# 安装依赖
echo "安装依赖..."
$PM install

# 启动开发服务器
echo "启动开发服务器..."
$PM run dev