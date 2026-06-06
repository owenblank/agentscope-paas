#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS Platform - Test Environment Verification Script
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass


def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python版本: {version_str} (满足要求)")
        return True
    else:
        print(f"❌ Python版本: {version_str} (需要 >= 3.8)")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n📦 检查依赖包...")

    required_packages = {
        'playwright': 'Playwright浏览器自动化框架',
        'pytest': 'Python测试框架',
        'yaml': 'YAML配置文件解析'
    }

    missing_packages = []

    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (未安装)")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️ 缺少以下包: {', '.join(missing_packages)}")
        print("💡 安装命令: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ 所有依赖包已安装")
        return True


def check_playwright_browsers():
    """检查Playwright浏览器"""
    print("\n🌐 检查Playwright浏览器...")

    try:
        result = subprocess.run(
            ['python', '-m', 'playwright', 'install', '--dry-run', 'chromium'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✅ Chromium浏览器已安装")
            return True
        else:
            print("❌ Chromium浏览器未安装")
            print("💡 安装命令: python -m playwright install chromium")
            return False

    except Exception as e:
        print(f"❌ 浏览器检查失败: {e}")
        print("💡 安装命令: python -m playwright install chromium")
        return False


def check_test_files():
    """检查测试文件"""
    print("\n📁 检查测试文件...")

    required_files = [
        'complete_e2e_test.py',
        'quick_start.py',
        'performance_test.py',
        'main_test_runner.py',
        'test_config.json',
        'requirements.txt',
        'README.md'
    ]

    missing_files = []

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (缺失)")
            missing_files.append(file)

    if missing_files:
        print(f"\n⚠️ 缺少以下文件: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ 所有测试文件完整")
        return True


def check_config_file():
    """检查配置文件"""
    print("\n⚙️ 检查配置文件...")

    try:
        if not os.path.exists('test_config.json'):
            print("❌ test_config.json 文件不存在")
            return False

        with open('test_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 检查必需的配置项
        required_sections = ['test_environment', 'test_settings']
        missing_sections = []

        for section in required_sections:
            if section not in config:
                missing_sections.append(section)

        if missing_sections:
            print(f"❌ 配置文件缺少以下部分: {', '.join(missing_sections)}")
            return False

        # 检查配置值
        frontend_url = config.get('test_environment', {}).get('frontend_url')
        backend_url = config.get('test_environment', {}).get('backend_url')

        if frontend_url and backend_url:
            print(f"✅ 前端URL: {frontend_url}")
            print(f"✅ 后端URL: {backend_url}")
            print("✅ 配置文件有效")
            return True
        else:
            print("❌ 配置文件缺少必要的URL配置")
            return False

    except json.JSONDecodeError as e:
        print(f"❌ 配置文件JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置文件检查失败: {e}")
        return False


def check_directories():
    """检查目录结构"""
    print("\n📂 检查目录结构...")

    directories = {
        'e2e_screenshots': '测试截图目录',
        'e2e_reports': '测试报告目录'
    }

    all_exist = True

    for dir_name, description in directories.items():
        if os.path.exists(dir_name):
            print(f"✅ {dir_name} - {description}")
        else:
            print(f"⚠️ {dir_name} - {description} (不存在，将自动创建)")
            try:
                os.makedirs(dir_name)
                print(f"✅ 已创建目录: {dir_name}")
            except Exception as e:
                print(f"❌ 无法创建目录 {dir_name}: {e}")
                all_exist = False

    return all_exist


def check_services():
    """检查服务状态"""
    print("\n🌐 检查服务状态...")

    import urllib.request
    import urllib.error

    # 加载配置
    try:
        with open('test_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        config = {
            'test_environment': {
                'frontend_url': 'http://localhost:3000',
                'backend_url': 'http://localhost:8000'
            }
        }

    frontend_url = config.get('test_environment', {}).get('frontend_url', 'http://localhost:3000')
    backend_url = config.get('test_environment', {}).get('backend_url', 'http://localhost:8000')

    services_ok = True

    # 检查前端服务
    print(f"检查前端服务: {frontend_url}")
    try:
        response = urllib.request.urlopen(frontend_url, timeout=3)
        print(f"✅ 前端服务运行中")
    except urllib.error.URLError:
        print(f"❌ 前端服务未运行")
        print("💡 启动命令: cd frontend && npm run dev")
        services_ok = False

    # 检查后端服务
    print(f"检查后端服务: {backend_url}")
    try:
        response = urllib.request.urlopen(backend_url, timeout=3)
        print(f"✅ 后端服务运行中")
    except urllib.error.URLError:
        print(f"❌ 后端服务未运行")
        print("💡 启动命令: python api_server/main.py")
        services_ok = False

    return services_ok


def run_import_tests():
    """运行导入测试"""
    print("\n🧪 运行导入测试...")

    test_modules = [
        ('playwright.sync_api', 'Playwright API'),
        ('yaml', 'YAML模块'),
        ('json', 'JSON模块'),
        ('datetime', 'Datetime模块'),
        ('time', 'Time模块'),
        ('concurrent.futures', '并发模块')
    ]

    all_ok = True

    for module_name, description in test_modules:
        try:
            __import__(module_name)
            print(f"✅ {description} ({module_name})")
        except ImportError as e:
            print(f"❌ {description} ({module_name}): {e}")
            all_ok = False

    return all_ok


def main():
    """主函数"""
    print("🔍 AgentScope PaaS 平台 - 测试环境验证")
    print(f"验证时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        'Python版本': False,
        '依赖包': False,
        '浏览器驱动': False,
        '测试文件': False,
        '配置文件': False,
        '目录结构': False,
        '服务状态': False,
        '导入测试': False
    }

    try:
        # 1. 检查Python版本
        print_section("1. Python环境检查")
        results['Python版本'] = check_python_version()

        # 2. 检查依赖包
        print_section("2. 依赖包检查")
        results['依赖包'] = check_dependencies()

        # 3. 检查浏览器驱动
        print_section("3. 浏览器驱动检查")
        results['浏览器驱动'] = check_playwright_browsers()

        # 4. 检查测试文件
        print_section("4. 测试文件检查")
        results['测试文件'] = check_test_files()

        # 5. 检查配置文件
        print_section("5. 配置文件检查")
        results['配置文件'] = check_config_file()

        # 6. 检查目录结构
        print_section("6. 目录结构检查")
        results['目录结构'] = check_directories()

        # 7. 检查服务状态
        print_section("7. 服务状态检查")
        results['服务状态'] = check_services()

        # 8. 运行导入测试
        print_section("8. 模块导入测试")
        results['导入测试'] = run_import_tests()

        # 输出总结
        print_section("验证结果总结")

        passed_count = sum(1 for v in results.values() if v)
        total_count = len(results)

        for check, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{status} - {check}")

        print(f"\n通过率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")

        if passed_count == total_count:
            print("\n🎉 测试环境验证完全通过！")
            print("💡 您可以开始运行测试: python main_test_runner.py quick")
            return 0
        else:
            print("\n⚠️ 测试环境验证发现问题")
            print("💡 请根据上述提示修复问题后再运行测试")

            # 给出具体的修复建议
            if not results['Python版本']:
                print("\n📝 修复建议:")
                print("  - 升级Python到3.8或更高版本")

            if not results['依赖包']:
                print("\n📝 修复建议:")
                print("  - 运行: pip install -r requirements.txt")

            if not results['浏览器驱动']:
                print("\n📝 修复建议:")
                print("  - 运行: python -m playwright install chromium")

            if not results['服务状态']:
                print("\n📝 修复建议:")
                print("  - 启动前端服务: cd frontend && npm run dev")
                print("  - 启动后端服务: python api_server/main.py")

            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️ 验证被用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())