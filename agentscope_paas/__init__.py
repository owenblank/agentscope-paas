"""
AgentScope-PaaS: 基于AgentScope的PaaS化智能体框架

这是一个配置文件驱动的智能体框架，用户只需通过YAML配置文件，
即可自动创建和运行单智能体或多智能体协作团队，无需编写任何业务代码。

核心特性:
- 配置文件驱动: YAML配置文件定义智能体行为
- 无代码化: 无需编写Python代码，修改配置即可使用
- 多智能体协作: 支持所有AgentScope协作模式
- 生产级: 完整的错误处理、日志记录、配置验证
"""

__version__ = "1.0.0"
__author__ = "AgentScope PaaS Team"

from .config.loader import ConfigLoader
from .config.validator import ConfigValidator
from .factory.agent_factory import AgentFactory
from .factory.team_factory import TeamFactory
from .core.engine import Engine

__all__ = [
    "ConfigLoader",
    "ConfigValidator",
    "AgentFactory",
    "TeamFactory",
    "Engine",
]