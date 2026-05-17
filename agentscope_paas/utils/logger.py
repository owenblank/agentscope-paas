"""
日志工具模块

提供标准化的日志记录功能，支持不同日志级别、格式化输出、文件记录等。
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }

    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        # 格式化日志
        return super().format(record)


def setup_logger(
    name: str = "agentscope_paas",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径（可选）
        console: 是否输出到控制台

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)

    # 设置日志级别
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 清除现有处理器
    logger.handlers = []

    # 创建格式化器
    date_format = "%Y-%m-%d %H:%M:%S"
    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"

    # 控制台处理器
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # 使用带颜色的格式化器
        console_formatter = ColoredFormatter(
            fmt=log_format,
            datefmt=date_format
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)

        file_formatter = logging.Formatter(
            fmt=log_format,
            datefmt=date_format
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)


# 默认日志记录器
default_logger = setup_logger("agentscope_paas")


def log_config_info(logger: logging.Logger, config_info: dict) -> None:
    """
    记录配置信息

    Args:
        logger: 日志记录器
        config_info: 配置信息字典
    """
    logger.info("=" * 50)
    logger.info("配置信息")
    logger.info("=" * 50)

    for key, value in config_info.items():
        if isinstance(value, dict):
            logger.info(f"{key}:")
            for sub_key, sub_value in value.items():
                logger.info(f"  {sub_key}: {sub_value}")
        else:
            logger.info(f"{key}: {value}")

    logger.info("=" * 50)


def log_agent_info(logger: logging.Logger, agent) -> None:
    """
    记录智能体信息

    Args:
        logger: 日志记录器
        agent: 智能体实例
    """
    logger.info("=" * 50)
    logger.info("智能体信息")
    logger.info("=" * 50)

    try:
        logger.info(f"名称: {agent.name}")
        logger.info(f"类型: {type(agent).__name__}")

        if hasattr(agent, 'system_prompt'):
            prompt = agent.system_prompt
            if len(prompt) > 100:
                prompt = prompt[:100] + "..."
            logger.info(f"系统提示词: {prompt}")

        if hasattr(agent, 'model_config'):
            logger.info(f"模型配置: {agent.model_config}")

    except Exception as e:
        logger.error(f"记录智能体信息失败: {str(e)}")

    logger.info("=" * 50)