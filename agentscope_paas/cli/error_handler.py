# agentscope_paas/cli/error_handler.py
import sys
from typing import Optional

from agentscope_paas.utils.logger import get_logger

class ErrorHandler:
    """Handles CLI errors with user-friendly messages"""

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.logger = get_logger(__name__)

    def handle_config_error(self, config_path: str, error: Exception, strict: bool) -> None:
        """Handle configuration file errors"""
        error_type = type(error).__name__

        # Log detailed error
        self.logger.error(f"Config error in {config_path}: {error_type} - {error}")

        if strict:
            print(f"[ERROR] 严重错误: 配置文件 {config_path} 无法加载")
            print(f"   错误类型: {error_type}")
            print(f"   详细信息: {error}")
            sys.exit(1)
        else:
            print(f"[WARN] 跳过配置: {config_path} ({error_type})")

    def handle_launch_error(self, agent_id: str, error: Exception, continue_on_error: bool) -> None:
        """Handle agent launch errors"""
        if continue_on_error:
            print(f"[WARN] 智能体 {agent_id} 启动失败，继续其他智能体")
            print(f"   错误: {error}")
        else:
            print(f"[ERROR] 智能体 {agent_id} 启动失败，停止所有操作")
            self.logger.error(f"Launch failed for {agent_id}: {error}")
            sys.exit(1)
