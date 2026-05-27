#!/bin/bash
# AgentScope-PaaS 前端开发服务器启动脚本 (Linux/Mac)
# 用法: ./start_frontend.sh [端口]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PORT=${1:-3000}

echo "========================================"
echo "AgentScope-PaaS 前端开发服务器启动中..."
echo "========================================"
echo ""
echo -e "${BLUE}[INFO]${NC} 启动端口: $PORT"
echo -e "${BLUE}[INFO]${NC} 前端地址: http://localhost:$PORT"

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Node.js未安装或不在PATH中"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Node版本: $(node --version)"

# 检查npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} npm未安装或不在PATH中"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} npm版本: $(npm --version)"

# 进入前端目录
cd frontend

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}[INFO]${NC} node_modules不存在，正在安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} 依赖安装失败"
        exit 1
    fi
fi

# 检查package.json
if [ ! -f "package.json" ]; then
    echo -e "${RED}[ERROR]${NC} package.json文件不存在"
    exit 1
fi

echo ""
echo -e "${BLUE}[INFO]${NC} 启动前端开发服务器..."
echo -e "${BLUE}[INFO]${NC} 按 Ctrl+C 停止服务器"
echo ""

# 启动前端开发服务器（监听所有接口）
npm run dev -- --port $PORT --host