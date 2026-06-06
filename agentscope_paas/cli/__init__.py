"""CLI package for AgentScope PaaS command-line interface."""

from agentscope_paas.cli.error_handler import ErrorHandler
from agentscope_paas.cli.config_processor import ConfigProcessor
from agentscope_paas.cli.main import main, console_script_main

__version__ = "0.1.0"

__all__ = ["ErrorHandler", "ConfigProcessor", "main", "console_script_main"]
