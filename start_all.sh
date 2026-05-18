#!/bin/bash
# AgentScope-PaaS 完整系统启动脚本 (Linux/Mac)
# 同时启动后端API服务器和前端开发服务器

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BACKEND_PORT=8000
FRONTEND_PORT=3000

echo "========================================"
echo "AgentScope-PaaS 系统启动中..."
echo "========================================"
echo ""
echo -e "${BLUE}[配置信息]${NC}"
echo " 后端端口: $BACKEND_PORT"
echo " 前端端口: $FRONTEND_PORT"
echo ""

# 检查tmux是否安装
if command -v tmux &> /dev/null; then
    # 使用tmux启动服务
    echo -e "${BLUE}[INFO]${NC} 使用tmux启动服务..."

    # 启动后端服务
    tmux new-session -d -s agentscope-backend "$PWD/start_backend.sh $BACKEND_PORT"
    echo -e "${GREEN}[OK]${NC} 后端服务已启动在tmux session: agentscope-backend"

    # 等待后端启动
    sleep 3

    # 启动前端服务
    tmux new-session -d -s agentscope-frontend "cd $PWD/frontend && npm run dev -- --port $FRONTEND_PORT"
    echo -e "${GREEN}[OK]${NC} 前端服务已启动在tmux session: agentscope-frontend"

    echo ""
    echo "========================================"
    echo "系统启动完成！"
    echo "========================================"
    echo ""
    echo "访问地址:"
    echo "  前端界面: http://localhost:$FRONTEND_PORT"
    echo "  API文档:  http://localhost:$BACKEND_PORT/api/v1/docs"
    echo "  健康检查: http://localhost:$BACKEND_PORT/api/v1/health"
    echo ""
    echo "服务管理:"
    echo "  查看后端: tmux attach -t agentscope-backend"
    echo "  查看前端: tmux attach -t agentscope-frontend"
    echo "  停止服务: ./stop_all.sh"
    echo ""

else
    # 不使用tmux，使用后台进程
    echo -e "${YELLOW}[WARN]${NC} tmux未安装，使用后台进程启动服务"
    echo -e "${BLUE}[INFO]${NC} 安装tmux可以获得更好的体验: apt install tmux / brew install tmux"
    echo ""

    # 启动后端服务
    echo -e "${BLUE}[INFO]${NC} 启动后端API服务器..."
    nohup ./start_backend.sh $BACKEND_PORT > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > .backend_pid
    echo -e "${GREEN}[OK]${NC} 后端服务已启动 (PID: $BACKEND_PID)"

    # 等待后端启动
    sleep 3

    # 启动前端服务
    echo -e "${BLUE}[INFO]${NC} 启动前端开发服务器..."
    cd frontend
    nohup npm run dev -- --port $FRONTEND_PORT > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo $FRONTEND_PID > .frontend_pid
    echo -e "${GREEN}[OK]${NC} 前端服务已启动 (PID: $FRONTEND_PID)"

    echo ""
    echo "========================================"
    echo "系统启动完成！"
    echo "========================================"
    echo ""
    echo "访问地址:"
    echo "  前端界面: http://localhost:$FRONTEND_PORT"
    echo "  API文档:  http://localhost:$BACKEND_PORT/api/v1/docs"
    echo "  健康检查: http://localhost:$BACKEND_PORT/api/v1/health"
    echo ""
    echo "日志文件:"
    echo "  后端日志: backend.log"
    echo "  前端日志: frontend.log"
    echo ""
    echo "停止服务:"
    echo "  使用 ./stop_all.sh 停止所有服务"
    echo ""
fi