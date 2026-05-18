#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS - 测试结果查看工具
快速查看和分析测试结果
"""

import json
import os
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class TestResultsViewer:
    """测试结果查看器"""

    def __init__(self, results_dir: str = "test_results"):
        self.results_dir = Path(results_dir)
        self.results = []

    def load_latest_results(self) -> List[Dict[str, Any]]:
        """加载最新的测试结果"""
        json_files = list(self.results_dir.glob("e2e_report_*.json"))
        if not json_files:
            print("未找到测试结果文件")
            return []

        # 获取最新的文件
        latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
        print(f"加载测试结果: {latest_file.name}")

        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.results = data.get("test_results", [])
                return self.results
        except Exception as e:
            print(f"加载测试结果失败: {e}")
            return []

    def show_summary(self):
        """显示测试摘要"""
        if not self.results:
            print("没有测试结果可显示")
            return

        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        pass_rate = (passed / total * 100) if total > 0 else 0

        print("\n" + "=" * 60)
        print("测试结果摘要")
        print("=" * 60)
        print(f"总测试数: {total}")
        print(f"通过: {passed} ✓")
        print(f"失败: {failed} ✗")
        print(f"通过率: {pass_rate:.1f}%")
        print("=" * 60)

        # 显示评级
        if pass_rate == 100:
            print("🎉 完美！所有测试通过！")
        elif pass_rate >= 90:
            print("🥇 优秀！超过90%测试通过！")
        elif pass_rate >= 80:
            print("🥈 良好！超过80%测试通过！")
        elif pass_rate >= 70:
            print("🥉 及格！超过70%测试通过！")
        elif pass_rate >= 50:
            print("✓ 核心功能正常，超过一半测试通过！")
        else:
            print("⚠️ 需要进一步优化")

    def show_failed_tests(self):
        """显示失败的测试"""
        failed_tests = [r for r in self.results if r["status"] == "FAIL"]

        if not failed_tests:
            print("\n✓ 没有失败的测试")
            return

        print("\n" + "=" * 60)
        print(f"失败的测试 ({len(failed_tests)})")
        print("=" * 60)

        for test in failed_tests:
            print(f"\n✗ {test['test_name']}")
            if test.get('details'):
                print(f"  原因: {test['details']}")
            if test.get('timestamp'):
                print(f"  时间: {test['timestamp']}")

    def show_slow_tests(self, threshold: float = 2.0):
        """显示慢速测试"""
        slow_tests = [
            r for r in self.results
            if r.get('duration', 0) > threshold
        ]

        if not slow_tests:
            print(f"\n✓ 没有超过 {threshold} 秒的慢速测试")
            return

        print(f"\n慢速测试 (>{threshold}秒) ({len(slow_tests)})")
        print("-" * 60)

        # 按耗时排序
        slow_tests.sort(key=lambda x: x.get('duration', 0), reverse=True)

        for test in slow_tests[:10]:  # 只显示前10个
            duration = test.get('duration', 0)
            print(f"⏱️  {test['test_name']}: {duration:.2f}秒")

    def show_test_categories(self):
        """显示测试分类统计"""
        categories = {}

        for test in self.results:
            name = test['test_name']
            # 简单分类：按冒号前的部分分类
            category = name.split(':')[0] if ':' in name else '其他'

            if category not in categories:
                categories[category] = {"total": 0, "passed": 0, "failed": 0}

            categories[category]["total"] += 1
            if test["status"] == "PASS":
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1

        print("\n测试分类统计")
        print("-" * 60)

        for category, stats in categories.items():
            total = stats["total"]
            passed = stats["passed"]
            pass_rate = (passed / total * 100) if total > 0 else 0
            print(f"{category}: {passed}/{total} ({pass_rate:.0f}%)")

    def show_all_results(self):
        """显示所有测试结果"""
        print("\n详细测试结果")
        print("-" * 60)

        for i, test in enumerate(self.results, 1):
            status_icon = "✓" if test["status"] == "PASS" else "✗"
            duration = f" ({test.get('duration', 0):.2f}s)" if test.get('duration') else ""

            print(f"{i:2d}. {status_icon} {test['test_name']}{duration}")

            if test["status"] == "FAIL" and test.get('details'):
                print(f"    原因: {test['details']}")

    def export_report(self, output_file: str = None):
        """导出测试报告"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"test_results/summary_{timestamp}.txt"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("AgentScope PaaS 测试结果报告\n")
                f.write("=" * 60 + "\n\n")

                # 写入摘要
                total = len(self.results)
                passed = sum(1 for r in self.results if r["status"] == "PASS")
                failed = sum(1 for r in self.results if r["status"] == "FAIL")
                pass_rate = (passed / total * 100) if total > 0 else 0

                f.write(f"总测试数: {total}\n")
                f.write(f"通过: {passed} ✓\n")
                f.write(f"失败: {failed} ✗\n")
                f.write(f"通过率: {pass_rate:.1f}%\n\n")

                # 写入详细结果
                f.write("详细测试结果:\n")
                f.write("-" * 60 + "\n")

                for test in self.results:
                    status_icon = "✓" if test["status"] == "PASS" else "✗"
                    f.write(f"{status_icon} {test['test_name']}")

                    if test.get('duration'):
                        f.write(f" ({test['duration']:.2f}s)")
                    f.write("\n")

                    if test["status"] == "FAIL" and test.get('details'):
                        f.write(f"  原因: {test['details']}\n")

            print(f"\n报告已导出到: {output_file}")

        except Exception as e:
            print(f"导出报告失败: {e}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='查看AgentScope PaaS测试结果')
    parser.add_argument('--all', action='store_true', help='显示所有测试结果')
    parser.add_argument('--failed', action='store_true', help='只显示失败的测试')
    parser.add_argument('--slow', action='store_true', help='显示慢速测试')
    parser.add_argument('--categories', action='store_true', help='显示分类统计')
    parser.add_argument('--export', action='store_true', help='导出报告')
    parser.add_argument('--dir', default='test_results', help='测试结果目录')

    args = parser.parse_args()

    viewer = TestResultsViewer(args.dir)
    viewer.load_latest_results()

    if not viewer.results:
        return

    # 显示摘要
    viewer.show_summary()

    # 根据参数显示具体内容
    if args.failed:
        viewer.show_failed_tests()

    if args.slow:
        viewer.show_slow_tests()

    if args.categories:
        viewer.show_test_categories()

    if args.all:
        viewer.show_all_results()

    if args.export:
        viewer.export_report()

    # 如果没有指定任何选项，显示默认信息
    if not any([args.all, args.failed, args.slow, args.categories, args.export]):
        viewer.show_failed_tests()
        viewer.show_slow_tests()
        viewer.show_test_categories()

if __name__ == "__main__":
    main()