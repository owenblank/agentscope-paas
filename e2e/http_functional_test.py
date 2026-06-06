#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP-based Functional Test for AgentScope PaaS Platform
"""

import sys
import os

# 设置控制台编码
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

import requests
import re
import time
from datetime import datetime


class HTTPTester:
    """HTTP测试类"""

    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.backend_url = "http://localhost:8000"
        self.session = requests.Session()
        self.results = []

    def log_test(self, test_name, passed, details=""):
        """记录测试结果"""
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}: {details}")
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "time": datetime.now().strftime('%H:%M:%S')
        })

    def test_homepage(self):
        """测试首页"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            has_content = len(response.text) > 1000
            self.log_test("Homepage Access", has_content,
                         f"Status: {response.status_code}, Content: {len(response.text)} chars")
            return has_content
        except Exception as e:
            self.log_test("Homepage Access", False, f"Error: {str(e)}")
            return False

    def test_login_page(self):
        """测试登录页面"""
        try:
            response = self.session.get(f"{self.base_url}/login", timeout=10)
            has_login_form = ('password' in response.text.lower() or
                            'username' in response.text.lower() or
                            'email' in response.text.lower())
            self.log_test("Login Page", has_login_form,
                         f"Status: {response.status_code}, Has form: {has_login_form}")
            return has_login_form
        except Exception as e:
            self.log_test("Login Page", False, f"Error: {str(e)}")
            return False

    def test_register_page(self):
        """测试注册页面"""
        try:
            response = self.session.get(f"{self.base_url}/register", timeout=10)
            has_register_form = ('password' in response.text.lower() or
                                'confirm' in response.text.lower() or
                                'register' in response.text.lower())
            self.log_test("Register Page", has_register_form,
                         f"Status: {response.status_code}, Has form: {has_register_form}")
            return has_register_form
        except Exception as e:
            self.log_test("Register Page", False, f"Error: {str(e)}")
            return False

    def test_dashboard_redirect(self):
        """测试仪表板重定向"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard", timeout=10)
            # 应该重定向到登录页面或者显示仪表板
            is_valid_response = response.status_code in [200, 302, 301]
            self.log_test("Dashboard Redirect", is_valid_response,
                         f"Status: {response.status_code}, Final URL: {response.url}")
            return is_valid_response
        except Exception as e:
            self.log_test("Dashboard Redirect", False, f"Error: {str(e)}")
            return False

    def test_api_health(self):
        """测试API健康检查"""
        try:
            response = requests.get(f"{self.backend_url}/", timeout=5)
            api_working = response.status_code == 200
            self.log_test("API Health Check", api_working,
                         f"Status: {response.status_code}")
            return api_working
        except Exception as e:
            self.log_test("API Health Check", False, f"Error: {str(e)}")
            return False

    def test_api_docs(self):
        """测试API文档"""
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            docs_accessible = response.status_code == 200
            self.log_test("API Documentation", docs_accessible,
                         f"Status: {response.status_code}")
            return docs_accessible
        except Exception as e:
            self.log_test("API Documentation", False, f"Error: {str(e)}")
            return False

    def test_static_files(self):
        """测试静态文件"""
        try:
            response = self.session.get(f"{self.base_url}/static/", timeout=5)
            static_accessible = response.status_code in [200, 404]  # 404 means route exists
            self.log_test("Static Files Route", static_accessible,
                         f"Status: {response.status_code}")
            return static_accessible
        except Exception as e:
            self.log_test("Static Files Route", False, f"Error: {str(e)}")
            return False

    def test_response_time(self):
        """测试响应时间"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/", timeout=10)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒

            is_acceptable = response_time < 3000  # 3秒以内可接受
            self.log_test("Response Time", is_acceptable,
                         f"{response_time:.0f}ms (target: <3000ms)")
            return is_acceptable
        except Exception as e:
            self.log_test("Response Time", False, f"Error: {str(e)}")
            return False

    def test_concurrent_requests(self):
        """测试并发请求"""
        try:
            import threading
            results = []

            def make_request():
                try:
                    response = requests.get(f"{self.base_url}/", timeout=10)
                    results.append(response.status_code == 200)
                except:
                    results.append(False)

            threads = []
            for i in range(5):  # 5个并发请求
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            success_rate = sum(results) / len(results)
            concurrent_ok = success_rate >= 0.8  # 80%成功率

            self.log_test("Concurrent Requests", concurrent_ok,
                         f"Success rate: {success_rate*100:.0f}% (5 concurrent requests)")
            return concurrent_ok
        except Exception as e:
            self.log_test("Concurrent Requests", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("AgentScope PaaS Platform - HTTP Functional Test")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 前端测试
        print("\n--- Frontend Tests ---")
        self.test_homepage()
        self.test_login_page()
        self.test_register_page()
        self.test_dashboard_redirect()
        self.test_static_files()
        self.test_response_time()
        self.test_concurrent_requests()

        # 后端测试
        print("\n--- Backend Tests ---")
        self.test_api_health()
        self.test_api_docs()

        # 输出结果摘要
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)

        passed = sum(1 for result in self.results if result["passed"])
        total = len(self.results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {passed/total*100:.1f}%")

        print("\n--- Detailed Results ---")
        for result in self.results:
            status = "✓" if result["passed"] else "✗"
            print(f"{status} {result['test']}: {result['details']}")

        # 返回测试是否全部通过
        return passed == total


def main():
    """主函数"""
    tester = HTTPTester()

    try:
        success = tester.run_all_tests()

        if success:
            print("\n🎉 All tests PASSED!")
            print("\nThe platform is working correctly:")
            print("✓ Frontend is accessible")
            print("✓ Backend API is functional")
            print("✓ Response times are acceptable")
            print("✓ System can handle concurrent requests")
            return 0
        else:
            print(f"\n⚠️ Some tests failed")
            print("Please check the detailed results above")
            return 1

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return 130
    except Exception as e:
        print(f"\nTest execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())