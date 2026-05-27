@echo off
REM AgentScope-PaaS 完整系统启动脚本 (Windows)
REM 同时启动后端API服务器和前端开发服务器
REM 用法: start_all.bat [后端端口] [前端端口]

echo ========================================
echo AgentScope-PaaS 系统启动中...
echo ========================================
echo.

set BACKEND_PORT=%1
if "%BACKEND_PORT%"=="" set BACKEND_PORT=8000

set FRONTEND_PORT=%2
if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=3000

echo [配置信息]
echo 后端端口: %BACKEND_PORT%
echo 前端端口: %FRONTEND_PORT%
echo.

REM 检查Python环境
echo [检查] Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python未安装或不在PATH中
    pause
    exit /b 1
)
echo [成功] Python环境检查通过

REM 检查Node.js环境
echo [检查] Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Node.js未安装或不在PATH中
    pause
    exit /b 1
)
echo [成功] Node.js环境检查通过

REM 检查npm
echo [检查] npm环境...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] npm未安装或不在PATH中
    pause
    exit /b 1
)
echo [成功] npm环境检查通过
echo.

REM 检查端口占用
echo [检查] 端口占用情况...
netstat -an | findstr ":%BACKEND_PORT%" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] 后端端口 %BACKEND_PORT% 已被占用，尝试停止现有服务...
    taskkill /FI "WINDOWTITLE eq AgentScope-PaaS-Backend*" /T >nul 2>&1
    timeout /t 2 /nobreak >nul
)

netstat -an | findstr ":%FRONTEND_PORT%" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] 前端端口 %FRONTEND_PORT% 已被占用，尝试停止现有服务...
    taskkill /FI "WINDOWTITLE eq AgentScope-PaaS-Frontend*" /T >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo [启动后端API服务器]
start "AgentScope-PaaS-Backend" cmd /k "cd /d %~dp0 && start_backend.bat %BACKEND_PORT%"

echo [等待后端启动]
timeout /t 5 /nobreak >nul

REM 检查后端是否启动成功
echo [验证] 后端服务启动状态...
curl -s http://localhost:%BACKEND_PORT%/api/v1/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] 后端服务启动成功
) else (
    echo [警告] 后端服务可能还在启动中，请稍后访问
)

echo [启动前端开发服务器]
start "AgentScope-PaaS-Frontend" cmd /k "cd /d %~dp0 && start_frontend.bat %FRONTEND_PORT%"

echo [等待前端启动]
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 系统启动完成！
echo ========================================
echo.
echo 访问地址:
echo   前端界面: http://localhost:%FRONTEND_PORT%
echo   后端API:  http://localhost:%BACKEND_PORT%
echo   API文档:  http://localhost:%BACKEND_PORT%/api/v1/docs
echo   健康检查: http://localhost:%BACKEND_PORT%/api/v1/health
echo.
echo 注意:
echo   - 两个服务窗口会自动打开
echo   - 前端服务可能需要10-15秒完全启动
echo   - 关闭窗口即可停止对应服务
echo   - 或使用 stop_all.bat 停止所有服务
echo.
echo [提示] 按任意键关闭此窗口（服务将继续运行）...
pause >nul