#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS - Pytest 端到端测试套件
使用 pytest 框架的模块化测试
"""

import pytest
import requests
import json
import time
from datetime import datetime
from playwright.sync_api import Page, Browser
from pathlib import Path
from typing import Dict, Any, Generator

# ====================== 测试配置 ======================

class Config:
    """测试配置"""
    API_BASE_URL = "http://localhost:8000"
    FRONTEND_BASE_URL = "http://localhost:3000"
    TIMEOUT = 10

    # 测试数据
    TEST_USER = {
        "username": "pytest_user",
        "email": "pytest@example.com",
        "password": "Test123456"
    }

    TEST_AGENT = {
        "agent_metadata": {
            "agent_id": "pytest_agent_001",
            "agent_name": "Pytest测试智能体",
            "agent_type": "DialogAgent",
            "description": "用于pytest测试的智能体",
            "version": "1.0.0",
            "tags": ["pytest", "测试"]
        },
        "llm_config": {
            "model_name": "gpt-4o",
            "api_key": "pytest-test-key",
            "base_url": "https://api.openai.com/v1"
        },
        "prompt_config": {
            "system_prompt": "你是一个pytest测试用的AI助手。"
        }
    }

# ====================== 测试固件 ======================

@pytest.fixture(scope="session")
def base_url():
    """基础URL"""
    return Config.API_BASE_URL

@pytest.fixture(scope="session")
def frontend_url():
    """前端URL"""
    return Config.FRONTEND_BASE_URL

@pytest.fixture(scope="session")
def test_session():
    """测试会话数据"""
    return {
        "auth_token": None,
        "user_id": None,
        "agent_id": None,
        "conversation_id": None
    }

@pytest.fixture(scope="function")
def api_client():
    """API客户端"""
    class APIClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.token = None
            self.session = requests.Session()

        def set_token(self, token: str):
            """设置认证token"""
            self.token = token
            # 使用API key认证头部
            self.session.headers.update({
                "X-API-Key": token,
                "Content-Type": "application/json"
            })

        def request(self, method: str, endpoint: str, **kwargs) -> tuple[bool, dict]:
            """发送请求"""
            url = f"{self.base_url}{endpoint}"
            try:
                response = self.session.request(method, url, timeout=Config.TIMEOUT, **kwargs)
                try:
                    return response.ok, response.json()
                except:
                    return response.ok, {"status_code": response.status_code}
            except Exception as e:
                return False, {"error": str(e)}

        def get(self, endpoint: str, **kwargs):
            return self.request("GET", endpoint, **kwargs)

        def post(self, endpoint: str, **kwargs):
            return self.request("POST", endpoint, **kwargs)

        def put(self, endpoint: str, **kwargs):
            return self.request("PUT", endpoint, **kwargs)

        def delete(self, endpoint: str, **kwargs):
            return self.request("DELETE", endpoint, **kwargs)

    client = APIClient(Config.API_BASE_URL)
    yield client

@pytest.fixture(scope="function")
def browser_context(browser: Browser):
    """浏览器上下文"""
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="zh-CN"
    )
    page = context.new_page()
    yield page
    context.close()

@pytest.fixture(scope="function", autouse=True)
def test_screenshot(request, browser_context: Page):
    """自动截图"""
    yield
    if request.node.rep_call.failed:
        # 测试失败时自动截图
        screenshot_name = f"failed_{request.node.name}_{int(time.time())}"
        screenshot_path = Path(f"test_results/screenshots/{screenshot_name}.png")
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        browser_context.screenshot(path=str(screenshot_path))

# ====================== 健康检查测试 ======================

class TestHealthCheck:
    """健康检查测试"""

    @pytest.mark.order(1)
    def test_api_health_check(self, api_client):
        """测试API健康检查"""
        success, response = api_client.get("/api/v1/health")

        assert success, "API健康检查请求失败"
        assert response["data"]["status"] == "healthy", "系统状态不健康"
        assert "version" in response["data"], "缺少版本信息"

    @pytest.mark.order(2)
    def test_api_documentation_access(self, api_client):
        """测试API文档可访问性"""
        success, response = api_client.get("/api/v1/docs")
        # 文档页面可能返回HTML，不检查JSON
        assert success, "API文档页面不可访问"

# ====================== 认证测试 ======================

class TestAuthentication:
    """认证测试"""

    @pytest.mark.order(10)
    def test_user_registration(self, api_client, test_session):
        """测试用户注册"""
        timestamp = int(time.time())
        user_data = {
            "username": f"pytest_user_{timestamp}",
            "email": f"pytest_{timestamp}@example.com",
            "password": "Test123456"
        }

        success, response = api_client.post("/api/v1/auth/register", json=user_data)

        assert success, f"注册失败: {response}"
        assert "data" in response, "响应缺少data字段"

        test_session["test_username"] = user_data["username"]
        test_session["test_email"] = user_data["email"]
        test_session["test_password"] = user_data["password"]

    @pytest.mark.order(11)
    def test_user_login(self, api_client, test_session):
        """测试用户登录"""
        login_data = {
            "email": test_session["test_email"],  # API需要email字段
            "password": test_session["test_password"]
        }

        success, response = api_client.post("/api/v1/auth/login", json=login_data)

        assert success, f"登录失败: {response}"
        assert "data" in response, "响应缺少data字段"
        assert "api_key" in response["data"], "响应缺少api_key"

        # 保存API key用于后续测试
        api_key = response["data"]["api_key"]
        api_client.set_token(api_key)
        test_session["auth_token"] = api_key
        test_session["user_id"] = response["data"]["user"]["user_id"]

    @pytest.mark.order(12)
    def test_authenticated_request(self, api_client):
        """测试认证请求"""
        success, response = api_client.get("/api/v1/agents")

        assert success, f"认证请求失败: {response}"
        assert "data" in response, "响应缺少data字段"

# ====================== 智能体管理测试 ======================

class TestAgentManagement:
    """智能体管理测试"""

    @pytest.mark.order(20)
    def test_create_agent(self, api_client, test_session):
        """测试创建智能体"""
        timestamp = int(time.time())
        agent_config = Config.TEST_AGENT.copy()
        agent_config["agent_metadata"]["agent_id"] = f"pytest_agent_{timestamp}"

        success, response = api_client.post("/api/v1/agents", json={"config": agent_config})

        assert success, f"创建智能体失败: {response}"
        assert "data" in response, "响应缺少data字段"
        assert "agent_id" in response["data"], "响应缺少agent_id"

        test_session["agent_id"] = response["data"]["agent_id"]

    @pytest.mark.order(21)
    def test_get_agents_list(self, api_client):
        """测试获取智能体列表"""
        success, response = api_client.get("/api/v1/agents")

        assert success, f"获取智能体列表失败: {response}"
        assert "data" in response, "响应缺少data字段"
        assert "agents" in response["data"], "响应缺少agents字段"

    @pytest.mark.order(22)
    def test_get_agent_details(self, api_client, test_session):
        """测试获取智能体详情"""
        agent_id = test_session["agent_id"]
        success, response = api_client.get(f"/api/v1/agents/{agent_id}")

        assert success, f"获取智能体详情失败: {response}"
        assert "data" in response, "响应缺少data字段"
        assert response["data"]["agent_id"] == agent_id, "智能体ID不匹配"

    @pytest.mark.order(23)
    def test_start_agent(self, api_client, test_session):
        """测试启动智能体"""
        agent_id = test_session["agent_id"]
        success, response = api_client.post(f"/api/v1/agents/{agent_id}/start")

        assert success, f"启动智能体失败: {response}"
        assert "data" in response, "响应缺少data字段"
        assert response["data"]["status"] == "running", "智能体状态不正确"

# ====================== 对话功能测试 ======================

class TestConversation:
    """对话功能测试"""

    @pytest.mark.order(30)
    def test_create_conversation(self, api_client, test_session):
        """测试创建对话"""
        conversation_data = {
            "agent_id": test_session["agent_id"],
            "user_id": test_session["user_id"]
        }

        success, response = api_client.post(
            f"/api/v1/agents/{test_session['agent_id']}/conversations",
            json=conversation_data
        )

        assert success, f"创建对话失败: {response}"
        assert "data" in response, "响应缺少data字段"
        assert "conversation_id" in response["data"], "响应缺少conversation_id"

        test_session["conversation_id"] = response["data"]["conversation_id"]

    @pytest.mark.order(31)
    def test_send_message(self, api_client, test_session):
        """测试发送消息"""
        message_data = {
            "content": "你好，这是一条pytest测试消息。",
            "message_type": "text"
        }

        success, response = api_client.post(
            f"/api/v1/conversations/{test_session['conversation_id']}/messages",
            json=message_data
        )

        assert success, f"发送消息失败: {response}"
        assert "data" in response, "响应缺少data字段"

# ====================== 配置验证测试 ======================

class TestConfigurationValidation:
    """配置验证测试"""

    @pytest.mark.order(40)
    def test_valid_configuration(self, api_client):
        """测试有效配置验证"""
        valid_config = Config.TEST_AGENT.copy()

        success, response = api_client.post("/api/v1/config/validate", json={"config": valid_config})

        assert success, f"配置验证请求失败: {response}"
        assert response["data"]["valid"], "有效配置被错误标记为无效"
        assert response["data"]["quality_score"] > 0, "质量分数异常"

    @pytest.mark.order(41)
    def test_invalid_configuration(self, api_client):
        """测试无效配置验证"""
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

        success, response = api_client.post("/api/v1/config/validate", json={"config": invalid_config})

        assert success, f"配置验证请求失败: {response}"
        assert not response["data"]["valid"], "无效配置被错误标记为有效"
        assert len(response["data"]["errors"]) > 0, "未返回配置错误"

# ====================== 前端页面测试 ======================

class TestFrontendPages:
    """前端页面测试"""

    @pytest.mark.order(50)
    def test_homepage_loads(self, browser_context: Page, frontend_url):
        """测试首页加载"""
        browser_context.goto(frontend_url, timeout=15000)
        browser_context.wait_for_load_state('domcontentloaded', timeout=10000)

        assert "localhost" in browser_context.url, "页面URL不正确"

    @pytest.mark.order(51)
    def test_login_page_loads(self, browser_context: Page, frontend_url):
        """测试登录页面加载"""
        browser_context.goto(f"{frontend_url}/login", timeout=15000)
        browser_context.wait_for_load_state('domcontentloaded', timeout=10000)

        assert "login" in browser_context.url.lower(), "未正确导航到登录页面"

    @pytest.mark.order(52)
    def test_dashboard_loads(self, browser_context: Page, frontend_url):
        """测试仪表板加载"""
        browser_context.goto(f"{frontend_url}/dashboard", timeout=15000)
        browser_context.wait_for_load_state('domcontentloaded', timeout=10000)

        # 可能被重定向到登录页面，这是正常的
        assert "localhost" in browser_context.url, "页面URL异常"

    @pytest.mark.order(53)
    def test_agents_page_loads(self, browser_context: Page, frontend_url):
        """测试智能体页面加载"""
        browser_context.goto(f"{frontend_url}/agents", timeout=15000)
        browser_context.wait_for_load_state('domcontentloaded', timeout=10000)

        assert "localhost" in browser_context.url, "页面URL异常"

    @pytest.mark.order(54)
    def test_agent_create_page_loads(self, browser_context: Page, frontend_url):
        """测试创建智能体页面加载"""
        browser_context.goto(f"{frontend_url}/agents/create", timeout=15000)
        browser_context.wait_for_load_state('domcontentloaded', timeout=10000)

        assert "localhost" in browser_context.url, "页面URL异常"

# ====================== 模板和工具测试 ======================

class TestTemplatesAndTools:
    """模板和工具测试"""

    @pytest.mark.order(60)
    def test_get_templates(self, api_client):
        """测试获取模板列表"""
        success, response = api_client.get("/api/v1/templates")

        assert success, f"获取模板列表失败: {response}"
        assert "data" in response, "响应缺少data字段"
        assert "templates" in response["data"], "响应缺少templates字段"

    @pytest.mark.order(61)
    def test_get_tool_categories(self, api_client):
        """测试获取工具类别"""
        success, response = api_client.get("/api/v1/tools/categories")

        assert success, f"获取工具类别失败: {response}"
        assert "data" in response, "响应缺少data字段"
        assert "categories" in response["data"], "响应缺少categories字段"

    @pytest.mark.order(62)
    def test_get_compression_strategies(self, api_client):
        """测试获取压缩策略"""
        success, response = api_client.get("/api/v1/compression/strategies")

        assert success, f"获取压缩策略失败: {response}"
        assert "data" in response, "响应缺少data字段"
        assert "strategies" in response["data"], "响应缺少strategies字段"

# ====================== 性能测试 ======================

class TestPerformance:
    """性能测试"""

    @pytest.mark.order(70)
    def test_api_response_time(self, api_client):
        """测试API响应时间"""
        start_time = time.time()
        success, response = api_client.get("/api/v1/health")
        response_time = time.time() - start_time

        assert success, "健康检查请求失败"
        assert response_time < 2.0, f"API响应时间过长: {response_time:.2f}秒"

    @pytest.mark.order(71)
    def test_concurrent_requests(self, api_client):
        """测试并发请求"""
        import concurrent.futures

        def make_request():
            return api_client.get("/api/v1/health")

        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        total_time = time.time() - start_time

        success_count = sum(1 for success, _ in results if success)
        assert success_count >= 8, f"并发请求成功率过低: {success_count}/10"
        assert total_time < 5.0, f"并发请求总时间过长: {total_time:.2f}秒"

# ====================== Pytest 配置 ======================

def pytest_configure(config):
    """Pytest配置"""
    config.addinivalue_line("markers", "order: mark test to run in specific order")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_call(item):
    """测试调用钩子"""
    yield
    item.rep_call = getattr(item, "rep_call", None)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 创建必要的目录
    Path("test_results").mkdir(exist_ok=True)
    Path("test_results/screenshots").mkdir(exist_ok=True)
    Path("test_results/html").mkdir(exist_ok=True)

    yield

    print("\n" + "=" * 80)
    print("测试执行完成")
    print("=" * 80)

# ====================== 主程序 ======================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--html=test_results/html/report.html", "-self-contained-html"])