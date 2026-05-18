#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS - 一键测试启动器
最简单的方式开始测试
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def print_step(step_num, description):
    """打印步骤"""
    print(f"[步骤 {step_num}] {description}")

def check_service(url, service_name):
    """检查服务状态"""
    try:
        response = requests.get(url, timeout=3)
        if response.ok or response.status_code < 500:
            print(f"✅ {service_name} 正在运行")
            return True
        else:
            print(f"⚠️  {service_name} 响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"❌ {service_name} 未运行")
        return False

def install_dependencies():
    """安装测试依赖"""
    print_step(1, "安装测试依赖")

    dependencies = [
        "playwright",
        "requests",
        "pytest",
        "pytest-html"
    ]

    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✓ {dep} 已安装")
        except ImportError:
            print(f"正在安装 {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep, "-q"], check=True)

    # 安装Playwright浏览器
    print("正在安装 Playwright 浏览器...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    print("✓ 浏览器安装完成\n")

def check_services():
    """检查服务状态"""
    print_step(2, "检查服务状态")

    api_running = check_service("http://localhost:8000/api/v1/health", "API服务器")
    frontend_running = check_service("http://localhost:3000", "前端服务器")

    if not api_running:
        print("\n💡 启动API服务器:")
        print("   python api_server/main.py")
        print("   或: python -m api_server.main")

    if not frontend_running:
        print("\n💡 启动前端服务器:")
        print("   cd frontend")
        print("   npm run dev")

    if not (api_running and frontend_running):
        print("\n请启动上述服务后重新运行测试")
        return False

    return True

def create_test_directories():
    """创建测试目录"""
    print_step(3, "创建测试目录")

    directories = [
        "test_results",
        "test_results/screenshots",
        "test_results/logs",
        "test_results/html"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建目录: {directory}")

    print()

def choose_test_mode():
    """选择测试模式"""
    print_step(4, "选择测试模式")
    print("请选择测试模式:")
    print("1. 快速测试 (30秒) - 验证基本功能")
    print("2. 完整测试 (5分钟) - 全面的端到端测试")
    print("3. Pytest测试 (3分钟) - 模块化测试套件")
    print("4. 只检查服务状态")
    print()

    while True:
        try:
            choice = input("请输入选项 (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return int(choice)
            print("无效选项，请重新输入")
        except KeyboardInterrupt:
            print("\n\n已取消")
            sys.exit(0)

def run_quick_test():
    """运行快速测试"""
    print("\n🚀 开始快速测试...\n")
    result = subprocess.run([sys.executable, "quick_test.py"])
    return result.returncode

def run_full_test():
    """运行完整测试"""
    print("\n🚀 开始完整端到端测试...\n")
    result = subprocess.run([sys.executable, "e2e/comprehensive_integration_test.py"])
    return result.returncode

def run_pytest():
    """运行pytest测试"""
    print("\n🚀 开始Pytest测试...\n")

    # 检查pytest是否安装
    try:
        import pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "e2e/test_pytest_e2e.py",
            "-v",
            "--html=test_results/html/report.html"
        ])
        return result.returncode
    except ImportError:
        print("Pytest未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "-q"], check=True)
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "e2e/test_pytest_e2e.py",
            "-v"
        ])
        return result.returncode

def show_results():
    """显示测试结果"""
    print_step(5, "查看测试结果")

    print("\n测试完成！查看结果:")
    print("1. 查看摘要: python show_test_results.py")
    print("2. 查看失败: python show_test_results.py --failed")
    print("3. 查看详细: python show_test_results.py --all")
    print("4. 查看HTML报告: 打开 test_results/html/report.html")

def main():
    """主函数"""
    print_header("AgentScope PaaS 一键测试启动器")

    try:
        # 1. 安装依赖
        install_dependencies()

        # 2. 检查服务
        if not check_services():
            return 1

        # 3. 创建目录
        create_test_directories()

        # 4. 选择测试模式
        choice = choose_test_mode()

        # 5. 运行测试
        exit_code = 0

        if choice == 1:
            exit_code = run_quick_test()
        elif choice == 2:
            exit_code = run_full_test()
        elif choice == 3:
            exit_code = run_pytest()
        elif choice == 4:
            print("\n✅ 服务状态检查完成")
            return 0

        # 6. 显示结果
        if choice != 4:
            show_results()

        return exit_code

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())