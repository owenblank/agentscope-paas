@echo off
REM AgentScope PaaS - Playwright Frontend Test Runner
REM 此脚本使用系统 Python 运行 Playwright 测试

echo ========================================
echo AgentScope PaaS - Playwright Test Runner
echo ========================================
echo.

echo Checking Playwright installation...
"C:\Program Files\python\python.exe" -c "import playwright; print('Playwright installed: ' + playwright.__version__)" 2>nul
if errorlevel 1 (
    echo Playwright not found, installing...
    "C:\Program Files\python\python.exe" -m pip install playwright pytest-playwright
    if errorlevel 1 (
        echo Failed to install Playwright
        pause
        exit /b 1
    )
    echo Installing Playwright browsers...
    "C:\Program Files\python\python.exe" -m playwright install chromium
)

echo.
echo Running Playwright frontend tests...
echo.

cd /d "%~dp0e2e"
"C:\Program Files\python\python.exe" simple_playwright_test.py

echo.
echo Test completed. Check screenshots in e2e_screenshots folder.
pause