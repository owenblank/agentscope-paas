#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS Platform - Playwright Frontend E2E Test
使用Playwright进行浏览器端测试，诊断前端空白页问题
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# 尝试导入playwright
try:
    from playwright.sync_api import sync_playwright, Page, Browser
except ImportError:
    print("[ERROR] Playwright not installed, please run: pip install playwright")
    print("Then run: playwright install chromium")
    sys.exit(1)


class PlaywrightFrontendTest:
    def __init__(self, frontend_url="http://localhost:3000", backend_url="http://localhost:8000"):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.test_results = []
        self.screenshots_dir = Path("e2e_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)

    def log_test(self, test_name, passed, details=""):
        """记录测试结果"""
        status = "[PASS]" if passed else "[FAIL]"
        result = {
            "name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")

    def test_backend_connection(self):
        """测试后端连接"""
        try:
            import urllib.request
            response = urllib.request.urlopen(f"{self.backend_url}/api/v1/health", timeout=3)
            passed = response.status == 200
            self.log_test("Backend Connection", passed, f"Status: {response.status}")
            return passed
        except Exception as e:
            self.log_test("Backend Connection", False, f"Exception: {str(e)}")
            return False

    def run_tests(self):
        """运行所有浏览器测试"""
        print("Starting Playwright Frontend E2E Tests")
        print("=" * 50)

        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(
                headless=False,  # 显示浏览器窗口以便观察
                slow_mo=1000  # 慢速执行以便观察
            )

            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            # 启用控制台日志收集
            console_messages = []
            page = context.new_page()

            def handle_console(msg):
                console_messages.append({
                    'type': msg.type,
                    'text': msg.text,
                    'location': msg.location
                })
                print(f"Console [{msg.type}]: {msg.text}")

            page.on('console', handle_console)

            # 监听网络请求
            network_requests = []
            def handle_request(request):
                network_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'resource_type': request.resource_type
                })

            def handle_response(response):
                if response.status >= 400:
                    print(f"HTTP Error: {response.status} - {response.url}")

            page.on('request', handle_request)
            page.on('response', handle_response)

            try:
                # 测试1: 访问首页
                print("\n[Test 1]: Homepage Access")
                try:
                    start_time = time.time()
                    response = page.goto(self.frontend_url, wait_until='networkidle', timeout=10000)
                    load_time = time.time() - start_time

                    # 截图
                    screenshot_path = self.screenshots_dir / f"homepage_{int(time.time())}.png"
                    page.screenshot(path=str(screenshot_path))

                    # 检查响应状态
                    status_ok = response.status == 200
                    self.log_test("Homepage Access", status_ok, f"Status: {response.status}, Load time: {load_time:.2f}s")

                    # 等待一段时间检查页面内容
                    page.wait_for_timeout(2000)

                    # 检查页面内容
                    title = page.title()
                    print(f"Page Title: {title}")

                    # 检查是否有React应用
                    has_root = page.query_selector("#root") is not None
                    self.log_test("React Root Element", has_root, f"#root element found: {has_root}")

                    # 检查页面内容是否为空
                    body_text = page.evaluate("() => document.body.innerText")
                    is_empty = len(body_text.strip()) == 0 or body_text.strip() == "AgentScope PaaS - 智能体开发平台"
                    self.log_test("Page Content", not is_empty, f"Body text length: {len(body_text)}, Empty: {is_empty}")

                    # 检查控制台错误
                    errors = [msg for msg in console_messages if msg['type'] == 'error']
                    has_errors = len(errors) == 0
                    self.log_test("Console Errors", has_errors, f"Error count: {len(errors)}")

                    if errors:
                        print("[ERROR] Console Errors Found:")
                        for error in errors[:5]:  # 显示前5个错误
                            print(f"   - {error['text']}")

                except Exception as e:
                    self.log_test("Homepage Access", False, f"Exception: {str(e)}")
                    print(f"[ERROR] Navigation failed: {str(e)}")

                # 测试2: 尝试访问登录页面
                print("\n[Test 2]: Login Page Access")
                try:
                    login_response = page.goto(f"{self.frontend_url}/login", wait_until='networkidle', timeout=10000)
                    login_status = login_response.status == 200

                    # 截图
                    screenshot_path = self.screenshots_dir / f"login_page_{int(time.time())}.png"
                    page.screenshot(path=str(screenshot_path))

                    self.log_test("Login Page Access", login_status, f"Status: {login_response.status}")

                    # 等待页面加载
                    page.wait_for_timeout(2000)

                    # 检查是否有登录表单
                    login_form = page.query_selector("form") is not None
                    self.log_test("Login Form Present", login_form, f"Login form found: {login_form}")

                    # 检查输入框
                    email_input = page.query_selector("input[type='email']") is not None
                    password_input = page.query_selector("input[type='password']") is not None
                    self.log_test("Login Input Fields", email_input and password_input,
                                f"Email input: {email_input}, Password input: {password_input}")

                except Exception as e:
                    self.log_test("Login Page Access", False, f"Exception: {str(e)}")

                # 测试3: 检查API请求
                print("\n[Test 3]: API Requests Check")
                api_requests = [req for req in network_requests if '/api/' in req['url']]
                self.log_test("API Requests Made", len(api_requests) > 0, f"API request count: {len(api_requests)}")

                if api_requests:
                    print("[API] Requests Found:")
                    for req in api_requests[:5]:  # 显示前5个API请求
                        print(f"   - {req['method']} {req['url']}")

                # 测试4: 检查JavaScript状态
                print("\n[Test 4]: JavaScript State Check")
                try:
                    js_enabled = page.evaluate("() => typeof window !== 'undefined'")
                    react_loaded = page.evaluate("() => typeof window.React !== 'undefined'") or \
                                  page.evaluate("() => document.querySelector('[data-reactroot]') !== null")

                    self.log_test("JavaScript Enabled", js_enabled, f"JavaScript working: {js_enabled}")
                    self.log_test("React Loaded", react_loaded, f"React detected: {react_loaded}")

                except Exception as e:
                    self.log_test("JavaScript State", False, f"Exception: {str(e)}")

                # 测试5: 检查路由配置
                print("\n[Test 5]: Frontend Routes Test")
                test_routes = ['/register', '/dashboard', '/agents']
                for route in test_routes:
                    try:
                        route_response = page.goto(f"{self.frontend_url}{route}", wait_until='domcontentloaded', timeout=5000)
                        route_ok = route_response.status in [200, 301, 302]  # 允许重定向
                        self.log_test(f"Route {route}", route_ok, f"Status: {route_response.status}")

                        # 截图
                        screenshot_path = self.screenshots_dir / f"route_{route.replace('/', '_')}_{int(time.time())}.png"
                        page.screenshot(path=str(screenshot_path))

                    except Exception as e:
                        self.log_test(f"Route {route}", False, f"Exception: {str(e)}")

                # 测试6: 检查开发服务器状态
                print("\n[Test 6]: Dev Server Features")
                try:
                    # 检查Vite客户端脚本
                    vite_script = page.query_selector("script[src*='/@vite/client']") is not None
                    self.log_test("Vite Dev Server", vite_script, f"Vite client script found: {vite_script}")

                    # 检查热更新连接
                    hmr_working = page.evaluate("""() => {
                        return typeof window.__vite_plugin_react_preamble_installed__ !== 'undefined' ||
                               document.querySelector('[data-vite-dev-id]') !== null
                    }""")
                    self.log_test("Hot Module Reload", hmr_working, f"HMR detected: {hmr_working}")

                except Exception as e:
                    self.log_test("Dev Server Features", False, f"Exception: {str(e)}")

            finally:
                # 关闭浏览器
                context.close()
                browser.close()

        # 打印测试总结
        self.print_summary()
        print(f"\n[Screenshots] Saved to: {self.screenshots_dir}")

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 50)
        print("Playwright Test Summary")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")

        if failed_tests > 0:
            print("\n[X] Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['name']}: {result['details']}")

        print("=" * 50)

        return failed_tests == 0


def main():
    """主函数"""
    tester = PlaywrightFrontendTest()

    # 首先检查后端连接
    if not tester.test_backend_connection():
        print("[WARNING] Backend service not available, some tests may fail")

    # 运行浏览器测试
    success = tester.run_tests()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())