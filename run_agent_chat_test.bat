@echo off
REM Agent Creation and Chat E2E Test Runner
REM This script runs the complete agent creation and chat functionality test

echo ==================================================
echo Agent Creation and Chat E2E Test
echo ==================================================
echo.

REM Check if Playwright is installed
python -c "import playwright" 2>nul
if errorlevel 1 (
    echo [ERROR] Playwright is not installed
    echo Please run: pip install playwright
    echo Then run: playwright install chromium
    pause
    exit /b 1
)

echo [INFO] Starting agent creation and chat test...
echo.

REM Check if frontend is running
echo [INFO] Checking if frontend is running on http://localhost:3000...
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Frontend does not appear to be running on http://localhost:3000
    echo Please start the frontend with: cd frontend ^&^& npm run dev
    echo.
    set /p continue="Do you want to continue anyway? (y/n): "
    if /i not "%continue%"=="y" (
        pause
        exit /b 1
    )
)

REM Check if backend is running
echo [INFO] Checking if backend is running on http://localhost:8000...
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend does not appear to be running on http://localhost:8000
    echo Please start the backend with: cd api_server ^&^& python main.py
    echo.
    set /p continue="Do you want to continue anyway? (y/n): "
    if /i not "%continue%"=="y" (
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Running E2E test...
echo.

REM Run the test
python e2e/agent_creation_chat_test.py

if errorlevel 1 (
    echo.
    echo [ERROR] Test failed with error code %errorlevel%
    pause
    exit /b 1
) else (
    echo.
    echo [SUCCESS] Test completed successfully
    echo Check e2e_screenshots directory for screenshots
    echo Check e2e_test_results.json for detailed results
    pause
    exit /b 0
)