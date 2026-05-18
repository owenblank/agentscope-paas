#!/bin/bash
# AgentScope-PaaS 停止所有服务脚本 (Linux/Mac)

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "停止 AgentScope-PaaS 服务..."
echo "========================================"
echo ""

# 检查tmux是否安装并使用tmux停止服务
if command -v tmux &> /dev/null; then
    echo -e "${BLUE}[INFO]${NC} 使用tmux停止服务..."

    # 停止后端服务
    if tmux has-session -t agentscope-backend 2>/dev/null; then
        tmux kill-session -t agentscope-backend
        echo -e "${GREEN}[OK]${NC} 后端服务已停止"
    else
        echo -e "${YELLOW}[INFO]${NC} 后端服务未运行"
    fi

    # 停止前端服务
    if tmux has-session -t agentscope-frontend 2>/dev/null; then
        tmux kill-session -t agentscope-frontend
        echo -e "${GREEN}[OK]${NC} 前端服务已停止"
    else
        echo -e "${YELLOW}[INFO]${NC} 前端服务未运行"
    fi
else
    # 使用PID文件停止服务
    echo -e "${BLUE}[INFO]${NC} 使用PID文件停止服务..."

    # 停止后端服务
    if [ -f ".backend_pid" ]; then
        BACKEND_PID=$(cat .backend_pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID
            echo -e "${GREEN}[OK]${NC} 后端服务已停止 (PID: $BACKEND_PID)"
        else
            echo -e "${YELLOW}[INFO]${NC} 后端服务未运行"
        fi
        rm -f .backend_pid
    else
        echo -e "${YELLOW}[INFO]${NC} 后端PID文件不存在"
    fi

    # 停止前端服务
    if [ -f ".frontend_pid" ]; then
        FRONTEND_PID=$(cat .frontend_pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill $FRONTEND_PID
            echo -e "${GREEN}[OK]${NC} 前端服务已停止 (PID: $FRONTEND_PID)"
        else
            echo -e "${YELLOW}[INFO]${NC} 前端服务未运行"
        fi
        rm -f .frontend_pid
    else
        echo -e "${YELLOW}[INFO]${NC} 前端PID文件不存在"
    fi
fi

# 清理可能残留的进程
echo -e "${BLUE}[INFO]${NC} 清理残留进程..."

# 清理Python uvicorn进程
pkill -f "uvicorn api_server.main:app" 2>/dev/null && echo -e "${GREEN}[OK]${NC} Python uvicorn进程已清理" || echo -e "${YELLOW}[INFO]${NC} 无Python uvicorn进程需要清理"

# 清理Node vite进程
pkill -f "vite" 2>/dev/null && echo -e "${GREEN}[OK]${NC} Node vite进程已清理" || echo -e "${YELLOW}[INFO]${NC} 无Node vite进程需要清理"

echo ""
echo "========================================"
echo "所有服务已停止"
echo "========================================"