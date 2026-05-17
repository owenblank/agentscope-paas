"""
自定义异常类模块

定义框架中使用的各种自定义异常，提供清晰的错误信息和类型。
"""


class AgentScopePaaSError(Exception):
    """AgentScope-PaaS框架基础异常类"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ConfigError(AgentScopePaaSError):
    """配置相关错误"""

    def __init__(self, message: str, config_path: str = ""):
        self.config_path = config_path
        super().__init__(f"配置错误: {message} (配置文件: {config_path})")


class ValidationError(ConfigError):
    """配置验证错误"""

    def __init__(self, message: str, field: str = ""):
        self.field = field
        super().__init__(f"验证错误: {message} (字段: {field})")


class AgentCreationError(AgentScopePaaSError):
    """智能体创建错误"""

    def __init__(self, message: str, agent_name: str = ""):
        self.agent_name = agent_name
        super().__init__(f"智能体创建错误: {message} (智能体: {agent_name})")


class TeamCreationError(AgentScopePaaSError):
    """团队创建错误"""

    def __init__(self, message: str, team_name: str = ""):
        self.team_name = team_name
        super().__init__(f"团队创建错误: {message} (团队: {team_name})")


class EngineError(AgentScopePaaSError):
    """引擎运行错误"""

    def __init__(self, message: str):
        super().__init__(f"引擎错误: {message}")


class ModelConfigError(AgentScopePaaSError):
    """模型配置错误"""

    def __init__(self, message: str, model_name: str = ""):
        self.model_name = model_name
        super().__init__(f"模型配置错误: {message} (模型: {model_name})")


class ToolExecutionError(AgentScopePaaSError):
    """工具执行错误"""

    def __init__(self, message: str, tool_name: str = ""):
        self.tool_name = tool_name
        super().__init__(f"工具执行错误: {message} (工具: {tool_name})")


class KnowledgeBaseError(AgentScopePaaSError):
    """知识库错误"""

    def __init__(self, message: str, knowledge_base_id: str = ""):
        self.knowledge_base_id = knowledge_base_id
        super().__init__(f"知识库错误: {message} (知识库: {knowledge_base_id})")