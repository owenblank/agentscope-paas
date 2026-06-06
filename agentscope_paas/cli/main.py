# agentscope_paas/cli/main.py
"""AgentScope PaaS CLI - Main entry point"""

import argparse
import logging
import sys
import signal
from pathlib import Path
from typing import Optional

from agentscope_paas.cli.error_handler import ErrorHandler
from agentscope_paas.cli.config_processor import ConfigProcessor
from agentscope_paas.cli.launcher import Launcher


# Setup logging
def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure logging based on verbosity"""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def setup_signal_handlers(launcher: Optional[Launcher] = None) -> None:
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print("\n接收到退出信号，正在清理...")
        if launcher:
            print("关闭智能体...")
        sys.exit(0)

    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except (ImportError, AttributeError):
        # Windows doesn't have SIGTERM, ignore errors
        pass


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='AgentScope PaaS - 智能体平台命令行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Global options
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出模式')
    parser.add_argument('-q', '--quiet', action='store_true', help='静默模式')
    parser.add_argument('--strict', action='store_true', help='严格模式，遇到错误立即停止')

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # run command
    run_parser = subparsers.add_parser('run', help='运行单个配置文件')
    run_parser.add_argument('config', help='YAML配置文件路径')
    run_parser.add_argument('-m', '--mode', choices=['interactive', 'daemon'],
                           default='interactive', help='运行模式')
    run_parser.add_argument('-w', '--workers', type=int, default=1,
                           help='并发工作线程数')

    # batch command
    batch_parser = subparsers.add_parser('batch', help='批量运行配置目录')
    batch_parser.add_argument('config_dir', help='配置文件目录路径')
    batch_parser.add_argument('-m', '--mode', choices=['interactive', 'daemon'],
                             default='interactive', help='运行模式')
    batch_parser.add_argument('--pattern', default='*.yaml',
                             help='文件匹配模式')
    batch_parser.add_argument('--parallel', type=int, default=3,
                             help='并行启动数量')

    # serve command
    serve_parser = subparsers.add_parser('serve', help='启动后台服务')
    serve_parser.add_argument('config_dir', help='配置文件目录路径')
    serve_parser.add_argument('-p', '--port', type=int, default=8888,
                             help='API服务端口')
    serve_parser.add_argument('--workers', type=int,
                             help='工作进程数')
    serve_parser.add_argument('--reload', action='store_true',
                             help='配置文件变化时自动重载')

    # validate command
    validate_parser = subparsers.add_parser('validate', help='验证配置文件')
    validate_parser.add_argument('config_path', help='配置文件或目录路径')
    validate_parser.add_argument('--strict', action='store_true',
                                help='严格模式')

    # info command
    subparsers.add_parser('info', help='显示系统信息')

    return parser


def handle_run_command(args, parser) -> int:
    """Handle run subcommand"""
    config_path = Path(args.config)

    if not config_path.exists():
        print(f"[ERROR] 配置文件不存在: {args.config}")
        return 1

    print(f"[RUN] 运行配置: {args.config}")

    # Load and validate config
    try:
        from agentscope_paas.config.loader import ConfigLoader
        loader = ConfigLoader(str(config_path))
        success, config, errors = loader.load()
        if not success:
            print(f"[ERROR] 配置加载失败: {', '.join(errors)}")
            return 1
    except Exception as e:
        print(f"[ERROR] 配置加载失败: {e}")
        return 1

    # Launch agent
    launcher = Launcher(mode=args.mode)
    error_handler = ErrorHandler(strict=args.strict)

    if not launcher.launch_agent(config, "agent1"):
        error_handler.handle_launch_error("agent1", Exception("Launch failed"),
                                          args.strict)
        return 1

    # Run in requested mode
    if args.mode == 'interactive':
        launcher.launch_interactive_session()
    else:
        print("后台模式尚未完全实现")

    return 0


def handle_batch_command(args, parser) -> int:
    """Handle batch subcommand"""
    print(f"[BATCH] 扫描配置目录: {args.config_dir}")

    processor = ConfigProcessor()
    error_handler = ErrorHandler(strict=args.strict)

    try:
        config_files = processor.scan_directory(args.config_dir, args.pattern)
    except Exception as e:
        print(f"[ERROR] 目录扫描失败: {e}")
        return 1

    if not config_files:
        print("[WARN] 未找到配置文件")
        return 0

    print(f"找到 {len(config_files)} 个配置文件:")
    for config_file in config_files:
        print(f"  [OK] {Path(config_file).name}")

    # Launch agents
    launcher = Launcher(mode=args.mode)
    success_count = 0

    for config_file in config_files:
        try:
            from agentscope_paas.config.loader import ConfigLoader
            loader = ConfigLoader(config_file)
            success, config, errors = loader.load()

            if not success:
                print(f"  [FAIL] {Path(config_file).name}: {', '.join(errors)}")
                continue

            agent_id = Path(config_file).stem
            if launcher.launch_agent(config, agent_id):
                success_count += 1
            else:
                error_handler.handle_launch_error(agent_id, Exception("Launch failed"),
                                                  True)

        except Exception as e:
            error_handler.handle_config_error(config_file, e, args.strict)

    print(f"\n[RESULT] 启动结果:")
    print(f"  [OK] 成功: {success_count} agents")
    print(f"  [FAIL] 失败: {len(config_files) - success_count} agents")

    if args.mode == 'interactive' and success_count > 0:
        launcher.launch_interactive_session()

    return 0


def handle_validate_command(args, parser) -> int:
    """Handle validate subcommand"""
    print(f"[VALIDATE] 验证配置: {args.config_path}")

    path = Path(args.config_path)

    if path.is_file():
        config_files = [str(path)]
    elif path.is_dir():
        processor = ConfigProcessor()
        try:
            config_files = processor.scan_directory(str(path), "*.yaml")
        except Exception as e:
            print(f"[ERROR] 目录扫描失败: {e}")
            return 1
    else:
        print(f"[ERROR] 路径不存在: {args.config_path}")
        return 1

    valid_count = 0
    error_handler = ErrorHandler(strict=args.strict)

    for config_file in config_files:
        try:
            from agentscope_paas.config.loader import ConfigLoader
            loader = ConfigLoader(config_file)
            success, config, errors = loader.load()

            if success:
                valid_count += 1
                print(f"  [OK] {Path(config_file).name}")
            else:
                print(f"  [FAIL] {Path(config_file).name}: {', '.join(errors)}")
                error_handler.handle_config_error(config_file, Exception(', '.join(errors)), args.strict)

        except Exception as e:
            print(f"  [FAIL] {Path(config_file).name}: {e}")
            error_handler.handle_config_error(config_file, e, args.strict)

    print(f"\n[RESULT] 验证结果: {valid_count}/{len(config_files)} 有效")
    return 0


def handle_info_command(args, parser) -> int:
    """Handle info subcommand"""
    print("AgentScope PaaS 系统信息")
    print("=" * 50)
    print(f"版本: 0.1.0")
    print(f"Python: {sys.version}")

    try:
        import agentscope
        print(f"AgentScope: {agentscope.__version__}")
    except:
        print("AgentScope: 未安装")

    print("=" * 50)
    return 0


def main() -> int:
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose, args.quiet)

    # Handle no command
    if not args.command:
        parser.print_help()
        return 0

    # Setup signal handlers
    setup_signal_handlers()

    # Route to command handler
    try:
        if args.command == 'run':
            return handle_run_command(args, parser)
        elif args.command == 'batch':
            return handle_batch_command(args, parser)
        elif args.command == 'serve':
            print("[SERVE] 启动后台服务模式 (尚未完全实现)")
            return 0
        elif args.command == 'validate':
            return handle_validate_command(args, parser)
        elif args.command == 'info':
            return handle_info_command(args, parser)
        else:
            parser.print_help()
            return 0

    except KeyboardInterrupt:
        print("\n[INFO] 操作已取消")
        return 130
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        return 1


def console_script_main() -> int:
    """Entry point for console_scripts - properly handles sys.argv"""
    return main()


if __name__ == '__main__':
    sys.exit(main())