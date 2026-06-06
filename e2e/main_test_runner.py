#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS Platform - Main Test Runner
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

import argparse
import json
from datetime import datetime


class TestRunner:
    """测试运行器"""

    def __init__(self, config_file='test_config.json'):
        self.config = self.load_config(config_file)
        self.test_results = []

    def load_config(self, config_file):
        """加载测试配置"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"⚠️ 配置文件不存在: {config_file}，使用默认配置")
                return self.get_default_config()
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}，使用默认配置")
            return self.get_default_config()

    def get_default_config(self):
        """获取默认配置"""
        return {
            "test_environment": {
                "frontend_url": "http://localhost:3000",
                "backend_url": "http://localhost:8000",
                "timeout": 5000,
            },
            "test_settings": {
                "headless": True,
                "browser": "chromium"
            }
        }

    def run_quick_test(self):
        """运行快速测试"""
        print("🚀 运行快速测试...")
        try:
            from quick_start import quick_test
            results = quick_test()
            self.test_results.append(("快速测试", results))
            return all(results.values()) if results else False
        except Exception as e:
            print(f"❌ 快速测试执行失败: {e}")
            return False

    def run_complete_e2e(self, headless=None):
        """运行完整端到端测试"""
        print("🔧 运行完整端到端测试...")
        try:
            # 导入端到端测试模块
            sys.path.insert(0, os.path.dirname(__file__))
            from complete_e2e_test import run_complete_e2e_tests

            # 使用配置中的headless设置，除非命令行参数覆盖
            if headless is None:
                headless = self.config.get("test_settings", {}).get("headless", True)

            results = run_complete_e2e_tests(headless=headless)
            self.test_results.append(("完整E2E测试", results))
            return results.get('失败测试数', 1) == 0
        except Exception as e:
            print(f"❌ 端到端测试执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_performance_tests(self):
        """运行性能测试"""
        print("⚡ 运行性能测试...")
        try:
            from performance_test import run_performance_tests
            run_performance_tests()
            self.test_results.append(("性能测试", {"status": "completed"}))
            return True
        except Exception as e:
            print(f"❌ 性能测试执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def check_dependencies(self):
        """检查测试依赖"""
        print("🔍 检查测试依赖...")

        missing_deps = []

        # 检查Playwright
        try:
            import playwright
            print("✅ Playwright 已安装")
        except ImportError:
            missing_deps.append("playwright")
            print("❌ Playwright 未安装")

        # 检查其他依赖
        required_packages = ['pytest', 'yaml']
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} 已安装")
            except ImportError:
                missing_deps.append(package)
                print(f"❌ {package} 未安装")

        if missing_deps:
            print(f"\n⚠️ 缺少以下依赖: {', '.join(missing_deps)}")
            print("请运行: pip install -r requirements.txt")
            return False

        return True

    def check_services(self):
        """检查服务状态"""
        print("🌐 检查服务状态...")

        import urllib.request
        import urllib.error

        frontend_url = self.config.get("test_environment", {}).get("frontend_url", "http://localhost:3000")
        backend_url = self.config.get("test_environment", {}).get("backend_url", "http://localhost:8000")

        services_ok = True

        # 检查前端服务
        try:
            response = urllib.request.urlopen(frontend_url, timeout=3)
            print(f"✅ 前端服务运行中: {frontend_url}")
        except urllib.error.URLError:
            print(f"❌ 前端服务未运行: {frontend_url}")
            services_ok = False

        # 检查后端服务
        try:
            response = urllib.request.urlopen(backend_url, timeout=3)
            print(f"✅ 后端服务运行中: {backend_url}")
        except urllib.error.URLError:
            print(f"❌ 后端服务未运行: {backend_url}")
            services_ok = False

        return services_ok

    def setup_test_environment(self):
        """设置测试环境"""
        print("🛠️ 设置测试环境...")

        # 创建必要的目录
        dirs = [
            self.config.get("test_environment", {}).get("screenshot_directory", "e2e_screenshots"),
            self.config.get("test_environment", {}).get("report_directory", "e2e_reports")
        ]

        for dir_path in dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"📁 创建目录: {dir_path}")

        print("✅ 测试环境设置完成")
        return True

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*50)
        print("📋 测试执行摘要")
        print("="*50)
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试数量: {len(self.test_results)}")

        for i, (test_name, result) in enumerate(self.test_results, 1):
            status = "✅ 通过" if self.is_test_passed(result) else "❌ 失败"
            print(f"{i}. {test_name}: {status}")

        print("="*50)

    def is_test_passed(self, result):
        """判断测试是否通过"""
        if isinstance(result, dict):
            # 处理字典类型结果
            if '失败测试数' in result:
                return result['失败测试数'] == 0
            elif 'status' in result:
                return result['status'] == 'completed'
            elif all(v in [True, False] for v in result.values()):
                return all(result.values())
        elif isinstance(result, bool):
            return result
        return True  # 默认认为通过


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AgentScope PaaS 测试运行器')
    parser.add_argument('test_type', nargs='?', default='quick',
                       choices=['quick', 'e2e', 'performance', 'all'],
                       help='测试类型: quick(快速测试), e2e(端到端测试), performance(性能测试), all(所有测试)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='交互模式（显示浏览器）')
    parser.add_argument('--config', '-c', default='test_config.json',
                       help='配置文件路径')
    parser.add_argument('--check-only', action='store_true',
                       help='仅检查依赖和服务状态')
    parser.add_argument('--no-check', action='store_true',
                       help='跳过依赖和服务检查')

    args = parser.parse_args()

    # 打印欢迎信息
    print("🧪 AgentScope PaaS 平台 - 测试运行器")
    print("="*50)
    print(f"测试类型: {args.test_type}")
    print(f"配置文件: {args.config}")
    print(f"交互模式: {'是' if args.interactive else '否'}")
    print("="*50)

    # 创建测试运行器
    runner = TestRunner(args.config)

    # 检查依赖
    if not runner.check_dependencies():
        print("\n❌ 依赖检查失败，请安装缺少的依赖")
        return 1

    # 如果只是检查状态
    if args.check_only:
        print("\n🔍 仅检查状态模式")
        deps_ok = runner.check_dependencies()
        services_ok = runner.check_services()
        return 0 if (deps_ok and services_ok) else 1

    # 检查服务状态
    if not args.no_check:
        if not runner.check_services():
            print("\n⚠️ 警告: 部分服务未运行")
            print("建议: 请先启动前后端服务，或使用 --no-check 跳过检查")

            response = input("是否继续测试？ (y/N): ").strip().lower()
            if response != 'y':
                print("测试已取消")
                return 0

    # 设置测试环境
    runner.setup_test_environment()

    # 运行相应的测试
    success = True

    try:
        if args.test_type == 'quick':
            success = runner.run_quick_test()

        elif args.test_type == 'e2e':
            success = runner.run_complete_e2e(headless=not args.interactive)

        elif args.test_type == 'performance':
            success = runner.run_performance_tests()

        elif args.test_type == 'all':
            print("🔄 运行所有测试...")
            success = True

            # 快速测试
            if not runner.run_quick_test():
                success = False

            # 端到端测试
            if not runner.run_complete_e2e(headless=not args.interactive):
                success = False

            # 性能测试
            if not runner.run_performance_tests():
                success = False

    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        return 130

    except Exception as e:
        print(f"\n❌ 测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # 打印测试摘要
        runner.print_summary()

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())