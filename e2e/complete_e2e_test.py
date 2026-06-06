#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS Platform - Complete E2E Test Suite
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

from playwright.sync_api import sync_playwright, Page, Browser
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any


class E2ETestHelper:
    """端到端测试辅助类"""

    def __init__(self, page: Page, screenshots_dir: str = "e2e_screenshots"):
        self.page = page
        self.screenshots_dir = screenshots_dir
        self.test_data = {}
        os.makedirs(screenshots_dir, exist_ok=True)

    def screenshot(self, name: str, full_page: bool = True):
        """保存截图"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshots_dir}/{name}_{timestamp}.png"
        self.page.screenshot(path=filename, full_page=full_page)
        print(f"📸 截图保存: {filename}")

    def wait_for_network_idle(self, timeout: int = 5000):
        """等待网络空闲"""
        self.page.wait_for_load_state('networkidle', timeout=timeout)

    def fill_form(self, selectors: Dict[str, str]):
        """填充表单"""
        for field, value in selectors.items():
            try:
                self.page.fill(field, value)
                print(f"✅ 填充字段 {field}: {value}")
            except Exception as e:
                print(f"❌ 填充字段失败 {field}: {e}")

    def click_button(self, selector: str, description: str = ""):
        """点击按钮"""
        try:
            self.page.click(selector)
            print(f"✅ 点击按钮: {description or selector}")
            time.sleep(1)  # 等待响应
        except Exception as e:
            print(f"❌ 点击按钮失败 {selector}: {e}")

    def check_element_exists(self, selector: str, description: str = "") -> bool:
        """检查元素是否存在"""
        try:
            count = self.page.locator(selector).count()
            exists = count > 0
            print(f"{'✅' if exists else '❌'} 元素检查 {description or selector}: {exists}")
            return exists
        except Exception as e:
            print(f"❌ 检查元素时出错 {selector}: {e}")
            return False

    def check_text_visible(self, text: str) -> bool:
        """检查文本是否可见"""
        try:
            visible = self.page.locator(f"text={text}").count() > 0
            print(f"{'✅' if visible else '❌'} 文本检查 '{text}': {visible}")
            return visible
        except Exception as e:
            print(f"❌ 检查文本时出错 '{text}': {e}")
            return False


class AuthE2ETest:
    """用户认证端到端测试"""

    def __init__(self, helper: E2ETestHelper):
        self.helper = helper
        self.test_user = {
            "username": f"e2e_user_{int(time.time())}",
            "email": f"e2e_test_{int(time.time())}@test.com",
            "password": "Test123456!",
            "confirm_password": "Test123456!"
        }

    def test_registration(self):
        """测试用户注册流程"""
        print("\n🔐 [开始] 用户注册测试")

        # 导航到注册页面
        self.helper.page.goto('http://localhost:3000/register')
        self.helper.wait_for_network_idle()
        self.helper.screenshot("register_page")

        # 检查注册表单是否存在
        if not self.helper.check_element_exists('#register_username', "用户名输入框"):
            return False

        if not self.helper.check_element_exists('#register_email', "邮箱输入框"):
            return False

        if not self.helper.check_element_exists('#register_password', "密码输入框"):
            return False

        # 填写注册表单
        self.helper.fill_form({
            '#register_username': self.test_user['username'],
            '#register_email': self.test_user['email'],
            '#register_password': self.test_user['password'],
            '#register_confirmPassword': self.test_user['confirm_password']
        })

        self.helper.screenshot("register_form_filled")

        # 提交表单
        self.helper.click_button('button[type="submit"]', "注册按钮")

        # 等待响应
        time.sleep(3)
        self.helper.wait_for_network_idle()
        self.helper.screenshot("register_result")

        # 检查是否跳转到仪表板或显示成功消息
        current_url = self.helper.page.url
        print(f"📍 当前URL: {current_url}")

        # 成功条件：跳转到仪表板或显示成功消息
        success = 'dashboard' in current_url or self.helper.check_text_visible('注册成功')

        if success:
            print("✅ 注册测试通过")
        else:
            print("❌ 注册测试失败")

        return success

    def test_login(self):
        """测试用户登录流程"""
        print("\n🔑 [开始] 用户登录测试")

        # 导航到登录页面
        self.helper.page.goto('http://localhost:3000/login')
        self.helper.wait_for_network_idle()
        self.helper.screenshot("login_page")

        # 检查登录表单是否存在
        if not self.helper.check_element_exists('#login_username', "用户名输入框"):
            return False

        if not self.helper.check_element_exists('#login_password', "密码输入框"):
            return False

        # 填写登录表单
        self.helper.fill_form({
            '#login_username': self.test_user['username'],
            '#login_password': self.test_user['password']
        })

        self.helper.screenshot("login_form_filled")

        # 提交表单
        self.helper.click_button('button[type="submit"]', "登录按钮")

        # 等待响应
        time.sleep(3)
        self.helper.wait_for_network_idle()
        self.helper.screenshot("login_result")

        # 检查是否跳转到仪表板
        current_url = self.helper.page.url
        print(f"📍 当前URL: {current_url}")

        success = 'dashboard' in current_url
        if success:
            print("✅ 登录测试通过")
        else:
            print("❌ 登录测试失败")

        return success

    def test_logout(self):
        """测试用户登出流程"""
        print("\n🚪 [开始] 用户登出测试")

        # 先确保已登录
        if 'login' in self.helper.page.url:
            if not self.test_login():
                return False

        # 查找并点击登出按钮
        logout_selectors = [
            'text=/登出|退出|Logout/i',
            '[data-testid="logout-button"]',
            '.ant-dropdown-menu-item:text("登出")'
        ]

        logout_clicked = False
        for selector in logout_selectors:
            try:
                if self.helper.page.locator(selector).count() > 0:
                    self.helper.click_button(selector, "登出按钮")
                    logout_clicked = True
                    break
            except:
                continue

        if not logout_clicked:
            print("❌ 未找到登出按钮")
            return False

        time.sleep(2)
        self.helper.wait_for_network_idle()
        self.helper.screenshot("logout_result")

        # 检查是否跳转到登录页面
        current_url = self.helper.page.url
        success = 'login' in current_url

        if success:
            print("✅ 登出测试通过")
        else:
            print("❌ 登出测试失败")

        return success


class DashboardE2ETest:
    """仪表板功能端到端测试"""

    def __init__(self, helper: E2ETestHelper):
        self.helper = helper

    def test_dashboard_access(self):
        """测试仪表板访问"""
        print("\n📊 [开始] 仪表板访问测试")

        # 导航到仪表板
        self.helper.page.goto('http://localhost:3000/dashboard')
        self.helper.wait_for_network_idle()
        time.sleep(2)  # 等待数据加载
        self.helper.screenshot("dashboard_page")

        # 检查仪表板核心元素
        checks = [
            ('.ant-layout', '布局容器'),
            ('.ant-layout-sider', '侧边栏'),
            ('.ant-layout-content', '内容区域'),
            ('h1, h2, h3', '标题元素'),
        ]

        all_passed = True
        for selector, description in checks:
            if not self.helper.check_element_exists(selector, description):
                all_passed = False

        if all_passed:
            print("✅ 仪表板访问测试通过")
        else:
            print("❌ 仪表板访问测试失败")

        return all_passed

    def test_dashboard_statistics(self):
        """测试仪表板统计信息"""
        print("\n📈 [开始] 仪表板统计测试")

        # 检查统计卡片
        stat_checks = [
            ('.ant-statistic', '统计组件'),
            ('.ant-card', '卡片组件'),
        ]

        all_passed = True
        for selector, description in stat_checks:
            if not self.helper.check_element_exists(selector, description):
                all_passed = False

        self.helper.screenshot("dashboard_statistics")

        if all_passed:
            print("✅ 仪表板统计测试通过")
        else:
            print("❌ 仪表板统计测试失败")

        return all_passed


class AgentManagementE2ETest:
    """智能体管理端到端测试"""

    def __init__(self, helper: E2ETestHelper):
        self.helper = helper
        self.test_agent = {
            "name": f"测试智能体_{int(time.time())}",
            "type": "ReActAgent",
            "description": "这是一个端到端测试创建的智能体",
            "model_name": "gpt-4",
            "api_key": "test_key_123",
            "base_url": "https://api.openai.com/v1",
            "system_prompt": "你是一个有帮助的助手。"
        }

    def test_agent_list_access(self):
        """测试智能体列表访问"""
        print("\n🤖 [开始] 智能体列表访问测试")

        # 导航到智能体列表页面
        self.helper.page.goto('http://localhost:3000/agents')
        self.helper.wait_for_network_idle()
        time.sleep(2)
        self.helper.screenshot("agent_list")

        # 检查列表元素
        checks = [
            ('.ant-table', '表格组件'),
            ('.ant-btn', '按钮组件'),
        ]

        all_passed = True
        for selector, description in checks:
            if not self.helper.check_element_exists(selector, description):
                all_passed = False

        if all_passed:
            print("✅ 智能体列表访问测试通过")
        else:
            print("❌ 智能体列表访问测试失败")

        return all_passed

    def test_agent_creation(self):
        """测试智能体创建"""
        print("\n🔧 [开始] 智能体创建测试")

        # 导航到创建页面
        self.helper.page.goto('http://localhost:3000/agents/create')
        self.helper.wait_for_network_idle()
        self.helper.screenshot("agent_create_page")

        # 检查创建表单元素
        form_checks = [
            ('input[name="name"], #agent_name', '智能体名称'),
            ('select[name="type"], #agent_type', '智能体类型'),
            ('textarea[name="description"], #agent_description', '智能体描述'),
            ('input[name="model_name"], #model_name', '模型名称'),
            ('input[name="api_key"], #api_key', 'API密钥'),
            ('input[name="base_url"], #base_url', 'API地址'),
            ('textarea[name="system_prompt"], #system_prompt', '系统提示词'),
        ]

        form_ready = True
        for selector, description in form_checks:
            if not self.helper.check_element_exists(selector, description):
                form_ready = False

        if not form_ready:
            print("❌ 智能体创建表单未准备好")
            return False

        # 尝试填写表单（如果字段存在）
        try:
            # 基本信息填写
            self.helper.fill_form({
                'input[name="name"], #agent_name': self.test_agent['name'],
                'textarea[name="description"], #agent_description': self.test_agent['description'],
            })

            self.helper.screenshot("agent_create_basic_info")

            print("✅ 智能体创建表单填写成功")

            # 尝试提交（如果提交按钮存在）
            submit_selectors = [
                'button[type="submit"]',
                '.ant-btn-primary',
                'text=/创建|Create/i'
            ]

            for selector in submit_selectors:
                try:
                    if self.helper.page.locator(selector).count() > 0:
                        self.helper.click_button(selector, "创建按钮")
                        time.sleep(2)
                        self.helper.screenshot("agent_create_result")
                        break
                except:
                    continue

            return True

        except Exception as e:
            print(f"❌ 智能体创建失败: {e}")
            return False


class ConversationE2ETest:
    """对话功能端到端测试"""

    def __init__(self, helper: E2ETestHelper):
        self.helper = helper

    def test_conversation_access(self):
        """测试对话页面访问"""
        print("\n💬 [开始] 对话页面访问测试")

        # 导航到对话页面
        self.helper.page.goto('http://localhost:3000/conversation')
        self.helper.wait_for_network_idle()
        time.sleep(2)
        self.helper.screenshot("conversation_page")

        # 检查对话界面元素
        checks = [
            ('.ant-layout', '对话布局'),
            ('input[type="text"], textarea', '消息输入框'),
            ('.ant-btn', '发送按钮'),
        ]

        all_passed = True
        for selector, description in checks:
            if not self.helper.check_element_exists(selector, description):
                all_passed = False

        if all_passed:
            print("✅ 对话页面访问测试通过")
        else:
            print("❌ 对话页面访问测试失败")

        return all_passed


class MonitoringE2ETest:
    """监控功能端到端测试"""

    def __init__(self, helper: E2ETestHelper):
        self.helper = helper

    def test_monitoring_access(self):
        """测试监控页面访问"""
        print("\n📊 [开始] 监控页面访问测试")

        # 导航到监控页面
        self.helper.page.goto('http://localhost:3000/monitoring')
        self.helper.wait_for_network_idle()
        time.sleep(2)
        self.helper.screenshot("monitoring_page")

        # 检查监控元素
        checks = [
            ('.ant-layout', '监控布局'),
            ('.ant-card', '信息卡片'),
        ]

        all_passed = True
        for selector, description in checks:
            if not self.helper.check_element_exists(selector, description):
                all_passed = False

        if all_passed:
            print("✅ 监控页面访问测试通过")
        else:
            print("❌ 监控页面访问测试失败")

        return all_passed


def run_complete_e2e_tests(headless: bool = False):
    """运行完整端到端测试套件"""
    print("🚀 AgentScope PaaS 平台 - 端到端测试套件")
    print("=" * 50)

    results = {
        "总测试数": 0,
        "通过测试数": 0,
        "失败测试数": 0,
        "测试详情": []
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        try:
            # 创建测试辅助类
            helper = E2ETestHelper(page)

            # 1. 用户认证测试
            print("\n" + "="*50)
            print("🔐 用户认证模块测试")
            print("="*50)

            auth_test = AuthE2ETest(helper)

            # 注册测试
            results["总测试数"] += 1
            register_result = auth_test.test_registration()
            if register_result:
                results["通过测试数"] += 1
            else:
                results["失败测试数"] += 1
            results["测试详情"].append({"测试": "用户注册", "结果": "通过" if register_result else "失败"})

            # 登录测试
            results["总测试数"] += 1
            login_result = auth_test.test_login()
            if login_result:
                results["通过测试数"] += 1
            else:
                results["失败测试数"] += 1
            results["测试详情"].append({"测试": "用户登录", "结果": "通过" if login_result else "失败"})

            # 2. 仪表板测试
            print("\n" + "="*50)
            print("📊 仪表板模块测试")
            print("="*50)

            dashboard_test = DashboardE2ETest(helper)

            results["总测试数"] += 1
            dashboard_result = dashboard_test.test_dashboard_access()
            if dashboard_result:
                results["通过测试数"] += 1
            else:
                results["失败测试数"] += 1
            results["测试详情"].append({"测试": "仪表板访问", "结果": "通过" if dashboard_result else "失败"})

            results["总测试数"] += 1
            stats_result = dashboard_test.test_dashboard_statistics()
            if stats_result:
                results["通过测试数"] += 1
            else:
                results["失败测试数"] += 1
            results["测试详情"].append({"测试": "仪表板统计", "结果": "通过" if stats_result else "失败"})

            # 3. 智能体管理测试
            print("\n" + "="*50)
            print("🤖 智能体管理模块测试")
            print("="*50)

            agent_test = AgentManagementE2ETest(helper)

            results["总测试数"] += 1
            agent_list_result = agent_test.test_agent_list_access()
            if agent_list_result:
                results["通过测试数"] += 1
            else:
                results["失败测试数"] += 1
            results["测试详情"].append({"测试": "智能体列表", "结果": "通过" if agent_list_result else "失败"})

            results["总测试数"] += 1
            agent_create_result = agent_test.test_agent_creation()
            if agent_create_result:
                results["通过测试数"] += 1
            else:
                results["失败测试数"] += 1
            results["测试详情"].append({"测试": "智能体创建", "结果": "通过" if agent_create_result else "失败"})

            # 4. 对话功能测试
            print("\n" + "="*50)
            print("💬 对话模块测试")
            print("="*50)

            conversation_test = ConversationE2ETest(helper)

            results["总测试数"] += 1
            conversation_result = conversation_test.test_conversation_access()
            if conversation_result:
                results["通过测试数"] += 1
            else:
                results["失败测试数"] += 1
            results["测试详情"].append({"测试": "对话功能", "结果": "通过" if conversation_result else "失败"})

            # 5. 监控功能测试
            print("\n" + "="*50)
            print("📊 监控模块测试")
            print("="*50)

            monitoring_test = MonitoringE2ETest(helper)

            results["总测试数"] += 1
            monitoring_result = monitoring_test.test_monitoring_access()
            if monitoring_result:
                results["通过测试数"] += 1
            else:
                results["失败测试数"] += 1
            results["测试详情"].append({"测试": "监控功能", "结果": "通过" if monitoring_result else "失败"})

            # 输出测试结果摘要
            print("\n" + "="*50)
            print("📋 测试结果摘要")
            print("="*50)
            print(f"总测试数: {results['总测试数']}")
            print(f"通过测试数: {results['通过测试数']} ✅")
            print(f"失败测试数: {results['失败测试数']} ❌")
            print(f"通过率: {results['通过测试数']/results['总测试数']*100:.1f}%")

            print("\n详细结果:")
            for detail in results["测试详情"]:
                status_icon = "✅" if detail["结果"] == "通过" else "❌"
                print(f"{status_icon} {detail['测试']}: {detail['结果']}")

            # 保存测试结果到JSON文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"e2e_test_results_{timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n📄 测试结果已保存到: {results_file}")

        except Exception as e:
            print(f"❌ 测试执行出错: {e}")
            import traceback
            traceback.print_exc()

        finally:
            browser.close()

    return results


if __name__ == '__main__':
    import sys

    # 支持命令行参数
    headless = '--headless' in sys.argv

    print("🔧 AgentScope PaaS 端到端测试")
    print(f"模式: {'无头模式' if headless else '有头模式（显示浏览器）'}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 运行测试
    results = run_complete_e2e_tests(headless=headless)

    # 返回退出码
    exit_code = 0 if results['失败测试数'] == 0 else 1
    sys.exit(exit_code)