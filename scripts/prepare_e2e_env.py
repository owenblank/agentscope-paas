#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E测试环境准备脚本
检查依赖、创建目录、准备测试环境
"""

import sys
import os
import subprocess
import json

# 设置控制台编码
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass


def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        return False


def check_dependencies():
    """检查必需的依赖包"""
    print("🔍 检查依赖包...")
    required_packages = [
        'playwright',
        'pytest',
        'yaml'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️ 缺少依赖: {', '.join(missing_packages)}")
        install = input("是否自动安装? (y/N): ").strip().lower()
        if install == 'y':
            for package in missing_packages:
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', package],
                                 check=True, capture_output=True)
                    print(f"✅ {package} 安装成功")
                except subprocess.CalledProcessError:
                    print(f"❌ {package} 安装失败")
                    return False
        else:
            return False

    return True


def check_playwright_browsers():
    """检查Playwright浏览器"""
    print("🔍 检查Playwright浏览器...")
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright 浏览器可用")
        return True
    except Exception as e:
        print(f"❌ Playwright 浏览器不可用: {e}")
        install = input("是否安装Chromium浏览器? (y/N): ").strip().lower()
        if install == 'y':
            try:
                subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'],
                             check=True)
                print("✅ Chromium 安装成功")
                return True
            except subprocess.CalledProcessError:
                print("❌ Chromium 安装失败")
                return False
        return False


def create_directories(config_file='e2e/test_config.json'):
    """创建必要的目录"""
    print("📁 创建测试目录...")
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            dirs = [
                config.get('test_settings', {}).get('screenshot_directory', 'e2e_screenshots'),
                config.get('test_settings', {}).get('report_directory', 'e2e_reports')
            ]

            for dir_path in dirs:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                    print(f"📁 创建目录: {dir_path}")
                else:
                    print(f"📁 目录已存在: {dir_path}")

            return True
        else:
            print(f"⚠️ 配置文件不存在: {config_file}")
            return False
    except Exception as e:
        print(f"❌ 创建目录失败: {e}")
        return False


def check_config_file():
    """检查配置文件"""
    print("🔍 检查配置文件...")
    config_file = 'e2e/test_config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                json.load(f)
            print(f"✅ 配置文件有效: {config_file}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            return False
    else:
        print(f"❌ 配置文件不存在: {config_file}")
        return False


def main():
    """主函数"""
    print("🧪 AgentScope PaaS - E2E测试环境准备")
    print("=" * 50)

    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("Playwright浏览器", check_playwright_browsers),
        ("配置文件", check_config_file),
        ("目录创建", create_directories)
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}检查出错: {e}")
            results.append((name, False))

    print("\n" + "=" * 50)
    print("📋 环境准备摘要")
    print("=" * 50)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)
    print("=" * 50)

    if all_passed:
        print("🎉 环境准备完成！可以开始运行E2E测试。")
        return 0
    else:
        print("⚠️ 环境准备未完成，请解决上述问题后重试。")
        return 1


if __name__ == '__main__':
    sys.exit(main())