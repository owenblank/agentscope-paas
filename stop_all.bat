@echo off
REM AgentScope-PaaS 停止所有服务脚本 (Windows)

echo ========================================
echo 停止 AgentScope-PaaS 服务...
echo ========================================
echo.

echo [信息] 正在停止后端服务...
taskkill /FI "WINDOWTITLE eq AgentScope-PaaS-Backend*" /T >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] 后端服务已停止
) else (
    echo [信息] 后端服务窗口未找到
)

echo [信息] 正在停止前端服务...
taskkill /FI "WINDOWTITLE eq AgentScope-PaaS-Frontend*" /T >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] 前端服务已停止
) else (
    echo [信息] 前端服务窗口未找到
)

REM 清理Python uvicorn进程
echo [信息] 正在清理Python uvicorn进程...
wmic process where "commandline like '%%uvicorn%%api_server.main:app%%'" delete >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] Python uvicorn进程已清理
) else (
    echo [信息] 无Python uvicorn进程需要清理
)

REM 清理Node vite进程
echo [信息] 正在清理Node vite进程...
wmic process where "commandline like '%%vite%%'" delete >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] Node vite进程已清理
) else (
    echo [信息] 无Node vite进程需要清理
)

REM 强制清理端口占用
echo [信息] 正在清理端口占用...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000.*LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo ========================================
echo 所有服务已停止
echo ========================================
echo.
echo [提示] 如果进程仍在运行，请手动检查任务管理器
echo [提示] 按任意键关闭此窗口...
pause >nul