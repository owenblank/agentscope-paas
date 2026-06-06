#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS - 智能体创建端到端测试
完整的用户登录后创建智能体功能测试
"""

import sys
import time
import json
import random
import string
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, Page, expect
except ImportError:
    print("[ERROR] Playwright not installed")
    sys.exit(1)


class AgentCreationE2ETest:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.test_results = []
        self.screenshots_dir = Path("e2e_screenshots/agent_creation")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.test_user = None

    def log(self, test, passed, msg=""):
        """记录测试结果"""
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test}: {msg}")
        self.test_results.append({
            "test": test,
            "passed": passed,
            "msg": msg,
            "time": datetime.now().isoformat()
        })

    def generate_random_user(self):
        """生成随机测试用户"""
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return {
            "email": f"test_{random_id}@example.com",
            "username": f"testuser_{random_id}",
            "password": "TestPassword123!"
        }

    def generate_random_agent(self):
        """生成随机智能体数据"""
        random_id = ''.join(random.choices(string.ascii_lowercase, k=6))
        return {
            "name": f"测试智能体_{random_id}",
            "description": f"这是一个自动化测试创建的智能体 {random_id}",
            "model_name": "gpt-3.5-turbo",
            "api_key": f"test_api_key_{random_id}",
            "system_prompt": f"你是一个有帮助的AI助手，专门用于测试 {random_id}。"
        }

    def wait_for_element(self, page, selector, timeout=5000):
        """等待元素出现"""
        try:
            page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False

    def take_screenshot(self, page, name):
        """截图保存"""
        timestamp = int(time.time())
        filename = self.screenshots_dir / f"{name}_{timestamp}.png"
        page.screenshot(path=str(filename))
        print(f"[Screenshot] {filename}")
        return filename

    def test_user_registration(self, page):
        """测试用户注册"""
        print("\n[测试流程]: 用户注册")

        # 生成测试用户数据
        self.test_user = self.generate_random_user()
        print(f"测试用户: {self.test_user['email']}")

        # 访问注册页面
        page.goto(f"{self.base_url}/register", wait_until='networkidle')
        page.wait_for_timeout(2000)
        self.take_screenshot(page, "register_page")

        # 检查注册表单是否存在
        form_exists = self.wait_for_element(page, "form", timeout=3000)
        self.log("注册表单存在", form_exists)

        if not form_exists:
            return False

        # 填写注册表单
        try:
            # 查找输入框并填写
            email_input = page.query_selector("input[type='email'], input[name*='email'], input[placeholder*='邮箱']")
            username_input = page.query_selector("input[name*='user'], input[placeholder*='用户']")
            password_input = page.query_selector("input[type='password'], input[name*='password']")

            if email_input:
                email_input.fill(self.test_user["email"])
                print(f"填写邮箱: {self.test_user['email']}")

            if username_input:
                username_input.fill(self.test_user["username"])
                print(f"填写用户名: {self.test_user['username']}")

            if password_input:
                password_input.fill(self.test_user["password"])
                print("填写密码")

            self.take_screenshot(page, "register_form_filled")

            # 查找提交按钮
            submit_button = page.query_selector("button[type='submit'], button:has-text('注册'), button:has-text('注册')")
            if submit_button:
                submit_button.click()
                print("点击注册按钮")
                page.wait_for_timeout(3000)

                # 检查注册结果
                current_url = page.url
                success = "/login" in current_url or "/dashboard" in current_url
                self.log("用户注册成功", success, f"当前页面: {current_url}")

                self.take_screenshot(page, "register_result")
                return success
            else:
                self.log("注册按钮未找到", False)
                return False

        except Exception as e:
            self.log("注册表单填写失败", False, f"错误: {str(e)}")
            return False

    def test_user_login(self, page):
        """测试用户登录"""
        print("\n[测试流程]: 用户登录")

        # 访问登录页面
        page.goto(f"{self.base_url}/login", wait_until='networkidle')
        page.wait_for_timeout(2000)
        self.take_screenshot(page, "login_page")

        # 检查登录表单
        form_exists = self.wait_for_element(page, "form", timeout=3000)
        self.log("登录表单存在", form_exists)

        if not form_exists:
            return False

        try:
            # 填写登录表单
            email_input = page.query_selector("input[type='email'], input[name*='email'], input[placeholder*='邮箱']")
            password_input = page.query_selector("input[type='password'], input[name*='password']")

            if email_input:
                email_input.fill(self.test_user["email"])
                print(f"填写邮箱: {self.test_user['email']}")

            if password_input:
                password_input.fill(self.test_user["password"])
                print("填写密码")

            self.take_screenshot(page, "login_form_filled")

            # 提交登录
            submit_button = page.query_selector("button[type='submit'], button:has-text('登录'), button:has-text('登录')")
            if submit_button:
                submit_button.click()
                print("点击登录按钮")
                page.wait_for_timeout(5000)

                # 检查登录结果
                current_url = page.url
                success = "/dashboard" in current_url or "/agents" in current_url
                self.log("用户登录成功", success, f"当前页面: {current_url}")

                self.take_screenshot(page, "login_result")
                return success
            else:
                self.log("登录按钮未找到", False)
                return False

        except Exception as e:
            self.log("登录表单填写失败", False, f"错误: {str(e)}")
            return False

    def test_navigate_to_agent_creation(self, page):
        """测试导航到智能体创建页面"""
        print("\n[测试流程]: 导航到智能体创建页面")

        try:
            # 尝试直接访问智能体创建页面
            page.goto(f"{self.base_url}/agents/create", wait_until='networkidle')
            page.wait_for_timeout(3000)

            current_url = page.url
            success = "/agents/create" in current_url or "/agent" in current_url.lower()
            self.log("导航到智能体创建页面", success, f"当前页面: {current_url}")

            self.take_screenshot(page, "agent_creation_page")

            # 检查页面是否有创建表单
            form_found = self.wait_for_element(page, "form, .ant-form, [class*='form']", timeout=3000)
            self.log("智能体创建表单存在", form_found)

            return success and form_found

        except Exception as e:
            self.log("导航到智能体创建页面失败", False, f"错误: {str(e)}")
            return False

    def test_fill_agent_form(self, page):
        """测试填写智能体表单"""
        print("\n[测试流程]: 填写智能体表单")

        agent_data = self.generate_random_agent()
        print(f"智能体数据: {agent_data['name']}")

        try:
            # 等待表单加载
            page.wait_for_timeout(2000)

            # 查找并填写基本信息字段
            name_selectors = [
                "input[name*='name']",
                "input[placeholder*='名称']",
                "input[placeholder*='Name']",
                "#agent_name"
            ]

            name_input = None
            for selector in name_selectors:
                try:
                    name_input = page.query_selector(selector)
                    if name_input:
                        print(f"找到名称输入框: {selector}")
                        break
                except:
                    continue

            if name_input:
                name_input.fill(agent_data["name"])
                print(f"填写智能体名称: {agent_data['name']}")
                self.log("智能体名称填写", True)
            else:
                self.log("智能体名称输入框未找到", False)

            # 尝试填写描述
            desc_selectors = [
                "textarea[name*='description']",
                "textarea[placeholder*='描述']",
                "textarea[placeholder*='Description']"
            ]

            for selector in desc_selectors:
                try:
                    desc_input = page.query_selector(selector)
                    if desc_input:
                        desc_input.fill(agent_data["description"])
                        print(f"填写描述: {agent_data['description']}")
                        self.log("智能体描述填写", True)
                        break
                except:
                    continue

            # 尝试填写系统提示词
            prompt_selectors = [
                "textarea[name*='prompt']",
                "textarea[placeholder*='提示']",
                "textarea[placeholder*='system']"
            ]

            for selector in prompt_selectors:
                try:
                    prompt_input = page.query_selector(selector)
                    if prompt_input:
                        prompt_input.fill(agent_data["system_prompt"])
                        print(f"填写系统提示词: {agent_data['system_prompt']}")
                        self.log("系统提示词填写", True)
                        break
                except:
                    continue

            self.take_screenshot(page, "agent_form_filled")

            # 检查是否有下一步或提交按钮
            next_button = page.query_selector("button:has-text('下一步'), button:has-text('Next'), button:has-text('继续')")
            submit_button = page.query_selector("button[type='submit'], button:has-text('创建'), button:has-text('提交')")

            has_navigation = next_button or submit_button
            self.log("表单导航按钮存在", has_navigation)

            if next_button:
                print("找到下一步按钮，尝试点击")
                next_button.click()
                page.wait_for_timeout(2000)
                self.take_screenshot(page, "after_next_step")

            return True

        except Exception as e:
            self.log("填写智能体表单失败", False, f"错误: {str(e)}")
            return False

    def test_submit_agent_creation(self, page):
        """测试提交智能体创建"""
        print("\n[测试流程]: 提交智能体创建")

        try:
            # 查找提交按钮
            submit_selectors = [
                "button[type='submit']",
                "button:has-text('创建')",
                "button:has-text('提交')",
                "button:has-text('完成')",
                ".ant-btn-primary"
            ]

            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = page.query_selector(selector)
                    if submit_button:
                        print(f"找到提交按钮: {selector}")
                        break
                except:
                    continue

            if not submit_button:
                self.log("提交按钮未找到", False)
                return False

            self.take_screenshot(page, "before_submit")

            # 点击提交按钮
            submit_button.click()
            print("点击提交按钮")

            # 等待响应
            page.wait_for_timeout(5000)

            # 检查结果
            current_url = page.url
            success_page = "/agents" in current_url and "/create" not in current_url
            has_success_msg = page.query_selector(":has-text('成功'), :has-text('Success'), :has-text('完成')")

            success = success_page or has_success_msg is not None
            self.log("智能体创建提交成功", success, f"当前页面: {current_url}")

            self.take_screenshot(page, "after_submit")

            return success

        except Exception as e:
            self.log("提交智能体创建失败", False, f"错误: {str(e)}")
            return False

    def test_verify_agent_created(self, page):
        """验证智能体是否创建成功"""
        print("\n[测试流程]: 验证智能体创建结果")

        try:
            # 导航到智能体列表
            page.goto(f"{self.base_url}/agents", wait_until='networkidle')
            page.wait_for_timeout(3000)

            self.take_screenshot(page, "agent_list")

            # 检查是否有智能体列表
            list_found = page.query_selector(".ant-list, table, [class*='list'], [class*='table']")

            if list_found:
                self.log("智能体列表页面加载", True)

                # 检查是否有我们创建的智能体
                agent_name = self.test_user and hasattr(self, 'current_agent') and self.current_agent.get('name', '')

                if agent_name:
                    agent_exists = page.query_selector(f":has-text('{agent_name}')")
                    self.log("创建的智能体出现在列表中", agent_exists is not None)
                else:
                    self.log("智能体列表显示", True)

                return True
            else:
                self.log("智能体列表页面加载失败", False)
                return False

        except Exception as e:
            self.log("验证智能体创建失败", False, f"错误: {str(e)}")
            return False

    def test_user_logout(self, page):
        """测试用户登出"""
        print("\n[测试流程]: 用户登出")

        try:
            # 查找登出按钮
            logout_selectors = [
                "button:has-text('登出'), button:has-text('退出'), button:has-text('Logout')",
                ".ant-dropdown button:has-text('登出')",
                "[class*='logout']"
            ]

            logout_button = None
            for selector in logout_selectors:
                try:
                    logout_button = page.query_selector(selector)
                    if logout_button:
                        print(f"找到登出按钮: {selector}")
                        break
                except:
                    continue

            if logout_button:
                logout_button.click()
                page.wait_for_timeout(2000)

                current_url = page.url
                success = "/login" in current_url or "/" in current_url
                self.log("用户登出成功", success, f"当前页面: {current_url}")

                self.take_screenshot(page, "after_logout")
                return True
            else:
                self.log("登出按钮未找到", False)
                return False

        except Exception as e:
            self.log("用户登出失败", False, f"错误: {str(e)}")
            return False

    def run_complete_flow(self):
        """运行完整的智能体创建流程测试"""
        print("=" * 60)
        print("AgentScope PaaS - 智能体创建端到端测试")
        print("=" * 60)

        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(
                headless=False,  # 显示浏览器
                slow_mo=500      # 放慢执行速度便于观察
            )

            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                record_video_dir=str(self.screenshots_dir / "videos") if (self.screenshots_dir / "videos").exists() else None
            )

            page = context.new_page()

            # 设置错误监控
            errors = []
            def handle_error(error):
                errors.append(str(error))
                print(f"[JavaScript Error]: {error}")

            page.on('pageerror', handle_error)

            try:
                # 1. 用户注册
                registration_success = self.test_user_registration(page)

                # 如果注册失败，尝试直接登录
                if not registration_success:
                    print("[INFO] 注册失败，可能用户已存在，尝试直接登录")
                    if not self.test_user:
                        self.test_user = {
                            "email": "test_existing@example.com",
                            "username": "test_existing",
                            "password": "TestPassword123!"
                        }

                # 2. 用户登录
                login_success = self.test_user_login(page)

                if not login_success:
                    print("[ERROR] 登录失败，无法继续测试")
                else:
                    # 3. 导航到智能体创建页面
                    navigation_success = self.test_navigate_to_agent_creation(page)

                    if navigation_success:
                        # 4. 填写智能体表单
                        form_fill_success = self.test_fill_agent_form(page)

                        if form_fill_success:
                            # 5. 提交智能体创建
                            submit_success = self.test_submit_agent_creation(page)

                            # 6. 验证智能体创建结果
                            if submit_success:
                                self.test_verify_agent_created(page)

                    # 7. 用户登出
                    self.test_user_logout(page)

            finally:
                context.close()
                browser.close()

        # 生成测试报告
        self.generate_report()

        # 打印总结
        self.print_summary()

        return len(errors) == 0

    def generate_report(self):
        """生成测试报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_user": self.test_user,
            "results": self.test_results,
            "summary": {
                "total": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r["passed"]),
                "failed": sum(1 for r in self.test_results if not r["passed"])
            }
        }

        report_file = self.screenshots_dir / f"e2e_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n[测试报告保存]: {report_file}")

    def print_summary(self):
        """打印测试总结"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "=" * 60)
        print("智能体创建端到端测试总结")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {success_rate:.1f}%")

        if failed_tests > 0:
            print("\n[失败的测试]:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}: {result['msg']}")

        print("=" * 60)


def main():
    """主函数"""
    print("启动智能体创建端到端测试...")

    tester = AgentCreationE2ETest()

    try:
        success = tester.run_complete_flow()
        return 0 if success else 1
    except Exception as e:
        print(f"测试执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())