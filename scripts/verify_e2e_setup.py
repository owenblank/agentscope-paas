#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E测试设置验证脚本
验证所有E2E测试组件是否正确配置
"""

import sys
import os
import json
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass


def verify_files():
    """验证文件存在性"""
    print("🔍 验证E2E测试文件...")
    required_files = [
        'e2e/test_config.json',
        'e2e/simple_e2e_test.py',
        'scripts/prepare_e2e_env.py',
        'scripts/start_services.py',
        'run_e2e_complete.bat',
        'E2E_TESTING_GUIDE.md'
    ]

    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False

    return all_exist


def verify_config():
    """验证配置文件"""
    print("\n🔍 验证配置文件...")
    config_file = 'e2e/test_config.json'
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        required_keys = ['test_environment', 'test_user', 'test_settings', 'test_agent']
        for key in required_keys:
            if key in config:
                print(f"✅ 配置项 {key} 存在")
            else:
                print(f"❌ 配置项 {key} 缺失")

        return True
    except Exception as e:
        print(f"❌ 配置文件验证失败: {e}")
        return False


def verify_directories():
    """验证目录创建"""
    print("\n🔍 验证目录结构...")
    try:
        with open('e2e/test_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        dirs = [
            config.get('test_settings', {}).get('screenshot_directory', 'e2e_screenshots'),
            config.get('test_settings', {}).get('report_directory', 'e2e_reports')
        ]

        for dir_path in dirs:
            if os.path.exists(dir_path):
                print(f"✅ 目录 {dir_path} 存在")
            else:
                print(f"⚠️ 目录 {dir_path} 不存在（运行测试时会自动创建）")

        return True
    except Exception as e:
        print(f"❌ 目录验证失败: {e}")
        return False


def verify_scripts():
    """验证脚本语法"""
    print("\n🔍 验证脚本语法...")
    scripts = [
        'scripts/prepare_e2e_env.py',
        'scripts/start_services.py',
        'e2e/simple_e2e_test.py'
    ]

    all_valid = True
    for script in scripts:
        try:
            with open(script, 'r', encoding='utf-8') as f:
                content = f.read()
                compile(content, script, 'exec')
            print(f"✅ {script} 语法正确")
        except SyntaxError as e:
            print(f"❌ {script} 语法错误: {e}")
            all_valid = False

    return all_valid


def generate_test_summary():
    """生成测试摘要报告"""
    print("\n📋 E2E测试设置摘要")
    print("=" * 50)

    checks = [
        ("文件完整性", verify_files()),
        ("配置文件", verify_config()),
        ("目录结构", verify_directories()),
        ("脚本语法", verify_scripts())
    ]

    for name, result in checks:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in checks)

    print("=" * 50)

    if all_passed:
        print("🎉 E2E测试设置验证完成！")
        print("\n下一步：")
        print("1. Windows用户: run_e2e_complete.bat")
        print("2. Linux/Mac用户: python e2e/simple_e2e_test.py")
        return 0
    else:
        print("⚠️ E2E测试设置验证未完全通过，请检查上述问题。")
        return 1


def main():
    """主函数"""
    print("🧪 AgentScope PaaS - E2E测试设置验证")
    print("=" * 50)

    return generate_test_summary()


if __name__ == '__main__':
    sys.exit(main())