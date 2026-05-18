@echo off
REM AgentScope-PaaS 完整系统启动脚本 (Windows)
REM 同时启动后端API服务器和前端开发服务器

echo ========================================
echo AgentScope-PaaS 系统启动中...
echo ========================================
echo.

set BACKEND_PORT=8000
set FRONTEND_PORT=3000

echo [配置信息]
echo 后端端口: %BACKEND_PORT%
echo 前端端口: %FRONTEND_PORT%
echo.

echo [启动后端API服务器]
start "AgentScope-PaaS-Backend" cmd /k "cd /d %~dp0 && start_backend.bat %BACKEND_PORT%"

echo [等待后端启动]
timeout /t 3 /nobreak >nul

echo [启动前端开发服务器]
start "AgentScope-PaaS-Frontend" cmd /k "cd /d %~dp0 && start_frontend.bat %FRONTEND_PORT%"

echo.
echo ========================================
echo 系统启动完成！
echo ========================================
echo.
echo 访问地址:
echo   前端界面: http://localhost:%FRONTEND_PORT%
echo   API文档:  http://localhost:%BACKEND_PORT%/api/v1/docs
echo   健康检查: http://localhost:%BACKEND_PORT%/api/v1/health
echo.
echo 注意:
echo   - 两个服务窗口会自动打开
echo   - 关闭窗口即可停止对应服务
echo   - 或使用 stop_all.bat 停止所有服务
echo.
pause