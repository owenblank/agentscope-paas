#!/bin/bash
# AgentScope PaaS 集成测试运行脚本 (Linux/Mac)

set -e

echo "========================================"
echo "AgentScope PaaS 集成测试启动脚本"
echo "========================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python环境"
    exit 1
fi

echo "[步骤 1] 安装测试依赖..."
pip3 install playwright requests pytest pytest-html pytest-json-report -q

echo "[步骤 2] 安装Playwright浏览器..."
playwright install chromium

echo "[步骤 3] 检查服务状态..."
echo "正在检查API服务器..."
if ! curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "[警告] API服务器未运行，请先启动: python api_server/main.py"
    echo "        或使用: python -m api_server.main"
    echo ""
    read -p "是否继续测试？ (y/n): " continue
    if [[ ! "$continue" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "正在检查前端服务器..."
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "[警告] 前端服务器未运行，请先启动: cd frontend && npm run dev"
    echo ""
    read -p "是否继续测试？ (y/n): " continue
    if [[ ! "$continue" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "[步骤 4] 开始执行集成测试..."
echo "========================================"
echo ""

# 创建必要的目录
mkdir -p test_results/screenshots

# 运行测试
python3 e2e/comprehensive_integration_test.py "$@"

echo ""
echo "========================================"
echo "测试完成！"
echo "========================================"
echo ""

# 显示最新的测试报告
if ls test_results/e2e_report_*.txt 1> /dev/null 2>&1; then
    echo "测试报告已生成，最新报告："
    cat $(ls -t test_results/e2e_report_*.txt | head -1)
fi