@echo off
REM AgentScope-PaaS 前端开发服务器启动脚本 (Windows)
REM 用法: start_frontend.bat [端口]

echo ========================================
echo AgentScope-PaaS 前端开发服务器启动中...
echo ========================================

set PORT=%1
if "%PORT%"=="" set PORT=3000

echo [INFO] 启动端口: %PORT%
echo [INFO] 前端地址: http://localhost:%PORT%

REM 检查Node.js环境
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js未安装或不在PATH中
    pause
    exit /b 1
)

REM 检查npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm未安装或不在PATH中
    pause
    exit /b 1
)

REM 进入前端目录
cd frontend

REM 检查node_modules
if not exist "node_modules" (
    echo [INFO] node_modules不存在，正在安装依赖...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] 依赖安装失败
        cd ..
        pause
        exit /b 1
    )
)

REM 检查package.json
if not exist "package.json" (
    echo [ERROR] package.json文件不存在
    cd ..
    pause
    exit /b 1
)

echo [INFO] 启动前端开发服务器...
echo [INFO] 按 Ctrl+C 停止服务器
echo.

REM 启动前端开发服务器（监听所有接口）
call npm run dev -- --port %PORT% --host

REM 返回根目录
cd ..

pause