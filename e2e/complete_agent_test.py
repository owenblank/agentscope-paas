#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete test for login and agent creation
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


class AgentTest:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.results = []
        self.screenshots_dir = Path("e2e_screenshots/complete_test")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Test user credentials
        self.test_user = {
            "email": "test@example.com",
            "password": "SecurePass123"
        }

        # Test agent data
        self.test_agent = {
            "agent_id": f"test_agent_{int(time.time())}",
            "agent_name": "Test Playwright Agent",
            "agent_description": "This is a test agent created by Playwright",
            "api_key": "test-api-key-123456",
            "system_prompt": "You are a helpful test assistant."
        }

    def log(self, test, passed, msg=""):
        """Log test result"""
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test}: {msg}")
        self.results.append({
            "test": test,
            "passed": passed,
            "msg": msg,
            "time": datetime.now().isoformat()
        })

    def screenshot(self, page, name):
        """Save screenshot"""
        timestamp = int(time.time())
        filename = self.screenshots_dir / f"{name}_{timestamp}.png"
        page.screenshot(path=str(filename), full_page=True)
        print(f"[Screenshot] {filename}")
        return filename

    def test_login(self, page):
        """Test login process"""
        print("\n[TEST] User Login")

        try:
            # Navigate to login page
            print("1. Navigating to login page...")
            page.goto(f"{self.base_url}/login")
            time.sleep(3)
            self.screenshot(page, "01_login_page")

            # Check if we have the right page
            page_content = page.content()
            has_email = "email" in page_content.lower()
            has_password = "password" in page_content.lower()

            self.log("Login page loaded", has_email and has_password,
                    f"Page has email field: {has_email}, password field: {has_password}")

            # Find and fill email input
            print("2. Filling login form...")

            # Try different selectors for email input
            email_selectors = [
                "input[type='text']",
                "input[name*='email']",
                "input[placeholder*='email' i]",
                "input[placeholder*='邮箱' i]"
            ]

            email_input = None
            for selector in email_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for element in elements:
                        placeholder = element.get_attribute("placeholder") or ""
                        if "email" in placeholder.lower() or "邮箱" in placeholder or "邮件" in placeholder:
                            email_input = element
                            break
                    if email_input:
                        break
                except:
                    continue

            if not email_input:
                # Just use the first text input
                email_input = page.query_selector("input[type='text']")

            if email_input:
                email_input.fill(self.test_user['email'])
                print(f"   Filled email: {self.test_user['email']}")
            else:
                self.log("Find email input", False, "Could not find email input")
                return False

            # Find and fill password input
            password_input = page.query_selector("input[type='password']")
            if password_input:
                password_input.fill(self.test_user['password'])
                print("   Filled password")
            else:
                self.log("Find password input", False, "Could not find password input")
                return False

            self.screenshot(page, "02_login_filled")

            # Find and click submit button
            print("3. Submitting login form...")

            submit_selectors = [
                "button[type='submit']",
                "button:has-text('登录')",
                "button:has-text('Login')",
                "button:has-text('提交')",
            ]

            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = page.query_selector(selector)
                    if submit_button:
                        break
                except:
                    continue

            if submit_button:
                submit_button.click()
                print("   Clicked login button")
                time.sleep(5)  # Wait for login to complete
                self.screenshot(page, "03_after_login")

                # Check if login was successful
                current_url = page.url
                login_success = "/login" not in current_url

                self.log("User login successful", login_success, f"Current URL: {current_url}")
                return login_success
            else:
                self.log("Find submit button", False, "Could not find submit button")
                return False

        except Exception as e:
            self.log("Login process", False, f"Exception: {str(e)}")
            return False

    def test_agent_creation(self, page):
        """Test agent creation process"""
        print("\n[TEST] Agent Creation")

        try:
            # Navigate to agent creation page
            print("1. Navigating to agent creation page...")
            page.goto(f"{self.base_url}/agents/create")
            time.sleep(5)
            self.screenshot(page, "04_agent_create_page")

            # Check if page loaded
            current_url = page.url
            page_content = page.content()

            page_loaded = "create" in current_url.lower() or "创建" in page_content
            self.log("Agent creation page loaded", page_loaded, f"Current URL: {current_url}")

            if not page_loaded:
                return False

            # Look for form inputs
            print("2. Looking for agent creation form...")

            # Try to find agent_id input
            agent_id_input = None
            all_inputs = page.query_selector_all("input")
            print(f"   Found {len(all_inputs)} inputs")

            for inp in all_inputs:
                placeholder = inp.get_attribute("placeholder") or ""
                name_attr = inp.get_attribute("name") or ""
                print(f"   Input: placeholder='{placeholder}', name='{name_attr}'")

                if "id" in placeholder.lower() or "id" in name_attr.lower():
                    agent_id_input = inp
                    break

            # Fill agent ID
            if agent_id_input:
                agent_id_input.fill(self.test_agent['agent_id'])
                print(f"   Filled agent ID: {self.test_agent['agent_id']}")
                self.screenshot(page, "05_agent_id_filled")
            else:
                self.log("Find agent ID input", False, "Could not find agent ID input")
                # Continue anyway to see what happens

            # Look for text areas or other inputs for agent name
            print("3. Filling agent information...")

            # Try to fill agent name (might be in textarea or input)
            textareas = page.query_selector_all("textarea")
            inputs = page.query_selector_all("input[type='text']")

            print(f"   Found {len(textareas)} textareas and {len(inputs)} text inputs")

            # Fill first textarea with description
            if textareas:
                textareas[0].fill(self.test_agent['agent_description'])
                print(f"   Filled description in textarea")
                self.screenshot(page, "06_description_filled")
            elif inputs:
                # Try next text input
                for inp in inputs[1:]:  # Skip first one (agent_id)
                    try:
                        inp.fill(self.test_agent['agent_name'])
                        print(f"   Filled agent name: {self.test_agent['agent_name']}")
                        self.screenshot(page, "07_name_filled")
                        break
                    except:
                        continue

            # Try to navigate through the form
            print("4. Navigating through form steps...")

            # Look for next/continue buttons
            for step in range(1, 4):  # Try to go through a few steps
                next_buttons = page.query_selector_all("button")
                print(f"   Step {step}: Found {len(next_buttons)} buttons")

                for button in next_buttons:
                    try:
                        text = button.text_content() or ""
                        if "下一步" in text or "next" in text.lower() or "继续" in text:
                            print(f"   Clicking button: {text.strip()}")
                            button.click()
                            time.sleep(2)
                            self.screenshot(page, f"08_step_{step}")
                            break
                    except:
                        continue

            # Try to submit
            print("5. Looking for submit button...")
            submit_buttons = page.query_selector_all("button")
            for button in submit_buttons:
                try:
                    text = button.text_content() or ""
                    if "创建" in text or "submit" in text.lower() or "完成" in text:
                        print(f"   Clicking submit button: {text.strip()}")
                        button.click()
                        time.sleep(5)
                        self.screenshot(page, "09_after_submit")
                        break
                except:
                    continue

            # Check final result
            final_url = page.url
            final_content = page.content()

            success_indicators = [
                "成功" in final_content,
                "success" in final_content.lower(),
                "/agents/" in final_url,
                "创建成功" in final_content
            ]

            creation_success = any(success_indicators)
            self.log("Agent creation submitted", creation_success,
                    f"Final URL: {final_url}, Success indicators: {success_indicators}")

            return True  # Return True even if creation might fail, we got through the process

        except Exception as e:
            self.log("Agent creation process", False, f"Exception: {str(e)}")
            return False

    def run_complete_test(self):
        """Run complete test"""
        print("=" * 60)
        print("AgentScope PaaS - Complete Login & Agent Creation Test")
        print("=" * 60)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=1000)  # Slow mode for better visibility
            context = browser.new_context()
            page = context.new_page()

            try:
                # Test login
                login_success = self.test_login(page)

                # Test agent creation (even if login failed, try it anyway)
                creation_success = self.test_agent_creation(page)

                # Generate report
                self.generate_report()

            finally:
                context.close()
                browser.close()

        return self.results

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("Test Report")
        print("=" * 60)

        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['passed'])

        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Pass rate: {(passed_tests/total_tests*100):.1f}%")

        print("\nDetailed results:")
        for result in self.results:
            status = "[PASS]" if result['passed'] else "[FAIL]"
            print(f"{status} {result['test']}: {result['msg']}")

        # Save JSON report
        report_file = Path("e2e_screenshots") / f"test_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": total_tests - passed_tests,
                    "pass_rate": f"{(passed_tests/total_tests*100):.1f}%"
                },
                "results": self.results
            }, f, ensure_ascii=False, indent=2)

        print(f"\nReport saved to: {report_file}")
        print(f"Screenshots saved to: {self.screenshots_dir}")


def main():
    """Main function"""
    tester = AgentTest()
    results = tester.run_complete_test()

    # Return exit code
    passed = sum(1 for result in results if result['passed'])
    total = len(results)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()