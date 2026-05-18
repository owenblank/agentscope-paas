#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS - 测试状态监控器
实时监控测试执行状态和进度
"""

import os
import time
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class TestMonitor:
    """测试状态监控器"""

    def __init__(self, results_dir: str = "test_results"):
        self.results_dir = Path(results_dir)
        self.monitoring = False
        self.last_results = []

    def get_latest_results(self) -> List[Dict[str, Any]]:
        """获取最新的测试结果"""
        json_files = list(self.results_dir.glob("e2e_report_*.json"))
        if not json_files:
            return []

        latest_file = max(json_files, key=lambda p: p.stat().st_mtime)

        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("test_results", [])
        except:
            return []

    def display_progress(self, results: List[Dict[str, Any]]):
        """显示测试进度"""
        if not results:
            print("等待测试开始...")
            return

        total = len(results)
        passed = sum(1 for r in results if r["status"] == "PASS")
        failed = sum(1 for r in results if r["status"] == "FAIL")
        pass_rate = (passed / total * 100) if total > 0 else 0

        # 清屏并显示进度
        os.system('cls' if os.name == 'nt' else 'clear')

        print("🔍 AgentScope PaaS 测试监控器")
        print("=" * 50)
        print(f"时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"进度: {total} 个测试完成")
        print(f"通过: {passed} ✓ | 失败: {failed} ✗")
        print(f"通过率: {pass_rate:.1f}%")
        print("=" * 50)

        # 显示进度条
        bar_length = 40
        filled = int(bar_length * pass_rate / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"[{bar}] {pass_rate:.0f}%")

        # 显示最新的测试结果
        if results:
            latest = results[-1]
            status_icon = "✓" if latest["status"] == "PASS" else "✗"
            print(f"\n最新测试: {status_icon} {latest['test_name']}")

            if latest["status"] == "FAIL" and latest.get('details'):
                print(f"失败原因: {latest['details']}")

        # 显示失败测试摘要
        failed_tests = [r for r in results if r["status"] == "FAIL"]
        if failed_tests:
            print(f"\n失败的测试 ({len(failed_tests)}):")
            for test in failed_tests[-3:]:  # 只显示最后3个
                print(f"  ✗ {test['test_name']}")

    def monitor_tests(self, interval: int = 2):
        """监控测试执行"""
        self.monitoring = True
        print("开始监控测试执行...")
        print("按 Ctrl+C 停止监控\n")

        try:
            while self.monitoring:
                current_results = self.get_latest_results()

                # 检查是否有新的测试结果
                if len(current_results) != len(self.last_results):
                    self.display_progress(current_results)
                    self.last_results = current_results

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n监控已停止")
            self.monitoring = False

            # 显示最终结果
            if self.last_results:
                print("\n最终测试结果:")
                self.display_progress(self.last_results)

class TestRunnerMonitor:
    """测试运行器监控器"""

    def __init__(self):
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
        self.current_results = {
            "test_suite": "AgentScope PaaS E2E Tests",
            "start_time": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": []
        }

    def update_result(self, test_name: str, status: str, details: str = ""):
        """更新测试结果"""
        self.current_results["total_tests"] += 1

        if status == "PASS":
            self.current_results["passed_tests"] += 1
        elif status == "FAIL":
            self.current_results["failed_tests"] += 1

        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

        self.current_results["test_results"].append(result)
        self.save_current_results()

    def save_current_results(self):
        """保存当前结果"""
        temp_file = self.results_dir / "current_test_results.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_results, f, ensure_ascii=False, indent=2)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='AgentScope PaaS 测试监控器')
    parser.add_argument('--interval', type=int, default=2, help='刷新间隔（秒）')
    parser.add_argument('--dir', default='test_results', help='测试结果目录')

    args = parser.parse_args()

    monitor = TestMonitor(args.dir)
    monitor.monitor_tests(args.interval)

if __name__ == "__main__":
    main()