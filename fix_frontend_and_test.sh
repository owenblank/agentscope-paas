#!/bin/bash
# AgentScope PaaS - 前端修复和端到端测试脚本

echo "========================================"
echo "AgentScope PaaS - 前端修复和测试"
echo "========================================"

# 1. 检查并修复前端依赖
echo "[STEP 1]: 检查和修复前端依赖..."
cd frontend

# 检查是否需要安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
else
    echo "node_modules 已存在，检查关键依赖..."
    npm list react react-dom antd 2>/dev/null || npm install
fi

# 2. 检查 Tailwind CSS 配置
echo "[STEP 2]: 检查 Tailwind CSS 配置..."
if [ ! -f "tailwind.config.js" ]; then
    echo "创建 Tailwind CSS 配置..."
    npx tailwindcss init -p
fi

# 3. 构建前端（生产模式）
echo "[STEP 3]: 构建前端..."
npm run build

# 4. 检查构建结果
if [ -d "dist" ]; then
    echo "✓ 前端构建成功"
    echo "构建产物位于: dist/"
else
    echo "✗ 前端构建失败"
    exit 1
fi

# 5. 返回项目根目录
cd ..

# 6. 确保后端依赖安装
echo "[STEP 4]: 检查后端依赖..."
pip install -q email-validator pydantic[email] fastapi uvicorn

# 7. 运行端到端测试
echo "[STEP 5]: 运行端到端测试..."
cd e2e

echo "启动前端服务器（后台）..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

echo "等待前端服务器启动..."
sleep 5

echo "启动后端服务器（后台）..."
cd ../api_server && python main.py &
BACKEND_PID=$!

echo "等待后端服务器启动..."
sleep 3

echo "运行 Playwright 测试..."
cd ../e2e
python comprehensive_playwright_test.py

# 清理后台进程
echo "清理后台进程..."
kill $FRONTEND_PID $BACKEND_PID 2>/dev/null

echo "========================================"
echo "测试完成！"
echo "========================================"