#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS - 快速集成测试
用于验证系统基本功能的快速测试脚本
"""

import sys
import os
import time
import requests
from datetime import datetime

# 设置Windows控制台编码
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

class QuickIntegrationTest:
    """快速集成测试"""

    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.frontend_base = "http://localhost:3000"
        self.passed = 0
        self.failed = 0
        self.tests = []

    def log(self, message: str, level: str = "INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")

    def test(self, name: str, func):
        """执行测试"""
        start_time = time.time()
        try:
            result = func()
            duration = time.time() - start_time

            if result:
                self.passed += 1
                self.tests.append({"name": name, "status": "PASS", "duration": duration})
                self.log(f"[PASS] {name}", "PASS")
            else:
                self.failed += 1
                self.tests.append({"name": name, "status": "FAIL", "duration": duration})
                self.log(f"[FAIL] {name}", "FAIL")
        except Exception as e:
            self.failed += 1
            self.tests.append({"name": name, "status": "ERROR", "error": str(e)})
            self.log(f"✗ {name} - {str(e)}", "ERROR")

    def check_service(self, url: str) -> bool:
        """检查服务可用性"""
        try:
            response = requests.get(url, timeout=5)
            return response.ok or response.status_code < 500
        except:
            return False

    def check_api(self, endpoint: str) -> bool:
        """检查API端点"""
        try:
            response = requests.get(f"{self.api_base}{endpoint}", timeout=5)
            return response.ok
        except:
            return False

    def run_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("AgentScope PaaS - 快速集成测试")
        print("=" * 60)
        print()

        # 服务可用性测试
        self.test("API服务可用性", lambda: self.check_service(self.api_base))
        self.test("前端服务可用性", lambda: self.check_service(self.frontend_base))

        # 核心API测试
        self.test("健康检查API", lambda: self.check_api("/api/v1/health"))
        self.test("模板列表API", lambda: self.check_api("/api/v1/templates"))
        self.test("智能体列表API", lambda: self.check_api("/api/v1/agents"))
        self.test("工具类别API", lambda: self.check_api("/api/v1/tools/categories"))

        # 系统状态检查
        def check_system_health():
            try:
                response = requests.get(f"{self.api_base}/api/v1/health", timeout=5)
                if response.ok:
                    data = response.json()
                    return data.get("data", {}).get("status") == "healthy"
                return False
            except:
                return False

        self.test("系统健康状态", check_system_health)

        # API响应时间测试
        def check_response_time():
            try:
                start = time.time()
                response = requests.get(f"{self.api_base}/api/v1/health", timeout=5)
                duration = time.time() - start
                return response.ok and duration < 2.0
            except:
                return False

        self.test("API响应时间 (<2s)", check_response_time)

        # 输出结果
        print()
        print("=" * 60)
        print("测试结果")
        print("=" * 60)

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"总测试数: {total}")
        print(f"通过: {self.passed} [PASS]")
        print(f"失败: {self.failed} [FAIL]")
        print(f"通过率: {pass_rate:.1f}%")
        print()

        if pass_rate == 100:
            print("[SUCCESS] 完美！所有测试通过！")
        elif pass_rate >= 80:
            print("[SUCCESS] 优秀！大部分测试通过！")
        elif pass_rate >= 60:
            print("[SUCCESS] 良好！主要功能正常！")
        else:
            print("[WARNING] 需要检查系统状态")

        print("=" * 60)

        return pass_rate >= 60

def main():
    """主函数"""
    tester = QuickIntegrationTest()

    try:
        success = tester.run_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n\n测试执行异常: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())