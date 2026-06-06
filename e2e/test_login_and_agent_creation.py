#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS - 登录和智能体创建完整流程测试
使用Playwright模拟用户从登录到创建智能体的完整操作流程
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, Page, Browser
except ImportError:
    print("[ERROR] Playwright not installed")
    print("Please run: pip install playwright")
    print("Then run: playwright install chromium")
    sys.exit(1)


class LoginAndAgentCreationTest:
    def __init__(self, base_url="http://localhost:5173"):
        self.base_url = base_url
        self.test_results = []
        self.screenshots_dir = Path("e2e_screenshots/full_flow")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        # 测试用户凭证
        self.test_user = {
            "email": "test@example.com",
            "password": "SecurePass123"
        }

        # 测试智能体数据
        self.test_agent = {
            "agent_id": "test_playwright_agent",
            "agent_name": "Playwright测试智能体",
            "agent_description": "这是一个通过Playwright自动化测试创建的智能体",
            "model_provider": "dashscope",
            "model_name": "qwen-max",
            "api_key": "test-api-key-123456",
            "system_prompt": "你是一个专业的测试助手，专门用于验证AgentScope PaaS平台的创建智能体功能。"
        }

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

    def screenshot(self, page, name):
        """截图保存"""
        timestamp = int(time.time())
        filename = self.screenshots_dir / f"{name}_{timestamp}.png"
        page.screenshot(path=str(filename), full_page=True)
        print(f"[Screenshot] {filename}")
        return filename

    def test_login(self, page: Page):
        """测试登录流程"""
        print("\n[测试]: 用户登录流程")

        try:
            # 访问登录页面
            page.goto(f"{self.base_url}/login", wait_until='networkidle')
            page.wait_for_timeout(2000)
            self.screenshot(page, "01_login_page")

            # 检查登录页面元素
            email_input = page.query_selector("input[type='email']")
            password_input = page.query_selector("input[type='password']")
            submit_button = page.query_selector("button[type='submit']")

            self.log("登录页面加载",
                    email_input is not None and password_input is not None and submit_button is not None,
                    "登录页面包含必要的表单元素")

            if not all([email_input, password_input, submit_button]):
                return False

            # 填写登录表单
            print(f"输入测试用户邮箱: {self.test_user['email']}")
            page.fill("input[type='email']", self.test_user['email'])

            print("输入测试用户密码")
            page.fill("input[type='password']", self.test_user['password'])

            self.screenshot(page, "02_login_form_filled")

            # 点击登录按钮
            print("点击登录按钮")
            page.click("button[type='submit']")

            # 等待登录完成
            page.wait_for_timeout(3000)
            self.screenshot(page, "03_after_login")

            # 检查是否成功登录（可能跳转到首页或显示登录成功消息）
            current_url = page.url
            login_success = "/login" not in current_url

            self.log("用户登录成功", login_success, f"登录后当前URL: {current_url}")

            return login_success

        except Exception as e:
            self.log("用户登录流程", False, f"登录过程异常: {str(e)}")
            self.screenshot(page, "login_error")
            return False

    def test_navigate_to_agent_creation(self, page: Page):
        """测试导航到智能体创建页面"""
        print("\n[测试]: 导航到智能体创建页面")

        try:
            # 尝试多种方式导航到创建页面
            # 方法1: 直接访问URL
            print(f"直接访问智能体创建页面: {self.base_url}/agents/create")
            page.goto(f"{self.base_url}/agents/create", wait_until='networkidle')
            page.wait_for_timeout(3000)
            self.screenshot(page, "04_agent_create_page")

            # 检查是否成功到达创建页面
            current_url = page.url
            page_content = page.content()

            # 检查页面标题或关键元素
            is_create_page = (
                "创建智能体" in page_content or
                "agent" in current_url.lower() or
                "create" in current_url.lower()
            )

            self.log("导航到智能体创建页面", is_create_page, f"当前URL: {current_url}")

            if not is_create_page:
                # 方法2: 通过导航菜单
                print("尝试通过导航菜单访问")
                page.goto(f"{self.base_url}", wait_until='networkidle')
                page.wait_for_timeout(2000)

                # 查找可能的导航链接
                nav_links = page.query_selector_all("a")
                for link in nav_links:
                    text = link.text_content() or ""
                    href = link.get_attribute("href") or ""
                    if "智能体" in text or "agent" in text.lower() or "create" in text.lower():
                        print(f"找到导航链接: {text} -> {href}")
                        link.click()
                        page.wait_for_timeout(2000)
                        break

                self.screenshot(page, "05_after_nav_click")

            return True

        except Exception as e:
            self.log("导航到智能体创建页面", False, f"导航过程异常: {str(e)}")
            self.screenshot(page, "nav_error")
            return False

    def test_agent_creation_process(self, page: Page):
        """测试智能体创建流程"""
        print("\n[测试]: 智能体创建流程")

        try:
            # 等待页面完全加载
            page.wait_for_timeout(3000)

            # 检查当前是否在创建页面
            current_url = page.url
            page_content = page.content()

            if "创建智能体" not in page_content and "create" not in current_url.lower():
                self.log("智能体创建页面", False, "当前不在智能体创建页面")
                return False

            self.screenshot(page, "06_creation_page_ready")

            # 步骤1: 检查是否有模板选择，如果有则跳过或选择第一个
            print("检查模板选择步骤")
            template_cards = page.query_selector_all(".ant-card, [class*='template'], [class*='Template']")
            if template_cards:
                print(f"找到 {len(template_cards)} 个模板选项，尝试选择第一个")
                # 尝试点击第一个模板或下一步按钮
                next_buttons = page.query_selector_all("button:has-text('下一步'), button:has-text('Next'), button:has-text('跳过')")
                if next_buttons:
                    next_buttons[0].click()
                    page.wait_for_timeout(1000)

            # 步骤2: 填写基础信息
            print("填写智能体基础信息")
            page.wait_for_timeout(1000)

            # 查找并填写agent_id字段
            agent_id_selectors = [
                "input[name*='agent_id']",
                "input[placeholder*='ID']",
                "input[id*='agent_id']",
                "#agent_id"
            ]

            for selector in agent_id_selectors:
                try:
                    if page.query_selector(selector):
                        page.fill(selector, self.test_agent['agent_id'])
                        print(f"使用选择器 {selector} 填写agent_id")
                        break
                except:
                    continue

            # 查找并填写agent_name字段
            agent_name_selectors = [
                "input[name*='agent_name']",
                "input[placeholder*='名称']",
                "input[id*='agent_name']",
                "#agent_name"
            ]

            for selector in agent_name_selectors:
                try:
                    if page.query_selector(selector):
                        page.fill(selector, self.test_agent['agent_name'])
                        print(f"使用选择器 {selector} 填写agent_name")
                        break
                except:
                    continue

            # 查找并填写描述字段
            desc_selectors = [
                "textarea[name*='description']",
                "textarea[placeholder*='描述']",
                "input[name*='description']",
                "#agent_description"
            ]

            for selector in desc_selectors:
                try:
                    if page.query_selector(selector):
                        page.fill(selector, self.test_agent['agent_description'])
                        print(f"使用选择器 {selector} 填写描述")
                        break
                except:
                    continue

            self.screenshot(page, "07_basic_info_filled")

            # 点击下一步
            next_buttons = page.query_selector_all("button:has-text('下一步'), button:has-text('Next')")
            if next_buttons:
                print("点击下一步按钮")
                next_buttons[0].click()
                page.wait_for_timeout(2000)

            # 步骤3: 填写模型配置
            print("填写模型配置")
            self.screenshot(page, "08_model_config_step")

            # 查找并填写API密钥
            api_key_selectors = [
                "input[name*='api_key']",
                "input[placeholder*='API']",
                "input[id*='api_key']",
                "#api_key"
            ]

            for selector in api_key_selectors:
                try:
                    if page.query_selector(selector):
                        page.fill(selector, self.test_agent['api_key'])
                        print(f"使用选择器 {selector} 填写API密钥")
                        break
                except:
                    continue

            self.screenshot(page, "09_model_config_filled")

            # 继续点击下一步直到提示词配置
            for i in range(3):  # 最多点击3次下一步
                next_buttons = page.query_selector_all("button:has-text('下一步'), button:has-text('Next')")
                if next_buttons:
                    print(f"点击下一步按钮 (第{i+1}次)")
                    next_buttons[0].click()
                    page.wait_for_timeout(2000)
                    self.screenshot(page, f"10_step_{i+4}")
                else:
                    break

            # 步骤4: 填写系统提示词
            print("填写系统提示词")
            prompt_selectors = [
                "textarea[name*='prompt']",
                "textarea[placeholder*='提示词']",
                "textarea[id*='prompt']",
                "#system_prompt"
            ]

            for selector in prompt_selectors:
                try:
                    if page.query_selector(selector):
                        page.fill(selector, self.test_agent['system_prompt'])
                        print(f"使用选择器 {selector} 填写系统提示词")
                        break
                except:
                    continue

            self.screenshot(page, "11_prompt_filled")

            # 步骤5: 提交创建智能体
            print("提交智能体创建")

            # 查找创建按钮
            create_buttons = page.query_selector_all("button:has-text('创建'), button:has-text('提交'), button:has-text('完成')")
            submit_buttons = page.query_selector_all("button[type='submit']")

            all_buttons = create_buttons + submit_buttons
            if all_buttons:
                print(f"找到提交按钮，点击创建")
                all_buttons[0].click()
                page.wait_for_timeout(5000)  # 等待提交完成
                self.screenshot(page, "12_after_submit")
            else:
                print("未找到提交按钮，尝试继续点击下一步")
                next_buttons = page.query_selector_all("button:has-text('下一步'), button:has-text('Next')")
                if next_buttons:
                    next_buttons[0].click()
                    page.wait_for_timeout(3000)

            # 检查创建结果
            final_url = page.url
            final_content = page.content()

            # 判断是否创建成功
            success_indicators = [
                "成功" in final_content,
                "success" in final_content.lower(),
                "/agents/" in final_url,
                "创建成功" in final_content
            ]

            creation_success = any(success_indicators)

            self.log("智能体创建提交", creation_success,
                    f"最终URL: {final_url}, 成功指示器: {success_indicators}")

            return creation_success

        except Exception as e:
            self.log("智能体创建流程", False, f"创建过程异常: {str(e)}")
            self.screenshot(page, "creation_error")
            return False

    def run_complete_test(self):
        """运行完整的测试流程"""
        print("=" * 60)
        print("AgentScope PaaS - 登录和智能体创建完整流程测试")
        print("=" * 60)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # 设置为False以便观察
            page = browser.new_page()

            try:
                # 设置视口大小
                page.set_viewport_size({"width": 1280, "height": 720})

                # 测试1: 登录
                login_success = self.test_login(page)
                if not login_success:
                    print("[警告] 登录失败，但继续测试其他功能")

                # 测试2: 导航到智能体创建页面
                nav_success = self.test_navigate_to_agent_creation(page)
                if not nav_success:
                    print("[警告] 导航失败，尝试继续测试")

                # 测试3: 智能体创建流程
                creation_success = self.test_agent_creation_process(page)

                # 生成测试报告
                self.generate_report()

            finally:
                browser.close()

        return self.test_results

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("测试报告")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests

        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"通过率: {(passed_tests/total_tests*100):.1f}%")

        print("\n详细结果:")
        for result in self.test_results:
            status = "[PASS]" if result['passed'] else "[FAIL]"
            print(f"{status} {result['test']}: {result['msg']}")

        # 保存JSON报告
        report_file = Path("e2e_screenshots") / f"test_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "pass_rate": f"{(passed_tests/total_tests*100):.1f}%"
                },
                "results": self.test_results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n报告已保存至: {report_file}")
        print(f"截图保存在: {self.screenshots_dir}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='AgentScope PaaS - 登录和智能体创建完整流程测试')
    parser.add_argument('--base-url', default='http://localhost:5173',
                       help='Frontend base URL (default: http://localhost:5173)')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode')

    args = parser.parse_args()

    tester = LoginAndAgentCreationTest(base_url=args.base_url)

    # 如果命令行指定了headless，修改浏览器启动模式
    if args.headless:
        original_method = tester.run_complete_test
        def run_with_headless():
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_viewport_size({"width": 1280, "height": 720})

                try:
                    login_success = tester.test_login(page)
                    nav_success = tester.test_navigate_to_agent_creation(page)
                    creation_success = tester.test_agent_creation_process(page)
                    tester.generate_report()
                finally:
                    browser.close()

            return tester.test_results

        tester.run_complete_test = run_with_headless

    results = tester.run_complete_test()

    # 返回退出码
    passed = sum(1 for result in results if result['passed'])
    total = len(results)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()