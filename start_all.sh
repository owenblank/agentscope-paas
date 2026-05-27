#!/bin/bash
# AgentScope-PaaS 完整系统启动脚本 (Linux/Mac)
# 同时启动后端API服务器和前端开发服务器
# 用法: ./start_all.sh [后端端口] [前端端口]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BACKEND_PORT=${1:-8000}
FRONTEND_PORT=${2:-3000}

echo "========================================"
echo "AgentScope-PaaS 系统启动中..."
echo "========================================"
echo ""
echo -e "${BLUE}[配置信息]${NC}"
echo " 后端端口: $BACKEND_PORT"
echo " 前端端口: $FRONTEND_PORT"
echo ""

# 环境检查
echo -e "${BLUE}[检查]${NC} Python环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误]${NC} Python3未安装或不在PATH中"
    exit 1
fi
echo -e "${GREEN}[成功]${NC} Python版本: $(python3 --version)"

echo -e "${BLUE}[检查]${NC} Node.js环境..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}[错误]${NC} Node.js未安装或不在PATH中"
    exit 1
fi
echo -e "${GREEN}[成功]${NC} Node版本: $(node --version)"

echo -e "${BLUE}[检查]${NC} npm环境..."
if ! command -v npm &> /dev/null; then
    echo -e "${RED}[错误]${NC} npm未安装或不在PATH中"
    exit 1
fi
echo -e "${GREEN}[成功]${NC} npm版本: $(npm --version)"
echo ""

# 检查端口占用
echo -e "${BLUE}[检查]${NC} 端口占用情况..."
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}[警告]${NC} 后端端口 $BACKEND_PORT 已被占用"
    echo -e "${BLUE}[信息]${NC} 尝试停止现有服务..."
    ./stop_all.sh >/dev/null 2>&1 || true
    sleep 2
fi

if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}[警告]${NC} 前端端口 $FRONTEND_PORT 已被占用"
    echo -e "${BLUE}[信息]${NC} 尝试停止现有服务..."
    ./stop_all.sh >/dev/null 2>&1 || true
    sleep 2
fi

# 检查tmux是否安装
if command -v tmux &> /dev/null; then
    # 使用tmux启动服务
    echo -e "${BLUE}[信息]${NC} 使用tmux启动服务..."

    # 启动后端服务
    tmux new-session -d -s agentscope-backend "$PWD/start_backend.sh $BACKEND_PORT"
    echo -e "${GREEN}[成功]${NC} 后端服务已启动在tmux session: agentscope-backend"

    # 等待后端启动
    sleep 5

    # 验证后端服务
    echo -e "${BLUE}[验证]${NC} 后端服务启动状态..."
    if curl -s http://localhost:$BACKEND_PORT/api/v1/health >/dev/null 2>&1; then
        echo -e "${GREEN}[成功]${NC} 后端服务启动成功"
    else
        echo -e "${YELLOW}[警告]${NC} 后端服务可能还在启动中，请稍后访问"
    fi

    # 启动前端服务
    tmux new-session -d -s agentscope-frontend "cd $PWD/frontend && npm run dev -- --port $FRONTEND_PORT --host"
    echo -e "${GREEN}[成功]${NC} 前端服务已启动在tmux session: agentscope-frontend"

    # 等待前端启动
    sleep 5

    echo ""
    echo "========================================"
    echo "系统启动完成！"
    echo "========================================"
    echo ""
    echo "访问地址:"
    echo "  前端界面: http://localhost:$FRONTEND_PORT"
    echo "  后端API:  http://localhost:$BACKEND_PORT"
    echo "  API文档:  http://localhost:$BACKEND_PORT/api/v1/docs"
    echo "  健康检查: http://localhost:$BACKEND_PORT/api/v1/health"
    echo ""
    echo "服务管理:"
    echo "  查看后端: tmux attach -t agentscope-backend"
    echo "  查看前端: tmux attach -t agentscope-frontend"
    echo "  停止服务: ./stop_all.sh"
    echo ""
    echo "提示:"
    echo "  - 前端服务可能需要10-15秒完全启动"
    echo "  - 使用 tmux attach -t session-name 查看服务日志"
    echo "  - 按 Ctrl+B 然后按 D 退出tmux会话（服务继续运行）"
    echo ""

else
    # 不使用tmux，使用后台进程
    echo -e "${YELLOW}[警告]${NC} tmux未安装，使用后台进程启动服务"
    echo -e "${BLUE}[信息]${NC} 安装tmux可以获得更好的体验: apt install tmux / brew install tmux"
    echo ""

    # 启动后端服务
    echo -e "${BLUE}[信息]${NC} 启动后端API服务器..."
    nohup ./start_backend.sh $BACKEND_PORT > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > .backend_pid
    echo -e "${GREEN}[成功]${NC} 后端服务已启动 (PID: $BACKEND_PID)"

    # 等待后端启动
    sleep 5

    # 验证后端服务
    echo -e "${BLUE}[验证]${NC} 后端服务启动状态..."
    if curl -s http://localhost:$BACKEND_PORT/api/v1/health >/dev/null 2>&1; then
        echo -e "${GREEN}[成功]${NC} 后端服务启动成功"
    else
        echo -e "${YELLOW}[警告]${NC} 后端服务可能还在启动中，请稍后访问"
    fi

    # 启动前端服务
    echo -e "${BLUE}[信息]${NC} 启动前端开发服务器..."
    cd frontend
    nohup npm run dev -- --port $FRONTEND_PORT --host > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo $FRONTEND_PID > .frontend_pid
    echo -e "${GREEN}[成功]${NC} 前端服务已启动 (PID: $FRONTEND_PID)"

    # 等待前端启动
    sleep 5

    echo ""
    echo "========================================"
    echo "系统启动完成！"
    echo "========================================"
    echo ""
    echo "访问地址:"
    echo "  前端界面: http://localhost:$FRONTEND_PORT"
    echo "  后端API:  http://localhost:$BACKEND_PORT"
    echo "  API文档:  http://localhost:$BACKEND_PORT/api/v1/docs"
    echo "  健康检查: http://localhost:$BACKEND_PORT/api/v1/health"
    echo ""
    echo "日志文件:"
    echo "  后端日志: backend.log"
    echo "  前端日志: frontend.log"
    echo ""
    echo "进程管理:"
    echo "  后端PID: $BACKEND_PID"
    echo "  前端PID: $FRONTEND_PID"
    echo "  停止服务: ./stop_all.sh"
    echo ""
    echo "提示:"
    echo "  - 前端服务可能需要10-15秒完全启动"
    echo "  - 使用 tail -f backend.log 或 tail -f frontend.log 查看日志"
    echo ""
fi