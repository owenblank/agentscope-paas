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
    echo -e "${BLUE}[信息]${NC} 使用tmux停止服务..."

    # 停止后端服务
    if tmux has-session -t agentscope-backend 2>/dev/null; then
        tmux kill-session -t agentscope-backend
        echo -e "${GREEN}[成功]${NC} 后端服务已停止"
    else
        echo -e "${YELLOW}[信息]${NC} 后端服务tmux会话未找到"
    fi

    # 停止前端服务
    if tmux has-session -t agentscope-frontend 2>/dev/null; then
        tmux kill-session -t agentscope-frontend
        echo -e "${GREEN}[成功]${NC} 前端服务已停止"
    else
        echo -e "${YELLOW}[信息]${NC} 前端服务tmux会话未找到"
    fi
fi

# 使用PID文件停止服务（备用方案）
echo -e "${BLUE}[信息]${NC} 检查PID文件..."

# 停止后端服务
if [ -f ".backend_pid" ]; then
    BACKEND_PID=$(cat .backend_pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}[成功]${NC} 后端服务已停止 (PID: $BACKEND_PID)"
    else
        echo -e "${YELLOW}[信息]${NC} 后端进程未运行 (PID: $BACKEND_PID)"
    fi
    rm -f .backend_pid
else
    echo -e "${YELLOW}[信息]${NC} 后端PID文件不存在"
fi

# 停止前端服务
if [ -f ".frontend_pid" ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}[成功]${NC} 前端服务已停止 (PID: $FRONTEND_PID)"
    else
        echo -e "${YELLOW}[信息]${NC} 前端进程未运行 (PID: $FRONTEND_PID)"
    fi
    rm -f .frontend_pid
else
    echo -e "${YELLOW}[信息]${NC} 前端PID文件不存在"
fi

# 清理可能残留的进程
echo -e "${BLUE}[信息]${NC} 清理残留进程..."

# 清理Python uvicorn进程
if pkill -f "uvicorn api_server.main:app" 2>/dev/null; then
    echo -e "${GREEN}[成功]${NC} Python uvicorn进程已清理"
else
    echo -e "${YELLOW}[信息]${NC} 无Python uvicorn进程需要清理"
fi

# 清理Node vite进程
if pkill -f "vite" 2>/dev/null; then
    echo -e "${GREEN}[成功]${NC} Node vite进程已清理"
else
    echo -e "${YELLOW}[信息]${NC} 无Node vite进程需要清理"
fi

# 清理端口占用（备用方案）
echo -e "${BLUE}[信息]${NC} 清理端口占用..."

# 清理端口8000
if lsof -ti:8000 >/dev/null 2>&1; then
    kill -9 $(lsof -ti:8000) 2>/dev/null
    echo -e "${GREEN}[成功]${NC} 端口8000已清理"
else
    echo -e "${YELLOW}[信息]${NC} 端口8000未被占用"
fi

# 清理端口3000
if lsof -ti:3000 >/dev/null 2>&1; then
    kill -9 $(lsof -ti:3000) 2>/dev/null
    echo -e "${GREEN}[成功]${NC} 端口3000已清理"
else
    echo -e "${YELLOW}[信息]${NC} 端口3000未被占用"
fi

# 清理日志文件
echo -e "${BLUE}[信息]${NC} 清理临时文件..."
rm -f .backend_pid .frontend_pid backend.log frontend.log 2>/dev/null
echo -e "${GREEN}[成功]${NC} 临时文件已清理"

echo ""
echo "========================================"
echo "所有服务已停止"
echo "========================================"
echo ""
echo "提示:"
echo "  - 如果进程仍在运行，请使用: ps aux | grep -E 'uvicorn|vite'"
echo "  - 强制清理: pkill -9 -f 'uvicorn|vite'"
echo ""