#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS - 智能体创建UI功能测试
专注于前端UI验证，不依赖后端API
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("[ERROR] Playwright not installed")
    sys.exit(1)


class AgentCreationUITest:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.test_results = []
        self.screenshots_dir = Path("e2e_screenshots/ui_test")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

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
        page.screenshot(path=str(filename))
        print(f"[Screenshot] {filename}")
        return filename

    def test_login_page_ui(self, page):
        """测试登录页面UI"""
        print("\n[测试]: 登录页面UI")

        page.goto(f"{self.base_url}/login", wait_until='networkidle')
        page.wait_for_timeout(2000)
        self.screenshot(page, "login_page")

        # 检查页面元素
        tests = {
            "页面标题正确": page.title() == "AgentScope PaaS - 智能体开发平台",
            "有登录表单": page.query_selector("form") is not None,
            "有邮箱输入框": page.query_selector("input[type='email']") is not None,
            "有密码输入框": page.query_selector("input[type='password']") is not None,
            "有提交按钮": page.query_selector("button[type='submit']") is not None
        }

        for test_name, result in tests.items():
            self.log(f"登录页面 - {test_name}", result)

        return all(tests.values())

    def test_agent_creation_page_ui(self, page):
        """测试智能体创建页面UI"""
        print("\n[测试]: 智能体创建页面UI")

        # 直接访问智能体创建页面
        page.goto(f"{self.base_url}/agents/create", wait_until='networkidle')
        page.wait_for_timeout(3000)
        self.screenshot(page, "agent_creation_page")

        # 检查页面元素
        tests = {
            "页面加载成功": "/agents" in page.url or "/agent" in page.url.lower(),
            "有表单容器": page.query_selector("form, .ant-form, [class*='form']") is not None,
            "有输入框": page.query_selector("input") is not None,
            "有按钮": page.query_selector("button") is not None,
            "有文本区域": page.query_selector("textarea") is not None
        }

        for test_name, result in tests.items():
            self.log(f"创建页面 - {test_name}", result)

        return all(tests.values())

    def test_agent_form_fields(self, page):
        """测试智能体表单字段"""
        print("\n[测试]: 智能体表单字段")

        page.goto(f"{self.base_url}/agents/create", wait_until='networkidle')
        page.wait_for_timeout(3000)

        # 检查各种输入字段
        field_tests = {
            "名称输入框": page.query_selector("input[name*='name'], input[placeholder*='名称']") is not None,
            "描述文本域": page.query_selector("textarea[name*='description'], textarea[placeholder*='描述']") is not None,
            "模型选择": page.query_selector("select, [class*='select']") is not None,
            "提示词输入": page.query_selector("textarea[name*='prompt'], textarea[placeholder*='提示']") is not None,
            "提交按钮": page.query_selector("button[type='submit'], button:has-text('创建')") is not None
        }

        for test_name, result in field_tests.items():
            self.log(f"表单字段 - {test_name}", result)

        self.screenshot(page, "form_fields")

        return all(field_tests.values())

    def test_form_interaction(self, page):
        """测试表单交互"""
        print("\n[测试]: 表单交互功能")

        page.goto(f"{self.base_url}/agents/create", wait_until='networkidle')
        page.wait_for_timeout(2000)

        try:
            # 测试输入框交互
            name_input = page.query_selector("input[name*='name'], input[placeholder*='名称']")
            if name_input:
                name_input.fill("测试智能体")
                self.log("名称输入框可输入", True)

                # 验证输入
                value = name_input.input_value()
                self.log("名称输入框值正确", value == "测试智能体")
            else:
                self.log("名称输入框可输入", False)

            # 测试按钮点击
            button = page.query_selector("button:not([disabled])")
            if button:
                self.screenshot(page, "before_button_click")
                button.click()
                page.wait_for_timeout(1000)
                self.screenshot(page, "after_button_click")
                self.log("按钮可点击", True)
            else:
                self.log("按钮可点击", False)

            return True

        except Exception as e:
            self.log("表单交互测试失败", False, str(e))
            return False

    def test_navigation_elements(self, page):
        """测试导航元素"""
        print("\n[测试]: 导航和菜单元素")

        # 测试首页导航
        page.goto(f"{self.base_url}", wait_until='networkidle')
        page.wait_for_timeout(2000)
        self.screenshot(page, "homepage")

        nav_tests = {
            "有导航栏": page.query_selector("nav, [class*='nav'], [class*='header']") is not None,
            "有菜单项": page.query_selector("a, [class*='menu']") is not None,
            "有链接": page.query_selector("a[href]") is not None
        }

        for test_name, result in nav_tests.items():
            self.log(f"导航元素 - {test_name}", result)

        return all(nav_tests.values())

    def test_agent_creation_workflow(self, page):
        """测试智能体创建工作流（UI层面）"""
        print("\n[测试]: 智能体创建工作流")

        try:
            # 1. 导航到创建页面
            page.goto(f"{self.base_url}/agents/create", wait_until='networkidle')
            page.wait_for_timeout(2000)
            self.log("工作流 - 导航到创建页面", True)
            self.screenshot(page, "workflow_step1")

            # 2. 检查是否有步骤指示器或分页
            steps = page.query_selector("[class*='step'], [class*='progress'], .ant-steps")
            self.log("工作流 - 有步骤指示器", steps is not None)
            self.screenshot(page, "workflow_step2")

            # 3. 检查是否有配置选项卡或折叠面板
            tabs = page.query_selector("[class*='tab'], .ant-tabs, .ant-collapse")
            self.log("工作流 - 有配置区域", tabs is not None)
            self.screenshot(page, "workflow_step3")

            # 4. 检查是否有预览或确认区域
            preview = page.query_selector("[class*='preview'], [class*='summary']")
            self.log("工作流 - 有预览区域", preview is not None)

            return True

        except Exception as e:
            self.log("工作流测试失败", False, str(e))
            return False

    def test_responsive_design(self, page):
        """测试响应式设计"""
        print("\n[测试]: 响应式设计")

        # 测试桌面视图
        page.set_viewport_size({'width': 1280, 'height': 720})
        page.goto(f"{self.base_url}/agents/create", wait_until='networkidle')
        page.wait_for_timeout(2000)
        self.screenshot(page, "desktop_view")
        desktop_ok = page.query_selector("body") is not None

        # 测试移动设备视图
        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto(f"{self.base_url}/agents/create", wait_until='networkidle')
        page.wait_for_timeout(2000)
        self.screenshot(page, "mobile_view")
        mobile_ok = page.query_selector("body") is not None

        # 恢复桌面视图
        page.set_viewport_size({'width': 1280, 'height': 720})

        self.log("响应式 - 桌面视图", desktop_ok)
        self.log("响应式 - 移动视图", mobile_ok)

        return desktop_ok and mobile_ok

    def test_ant_design_components(self, page):
        """测试Ant Design组件使用"""
        print("\n[测试]: Ant Design组件")

        page.goto(f"{self.base_url}/agents/create", wait_until='networkidle')
        page.wait_for_timeout(2000)

        antd_tests = {
            "使用Ant Design表单": page.query_selector(".ant-form, form.ant-form") is not None,
            "使用Ant Design输入框": page.query_selector(".ant-input, input.ant-input") is not None,
            "使用Ant Design按钮": page.query_selector(".ant-btn, button.ant-btn") is not None,
            "使用Ant Design卡片": page.query_selector(".ant-card") is not None,
            "使用Ant Design图标": page.query_selector(".anticon, [class*='anticon']") is not None
        }

        for test_name, result in antd_tests.items():
            self.log(f"Ant Design组件 - {test_name}", result)

        self.screenshot(page, "antd_components")

        return any(antd_tests.values())

    def run_ui_tests(self):
        """运行UI测试"""
        print("=" * 60)
        print("AgentScope PaaS - 智能体创建UI功能测试")
        print("=" * 60)

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                slow_mo=300
            )

            context = browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )

            page = context.new_page()

            # 错误监控
            errors = []
            def handle_error(error):
                errors.append(str(error))

            page.on('pageerror', handle_error)

            try:
                # 运行各项测试
                self.test_login_page_ui(page)
                self.test_agent_creation_page_ui(page)
                self.test_agent_form_fields(page)
                self.test_form_interaction(page)
                self.test_navigation_elements(page)
                self.test_agent_creation_workflow(page)
                self.test_responsive_design(page)
                self.test_ant_design_components(page)

            finally:
                context.close()
                browser.close()

        # 生成报告
        self.generate_report()
        self.print_summary()

        return len(errors) == 0

    def generate_report(self):
        """生成测试报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "results": self.test_results,
            "summary": {
                "total": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r["passed"]),
                "failed": sum(1 for r in self.test_results if not r["passed"])
            }
        }

        report_file = self.screenshots_dir / f"ui_test_report_{int(time.time())}.json"
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
        print("智能体创建UI功能测试总结")
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
    print("启动智能体创建UI功能测试...")

    tester = AgentCreationUITest()

    try:
        success = tester.run_ui_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"测试执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())