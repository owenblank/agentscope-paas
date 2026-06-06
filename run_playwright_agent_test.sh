#!/bin/bash
# AgentScope PaaS - Playwright 登录和智能体创建测试
# 这个脚本会启动前端服务器并运行完整的测试流程

echo "===================================="
echo "AgentScope PaaS - Playwright 测试"
echo "===================================="
echo ""

# 检查 Playwright 是否安装
python -c "import playwright; print('Playwright installed')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[ERROR] Playwright 未安装"
    echo "请运行: pip install playwright"
    echo "然后运行: playwright install chromium"
    exit 1
fi

echo "[1/4] 检查依赖..."

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "[2/4] 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

echo "[3/4] 启动前端服务器并运行测试..."
echo ""

# 使用 with_server.py 脚本管理服务器并运行测试
python "C:\Users\Administrator\.claude\skills\webapp-testing\scripts\with_server.py" \
    --server "cd frontend && npm run dev" \
    --port 5173 \
    -- python e2e/test_login_and_agent_creation.py --base-url http://localhost:5173

echo ""
echo "[4/4] 测试完成！"
echo ""
echo "查看结果:"
echo "- 截图: e2e_screenshots/full_flow/"
echo "- 报告: e2e_screenshots/test_report_*.json"
echo ""