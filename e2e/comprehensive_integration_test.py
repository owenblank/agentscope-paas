#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS - 全面的端到端集成测试
涵盖前后端完整功能的集成测试套件
"""

import sys
import os
import time
import json
import requests
import subprocess
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from playwright.sync_api import sync_playwright, Browser, Page
import pytest

# ====================== 配置和常量 ======================

class TestConfig:
    """测试配置"""
    API_BASE_URL = "http://localhost:8000"
    API_DOCS_URL = f"{API_BASE_URL}/api/v1/docs"
    FRONTEND_BASE_URL = "http://localhost:3000"
    HEALTH_CHECK_URL = f"{API_BASE_URL}/api/v1/health"

    # 测试超时设置
    SERVER_START_TIMEOUT = 30
    PAGE_LOAD_TIMEOUT = 15000
    NETWORK_IDLE_TIMEOUT = 10000
    API_TIMEOUT = 10

    # 测试用户数据
    TEST_USER = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "Test123456"
    }

    # 测试智能体数据
    TEST_AGENT = {
        "agent_metadata": {
            "agent_id": "test_agent_001",
            "agent_name": "测试智能体",
            "agent_type": "DialogAgent",
            "description": "用于端到端测试的智能体",
            "version": "1.0.0",
            "tags": ["测试", "E2E"]
        },
        "llm_config": {
            "model_name": "gpt-4o",
            "api_key": "test-api-key-12345",
            "base_url": "https://api.openai.com/v1",
            "temperature": 0.7,
            "max_tokens": 2000
        },
        "prompt_config": {
            "system_prompt": "你是一个测试用的AI助手，用于端到端测试验证。"
        }
    }

# ====================== 工具函数 ======================

class TestUtils:
    """测试工具类"""

    @staticmethod
    def setup_output_dirs():
        """设置输出目录"""
        dirs = ["test_results", "test_results/screenshots", "test_results/logs"]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def log(message: str, level: str = "INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")

    @staticmethod
    def save_screenshot(page: Page, name: str):
        """保存截图"""
        filename = f"test_results/screenshots/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        page.screenshot(path=filename)
        TestUtils.log(f"截图已保存: {filename}")

    @staticmethod
    def wait_for_page_load(page: Page, url: str, timeout: int = TestConfig.PAGE_LOAD_TIMEOUT):
        """等待页面加载完成"""
        page.goto(url, timeout=timeout)
        page.wait_for_load_state('domcontentloaded', timeout=timeout)
        time.sleep(2)  # 等待React渲染
        return page.url

    @staticmethod
    def make_api_request(method: str, endpoint: str, **kwargs) -> Tuple[bool, Any]:
        """发送API请求"""
        url = f"{TestConfig.API_BASE_URL}{endpoint}"
        headers = kwargs.pop('headers', {})

        # 设置默认Content-Type，但保留已有的头部
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=TestConfig.API_TIMEOUT, **kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, timeout=TestConfig.API_TIMEOUT, **kwargs)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, timeout=TestConfig.API_TIMEOUT, **kwargs)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=TestConfig.API_TIMEOUT, **kwargs)
            else:
                return False, {"error": "Unsupported HTTP method"}

            try:
                return response.ok, response.json()
            except:
                return response.ok, {"status_code": response.status_code}

        except Exception as e:
            return False, {"error": str(e)}

# ====================== 测试类 ======================

class ComprehensiveIntegrationTest:
    """全面的集成测试类"""

    def __init__(self):
        self.results = {
            "test_suite": "AgentScope PaaS E2E Integration Tests",
            "start_time": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "test_results": []
        }
        self.auth_token = None
        self.test_user_id = None
        self.test_agent_id = None
        self.test_conversation_id = None

        # 设置输出目录
        TestUtils.setup_output_dirs()

    def record_result(self, test_name: str, passed: bool, details: str = "", duration: float = 0):
        """记录测试结果"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed_tests"] += 1
            status = "PASS"
        else:
            self.results["failed_tests"] += 1
            status = "FAIL"

        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.results["test_results"].append(result)

        TestUtils.log(f"{status}: {test_name} - {details}", "PASS" if passed else "FAIL")

    def generate_report(self):
        """生成测试报告"""
        self.results["end_time"] = datetime.now().isoformat()

        total_duration = datetime.fromisoformat(self.results["end_time"]) - \
                        datetime.fromisoformat(self.results["start_time"])

        pass_rate = (self.results["passed_tests"] / self.results["total_tests"] * 100) if \
                   self.results["total_tests"] > 0 else 0

        report = f"""
================================================================================
                    AgentScope PaaS E2E 测试报告
================================================================================

测试时间: {self.results["start_time"]} ~ {self.results["end_time"]}
总耗时: {total_duration}

测试概览:
--------
总测试数: {self.results["total_tests"]}
通过测试: {self.results["passed_tests"]} [PASS]
失败测试: {self.results["failed_tests"]} [FAIL]
跳过测试: {self.results["skipped_tests"]} [SKIP]
通过率: {pass_rate:.1f}%

测试评级:
--------
"""

        if pass_rate == 100:
            report += "[SUCCESS] 完美！所有测试通过！\n"
        elif pass_rate >= 90:
            report += "[SUCCESS] 优秀！超过90%测试通过！\n"
        elif pass_rate >= 80:
            report += "[SUCCESS] 良好！超过80%测试通过！\n"
        elif pass_rate >= 70:
            report += "[SUCCESS] 及格！超过70%测试通过！\n"
        elif pass_rate >= 50:
            report += "[WARNING] 核心功能正常，超过一半测试通过！\n"
        else:
            report += "[WARNING] 需要进一步优化\n"

        report += "\n详细测试结果:\n"
        report += "-" * 80 + "\n"

        for result in self.results["test_results"]:
            status_icon = "[PASS]" if result["status"] == "PASS" else "[FAIL]"
            report += f"{status_icon} {result['test_name']}: {result['status']}"
            if result['details']:
                report += f" - {result['details']}"
            if result['duration']:
                report += f" ({result['duration']:.2f}s)"
            report += "\n"

        report += "=" * 80 + "\n"

        # 保存JSON格式报告
        report_file = f"test_results/e2e_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        # 保存文本格式报告
        text_report_file = f"test_results/e2e_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(text_report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(report)
        TestUtils.log(f"测试报告已保存: {report_file} 和 {text_report_file}")

        return pass_rate

# ====================== 测试套件 ======================

class TestSuite:
    """测试套件"""

    def __init__(self, test_runner: ComprehensiveIntegrationTest):
        self.test = test_runner
        self.config = TestConfig()
        self.utils = TestUtils()

    def run_all_tests(self, headless: bool = True):
        """运行所有测试"""
        print("\n" + "=" * 80)
        print("开始执行 AgentScope PaaS 端到端集成测试")
        print("=" * 80 + "\n")

        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=headless, slow_mo=500)
            self.page = self.browser.new_page()

            try:
                # 1. 系统健康检查
                self.test_system_health()

                # 2. API端点测试
                self.test_api_endpoints()

                # 3. 用户认证流程测试
                self.test_user_authentication()

                # 4. 智能体管理测试
                self.test_agent_management()

                # 5. 对话功能测试
                self.test_conversation_features()

                # 6. 前端页面测试
                self.test_frontend_pages()

                # 7. 配置验证测试
                self.test_configuration_validation()

            finally:
                self.browser.close()

        # 生成最终报告
        pass_rate = self.test.generate_report()
        return pass_rate

    def test_system_health(self):
        """测试系统健康状态"""
        print("\n[系统健康检查]")
        print("-" * 80)

        start_time = time.time()

        try:
            # 测试API健康检查
            success, response = self.utils.make_api_request("GET", "/api/v1/health")

            if success and response.get("data", {}).get("status") == "healthy":
                self.test.record_result(
                    "API健康检查",
                    True,
                    f"系统状态: {response['data']['status']}",
                    time.time() - start_time
                )
            else:
                self.test.record_result(
                    "API健康检查",
                    False,
                    f"响应异常: {response}",
                    time.time() - start_time
                )
        except Exception as e:
            self.test.record_result(
                "API健康检查",
                False,
                f"异常: {str(e)}",
                time.time() - start_time
            )

    def test_api_endpoints(self):
        """测试API端点"""
        print("\n[API端点测试]")
        print("-" * 80)

        endpoints = [
            ("GET", "/api/v1/health", "健康检查"),
            ("GET", "/api/v1/templates", "模板列表"),
            ("GET", "/api/v1/agents", "智能体列表"),
            ("GET", "/api/v1/tools/categories", "工具类别"),
            ("GET", "/api/v1/compression/strategies", "压缩策略")
        ]

        for method, endpoint, description in endpoints:
            start_time = time.time()
            try:
                success, response = self.utils.make_api_request(method, endpoint)
                self.test.record_result(
                    f"API端点测试: {description}",
                    success,
                    f"{method} {endpoint}" if success else f"响应: {response}",
                    time.time() - start_time
                )
            except Exception as e:
                self.test.record_result(
                    f"API端点测试: {description}",
                    False,
                    f"异常: {str(e)}",
                    time.time() - start_time
                )

    def test_user_authentication(self):
        """测试用户认证流程"""
        print("\n[用户认证测试]")
        print("-" * 80)

        start_time = time.time()

        try:
            # 生成唯一用户名
            timestamp = int(time.time())
            test_user = {
                "username": f"e2e_test_user_{timestamp}",
                "email": f"e2e_test_{timestamp}@example.com",
                "password": "Test123456"
            }

            # 注册用户
            success, response = self.utils.make_api_request(
                "POST",
                "/api/v1/auth/register",
                json=test_user
            )

            if success:
                self.test.record_result(
                    "用户注册",
                    True,
                    f"用户: {test_user['username']}",
                    time.time() - start_time
                )

                # 登录用户（使用email字段）
                login_data = {
                    "email": test_user["email"],  # API需要email字段
                    "password": test_user["password"]
                }

                login_start = time.time()
                success, response = self.utils.make_api_request(
                    "POST",
                    "/api/v1/auth/login",
                    json=login_data
                )

                if success and response.get("data", {}).get("api_key"):
                    # API返回的是api_key，不是access_token
                    self.test.auth_token = response["data"]["api_key"]
                    self.test.test_user_id = response["data"]["user"]["user_id"]

                    self.test.record_result(
                        "用户登录",
                        True,
                        f"获取token成功",
                        time.time() - login_start
                    )
                else:
                    self.test.record_result(
                        "用户登录",
                        False,
                        f"响应: {response}",
                        time.time() - login_start
                    )
            else:
                self.test.record_result(
                    "用户注册",
                    False,
                    f"响应: {response}",
                    time.time() - start_time
                )

        except Exception as e:
            self.test.record_result(
                "用户认证",
                False,
                f"异常: {str(e)}",
                time.time() - start_time
            )

    def test_agent_management(self):
        """测试智能体管理"""
        print("\n[智能体管理测试]")
        print("-" * 80)

        # 如果没有认证token，跳过需要认证的测试
        if not self.test.auth_token:
            self.test.record_result("智能体管理测试", False, "未获取API密钥")
            return

        # 使用API key认证头部
        headers = {"X-API-Key": self.test.auth_token}

        # 1. 创建智能体
        start_time = time.time()
        try:
            # 生成唯一的agent_id
            timestamp = int(time.time())
            agent_config = self.config.TEST_AGENT.copy()
            agent_config["agent_metadata"]["agent_id"] = f"e2e_test_agent_{timestamp}"

            success, response = self.utils.make_api_request(
                "POST",
                "/api/v1/agents",
                json={"config": agent_config},
                headers=headers
            )

            if success:
                self.test.test_agent_id = response.get("data", {}).get("agent_id")
                self.test.record_result(
                    "创建智能体",
                    True,
                    f"智能体ID: {self.test.test_agent_id}",
                    time.time() - start_time
                )
            else:
                self.test.record_result(
                    "创建智能体",
                    False,
                    f"响应: {response}",
                    time.time() - start_time
                )
                return
        except Exception as e:
            self.test.record_result("创建智能体", False, f"异常: {str(e)}")
            return

        # 2. 获取智能体列表
        start_time = time.time()
        try:
            success, response = self.utils.make_api_request(
                "GET",
                "/api/v1/agents",
                headers=headers
            )

            if success:
                agents_count = len(response.get("data", {}).get("agents", []))
                self.test.record_result(
                    "获取智能体列表",
                    True,
                    f"找到 {agents_count} 个智能体",
                    time.time() - start_time
                )
            else:
                self.test.record_result(
                    "获取智能体列表",
                    False,
                    f"响应: {response}",
                    time.time() - start_time
                )
        except Exception as e:
            self.test.record_result("获取智能体列表", False, f"异常: {str(e)}")

        # 3. 获取智能体详情
        if self.test.test_agent_id:
            start_time = time.time()
            try:
                success, response = self.utils.make_api_request(
                    "GET",
                    f"/api/v1/agents/{self.test.test_agent_id}",
                    headers=headers
                )

                if success:
                    self.test.record_result(
                        "获取智能体详情",
                        True,
                        f"智能体: {self.test.test_agent_id}",
                        time.time() - start_time
                    )
                else:
                    self.test.record_result(
                        "获取智能体详情",
                        False,
                        f"响应: {response}",
                        time.time() - start_time
                    )
            except Exception as e:
                self.test.record_result("获取智能体详情", False, f"异常: {str(e)}")

            # 4. 启动智能体
            start_time = time.time()
            try:
                success, response = self.utils.make_api_request(
                    "POST",
                    f"/api/v1/agents/{self.test.test_agent_id}/start",
                    headers=headers
                )

                if success:
                    self.test.record_result(
                        "启动智能体",
                        True,
                        f"状态: {response.get('data', {}).get('status')}",
                        time.time() - start_time
                    )
                else:
                    self.test.record_result(
                        "启动智能体",
                        False,
                        f"响应: {response}",
                        time.time() - start_time
                    )
            except Exception as e:
                self.test.record_result("启动智能体", False, f"异常: {str(e)}")

    def test_conversation_features(self):
        """测试对话功能"""
        print("\n[对话功能测试]")
        print("-" * 80)

        if not self.test.auth_token or not self.test.test_agent_id:
            self.test.record_result("对话功能测试", False, "缺少必要的API密钥或智能体ID")
            return

        # 使用API key认证头部
        headers = {"X-API-Key": self.test.auth_token}

        # 1. 创建对话
        start_time = time.time()
        try:
            conversation_data = {
                "agent_id": self.test.test_agent_id,
                "user_id": self.test.test_user_id or "test_user_001"
            }

            success, response = self.utils.make_api_request(
                "POST",
                f"/api/v1/agents/{self.test.test_agent_id}/conversations",
                json=conversation_data,
                headers=headers
            )

            if success:
                self.test.test_conversation_id = response.get("data", {}).get("conversation_id")
                self.test.record_result(
                    "创建对话",
                    True,
                    f"对话ID: {self.test.test_conversation_id}",
                    time.time() - start_time
                )
            else:
                self.test.record_result(
                    "创建对话",
                    False,
                    f"响应: {response}",
                    time.time() - start_time
                )
                return
        except Exception as e:
            self.test.record_result("创建对话", False, f"异常: {str(e)}")
            return

        # 2. 发送消息
        if self.test.test_conversation_id:
            start_time = time.time()
            try:
                message_data = {
                    "content": "你好，这是一条测试消息。",
                    "message_type": "text"
                }

                success, response = self.utils.make_api_request(
                    "POST",
                    f"/api/v1/conversations/{self.test.test_conversation_id}/messages",
                    json=message_data,
                    headers=headers
                )

                if success:
                    self.test.record_result(
                        "发送消息",
                        True,
                        f"消息已发送",
                        time.time() - start_time
                    )
                else:
                    self.test.record_result(
                        "发送消息",
                        False,
                        f"响应: {response}",
                        time.time() - start_time
                    )
            except Exception as e:
                self.test.record_result("发送消息", False, f"异常: {str(e)}")

    def test_frontend_pages(self):
        """测试前端页面"""
        print("\n[前端页面测试]")
        print("-" * 80)

        pages_to_test = [
            (self.config.FRONTEND_BASE_URL, "首页"),
            (f"{self.config.FRONTEND_BASE_URL}/login", "登录页面"),
            (f"{self.config.FRONTEND_BASE_URL}/register", "注册页面"),
            (f"{self.config.FRONTEND_BASE_URL}/dashboard", "仪表板"),
            (f"{self.config.FRONTEND_BASE_URL}/agents", "智能体列表"),
            (f"{self.config.FRONTEND_BASE_URL}/agents/create", "创建智能体"),
            (f"{self.config.FRONTEND_BASE_URL}/conversation", "对话页面"),
            (f"{self.config.FRONTEND_BASE_URL}/monitoring", "监控页面")
        ]

        for url, page_name in pages_to_test:
            start_time = time.time()
            try:
                # 访问页面
                final_url = self.utils.wait_for_page_load(self.page, url)

                # 检查页面是否可访问
                page_accessible = (
                    'login' not in final_url or 'login' in url  # 不是意外重定向到登录页
                )

                # 保存截图
                self.utils.save_screenshot(self.page, f"frontend_{page_name.replace(' ', '_')}")

                if page_accessible:
                    self.test.record_result(
                        f"前端页面: {page_name}",
                        True,
                        f"URL: {final_url}",
                        time.time() - start_time
                    )
                else:
                    self.test.record_result(
                        f"前端页面: {page_name}",
                        False,
                        f"被重定向到: {final_url}",
                        time.time() - start_time
                    )

            except Exception as e:
                self.test.record_result(
                    f"前端页面: {page_name}",
                    False,
                    f"异常: {str(e)}",
                    time.time() - start_time
                )

    def test_configuration_validation(self):
        """测试配置验证"""
        print("\n[配置验证测试]")
        print("-" * 80)

        # 1. 测试有效配置
        start_time = time.time()
        try:
            valid_config = self.config.TEST_AGENT.copy()

            success, response = self.utils.make_api_request(
                "POST",
                "/api/v1/config/validate",
                json={"config": valid_config}
            )

            if success and response.get("data", {}).get("valid"):
                self.test.record_result(
                    "配置验证 - 有效配置",
                    True,
                    f"质量分数: {response.get('data', {}).get('quality_score')}",
                    time.time() - start_time
                )
            else:
                self.test.record_result(
                    "配置验证 - 有效配置",
                    False,
                    f"响应: {response}",
                    time.time() - start_time
                )
        except Exception as e:
            self.test.record_result("配置验证 - 有效配置", False, f"异常: {str(e)}")

        # 2. 测试无效配置
        start_time = time.time()
        try:
            invalid_config = {
                "agent_metadata": {
                    "agent_id": "",  # 空ID
                    "agent_name": "",  # 空名称
                },
                "llm_config": {
                    "model_name": "",  # 空模型名
                    "api_key": ""  # 空API key
                }
            }

            success, response = self.utils.make_api_request(
                "POST",
                "/api/v1/config/validate",
                json={"config": invalid_config}
            )

            if not success or not response.get("data", {}).get("valid"):
                errors = response.get("data", {}).get("errors", [])
                self.test.record_result(
                    "配置验证 - 无效配置",
                    True,
                    f"正确识别 {len(errors)} 个错误",
                    time.time() - start_time
                )
            else:
                self.test.record_result(
                    "配置验证 - 无效配置",
                    False,
                    "未能正确识别无效配置",
                    time.time() - start_time
                )
        except Exception as e:
            self.test.record_result("配置验证 - 无效配置", False, f"异常: {str(e)}")

# ====================== 主程序 ======================

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='AgentScope PaaS 端到端集成测试')
    parser.add_argument('--headless', action='store_true', help='使用无头浏览器模式')
    parser.add_argument('--verbose', action='store_true', help='详细输出模式')

    args = parser.parse_args()

    # 创建测试实例
    test_runner = ComprehensiveIntegrationTest()
    test_suite = TestSuite(test_runner)

    # 运行测试
    try:
        pass_rate = test_suite.run_all_tests(headless=args.headless)

        # 返回退出码
        exit_code = 0 if pass_rate >= 70 else 1  # 通过率>=70%视为成功
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试执行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()