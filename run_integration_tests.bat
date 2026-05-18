@echo off
REM AgentScope PaaS 集成测试运行脚本
echo ========================================
echo AgentScope PaaS 集成测试启动脚本
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python环境
    pause
    exit /b 1
)

echo [步骤 1] 安装测试依赖...
pip install playwright requests pytest pytest-html pytest-json-report -q

echo [步骤 2] 安装Playwright浏览器...
playwright install chromium

echo [步骤 3] 检查服务状态...
echo 正在检查API服务器...
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] API服务器未运行，请先启动: python api_server/main.py
    echo         或使用: python -m api_server.main
    echo.
    set /p continue="是否继续测试？ (y/n): "
    if /i not "%continue%"=="y" (
        pause
        exit /b 1
    )
)

echo 正在检查前端服务器...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 前端服务器未运行，请先启动: cd frontend && npm run dev
    echo.
    set /p continue="是否继续测试？ (y/n): "
    if /i not "%continue%"=="y" (
        pause
        exit /b 1
    )
)

echo.
echo [步骤 4] 开始执行集成测试...
echo ========================================
echo.

REM 创建必要的目录
if not exist "test_results" mkdir test_results
if not exist "test_results\screenshots" mkdir test_results\screenshots

REM 运行测试
python e2e/comprehensive_integration_test.py %*

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.

REM 检查测试结果
if exist "test_results\e2e_report_*.txt" (
    echo 测试报告已生成，最新报告：
    for /f "delims=" %%i in ('dir /b /o-d test_results\e2e_report_*.txt') do (
        type "test_results\%%i"
        goto :found_report
    )
    :found_report
)

pause