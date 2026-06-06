#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务启动脚本
自动启动后端和前端服务
"""

import subprocess
import time
import sys
import os
import signal
import atexit
from pathlib import Path


class ServiceManager:
    """服务管理器"""

    def __init__(self):
        self.processes = []
        self.project_root = Path(__file__).parent.parent

    def start_backend(self):
        """启动后端服务"""
        print("🚀 启动后端服务...")
        backend_dir = self.project_root / "api_server"

        if not backend_dir.exists():
            print(f"❌ 后端目录不存在: {backend_dir}")
            return False

        try:
            # 检查端口是否已被占用
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()

            if result == 0:
                print("⚠️ 后端服务已在运行（端口8000已占用）")
                return True

            # 启动后端服务
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("backend", process))
            print(f"✅ 后端服务启动成功 (PID: {process.pid})")

            # 等待服务启动
            time.sleep(3)
            return True

        except Exception as e:
            print(f"❌ 启动后端服务失败: {e}")
            return False

    def start_frontend(self):
        """启动前端服务"""
        print("🚀 启动前端服务...")
        frontend_dir = self.project_root / "frontend"

        if not frontend_dir.exists():
            print(f"❌ 前端目录不存在: {frontend_dir}")
            return False

        try:
            # 检查node_modules是否存在
            node_modules = frontend_dir / "node_modules"
            if not node_modules.exists():
                print("📦 首次启动，安装npm依赖...")
                subprocess.run(
                    ["npm", "install"],
                    cwd=frontend_dir,
                    check=True,
                    capture_output=True
                )
                print("✅ npm依赖安装完成")

            # 检查端口是否已被占用
            import socket
            ports = [3000, 3005, 3010]
            available_port = None

            for port in ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()

                if result != 0:
                    available_port = port
                    break

            if available_port:
                print(f"🔍 使用可用端口: {available_port}")
            else:
                print("⚠️ 前端服务已在运行（常用端口均被占用）")
                return True

            # 启动前端服务
            process = subprocess.Popen(
                ["npm", "run", "dev", "--", "--port", str(available_port)],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True if sys.platform == 'win32' else False
            )
            self.processes.append(("frontend", process))
            print(f"✅ 前端服务启动成功 (PID: {process.pid}, Port: {available_port})")

            # 等待服务启动
            time.sleep(5)
            return True

        except Exception as e:
            print(f"❌ 启动前端服务失败: {e}")
            return False

    def stop_all(self):
        """停止所有服务"""
        print("🛑 停止所有服务...")
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name}服务已停止")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔥 强制停止{name}服务")
            except Exception as e:
                print(f"❌ 停止{name}服务失败: {e}")

    def cleanup(self):
        """清理函数"""
        self.stop_all()

    def verify_services(self):
        """验证服务状态"""
        print("🌐 验证服务状态...")

        import urllib.request
        import urllib.error

        services_ok = True

        # 检查后端
        try:
            response = urllib.request.urlopen('http://localhost:8000', timeout=3)
            print("✅ 后端服务可访问")
        except urllib.error.URLError:
            print("❌ 后端服务不可访问")
            services_ok = False

        # 检查前端
        try:
            response = urllib.request.urlopen('http://localhost:3005', timeout=3)
            print("✅ 前端服务可访问")
        except urllib.error.URLError:
            # 尝试其他端口
            try:
                response = urllib.request.urlopen('http://localhost:3000', timeout=3)
                print("✅ 前端服务可访问 (端口3000)")
            except urllib.error.URLError:
                print("❌ 前端服务不可访问")
                services_ok = False

        return services_ok


def main():
    """主函数"""
    print("🚀 AgentScope PaaS - 服务启动脚本")
    print("=" * 50)

    manager = ServiceManager()

    # 注册清理函数
    atexit.register(manager.cleanup)

    # 启动服务
    if not manager.start_backend():
        print("❌ 后端服务启动失败")
        return 1

    if not manager.start_frontend():
        print("❌ 前端服务启动失败")
        return 1

    # 验证服务
    if not manager.verify_services():
        print("⚠️ 服务验证失败，但继续运行...")

    print("\n" + "=" * 50)
    print("✅ 服务启动完成！")
    print("=" * 50)
    print("后端: http://localhost:8000")
    print("前端: http://localhost:3005")
    print("=" * 50)
    print("按 Ctrl+C 停止所有服务")

    try:
        # 保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 收到停止信号，正在关闭服务...")
        manager.cleanup()
        return 0


if __name__ == '__main__':
    sys.exit(main())