@echo off
REM AgentScope-PaaS 后端API服务器启动脚本 (Windows)
REM 用法: start_backend.bat [端口]

echo ========================================
echo AgentScope-PaaS 后端API服务器启动中...
echo ========================================

set PORT=%1
if "%PORT%"=="" set PORT=8000

echo [INFO] 启动端口: %PORT%
echo [INFO] API文档: http://localhost:%PORT%/api/v1/docs
echo [INFO] 健康检查: http://localhost:%PORT%/api/v1/health

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python未安装或不在PATH中
    pause
    exit /b 1
)

REM 检查必要的包
echo [INFO] 检查依赖包...
python -c "import fastapi; import uvicorn; import agentscope_paas" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] 部分依赖包缺失，正在安装...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] 依赖包安装失败
        pause
        exit /b 1
    )
)

REM 创建必要的目录
if not exist "api_server\data" mkdir "api_server\data"
if not exist "api_server\data\agents" mkdir "api_server\data\agents"
if not exist "api_server\logs" mkdir "api_server\logs"

echo [INFO] 启动API服务器...
echo [INFO] 按 Ctrl+C 停止服务器
echo.

REM 启动API服务器
python -m uvicorn api_server.main:app --host 0.0.0.0 --port %PORT% --reload

pause