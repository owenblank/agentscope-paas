#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版前端UI测试 - 专注于测试智能体创建界面和聊天功能
不依赖后端认证，直接测试前端UI组件
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed")
    sys.exit(1)


class FrontendUITest:
    def __init__(self, base_url="http://localhost:3005"):
        self.base_url = base_url
        self.results = []
        self.screenshots_dir = Path("e2e_screenshots/frontend_ui_test")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        # 测试数据
        timestamp = int(time.time())
        self.test_agent = {
            "agent_id": f"ui_test_agent_{timestamp}",
            "agent_name": "UI测试智能体",
            "agent_description": "这是一个用于前端UI测试的智能体",
            "api_key": "sk-ui-test-key-123456",
            "system_prompt": "你是一个专业的测试助手，请简洁地回复测试消息。",
            "model_provider": "dashscope",
            "model_name": "qwen-max"
        }

    def log(self, test, passed, msg=""):
        """记录测试结果"""
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test}: {msg}")
        self.results.append({
            "test": test,
            "passed": passed,
            "msg": msg,
            "time": datetime.now().isoformat()
        })

    def screenshot(self, page, name):
        """保存截图"""
        try:
            timestamp = int(time.time())
            filename = self.screenshots_dir / f"{name}_{timestamp}.png"
            page.screenshot(path=str(filename), timeout=10000, full_page=True)
            print(f"[Screenshot] {filename}")
            return filename
        except Exception as e:
            print(f"[Screenshot Error] {name}: {e}")
            return None

    def test_homepage(self, page):
        """测试首页加载和基本UI元素"""
        print("\n[测试1] 首页和基本UI元素")

        try:
            # 访问首页
            page.goto(self.base_url, wait_until='networkidle')
            time.sleep(3)
            self.screenshot(page, "01_homepage")

            # 检查页面标题
            page_title = page.title()
            print(f"页面标题: {page_title}")

            # 检查基本元素
            body_content = page.content()
            has_content = len(body_content) > 1000
            has_root = page.query_selector("#root") is not None

            # 检查导航元素
            nav_links = page.query_selector_all("a")
            buttons = page.query_selector_all("button")

            self.log("首页加载", has_content, f"内容长度: {len(body_content)}")
            self.log("React根元素", has_root, "#root元素存在")
            self.log("导航链接", len(nav_links) > 0, f"找到{len(nav_links)}个链接")
            self.log("页面按钮", len(buttons) > 0, f"找到{len(buttons)}个按钮")

            return has_content

        except Exception as e:
            self.log("首页测试", False, f"异常: {e}")
            return False

    def test_agent_creation_page(self, page):
        """测试智能体创建页面"""
        print("\n[测试2] 智能体创建页面")

        try:
            # 尝试访问创建页面
            page.goto(f"{self.base_url}/agents/create", wait_until='networkidle')
            time.sleep(4)
            self.screenshot(page, "02_agent_create_page")

            current_url = page.url
            page_content = page.content()

            # 检查是否在创建页面
            is_create_page = (
                "create" in current_url.lower() or
                "创建" in page_content or
                "agent" in current_url.lower()
            )

            # 检查表单元素
            inputs = page.query_selector_all("input")
            textareas = page.query_selector_all("textarea")
            forms = page.query_selector_all("form")

            print(f"当前URL: {current_url}")
            print(f"找到{len(inputs)}个输入框, {len(textareas)}个文本区域, {len(forms)}个表单")

            self.log("创建页面访问", is_create_page, f"URL: {current_url}")
            self.log("表单输入元素", len(inputs) > 0, f"输入框数量: {len(inputs)}")
            self.log("表单文本区域", len(textareas) > 0, f"文本区域数量: {len(textareas)}")

            # 如果找到了表单元素，尝试填写
            if len(inputs) > 0:
                self.test_fill_agent_form(page, inputs, textareas)

            return True

        except Exception as e:
            self.log("创建页面测试", False, f"异常: {e}")
            return False

    def test_fill_agent_form(self, page, inputs, textareas):
        """测试填写智能体表单"""
        print("\n[测试3] 填写智能体表单")

        try:
            filled_count = 0

            # 填写输入框
            field_data = [
                self.test_agent['agent_id'],
                self.test_agent['agent_name'],
                self.test_agent['api_key']
            ]

            for i, inp in enumerate(inputs):
                try:
                    if inp.is_visible() and inp.is_enabled():
                        input_type = inp.get_attribute("type") or "text"
                        if input_type not in ["hidden", "submit", "password"] and i < len(field_data):
                            print(f"填写字段 {i}: {field_data[i]}")
                            inp.fill(field_data[i])
                            filled_count += 1
                            time.sleep(0.5)
                except:
                    continue

            # 填写文本区域
            if textareas:
                for i, ta in enumerate(textareas):
                    try:
                        if ta.is_visible() and ta.is_enabled():
                            data_to_fill = self.test_agent['system_prompt'] if i == 0 else self.test_agent['agent_description']
                            print(f"填写文本区域 {i}")
                            ta.fill(data_to_fill)
                            filled_count += 1
                            break
                    except:
                        continue

            self.screenshot(page, "03_form_filled")

            # 查找并点击下一步按钮
            buttons = page.query_selector_all("button")
            button_clicked = False

            for button in buttons:
                try:
                    if button.is_visible() and button.is_enabled():
                        text = button.text_content() or ""
                        print(f"找到按钮: {text[:30]}")

                        if "下一步" in text or "next" in text.lower() or "创建" in text or "create" in text.lower():
                            print(f"点击按钮: {text[:30]}")
                            button.click()
                            button_clicked = True
                            time.sleep(3)
                            break
                except:
                    continue

            self.screenshot(page, "04_after_button_click")

            self.log("表单填写", filled_count >= 2, f"填写了{filled_count}个字段")
            self.log("按钮点击", button_clicked, "成功点击了按钮")

            return filled_count >= 2

        except Exception as e:
            self.log("表单填写测试", False, f"异常: {e}")
            return False

    def test_agent_list_page(self, page):
        """测试智能体列表页面"""
        print("\n[测试4] 智能体列表页面")

        try:
            page.goto(f"{self.base_url}/agents", wait_until='networkidle')
            time.sleep(4)
            self.screenshot(page, "05_agent_list")

            current_url = page.url
            page_content = page.content()

            # 检查页面内容
            has_agent_content = (
                "agent" in page_content.lower() or
                "智能体" in page_content or
                len(page_content) > 1000
            )

            # 检查列表元素
            cards = page.query_selector_all(".ant-card, [class*='card'], [class*='item']")
            list_items = page.query_selector_all("li, [class*='list']")

            print(f"当前URL: {current_url}")
            print(f"找到{len(cards)}个卡片, {len(list_items)}个列表项")

            self.log("列表页面访问", has_agent_content, f"内容长度: {len(page_content)}")
            self.log("列表元素存在", len(cards) > 0 or len(list_items) > 0, f"卡片: {len(cards)}, 列表项: {len(list_items)}")

            return has_agent_content

        except Exception as e:
            self.log("列表页面测试", False, f"异常: {e}")
            return False

    def test_navigation(self, page):
        """测试页面导航功能"""
        print("\n[测试5] 页面导航功能")

        try:
            routes_tested = 0
            routes_passed = 0

            test_routes = [
                ("/", "首页"),
                ("/agents", "智能体列表"),
                ("/agents/create", "创建智能体"),
                ("/login", "登录页面"),
                ("/register", "注册页面")
            ]

            for route, description in test_routes:
                try:
                    page.goto(f"{self.base_url}{route}", wait_until='domcontentloaded')
                    time.sleep(2)
                    routes_tested += 1

                    current_url = page.url
                    route_accessible = route in current_url or current_url.endswith("/")

                    if route_accessible:
                        routes_passed += 1
                        print(f"✓ {description}: {current_url}")
                    else:
                        print(f"✗ {description}: {current_url} (重定向了)")

                except Exception as e:
                    print(f"✗ {description}: 访问失败 - {e}")

            success_rate = routes_passed / routes_tested if routes_tested > 0 else 0
            self.log("页面导航", success_rate >= 0.6, f"通过率: {success_rate:.1%} ({routes_passed}/{routes_tested})")

            return success_rate >= 0.6

        except Exception as e:
            self.log("导航测试", False, f"异常: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("AgentScope PaaS - 前端UI测试")
        print("=" * 70)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            # 控制台日志监听
            def handle_console(msg):
                if msg.type == "error":
                    print(f"[Console Error] {msg.text[:80]}")

            page.on("console", handle_console)

            try:
                # 运行测试
                self.test_homepage(page)
                self.test_navigation(page)
                self.test_agent_creation_page(page)
                self.test_agent_list_page(page)

                # 生成报告
                self.generate_report()

            finally:
                context.close()
                browser.close()

        return self.results

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 70)
        print("测试报告")
        print("=" * 70)

        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])

        print(f"\n总结:")
        print(f"  总测试数: {total}")
        print(f"  通过: {passed}")
        print(f"  失败: {total - passed}")
        print(f"  通过率: {(passed/total*100):.1f}%")

        print(f"\n详细结果:")
        for i, r in enumerate(self.results, 1):
            status = "[PASS]" if r['passed'] else "[FAIL]"
            print(f"  {i}. {status} {r['test']}")
            if r['msg']:
                print(f"     -> {r['msg']}")

        # 保存JSON报告
        report_file = Path("e2e_screenshots") / f"frontend_ui_test_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_info": {
                    "name": "Frontend UI Test",
                    "description": "前端UI组件测试，不依赖后端认证",
                    "timestamp": datetime.now().isoformat()
                },
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": total - passed,
                    "pass_rate": f"{(passed/total*100):.1f}%"
                },
                "results": self.results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n报告已保存至: {report_file}")
        print(f"截图保存在: {self.screenshots_dir}")

        # 总体评估
        if passed == total:
            status = "🎉 完美 - 所有UI功能正常！"
        elif passed >= total * 0.8:
            status = "✅ 优秀 - UI功能运行良好"
        elif passed >= total * 0.6:
            status = "✅ 良好 - 核心UI功能可用"
        elif passed >= total * 0.4:
            status = "⚠️ 一般 - 基础UI可用，需要改进"
        else:
            status = "❌ 需要改进 - UI功能需要开发"

        print(f"\n总体评估: {status}")
        print("=" * 70)


def main():
    tester = FrontendUITest()

    try:
        results = tester.run_all_tests()
        passed = sum(1 for r in results if r['passed'])
        total = len(results)

        if passed >= total * 0.6:
            print("\n✅ 前端UI测试完成！")
            return 0
        else:
            print("\n⚠️ 前端UI测试完成，但存在一些问题")
            return 1

    except Exception as e:
        print(f"\n❌ 测试执行错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())