#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS Platform - API End-to-End Test
真正的API功能测试，发现系统bug
"""

import requests
import json
import time
import sys
from datetime import datetime

class APIE2ETest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.test_user = {
            "email": f"test_user_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "username": f"testuser_{int(time.time())}"
        }

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

    def test_health_check(self):
        """测试健康检查端点"""
        try:
            response = self.session.get(f"{self.api_base}/health")
            passed = response.status_code == 200
            self.log_test(
                "Health Check API",
                passed,
                f"Status: {response.status_code}, Response: {response.json() if passed else response.text}"
            )
            return passed
        except Exception as e:
            self.log_test("Health Check API", False, f"Exception: {str(e)}")
            return False

    def test_api_docs(self):
        """测试API文档端点"""
        try:
            response = self.session.get(f"{self.api_base}/docs")
            passed = response.status_code == 200
            self.log_test(
                "API Documentation",
                passed,
                f"Status: {response.status_code}"
            )
            return passed
        except Exception as e:
            self.log_test("API Documentation", False, f"Exception: {str(e)}")
            return False

    def test_register_user(self):
        """测试用户注册"""
        try:
            payload = {
                "email": self.test_user["email"],
                "password": self.test_user["password"],
                "username": self.test_user["username"]
            }
            response = self.session.post(
                f"{self.api_base}/auth/register",
                json=payload
            )
            passed = response.status_code in [200, 201]
            data = response.json() if passed else {}
            self.log_test(
                "User Registration",
                passed,
                f"Status: {response.status_code}, Email: {self.test_user['email']}"
            )
            return passed
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False

    def test_login_user(self):
        """测试用户登录"""
        try:
            payload = {
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
            response = self.session.post(
                f"{self.api_base}/auth/login",
                json=payload
            )
            passed = response.status_code == 200
            if passed:
                data = response.json()
                if "data" in data and "access_token" in data["data"]:
                    self.auth_token = data["data"]["access_token"]
                    # Use X-API-Key header since the API uses API key authentication
                    self.session.headers.update({
                        "X-API-Key": self.auth_token
                    })
                    self.log_test(
                        "User Login",
                        True,
                        f"Token received: {self.auth_token[:20]}..."
                    )
                    return True
                else:
                    self.log_test("User Login", False, f"No token in response: {data}")
                    return False
            else:
                self.log_test(
                    "User Login",
                    False,
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return False

    def test_create_agent_config(self):
        """测试创建智能体配置"""
        if not self.auth_token:
            self.log_test("Agent Config Creation", False, "No auth token available")
            return False

        try:
            agent_request = {
                "config": {
                    "agent_metadata": {
                        "agent_id": f"test_agent_{int(time.time())}",
                        "agent_name": "Test Agent",
                        "agent_type": "conversation",
                        "description": "Test agent for E2E testing",
                        "version": "1.0.0"
                    },
                    "llm_config": {  # Changed from model_config to llm_config
                        "model_name": "gpt-3.5-turbo",
                        "api_key": "test_key",
                        "base_url": "https://api.openai.com/v1"
                    },
                    "prompt_config": {
                        "system_prompt": "You are a helpful assistant for testing."
                    }
                }
            }

            response = self.session.post(
                f"{self.api_base}/agents",
                json=agent_request  # Changed from agent_config to agent_request
            )
            passed = response.status_code in [200, 201]
            data = response.json() if passed else {}
            self.log_test(
                "Agent Config Creation",
                passed,
                f"Status: {response.status_code}, Agent ID: {data.get('data', {}).get('agent_id', 'N/A')}"
            )
            return passed
        except Exception as e:
            self.log_test("Agent Config Creation", False, f"Exception: {str(e)}")
            return False

    def test_get_agents_list(self):
        """测试获取智能体列表"""
        if not self.auth_token:
            self.log_test("Get Agents List", False, "No auth token available")
            return False

        try:
            response = self.session.get(f"{self.api_base}/agents")
            passed = response.status_code == 200
            data = response.json() if passed else {}
            agent_count = len(data.get("data", []))
            self.log_test(
                "Get Agents List",
                passed,
                f"Status: {response.status_code}, Agents count: {agent_count}"
            )
            return passed
        except Exception as e:
            self.log_test("Get Agents List", False, f"Exception: {str(e)}")
            return False

    def test_validate_agent_config(self):
        """测试配置验证"""
        try:
            invalid_request = {
                "config": {
                    "agent_metadata": {
                        "name": "Invalid Agent"
                    }
                    # Missing required fields like agent_id, agent_name, agent_type
                }
            }

            response = self.session.post(
                f"{self.api_base}/config/validate",
                json=invalid_request
            )
            # API returns 200 but response should indicate validation failure
            passed = response.status_code == 200
            if passed:
                data = response.json()
                # Check if validation correctly identified invalid config
                is_valid = data.get("data", {}).get("valid", True)
                passed = not is_valid  # Config should be marked as invalid
                errors = data.get("data", {}).get("errors", [])
                has_errors = len(errors) > 0

            self.log_test(
                "Agent Config Validation",
                passed and has_errors,
                f"Status: {response.status_code}, Valid: {is_valid}, Errors: {len(errors) if has_errors else 0}"
            )
            return passed and has_errors
        except Exception as e:
            self.log_test("Agent Config Validation", False, f"Exception: {str(e)}")
            return False

    def test_unauthorized_access(self):
        """测试未授权访问"""
        try:
            # 创建一个没有token的session
            unauthorized_session = requests.Session()
            response = unauthorized_session.get(f"{self.api_base}/agents")
            # Should return 401 Unauthorized or 403 Forbidden
            passed = response.status_code in [401, 403]
            self.log_test(
                "Unauthorized Access Protection",
                passed,
                f"Status: {response.status_code} (should be 401/403)"
            )
            return passed
        except Exception as e:
            self.log_test("Unauthorized Access Protection", False, f"Exception: {str(e)}")
            return False

    def test_context_compression_config(self):
        """测试上下文压缩配置"""
        if not self.auth_token:
            self.log_test("Context Compression Config", False, "No auth token available")
            return False

        try:
            agent_request = {
                "config": {
                    "agent_metadata": {
                        "agent_id": f"compression_agent_{int(time.time())}",
                        "agent_name": "Compression Test Agent",
                        "agent_type": "conversation",
                        "description": "Test agent with context compression"
                    },
                    "llm_config": {  # Changed from model_config to llm_config
                        "model_name": "gpt-3.5-turbo",
                        "api_key": "test_key"
                    },
                    "prompt_config": {
                        "system_prompt": "You are a helpful assistant."
                    },
                    "context_compression_config": {
                        "enabled": True,
                        "max_tokens": 4000,
                        "compression_threshold": 2,
                        "compression_method": "summary"
                    }
                }
            }

            response = self.session.post(
                f"{self.api_base}/agents",
                json=agent_request  # Fixed request format
            )
            passed = response.status_code in [200, 201]
            self.log_test(
                "Context Compression Config",
                passed,
                f"Status: {response.status_code}"
            )
            return passed
        except Exception as e:
            self.log_test("Context Compression Config", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("Starting AgentScope PaaS API E2E Tests")
        print("=" * 50)

        # 基础健康检查
        self.test_health_check()
        self.test_api_docs()

        # 认证流程测试
        self.test_register_user()
        self.test_login_user()

        # 智能体配置测试
        self.test_create_agent_config()
        self.test_get_agents_list()
        self.test_validate_agent_config()

        # 高级功能测试
        self.test_context_compression_config()

        # 安全性测试
        self.test_unauthorized_access()

        # 打印测试总结
        self.print_summary()

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 50)
        print("Test Summary")
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

if __name__ == "__main__":
    tester = APIE2ETest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)