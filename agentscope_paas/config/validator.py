"""
配置验证器模块

负责验证YAML配置文件的完整性和正确性，包括必填字段检查、
数据类型验证、格式校验等，确保配置文件能够正确创建智能体。
"""

import re
from typing import Any, Dict, List, Optional, Tuple


class ConfigValidationError(Exception):
    """配置验证错误异常"""

    def __init__(self, message: str, field: str = ""):
        self.message = message
        self.field = field
        super().__init__(f"配置验证失败: {message} (字段: {field})")


class ConfigValidator:
    """配置验证器类"""

    # 必填字段列表
    REQUIRED_AGENT_FIELDS = [
        "agent_id",
        "agent_name",
        "agent_type",
        "description",
        "version"
    ]

    REQUIRED_MODEL_FIELDS = [
        "model_name",
        "api_key",
        "base_url"
    ]

    REQUIRED_PROMPT_FIELDS = [
        "system_prompt"
    ]

    # 支持的智能体类型
    SUPPORTED_AGENT_TYPES = ["ReActAgent", "DialogAgent", "FunctionCallAgent", "ToolAgent"]

    # 支持的协作模式
    SUPPORTED_COLLABORATION_MODES = ["SequentialChat", "RoundRobinChat", "ManagerProxy", "FreeChat"]

    def __init__(self):
        """初始化配置验证器"""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_agent_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证单智能体配置

        Args:
            config: 智能体配置字典

        Returns:
            (是否有效, 错误列表)
        """
        self.errors = []
        self.warnings = []

        try:
            # 验证基本结构
            if not isinstance(config, dict):
                self.errors.append("配置必须是字典类型")
                return False, self.errors

            # 验证必需的顶级字段
            if "agent_metadata" not in config:
                self.errors.append("缺少必需字段: agent_metadata")
            else:
                self._validate_agent_metadata(config["agent_metadata"])

            # 验证模型配置
            if "model_config" not in config:
                self.errors.append("缺少必需字段: model_config")
            else:
                self._validate_model_config(config["model_config"])

            # 验证提示词配置
            if "prompt_config" not in config:
                self.errors.append("缺少必需字段: prompt_config")
            else:
                self._validate_prompt_config(config["prompt_config"])

            # 可选字段验证
            if "knowledge_config" in config:
                self._validate_knowledge_config(config["knowledge_config"])

            if "skills_config" in config:
                self._validate_skills_config(config["skills_config"])

            return len(self.errors) == 0, self.errors

        except Exception as e:
            self.errors.append(f"验证过程中发生异常: {str(e)}")
            return False, self.errors

    def _validate_agent_metadata(self, metadata: Dict[str, Any]) -> None:
        """验证智能体元数据"""
        if not isinstance(metadata, dict):
            self.errors.append("agent_metadata 必须是字典类型")
            return

        # 检查必填字段
        for field in self.REQUIRED_AGENT_FIELDS:
            if field not in metadata:
                self.errors.append(f"agent_metadata 缺少必填字段: {field}")
            elif not metadata[field]:
                self.errors.append(f"agent_metadata.{field} 不能为空")

        # 验证agent_type
        if "agent_type" in metadata:
            agent_type = metadata["agent_type"]
            if agent_type not in self.SUPPORTED_AGENT_TYPES:
                self.warnings.append(
                    f"不支持的智能体类型: {agent_type}，"
                    f"支持的类型: {', '.join(self.SUPPORTED_AGENT_TYPES)}"
                )

        # 验证agent_id格式
        if "agent_id" in metadata:
            agent_id = metadata["agent_id"]
            if not re.match(r'^[a-z0-9_]+$', agent_id):
                self.errors.append(
                    "agent_id 只能包含小写字母、数字和下划线，"
                    "且不能以数字开头"
                )

        # 验证version格式
        if "version" in metadata:
            version = metadata["version"]
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                self.warnings.append(f"版本号格式建议为: x.y.z，当前为: {version}")

    def _validate_model_config(self, model_config: Dict[str, Any]) -> None:
        """验证模型配置"""
        if not isinstance(model_config, dict):
            self.errors.append("model_config 必须是字典类型")
            return

        # 检查必填字段
        for field in self.REQUIRED_MODEL_FIELDS:
            if field not in model_config:
                self.errors.append(f"model_config 缺少必填字段: {field}")
            elif not model_config[field]:
                self.errors.append(f"model_config.{field} 不能为空")

        # 验证base_url格式
        if "base_url" in model_config:
            base_url = model_config["base_url"]
            if not base_url.startswith(("http://", "https://")):
                self.errors.append("base_url 必须以 http:// 或 https:// 开头")

        # 验证数值范围
        if "temperature" in model_config:
            temp = model_config["temperature"]
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                self.errors.append("temperature 必须是0-2之间的数值")

        if "max_tokens" in model_config:
            tokens = model_config["max_tokens"]
            if not isinstance(tokens, int) or tokens <= 0:
                self.errors.append("max_tokens 必须是正整数")

    def _validate_prompt_config(self, prompt_config: Dict[str, Any]) -> None:
        """验证提示词配置"""
        if not isinstance(prompt_config, dict):
            self.errors.append("prompt_config 必须是字典类型")
            return

        # 检查必填字段
        for field in self.REQUIRED_PROMPT_FIELDS:
            if field not in prompt_config:
                self.errors.append(f"prompt_config 缺少必填字段: {field}")
            elif field == "system_prompt" and not prompt_config[field]:
                self.errors.append("system_prompt 不能为空")

        # 验证system_prompt长度
        if "system_prompt" in prompt_config:
            prompt = prompt_config["system_prompt"]
            if len(prompt) < 10:
                self.warnings.append("system_prompt 内容过短，可能影响智能体性能")

    def _validate_knowledge_config(self, knowledge_config: Dict[str, Any]) -> None:
        """验证知识库配置"""
        if not isinstance(knowledge_config, dict):
            self.errors.append("knowledge_config 必须是字典类型")
            return

        # 检查platform_knowledge配置
        if "platform_knowledge" in knowledge_config:
            platform_knowledge = knowledge_config["platform_knowledge"]
            if not isinstance(platform_knowledge, dict):
                self.errors.append("platform_knowledge 必须是字典类型")
                return

            # 验证必填字段
            if "platform_url" not in platform_knowledge:
                self.errors.append("platform_knowledge 缺少必填字段: platform_url")
            else:
                platform_url = platform_knowledge["platform_url"]
                if not platform_url.startswith(("http://", "https://")):
                    self.errors.append("platform_url 必须以 http:// 或 https:// 开头")

            # 验证连接配置
            if "connection_config" in platform_knowledge:
                conn_config = platform_knowledge["connection_config"]
                if "authentication" in conn_config:
                    auth = conn_config["authentication"]
                    if "type" in auth:
                        auth_type = auth["type"]
                        if auth_type not in ["bearer_token", "api_key", "oauth2"]:
                            self.warnings.append(f"不支持的认证类型: {auth_type}")

    def _validate_skills_config(self, skills_config: Dict[str, Any]) -> None:
        """验证技能配置"""
        if not isinstance(skills_config, dict):
            self.errors.append("skills_config 必须是字典类型")
            return

        # 检查上传模式配置
        if "upload_config" in skills_config:
            upload_config = skills_config["upload_config"]
            if not isinstance(upload_config, dict):
                self.errors.append("upload_config 必须是字典类型")
                return

            # 验证支持的文件大小
            if "max_file_size_mb" in upload_config:
                max_size = upload_config["max_file_size_mb"]
                if not isinstance(max_size, (int, float)) or max_size <= 0:
                    self.errors.append("max_file_size_mb 必须是正数")

            # 验证支持的文件格式
            if "supported_upload_methods" in upload_config:
                methods = upload_config["supported_upload_methods"]
                if not isinstance(methods, list):
                    self.errors.append("supported_upload_methods 必须是列表")
                else:
                    valid_methods = ["single_file", "folder", "zip"]
                    for method in methods:
                        if "method" in method and method["method"] not in valid_methods:
                            self.warnings.append(f"不支持的上传方法: {method.get('method')}")

    def validate_team_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证多智能体团队配置

        Args:
            config: 团队配置字典

        Returns:
            (是否有效, 错误列表)
        """
        self.errors = []
        self.warnings = []

        try:
            # 验证基本结构
            if not isinstance(config, dict):
                self.errors.append("配置必须是字典类型")
                return False, self.errors

            # 验证团队元数据
            if "team_metadata" not in config:
                self.errors.append("缺少必需字段: team_metadata")
            else:
                self._validate_team_metadata(config["team_metadata"])

            # 验证智能体列表
            if "agents" not in config:
                self.errors.append("缺少必需字段: agents")
            else:
                self._validate_agents_list(config["agents"])

            # 验证协作配置
            if "collaboration_config" in config:
                self._validate_collaboration_config(config["collaboration_config"])

            return len(self.errors) == 0, self.errors

        except Exception as e:
            self.errors.append(f"验证过程中发生异常: {str(e)}")
            return False, self.errors

    def _validate_team_metadata(self, team_metadata: Dict[str, Any]) -> None:
        """验证团队元数据"""
        if not isinstance(team_metadata, dict):
            self.errors.append("team_metadata 必须是字典类型")
            return

        # 检查必填字段
        required_team_fields = ["team_id", "team_name", "collaboration_mode", "team_goal"]
        for field in required_team_fields:
            if field not in team_metadata:
                self.errors.append(f"team_metadata 缺少必填字段: {field}")
            elif not team_metadata[field]:
                self.errors.append(f"team_metadata.{field} 不能为空")

        # 验证协作模式
        if "collaboration_mode" in team_metadata:
            mode = team_metadata["collaboration_mode"]
            if mode not in self.SUPPORTED_COLLABORATION_MODES:
                self.errors.append(
                    f"不支持的协作模式: {mode}，"
                    f"支持的模式: {', '.join(self.SUPPORTED_COLLABORATION_MODES)}"
                )

        # 验证终止条件
        if "termination_conditions" in team_metadata:
            term_conditions = team_metadata["termination_conditions"]
            if not isinstance(term_conditions, dict):
                self.errors.append("termination_conditions 必须是字典类型")
            elif "max_rounds" not in term_conditions:
                self.errors.append("termination_conditions 缺少必填字段: max_rounds")

    def _validate_agents_list(self, agents: List[Dict[str, Any]]) -> None:
        """验证智能体列表"""
        if not isinstance(agents, list):
            self.errors.append("agents 必须是列表类型")
            return

        if len(agents) == 0:
            self.errors.append("agents 列表不能为空")
            return

        # 验证每个智能体的配置
        for idx, agent in enumerate(agents):
            if not isinstance(agent, dict):
                self.errors.append(f"agents[{idx}] 必须是字典类型")
                continue

            if "agent_metadata" not in agent:
                self.errors.append(f"agents[{idx}] 缺少 agent_metadata")
            else:
                # 重用单智能体验证逻辑
                is_valid, agent_errors = self.validate_agent_config(agent)
                if not is_valid:
                    for error in agent_errors:
                        self.errors.append(f"agents[{idx}]: {error}")

    def _validate_collaboration_config(self, collab_config: Dict[str, Any]) -> None:
        """验证协作配置"""
        if not isinstance(collab_config, dict):
            self.errors.append("collaboration_config 必须是字典类型")
            return

        # 验证初始发言者
        if "initial_speaker" in collab_config:
            initial_speaker = collab_config["initial_speaker"]
            if not initial_speaker:
                self.errors.append("initial_speaker 不能为空")

        # 验证最大对话轮次
        if "max_conversation_rounds" in collab_config:
            max_rounds = collab_config["max_conversation_rounds"]
            if not isinstance(max_rounds, int) or max_rounds <= 0:
                self.errors.append("max_conversation_rounds 必须是正整数")

    def get_warnings(self) -> List[str]:
        """获取验证过程中的警告信息"""
        return self.warnings

    def clear_validation_results(self) -> None:
        """清除验证结果"""
        self.errors = []
        self.warnings = []