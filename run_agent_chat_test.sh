#!/bin/bash

# Agent Creation and Chat E2E Test Runner
# This script runs the complete agent creation and chat functionality test

echo "=================================================="
echo "Agent Creation and Chat E2E Test"
echo "=================================================="
echo ""

# Check if Playwright is installed
python -c "import playwright" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[ERROR] Playwright is not installed"
    echo "Please run: pip install playwright"
    echo "Then run: playwright install chromium"
    exit 1
fi

echo "[INFO] Starting agent creation and chat test..."
echo ""

# Check if frontend is running
echo "[INFO] Checking if frontend is running on http://localhost:3000..."
curl -s http://localhost:3000 > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[WARNING] Frontend does not appear to be running on http://localhost:3000"
    echo "Please start the frontend with: cd frontend && npm run dev"
    echo ""
    read -p "Do you want to continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        exit 1
    fi
fi

# Check if backend is running
echo "[INFO] Checking if backend is running on http://localhost:8000..."
curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[WARNING] Backend does not appear to be running on http://localhost:8000"
    echo "Please start the backend with: cd api_server && python main.py"
    echo ""
    read -p "Do you want to continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        exit 1
    fi
fi

echo ""
echo "[INFO] Running E2E test..."
echo ""

# Run the test
python e2e/agent_creation_chat_test.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Test failed with error code $?"
    exit 1
else
    echo ""
    echo "[SUCCESS] Test completed successfully"
    echo "Check e2e_screenshots directory for screenshots"
    echo "Check e2e_test_results.json for detailed results"
    exit 0
fi