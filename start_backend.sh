#!/bin/bash
# AgentScope-PaaS 后端API服务器启动脚本 (Linux/Mac)
# 用法: ./start_backend.sh [端口]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PORT=${1:-8000}

echo "========================================"
echo "AgentScope-PaaS 后端API服务器启动中..."
echo "========================================"
echo ""
echo -e "${BLUE}[INFO]${NC} 启动端口: $PORT"
echo -e "${BLUE}[INFO]${NC} API文档: http://localhost:$PORT/api/v1/docs"
echo -e "${BLUE}[INFO]${NC} 健康检查: http://localhost:$PORT/api/v1/health"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python3未安装或不在PATH中"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Python版本: $(python3 --version)"

# 检查必要的包
echo -e "${BLUE}[INFO]${NC} 检查依赖包..."
if ! python3 -c "import fastapi; import uvicorn; import agentscope_paas" 2>/dev/null; then
    echo -e "${YELLOW}[WARN]${NC} 部分依赖包缺失，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} 依赖包安装失败"
        exit 1
    fi
fi

# 创建必要的目录
mkdir -p api_server/data/agents
mkdir -p api_server/logs

echo ""
echo -e "${BLUE}[INFO]${NC} 启动API服务器..."
echo -e "${BLUE}[INFO]${NC} 按 Ctrl+C 停止服务器"
echo ""

# 启动API服务器
python3 -m uvicorn api_server.main:app --host 0.0.0.0 --port $PORT --reload