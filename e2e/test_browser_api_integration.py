#!/usr/bin/env python3
"""
Test Frontend API Integration from Browser Perspective
"""
import sys
import json
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("[ERROR] Playwright not installed")
    sys.exit(1)


def test_frontend_api_integration():
    """Test frontend API integration"""
    print("=" * 60)
    print("Frontend API Integration Test")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            ignore_https_errors=True
        )

        # Enable network monitoring
        network_logs = []
        def handle_request(request):
            network_logs.append({
                'url': request.url,
                'method': request.method,
                'type': request.resource_type
            })

        def handle_response(response):
            for log in network_logs:
                if log['url'] == response.url:
                    log['status'] = response.status
                    log['ok'] = response.ok
                    break
            if response.status >= 400:
                print(f"[NETWORK ERROR] {response.status} - {response.url}")

        page = context.new_page()
        page.on('request', handle_request)
        page.on('response', handle_response)

        # Monitor console
        console_logs = []
        def handle_console(msg):
            if msg.type == 'error':
                console_logs.append(msg.text)
                print(f"[CONSOLE ERROR] {msg.text}")

        page.on('console', handle_console)

        try:
            # Test 1: Navigate to registration page
            print("\n[Test 1]: Navigate to Registration Page")
            page.goto("http://localhost:3000/register", wait_until='networkidle')
            page.wait_for_timeout(3000)

            # Check network logs
            api_requests = [log for log in network_logs if '/api/' in log.get('url', '')]
            print(f"API Requests: {len(api_requests)}")

            # Test 2: Fill registration form
            print("\n[Test 2]: Fill Registration Form")
            timestamp = int(time.time())
            test_user = {
                "username": f"browser_test_{timestamp}",
                "email": f"browser_test_{timestamp}@example.com",
                "password": "TestPassword123!"
            }

            # Fill form fields
            username_input = page.query_selector("input[name='username']")
            email_input = page.query_selector("input[name='email']")
            password_input = page.query_selector("input[name='password']")
            confirm_input = page.query_selector("input[name='confirmPassword']")

            if username_input:
                username_input.fill(test_user["username"])
                print(f"Filled username: {test_user['username']}")

            if email_input:
                email_input.fill(test_user["email"])
                print(f"Filled email: {test_user['email']}")

            if password_input:
                password_input.fill(test_user["password"])
                print("Filled password")

            if confirm_input:
                confirm_input.fill(test_user["password"])
                print("Filled confirm password")

            # Clear network logs
            network_logs.clear()

            # Test 3: Submit form
            print("\n[Test 3]: Submit Registration Form")
            submit_button = page.query_selector("button[type='submit']")

            if submit_button:
                submit_button.click()
                print("Submit button clicked")

                # Wait for API response
                page.wait_for_timeout(5000)

                # Check API call
                api_calls = [log for log in network_logs if '/api/' in log.get('url', '')]
                print(f"API Calls Made: {len(api_calls)}")

                for call in api_calls:
                    print(f"  - {call['method']} {call['url']} -> Status: {call.get('status', 'N/A')}")

                # Check current URL
                current_url = page.url
                print(f"Current URL: {current_url}")

                # Check for success message
                success_message = page.query_selector(".ant-message-success, .ant-message-notice-success")
                if success_message:
                    print("Success message found")

            # Test 4: Try login with created user
            print("\n[Test 4]: Navigate to Login Page")
            page.goto("http://localhost:3000/login", wait_until='networkidle')
            page.wait_for_timeout(2000)

            network_logs.clear()

            # Fill login form
            login_email = page.query_selector("input[type='email'], input[name*='email']")
            login_password = page.query_selector("input[type='password']")

            if login_email:
                login_email.fill(test_user["email"])
                print(f"Filled email: {test_user['email']}")

            if login_password:
                login_password.fill(test_user["password"])
                print("Filled password")

            # Submit login
            print("\n[Test 5]: Submit Login Form")
            login_button = page.query_selector("button[type='submit']")

            if login_button:
                network_logs.clear()
                login_button.click()
                print("Login button clicked")

                # Wait for API response
                page.wait_for_timeout(5000)

                # Check API call
                login_api_calls = [log for log in network_logs if '/api/' in log.get('url', '')]
                print(f"Login API Calls: {len(login_api_calls)}")

                for call in login_api_calls:
                    print(f"  - {call['method']} {call['url']} -> Status: {call.get('status', 'N/A')}")

                # Check navigation
                current_url = page.url
                print(f"Current URL after login: {current_url}")

                success = "/dashboard" in current_url or "/agents" in current_url
                print(f"Login Success: {success}")

            # Take final screenshot
            screenshot_path = Path("e2e_screenshots/api_test_final.png")
            page.screenshot(path=str(screenshot_path))
            print(f"\n[Screenshot] Saved to: {screenshot_path}")

            # Summary
            print("\n" + "=" * 60)
            print("API Integration Test Summary")
            print("=" * 60)
            print(f"Console Errors: {len(console_logs)}")
            print(f"Network Requests: {len([log for log in network_logs if '/api/' in log.get('url', '')])}")

            if console_logs:
                print("\nConsole Errors Found:")
                for error in console_logs[:5]:
                    print(f"  - {error}")

        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    try:
        test_frontend_api_integration()
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)