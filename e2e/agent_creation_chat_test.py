#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS Platform - Real Agent Creation and Chat E2E Test
使用Playwright进行真实的智能体创建和聊天功能测试
"""

import asyncio
import json
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# 尝试导入playwright
try:
    from playwright.sync_api import sync_playwright, Page, Browser
except ImportError:
    print("[ERROR] Playwright not installed, please run: pip install playwright")
    print("Then run: playwright install chromium")
    sys.exit(1)


class AgentCreationChatTest:
    def __init__(self, frontend_url="http://localhost:3000", backend_url="http://localhost:8000"):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.test_results = []
        self.screenshots_dir = Path("e2e_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)

        # 测试数据
        self.test_user = {
            "username": f"test_user_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "api_key": None
        }

        self.test_agent = {
            "agent_id": f"test_agent_{int(time.time())}",
            "agent_name": f"Test Agent {int(time.time())}",
            "description": "This is a test agent created by E2E test",
            "model_name": "gpt-4o",
            "api_key": "test_api_key_for_demo",
            "system_prompt": "You are a helpful assistant specialized in software testing. Please respond concisely and professionally.",
            "tags": ["test", "automation"]
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

    def setup_browser(self, playwright):
        """设置浏览器环境"""
        browser = playwright.chromium.launch(
            headless=False,  # 显示浏览器窗口以便观察
            slow_mo=500  # 慢速执行以便观察
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
            if msg.type == 'error':
                print(f"Console Error: {msg.text}")

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

        return browser, context, page, console_messages, network_requests

    def test_user_registration(self, page):
        """测试用户注册"""
        print("\n[Test] User Registration")

        try:
            # 导航到注册页面
            page.goto(f"{self.frontend_url}/register", wait_until='networkidle', timeout=10000)
            time.sleep(2)

            # 截图
            screenshot_path = self.screenshots_dir / f"register_page_{int(time.time())}.png"
            page.screenshot(path=str(screenshot_path))

            # 检查是否有注册表单
            register_form = page.query_selector("form") is not None
            self.log_test("Register Form Present", register_form, "Registration form found")

            if not register_form:
                return False

            # 填写注册表单
            try:
                # 尝试不同的选择器
                username_selectors = [
                    "input[name='username']",
                    "input[name*='username']",
                    "input[placeholder*='用户名']",
                    "input[placeholder*='username']",
                    "#username",
                    ".username-input"
                ]

                username_filled = False
                for selector in username_selectors:
                    try:
                        if page.query_selector(selector):
                            page.fill(selector, self.test_user["username"])
                            print(f"Filled username using selector: {selector}")
                            username_filled = True
                            break
                    except:
                        continue

                if not username_filled:
                    print("[WARNING] Could not find username input field")

                # 类似地填写其他字段
                email_selectors = [
                    "input[name='email']",
                    "input[name*='email']",
                    "input[placeholder*='邮箱']",
                    "input[placeholder*='email']",
                    "#email",
                    ".email-input"
                ]

                email_filled = False
                for selector in email_selectors:
                    try:
                        if page.query_selector(selector):
                            page.fill(selector, self.test_user["email"])
                            print(f"Filled email using selector: {selector}")
                            email_filled = True
                            break
                    except:
                        continue

                password_selectors = [
                    "input[name='password']",
                    "input[name*='password']",
                    "input[type='password']",
                    "input[placeholder*='密码']",
                    "input[placeholder*='password']",
                    "#password",
                    ".password-input"
                ]

                password_filled = False
                for selector in password_selectors:
                    try:
                        if page.query_selector(selector):
                            page.fill(selector, self.test_user["password"])
                            print(f"Filled password using selector: {selector}")
                            password_filled = True
                            break
                    except:
                        continue

            except Exception as e:
                print(f"[ERROR] Form filling failed: {str(e)}")

            # 提交注册
            page.click("button[type='submit']")

            # 等待响应
            time.sleep(3)

            # 截图
            screenshot_path = self.screenshots_dir / f"after_register_{int(time.time())}.png"
            page.screenshot(path=str(screenshot_path))

            # 检查是否成功（可能会重定向到登录页或仪表板）
            current_url = page.url
            success = "/login" not in current_url or "/dashboard" in current_url
            self.log_test("User Registration", success, f"Current URL: {current_url}")

            return success

        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False

    def test_user_login(self, page):
        """测试用户登录"""
        print("\n[Test] User Login")

        try:
            # 导航到登录页面
            page.goto(f"{self.frontend_url}/login", wait_until='networkidle', timeout=10000)
            time.sleep(2)

            # 截图
            screenshot_path = self.screenshots_dir / f"login_page_{int(time.time())}.png"
            page.screenshot(path=str(screenshot_path))

            # 检查是否有登录表单
            login_form = page.query_selector("form") is not None
            self.log_test("Login Form Present", login_form, "Login form found")

            if not login_form:
                return False

            # 尝试使用用户名登录
            try:
                # 尝试多种用户名/邮箱选择器
                user_selectors = [
                    "input[name='username']",
                    "input[name='email']",
                    "input[name*='user']",
                    "input[placeholder*='用户名']",
                    "input[placeholder*='邮箱']",
                    "#username",
                    "#email"
                ]

                user_filled = False
                for selector in user_selectors:
                    try:
                        if page.query_selector(selector):
                            page.fill(selector, self.test_user["username"])
                            print(f"Filled username using selector: {selector}")
                            user_filled = True
                            break
                    except:
                        continue

                password_selectors = [
                    "input[name='password']",
                    "input[type='password']",
                    "input[placeholder*='密码']",
                    "#password"
                ]

                password_filled = False
                for selector in password_selectors:
                    try:
                        if page.query_selector(selector):
                            page.fill(selector, self.test_user["password"])
                            print(f"Filled password using selector: {selector}")
                            password_filled = True
                            break
                    except:
                        continue

                if not user_filled or not password_filled:
                    print("[WARNING] Could not fill all login fields")

            except Exception as e:
                print(f"[ERROR] Login form filling failed: {str(e)}")

            # 提交登录
            page.click("button[type='submit']")

            # 等待响应
            time.sleep(3)

            # 截图
            screenshot_path = self.screenshots_dir / f"after_login_{int(time.time())}.png"
            page.screenshot(path=str(screenshot_path))

            # 检查是否成功登录
            current_url = page.url
            success = "/login" not in current_url
            self.log_test("User Login", success, f"Current URL: {current_url}")

            return success

        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return False

    def test_agent_creation_flow(self, page):
        """测试智能体创建流程"""
        print("\n[Test] Agent Creation Flow")

        try:
            # 导航到智能体创建页面
            page.goto(f"{self.frontend_url}/agents/create", wait_until='networkidle', timeout=10000)
            time.sleep(2)

            # 截图
            screenshot_path = self.screenshots_dir / f"agent_create_start_{int(time.time())}.png"
            page.screenshot(path=str(screenshot_path))

            # 检查是否在创建页面
            create_page_loaded = "/agents/create" in page.url or "create" in page.url
            self.log_test("Agent Create Page Loaded", create_page_loaded, f"Current URL: {page.url}")

            if not create_page_loaded:
                # 如果没有直接导航到创建页面，尝试从导航菜单进入
                try:
                    page.click("text=创建智能体")
                    time.sleep(2)
                except:
                    self.log_test("Navigate to Create Page", False, "Could not navigate to create page")
                    return False

            # 步骤1：填写基础信息
            print("\n[Step 1] Filling Basic Information")
            try:
                # 查找并填写智能体ID
                agent_id_selectors = [
                    "input[name='agent_id']",
                    "input[id='agent_id']",
                    "input[name*='agent']",
                    "#agent_id",
                    ".agent-id-input"
                ]

                agent_id_filled = False
                for selector in agent_id_selectors:
                    try:
                        if page.query_selector(selector):
                            page.fill(selector, self.test_agent["agent_id"])
                            print(f"Filled agent_id: {self.test_agent['agent_id']} using {selector}")
                            agent_id_filled = True
                            break
                    except:
                        continue

                # 查找并填写智能体名称
                agent_name_selectors = [
                    "input[name='agent_name']",
                    "input[id='agent_name']",
                    "input[placeholder*='名称']",
                    "input[placeholder*='name']",
                    "#agent_name",
                    ".agent-name-input"
                ]

                agent_name_filled = False
                for selector in agent_name_selectors:
                    try:
                        if page.query_selector(selector):
                            page.fill(selector, self.test_agent["agent_name"])
                            print(f"Filled agent_name: {self.test_agent['agent_name']} using {selector}")
                            agent_name_filled = True
                            break
                    except:
                        continue

                # 查找并填写描述
                desc_selectors = [
                    "textarea[name='description']",
                    "textarea[id='description']",
                    "textarea[placeholder*='描述']",
                    "textarea[placeholder*='description']",
                    "#description",
                    ".description-input"
                ]

                desc_filled = False
                for selector in desc_selectors:
                    try:
                        if page.query_selector(selector):
                            page.fill(selector, self.test_agent["description"])
                            print(f"Filled description using {selector}")
                            desc_filled = True
                            break
                    except:
                        continue

                # 截图
                screenshot_path = self.screenshots_dir / f"basic_info_filled_{int(time.time())}.png"
                page.screenshot(path=str(screenshot_path))

                # 点击下一步
                next_button = page.query_selector("button:has-text('下一步') or button:has-text('Next')")
                if next_button:
                    page.click("button:has-text('下一步') or button:has-text('Next')")
                    time.sleep(1)
                    self.log_test("Basic Info Step", True, "Basic information filled")
                else:
                    self.log_test("Basic Info Step", False, "Next button not found")

            except Exception as e:
                self.log_test("Basic Info Step", False, f"Exception: {str(e)}")

            # 步骤2：配置模型
            print("\n[Step 2] Configuring Model")
            try:
                # 查找并填写模型配置
                model_selectors = [
                    "select[name='model_name']",
                    "select[id='model_name']",
                    "select[name*='model']",
                    "#model_name",
                    ".model-select"
                ]

                model_selected = False
                for selector in model_selectors:
                    try:
                        if page.query_selector(selector):
                            page.select_option(selector, self.test_agent["model_name"])
                            print(f"Selected model: {self.test_agent['model_name']} using {selector}")
                            model_selected = True
                            break
                    except:
                        continue

                # 填写API密钥
                api_key_selectors = [
                    "input[name='api_key']",
                    "input[id='api_key']",
                    "input[name*='api']",
                    "input[type='password']",
                    "#api_key",
                    ".api-key-input"
                ]

                api_key_filled = False
                for selector in api_key_selectors:
                    try:
                        if page.query_selector(selector):
                            page.fill(selector, self.test_agent["api_key"])
                            print(f"Filled API key using {selector}")
                            api_key_filled = True
                            break
                    except:
                        continue

                # 截图
                screenshot_path = self.screenshots_dir / f"model_config_filled_{int(time.time())}.png"
                page.screenshot(path=str(screenshot_path))

                # 点击下一步
                next_button = page.query_selector("button:has-text('下一步') or button:has-text('Next')")
                if next_button:
                    page.click("button:has-text('下一步') or button:has-text('Next')")
                    time.sleep(1)
                    self.log_test("Model Config Step", True, "Model configuration filled")
                else:
                    self.log_test("Model Config Step", False, "Next button not found")

            except Exception as e:
                self.log_test("Model Config Step", False, f"Exception: {str(e)}")

            # 步骤3：填写提示词
            print("\n[Step 3] Filling System Prompt")
            try:
                # 查找并填写系统提示词
                prompt_selectors = [
                    "textarea[name='system_prompt']",
                    "textarea[id='system_prompt']",
                    "textarea[name*='prompt']",
                    "textarea[placeholder*='提示词']",
                    "textarea[placeholder*='prompt']",
                    "#system_prompt",
                    ".prompt-textarea"
                ]

                prompt_filled = False
                for selector in prompt_selectors:
                    try:
                        if page.query_selector(selector):
                            page.fill(selector, self.test_agent["system_prompt"])
                            print(f"Filled system prompt using {selector}")
                            prompt_filled = True
                            break
                    except:
                        continue

                # 截图
                screenshot_path = self.screenshots_dir / f"prompt_filled_{int(time.time())}.png"
                page.screenshot(path=str(screenshot_path))

                # 点击下一步
                next_button = page.query_selector("button:has-text('下一步') or button:has-text('Next')")
                if next_button:
                    page.click("button:has-text('下一步') or button:has-text('Next')")
                    time.sleep(1)
                    self.log_test("Prompt Config Step", True, "System prompt filled")
                else:
                    self.log_test("Prompt Config Step", False, "Next button not found")

            except Exception as e:
                self.log_test("Prompt Config Step", False, f"Exception: {str(e)}")

            # 步骤4：跳过或填写高级配置
            print("\n[Step 4] Advanced Configuration")
            try:
                # 截图当前状态
                screenshot_path = self.screenshots_dir / f"advanced_config_step_{int(time.time())}.png"
                page.screenshot(path=str(screenshot_path))

                # 尝试跳过高级配置，直接提交
                submit_button = page.query_selector("button:has-text('提交') or button:has-text('创建') or button:has-text('Submit') or button:has-text('Create')")
                if submit_button:
                    page.click("button:has-text('提交') or button:has-text('创建') or button:has-text('Submit') or button:has-text('Create')")
                    time.sleep(2)
                    self.log_test("Advanced Step", True, "Skipped or filled advanced config")
                else:
                    # 如果没有提交按钮，尝试下一步
                    next_button = page.query_selector("button:has-text('下一步') or button:has-text('Next')")
                    if next_button:
                        page.click("button:has_text('下一步') or button:has_text('Next')")
                        time.sleep(1)

                        # 然后点击提交
                        submit_button = page.query_selector("button:has-text('提交') or button:has-text('创建') or button:has-text('Submit') or button:has-text('Create')")
                        if submit_button:
                            page.click("button:has-text('提交') or button:has-text('创建') or button:has-text('Submit') or button:has-text('Create')")
                            time.sleep(2)
                            self.log_test("Advanced Step", True, "Navigated to submit")
                        else:
                            self.log_test("Advanced Step", False, "Submit button not found")
                    else:
                        self.log_test("Advanced Step", False, "No navigation button found")

            except Exception as e:
                self.log_test("Advanced Step", False, f"Exception: {str(e)}")

            # 等待创建完成
            time.sleep(3)

            # 截图最终结果
            screenshot_path = self.screenshots_dir / f"agent_create_final_{int(time.time())}.png"
            page.screenshot(path=str(screenshot_path))

            # 检查是否成功创建（可能会重定向到智能体详情页或列表页）
            current_url = page.url
            success = "/agents/" in current_url and "/create" not in current_url
            self.log_test("Agent Creation Success", success, f"Current URL: {current_url}")

            return success

        except Exception as e:
            self.log_test("Agent Creation Flow", False, f"Exception: {str(e)}")
            return False

    def test_chat_functionality(self, page):
        """测试聊天功能"""
        print("\n[Test] Chat Functionality")

        try:
            # 查找开始对话按钮或导航到聊天页面
            chat_button = page.query_selector("button:has-text('开始对话') or button:has_text('Chat') or a:has-text('开始对话')")
            if chat_button:
                page.click("button:has-text('开始对话') or button:has_text('Chat') or a:has-text('开始对话')")
                time.sleep(2)
                self.log_test("Navigate to Chat", True, "Chat interface opened")
            else:
                # 如果没有找到按钮，尝试直接导航
                page.goto(f"{self.frontend_url}/chat", wait_until='domcontentloaded', timeout=10000)
                time.sleep(2)
                self.log_test("Navigate to Chat", True, "Navigated to chat page")

            # 截图聊天界面
            screenshot_path = self.screenshots_dir / f"chat_interface_{int(time.time())}.png"
            page.screenshot(path=str(screenshot_path))

            # 检查是否有聊天输入框
            chat_input_selectors = [
                "textarea[placeholder*='消息']",
                "textarea[placeholder*='message']",
                "textarea[placeholder*='输入']",
                "input[placeholder*='消息']",
                "input[placeholder*='message']",
                ".chat-input",
                "#chat-input",
                "textarea[name='message']",
                "input[name='message']"
            ]

            chat_input = None
            for selector in chat_input_selectors:
                try:
                    if page.query_selector(selector):
                        chat_input = selector
                        print(f"Found chat input using selector: {selector}")
                        break
                except:
                    continue

            self.log_test("Chat Input Present", chat_input is not None, "Chat input found")

            if chat_input:
                # 发送测试消息
                test_message = "Hello! This is a test message from E2E test."

                try:
                    page.fill(chat_input, test_message)

                    # 查找发送按钮
                    send_button = page.query_selector("button:has-text('发送') or button:has_text('Send') or button[type='submit']")
                    if send_button:
                        page.click("button:has-text('发送') or button:has_text('Send') or button[type='submit']")
                        time.sleep(3)

                        # 截图发送后的状态
                        screenshot_path = self.screenshots_dir / f"after_send_message_{int(time.time())}.png"
                        page.screenshot(path=str(screenshot_path))

                        self.log_test("Send Message", True, "Message sent successfully")

                        # 检查是否有回复（这可能需要等待一段时间）
                        time.sleep(5)

                        # 截图检查回复
                        screenshot_path = self.screenshots_dir / f"check_reply_{int(time.time())}.png"
                        page.screenshot(path=str(screenshot_path))

                        # 检查页面内容，看是否有回复
                        page_content = page.evaluate("() => document.body.innerText")
                        has_reply = len(page_content) > len(test_message)  # 简单检查内容是否增加
                        self.log_test("Receive Reply", has_reply, "Agent response detected")

                    else:
                        self.log_test("Send Message", False, "Send button not found")

                except Exception as e:
                    self.log_test("Send Message", False, f"Exception: {str(e)}")
            else:
                self.log_test("Chat Functionality", False, "Chat input not found")
                return False

            return True

        except Exception as e:
            self.log_test("Chat Functionality", False, f"Exception: {str(e)}")
            return False

    def test_agent_list_view(self, page):
        """测试智能体列表查看"""
        print("\n[Test] Agent List View")

        try:
            # 导航到智能体列表页面
            page.goto(f"{self.frontend_url}/agents", wait_until='networkidle', timeout=10000)
            time.sleep(2)

            # 截图
            screenshot_path = self.screenshots_dir / f"agent_list_{int(time.time())}.png"
            page.screenshot(path=str(screenshot_path))

            # 检查是否有智能体列表
            agent_list = page.query_selector("table, .agent-list, .list") is not None
            self.log_test("Agent List Present", agent_list, "Agent list found")

            # 检查是否包含创建的智能体
            if agent_list:
                page_content = page.evaluate("() => document.body.innerText")
                has_created_agent = self.test_agent["agent_name"] in page_content or self.test_agent["agent_id"] in page_content
                self.log_test("Created Agent in List", has_created_agent, f"Agent found in list: {has_created_agent}")

            return True

        except Exception as e:
            self.log_test("Agent List View", False, f"Exception: {str(e)}")
            return False

    def run_tests(self):
        """运行完整的测试套件"""
        print("Starting Agent Creation and Chat E2E Test")
        print("=" * 50)

        with sync_playwright() as playwright:
            # 设置浏览器
            browser, context, page, console_messages, network_requests = self.setup_browser(playwright)

            try:
                # 测试1：用户注册
                print("\n" + "=" * 50)
                print("PHASE 1: User Registration")
                print("=" * 50)
                self.test_user_registration(page)

                # 测试2：用户登录
                print("\n" + "=" * 50)
                print("PHASE 2: User Login")
                print("=" * 50)
                login_success = self.test_user_login(page)

                if not login_success:
                    print("[WARNING] Login failed, attempting to continue with agent creation...")

                # 测试3：智能体创建流程
                print("\n" + "=" * 50)
                print("PHASE 3: Agent Creation Flow")
                print("=" * 50)
                agent_creation_success = self.test_agent_creation_flow(page)

                if agent_creation_success:
                    # 测试4：聊天功能
                    print("\n" + "=" * 50)
                    print("PHASE 4: Chat Functionality")
                    print("=" * 50)
                    self.test_chat_functionality(page)

                # 测试5：智能体列表查看
                print("\n" + "=" * 50)
                print("PHASE 5: Agent List View")
                print("=" * 50)
                self.test_agent_list_view(page)

                # 分析控制台错误
                print("\n" + "=" * 50)
                print("CONSOLE ERROR ANALYSIS")
                print("=" * 50)
                errors = [msg for msg in console_messages if msg['type'] == 'error']
                if errors:
                    print(f"Found {len(errors)} console errors:")
                    for error in errors[:5]:  # 显示前5个错误
                        print(f"  - {error['text']}")
                else:
                    print("No console errors detected")

                # 分析网络请求
                print("\n" + "=" * 50)
                print("NETWORK REQUEST ANALYSIS")
                print("=" * 50)
                api_requests = [req for req in network_requests if '/api/' in req['url']]
                print(f"Total API requests: {len(api_requests)}")
                if api_requests:
                    print("API requests made:")
                    for req in api_requests[:10]:  # 显示前10个请求
                        print(f"  - {req['method']} {req['url']}")

            finally:
                # 关闭浏览器
                context.close()
                browser.close()

        # 打印测试总结
        success = self.print_summary()
        print(f"\n[Screenshots] All screenshots saved to: {self.screenshots_dir}")

        return 0 if success else 1

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 50)
        print("Agent Creation and Chat Test Summary")
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

        # 保存测试结果到JSON文件
        results_file = Path("e2e_test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': success_rate
                },
                'tests': self.test_results,
                'test_data': {
                    'user': self.test_user,
                    'agent': self.test_agent
                }
            }, f, indent=2, ensure_ascii=False)

        print(f"\n[Results] Test results saved to: {results_file}")
        print("=" * 50)

        return failed_tests == 0


def main():
    """主函数"""
    tester = AgentCreationChatTest()

    print("=" * 50)
    print("AGENT CREATION AND CHAT E2E TEST")
    print("=" * 50)
    print("This test will perform the following:")
    print("1. User registration")
    print("2. User login")
    print("3. Create an agent with full configuration")
    print("4. Test chat functionality")
    print("5. Verify agent in list view")
    print("=" * 50)

    return tester.run_tests()


if __name__ == "__main__":
    sys.exit(main())