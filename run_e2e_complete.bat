@echo off
chcp 65001 >nul
echo ====================================
echo AgentScope PaaS - 完整E2E测试
echo ====================================

echo.
echo 🔍 第一步：环境准备
python scripts/prepare_e2e_env.py
if %errorlevel% neq 0 (
    echo ❌ 环境准备失败
    pause
    exit /b 1
)

echo.
echo 🚀 第二步：启动服务
start "Backend Service" cmd /k "cd api_server && python main.py"
timeout /t 5 /nobreak >nul

start "Frontend Service" cmd /k "cd frontend && npm run dev"
timeout /t 10 /nobreak >nul

echo.
echo 🧪 第三步：运行E2E测试
python e2e/simple_e2e_test.py
if %errorlevel% neq 0 (
    echo ❌ E2E测试失败
)

echo.
echo ====================================
echo 测试完成！
echo ====================================
echo.
echo 查看测试报告和截图：
echo - 截图目录: e2e_screenshots/
echo - 报告目录: e2e_reports/
echo.
pause