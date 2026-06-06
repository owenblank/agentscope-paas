#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope PaaS Platform - Performance and Stress Test
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

from playwright.sync_api import sync_playwright
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import threading


class PerformanceMetrics:
    """性能指标收集器"""

    def __init__(self):
        self.page_load_times = []
        self.api_response_times = []
        self.memory_usage = []
        self.error_count = 0
        self.success_count = 0
        self.lock = threading.Lock()

    def add_page_load_time(self, time_ms):
        with self.lock:
            self.page_load_times.append(time_ms)

    def add_api_response_time(self, time_ms):
        with self.lock:
            self.api_response_times.append(time_ms)

    def record_success(self):
        with self.lock:
            self.success_count += 1

    def record_error(self):
        with self.lock:
            self.error_count += 1

    def get_statistics(self):
        """获取统计信息"""
        stats = {}

        if self.page_load_times:
            stats['page_load'] = {
                'count': len(self.page_load_times),
                'average': statistics.mean(self.page_load_times),
                'median': statistics.median(self.page_load_times),
                'min': min(self.page_load_times),
                'max': max(self.page_load_times),
                'std_dev': statistics.stdev(self.page_load_times) if len(self.page_load_times) > 1 else 0
            }

        if self.api_response_times:
            stats['api_response'] = {
                'count': len(self.api_response_times),
                'average': statistics.mean(self.api_response_times),
                'median': statistics.median(self.api_response_times),
                'min': min(self.api_response_times),
                'max': max(self.api_response_times),
                'std_dev': statistics.stdev(self.api_response_times) if len(self.api_response_times) > 1 else 0
            }

        stats['requests'] = {
            'success': self.success_count,
            'errors': self.error_count,
            'total': self.success_count + self.error_count,
            'success_rate': self.success_count / (self.success_count + self.error_count) * 100 if (self.success_count + self.error_count) > 0 else 0
        }

        return stats


def measure_page_load(page, url, metrics):
    """测量页面加载时间"""
    start_time = time.time()

    try:
        page.goto(url, wait_until='networkidle')
        load_time = (time.time() - start_time) * 1000  # 转换为毫秒
        metrics.add_page_load_time(load_time)
        metrics.record_success()
        return True, load_time
    except Exception as e:
        metrics.record_error()
        return False, 0


def test_page_load_performance(iterations=10):
    """测试页面加载性能"""
    print(f"🚀 页面加载性能测试 ({iterations} 次迭代)")
    print("=" * 50)

    metrics = PerformanceMetrics()
    urls = [
        'http://localhost:3000/',
        'http://localhost:3000/login',
        'http://localhost:3000/register',
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for i in range(iterations):
            print(f"\n📊 迭代 {i + 1}/{iterations}")

            for url in urls:
                page = browser.new_page()
                success, load_time = measure_page_load(page, url, metrics)

                page_name = url.split('/')[-1] or 'root'
                status = "✅" if success else "❌"
                print(f"{status} {page_name}: {load_time:.0f}ms" if success else f"{status} {page_name}: 加载失败")

                page.close()

        browser.close()

    # 输出统计结果
    stats = metrics.get_statistics()
    if 'page_load' in stats:
        print(f"\n📈 页面加载性能统计:")
        print(f"  平均加载时间: {stats['page_load']['average']:.0f}ms")
        print(f"  中位数: {stats['page_load']['median']:.0f}ms")
        print(f"  最快: {stats['page_load']['min']:.0f}ms")
        print(f"  最慢: {stats['page_load']['max']:.0f}ms")
        print(f"  标准差: {stats['page_load']['std_dev']:.0f}ms")

    return stats


def test_concurrent_users(concurrent_users=5, requests_per_user=10):
    """测试并发用户性能"""
    print(f"\n👥 并发用户性能测试 ({concurrent_users} 用户, {requests_per_user} 请求/用户)")
    print("=" * 50)

    metrics = PerformanceMetrics()

    def user_session(user_id):
        """模拟用户会话"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for request_id in range(requests_per_user):
                start_time = time.time()

                try:
                    # 模拟用户浏览不同页面
                    pages = [
                        'http://localhost:3000/',
                        'http://localhost:3000/login',
                        'http://localhost:3000/register',
                    ]

                    url = pages[request_id % len(pages)]
                    page.goto(url, wait_until='networkidle', timeout=10000)

                    response_time = (time.time() - start_time) * 1000
                    metrics.add_api_response_time(response_time)
                    metrics.record_success()

                    print(f"用户 {user_id}: 请求 {request_id + 1}/{requests_per_user} - {response_time:.0f}ms")

                except Exception as e:
                    metrics.record_error()
                    print(f"用户 {user_id}: 请求 {request_id + 1}/{requests_per_user} - 失败: {e}")

                # 模拟用户思考时间
                time.sleep(0.5)

            browser.close()

    # 使用线程池模拟并发用户
    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        for user_id in range(concurrent_users):
            executor.submit(user_session, user_id)

    # 输出统计结果
    stats = metrics.get_statistics()
    print(f"\n📈 并发测试统计:")
    print(f"  总请求数: {stats['requests']['total']}")
    print(f"  成功请求数: {stats['requests']['success']}")
    print(f"  失败请求数: {stats['requests']['errors']}")
    print(f"  成功率: {stats['requests']['success_rate']:.1f}%")

    if 'api_response' in stats:
        print(f"\n  响应时间统计:")
        print(f"  平均: {stats['api_response']['average']:.0f}ms")
        print(f"  中位数: {stats['api_response']['median']:.0f}ms")
        print(f"  最快: {stats['api_response']['min']:.0f}ms")
        print(f"  最慢: {stats['api_response']['max']:.0f}ms")

    return stats


def test_memory_leak(iterations=20):
    """测试内存泄漏"""
    print(f"\n💾 内存泄漏测试 ({iterations} 次迭代)")
    print("=" * 50)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for i in range(iterations):
            # 创建和销毁页面，模拟用户活动
            page = browser.new_page()
            page.goto('http://localhost:3000/', wait_until='networkidle')

            # 执行一些页面操作
            page.click('body')  # 模拟用户交互
            page.wait_for_timeout(1000)

            page.close()

            if (i + 1) % 5 == 0:
                print(f"已完成 {i + 1}/{iterations} 次迭代")

        browser.close()

    print("✅ 内存泄漏测试完成")
    print("💡 建议: 使用系统监控工具观察浏览器进程内存使用情况")


def test_stability(duration_minutes=5):
    """测试系统稳定性"""
    print(f"\n🔄 系统稳定性测试 ({duration_minutes} 分钟)")
    print("=" * 50)

    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)

    metrics = PerformanceMetrics()
    iteration = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        while time.time() < end_time:
            iteration += 1
            elapsed = time.time() - start_time
            remaining = end_time - time.time()

            print(f"稳定性测试: 迭代 {iteration} - 已运行: {elapsed/60:.1f}分钟 - 剩余: {remaining/60:.1f}分钟")

            try:
                page = browser.new_page()
                page.goto('http://localhost:3000/', wait_until='networkidle', timeout=10000)
                page.wait_for_timeout(1000)
                page.close()

                metrics.record_success()

            except Exception as e:
                metrics.record_error()
                print(f"❌ 错误: {e}")

            # 等待一段时间再进行下一次迭代
            time.sleep(10)

        browser.close()

    # 输出结果
    stats = metrics.get_statistics()
    print(f"\n📈 稳定性测试结果:")
    print(f"  总迭代次数: {stats['requests']['total']}")
    print(f"  成功次数: {stats['requests']['success']}")
    print(f"  失败次数: {stats['requests']['errors']}")
    print(f"  稳定性: {stats['requests']['success_rate']:.1f}%")

    return stats


def run_performance_tests():
    """运行所有性能测试"""
    print("🔧 AgentScope PaaS 平台 - 性能测试套件")
    print("=" * 50)
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    all_results = {}

    try:
        # 1. 页面加载性能测试
        all_results['page_load'] = test_page_load_performance(iterations=10)

        # 2. 并发用户测试
        all_results['concurrent_users'] = test_concurrent_users(concurrent_users=3, requests_per_user=5)

        # 3. 内存泄漏测试
        test_memory_leak(iterations=20)

        # 4. 稳定性测试
        # all_results['stability'] = test_stability(duration_minutes=2)  # 短时间测试

        # 总结
        print("\n" + "=" * 50)
        print("📋 性能测试总结")
        print("=" * 50)

        if 'page_load' in all_results:
            page_avg = all_results['page_load']['page_load']['average']
            print(f"页面加载性能: {'✅ 良好' if page_avg < 3000 else '⚠️ 需要优化'} (平均 {page_avg:.0f}ms)")

        if 'concurrent_users' in all_results:
            success_rate = all_results['concurrent_users']['requests']['success_rate']
            print(f"并发处理能力: {'✅ 优秀' if success_rate > 95 else '⚠️ 需要改进'} (成功率 {success_rate:.1f}%)")

        print(f"\n💡 性能优化建议:")
        print(f"  - 页面加载时间应控制在3秒以内")
        print(f"  - 并发成功率应保持在95%以上")
        print(f"  - 定期进行性能测试以发现退化")
        print(f"  - 监控生产环境的实际性能指标")

    except Exception as e:
        print(f"❌ 性能测试执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import sys

    try:
        run_performance_tests()

    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 性能测试执行失败: {e}")
        sys.exit(1)