#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS Platform - 综合的 Playwright 端到端测试
包含前端诊断、后端测试和完整的功能测试
"""

import asyncio
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin

# 尝试导入playwright
try:
    from playwright.sync_api import sync_playwright, Page, Browser, expect
except ImportError:
    print("[ERROR] Playwright not installed, please run: pip install playwright")
    print("Then run: playwright install chromium")
    sys.exit(1)


class ComprehensivePlaywrightTest:
    def __init__(self, frontend_url="http://localhost:3000", backend_url="http://localhost:8000"):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.test_results = []
        self.screenshots_dir = Path("e2e_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.diagnostics = {}

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

    def test_backend_health(self):
        """测试后端健康状态"""
        try:
            import urllib.request
            response = urllib.request.urlopen(f"{self.backend_url}/api/v1/health", timeout=3)
            data = json.loads(response.read().decode())
            passed = response.status == 200 and data.get("status") == "healthy"
            self.log_test("Backend Health Check", passed, f"Status: {response.status}, Data: {data}")
            return passed
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Exception: {str(e)}")
            return False

    def diagnose_frontend_issues(self, page):
        """诊断前端问题"""
        print("\n[DIAGNOSIS] Starting Frontend Diagnosis...")

        # 检查JavaScript错误
        js_errors = []
        def handle_console(msg):
            if msg.type == 'error':
                js_errors.append({
                    'text': msg.text,
                    'location': str(msg.location)
                })
                print(f"JS Error: {msg.text} at {msg.location}")

        page.on('console', handle_console)

        # 检查网络请求失败
        failed_requests = []
        def handle_response(response):
            if response.status >= 400:
                failed_requests.append({
                    'url': response.url,
                    'status': response.status,
                    'status_text': response.status_text
                })
                print(f"Failed Request: {response.status} - {response.url}")

        page.on('response', handle_response)

        # 检查DOM状态
        try:
            page.goto(self.frontend_url, wait_until='networkidle', timeout=10000)
            page.wait_for_timeout(3000)  # 等待JavaScript执行

            # 收集诊断信息
            self.diagnostics['js_errors'] = js_errors
            self.diagnostics['failed_requests'] = failed_requests

            # 检查React加载状态
            react_check = page.evaluate("""() => {
                return {
                    hasRoot: document.getElementById('root') !== null,
                    rootChildren: document.getElementById('root')?.children.length || 0,
                    bodyText: document.body?.innerText?.length || 0,
                    hasReact: typeof window.React !== 'undefined',
                    scripts: Array.from(document.querySelectorAll('script')).map(s => s.src).filter(Boolean),
                    styles: Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(s => s.href).filter(Boolean)
                };
            }""")

            self.diagnostics['react_check'] = react_check
            print(f"[DIAGNOSIS] React Check: {react_check}")

            # 检查Vite热更新状态
            vite_check = page.evaluate("""() => {
                return {
                    hasViteClient: Array.from(document.querySelectorAll('script')).some(s => s.src.includes('vite')),
                    viteConnected: typeof window.__vite_plugin_react_preamble_installed__ !== 'undefined'
                };
            }""")

            self.diagnostics['vite_check'] = vite_check
            print(f"[DIAGNOSIS] Vite Check: {vite_check}")

        except Exception as e:
            print(f"[DIAGNOSIS] Error during diagnosis: {str(e)}")
            self.diagnostics['diagnosis_error'] = str(e)

        return self.diagnostics

    def fix_frontend_issues(self):
        """尝试修复前端问题"""
        print("\n[FIX] Attempting to fix frontend issues...")

        fixes_applied = []

        # 检查是否需要重启开发服务器
        try:
            import requests
            response = requests.get(self.frontend_url, timeout=2)
            if response.status_code != 200:
                print("[FIX] Frontend server not responding properly")
                fixes_applied.append("frontend_restart_needed")
        except:
            print("[FIX] Frontend server not accessible")
            fixes_applied.append("frontend_server_down")

        # 检查依赖问题
        frontend_dir = Path(__file__).parent.parent / "frontend"
        node_modules = frontend_dir / "node_modules"

        if not node_modules.exists():
            print("[FIX] node_modules not found, npm install needed")
            fixes_applied.append("npm_install_needed")
        else:
            print("[FIX] node_modules exists")

        # 检查构建状态
        dist_dir = frontend_dir / "dist"
        if not dist_dir.exists():
            print("[FIX] No build found, development mode assumed")
            fixes_applied.append("dev_mode")

        return fixes_applied

    def run_comprehensive_tests(self):
        """运行综合测试"""
        print("Starting Comprehensive Playwright E2E Tests")
        print("=" * 60)

        # 1. 检查后端健康
        print("\n[PHASE 1]: Backend Health Check")
        backend_healthy = self.test_backend_health()

        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(
                headless=False,  # 显示浏览器窗口
                slow_mo=300     # 稍微放慢执行速度
            )

            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                record_video_dir=str(self.screenshots_dir / "videos") if (self.screenshots_dir / "videos").exists() else None
            )

            page = context.new_page()

            try:
                # 2. 前端诊断
                print("\n[PHASE 2]: Frontend Diagnosis")
                diagnostics = self.diagnose_frontend_issues(page)

                # 根据诊断结果决定是否尝试修复
                if diagnostics.get('react_check', {}).get('rootChildren', 0) == 0:
                    print("\n[PHASE 3]: Issue Fix Attempt")
                    fixes = self.fix_frontend_issues()

                # 3. 功能测试
                print("\n[PHASE 4]: Functional Testing")

                # 测试首页加载
                print("\n[TEST]: Homepage Functional Test")
                page.goto(self.frontend_url, wait_until='networkidle', timeout=15000)
                page.wait_for_timeout(2000)

                # 截图
                screenshot_path = self.screenshots_dir / f"homepage_functional_{int(time.time())}.png"
                page.screenshot(path=str(screenshot_path))

                # 检查是否有实际内容
                has_content = page.evaluate("""() => {
                    const root = document.getElementById('root');
                    if (!root) return false;
                    return root.innerText.trim().length > 0 || root.children.length > 0;
                }""")

                self.log_test("Homepage Has Content", has_content,
                            f"Content detected: {has_content}")

                # 测试用户注册流程（如果前端工作）
                if has_content:
                    print("\n[TEST]: User Registration Flow")
                    try:
                        page.goto(f"{self.frontend_url}/register", wait_until='networkidle')
                        page.wait_for_timeout(1000)

                        # 查找注册表单
                        form_exists = page.query_selector("form") is not None
                        self.log_test("Registration Form Present", form_exists)

                        if form_exists:
                            # 填写表单
                            email_input = page.query_selector("input[type='email']")
                            password_input = page.query_selector("input[type='password']")

                            if email_input and password_input:
                                test_email = f"test_{int(time.time())}@example.com"
                                email_input.fill(test_email)
                                password_input.fill("TestPassword123!")

                                # 截图填写的表单
                                screenshot_path = self.screenshots_dir / f"register_form_filled_{int(time.time())}.png"
                                page.screenshot(path=str(screenshot_path))

                                # 尝试提交（如果后端工作）
                                if backend_healthy:
                                    submit_button = page.query_selector("button[type='submit']")
                                    if submit_button:
                                        with page.expect_navigation(timeout=5000) as response_info:
                                            submit_button.click()

                                        response = response_info.value
                                        self.log_test("Registration Submit", response is not None,
                                                    f"Submit response received: {response is not None}")

                    except Exception as e:
                        self.log_test("User Registration Flow", False, f"Exception: {str(e)}")

                # 测试登录页面
                print("\n[TEST]: Login Page Test")
                page.goto(f"{self.frontend_url}/login", wait_until='networkidle')
                page.wait_for_timeout(1000)

                login_has_content = page.evaluate("""() => {
                    const body = document.body;
                    return body.innerText.trim().length > 0;
                }""")

                screenshot_path = self.screenshots_dir / f"login_page_{int(time.time())}.png"
                page.screenshot(path=str(screenshot_path))

                self.log_test("Login Page Has Content", login_has_content)

                # 测试响应式设计
                print("\n[TEST]: Responsive Design Test")
                page.set_viewport_size({'width': 375, 'height': 667})  # 移动设备尺寸
                page.goto(self.frontend_url, wait_until='networkidle')
                page.wait_for_timeout(1000)

                mobile_screenshot = self.screenshots_dir / f"homepage_mobile_{int(time.time())}.png"
                page.screenshot(path=str(mobile_screenshot))

                mobile_has_content = page.evaluate("""() => {
                    return document.getElementById('root')?.children.length > 0;
                }""")

                self.log_test("Mobile Responsive", mobile_has_content)

                # 恢复桌面尺寸
                page.set_viewport_size({'width': 1280, 'height': 720})

            finally:
                context.close()
                browser.close()

        # 生成详细报告
        self.generate_report()

        # 返回测试结果
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        return success_rate >= 70  # 70%以上的通过率视为成功

    def generate_report(self):
        """生成详细的测试报告"""
        report_path = self.screenshots_dir / f"test_report_{int(time.time())}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {
                "total": len(self.test_results),
                "passed": sum(1 for result in self.test_results if result["passed"]),
                "failed": sum(1 for result in self.test_results if not result["passed"])
            },
            "tests": self.test_results,
            "diagnostics": self.diagnostics
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n[REPORT] Detailed report saved to: {report_path}")

        # 保存诊断信息
        if self.diagnostics:
            diagnostics_path = self.screenshots_dir / f"diagnostics_{int(time.time())}.json"
            with open(diagnostics_path, 'w', encoding='utf-8') as f:
                json.dump(self.diagnostics, f, indent=2, ensure_ascii=False)
            print(f"[DIAGNOSTICS] Saved to: {diagnostics_path}")

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("Comprehensive Playwright Test Summary")
        print("=" * 60)

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

        print("=" * 60)
        return success_rate >= 70


def main():
    """主函数"""
    print("AgentScope PaaS - Comprehensive Playwright E2E Test")
    print("This test includes frontend diagnosis and functional testing")
    print()

    tester = ComprehensivePlaywrightTest()

    try:
        success = tester.run_comprehensive_tests()
        tester.print_summary()

        print(f"\n[Screenshots] All screenshots saved to: {tester.screenshots_dir.absolute()}")
        print("\nTo improve frontend issues:")
        print("1. Check browser console for JavaScript errors")
        print("2. Verify React components are rendering correctly")
        print("3. Check network requests in browser DevTools")
        print("4. Review the diagnostics JSON files for detailed information")

        return 0 if success else 1

    except Exception as e:
        print(f"[ERROR] Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())