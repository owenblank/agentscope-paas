@echo off
REM AgentScope-PaaS 停止所有服务脚本 (Windows)

echo ========================================
echo 停止 AgentScope-PaaS 服务...
echo ========================================
echo.

echo [INFO] 正在停止后端服务...
taskkill /FI "WINDOWTITLE eq AgentScope-PaaS-Backend*" /T >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 后端服务已停止
) else (
    echo [INFO] 后端服务未运行
)

echo [INFO] 正在停止前端服务...
taskkill /FI "WINDOWTITLE eq AgentScope-PaaS-Frontend*" /T >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 前端服务已停止
) else (
    echo [INFO] 前端服务未运行
)

echo [INFO] 正在清理Python进程...
for /f "tokens=2" %%i in ('tasklist ^| findstr "python.exe"') do taskkill /PID %%i /F >nul 2>&1

echo [INFO] 正在清理Node.js进程...
for /f "tokens=2" %%i in ('tasklist ^| findstr "node.exe"') do taskkill /PID %%i /F >nul 2>&1

echo.
echo ========================================
echo 所有服务已停止
echo ========================================
pause