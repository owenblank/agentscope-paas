"""
配置加载器模块

负责从YAML文件中加载配置、解析配置内容，并提供统一的配置访问接口。
支持单智能体和多智能体团队配置文件的加载和解析。
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .validator import ConfigValidator, ConfigValidationError


class ConfigLoader:
    """YAML配置文件加载器"""

    def __init__(self, config_path: str):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.validator = ConfigValidator()
        self.raw_config: Dict[str, Any] = {}
        self.config_type: Optional[str] = None  # "single" 或 "team"

    def load(self) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        加载并验证配置文件

        Returns:
            (是否成功, 配置字典, 错误列表)
        """
        errors = []

        try:
            # 1. 检查文件是否存在
            if not os.path.exists(self.config_path):
                errors.append(f"配置文件不存在: {self.config_path}")
                return False, {}, errors

            # 2. 读取YAML文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                try:
                    self.raw_config = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    errors.append(f"YAML文件解析失败: {str(e)}")
                    return False, {}, errors

            # 3. 检查配置是否为空
            if not self.raw_config:
                errors.append("配置文件为空")
                return False, {}, errors

            # 4. 确定配置类型
            self.config_type = self._determine_config_type()

            # 5. 根据类型进行验证
            if self.config_type == "single":
                is_valid, validation_errors = self.validator.validate_agent_config(self.raw_config)
            elif self.config_type == "team":
                is_valid, validation_errors = self.validator.validate_team_config(self.raw_config)
            else:
                errors.append("无法识别的配置类型，配置文件必须包含 agent_metadata 或 team_metadata")
                return False, {}, errors

            if not is_valid:
                errors.extend(validation_errors)
                return False, {}, errors

            # 6. 返回验证后的配置
            return True, self.raw_config, []

        except Exception as e:
            errors.append(f"加载配置时发生异常: {str(e)}")
            return False, {}, errors

    def _determine_config_type(self) -> Optional[str]:
        """
        确定配置文件类型

        Returns:
            "single" (单智能体), "team" (多智能体团队), 或 None
        """
        if not isinstance(self.raw_config, dict):
            return None

        # 检查是否包含团队配置
        if "team_metadata" in self.raw_config:
            return "team"

        # 检查是否包含单智能体配置
        if "agent_metadata" in self.raw_config:
            return "single"

        return None

    def get_config_type(self) -> Optional[str]:
        """
        获取配置文件类型

        Returns:
            "single", "team", 或 None
        """
        return self.config_type

    def get_full_config(self) -> Dict[str, Any]:
        """
        获取完整的配置字典

        Returns:
            完整的配置字典
        """
        return self.raw_config

    def get_agent_metadata(self) -> Dict[str, Any]:
        """
        获取智能体元数据

        Returns:
            智能体元数据字典
        """
        if self.config_type == "single":
            return self.raw_config.get("agent_metadata", {})
        elif self.config_type == "team":
            return self.raw_config.get("team_metadata", {})
        return {}

    def get_model_config(self, agent_index: int = 0) -> Dict[str, Any]:
        """
        获取模型配置

        Args:
            agent_index: 智能体索引（用于多智能体配置）

        Returns:
            模型配置字典
        """
        if self.config_type == "single":
            return self.raw_config.get("model_config", {})
        elif self.config_type == "team":
            agents = self.raw_config.get("agents", [])
            if agent_index < len(agents):
                return agents[agent_index].get("model_config", {})
            # 如果没有独立配置，使用全局配置
            return self.raw_config.get("global_model_config", {})
        return {}

    def get_prompt_config(self, agent_index: int = 0) -> Dict[str, Any]:
        """
        获取提示词配置

        Args:
            agent_index: 智能体索引（用于多智能体配置）

        Returns:
            提示词配置字典
        """
        if self.config_type == "single":
            return self.raw_config.get("prompt_config", {})
        elif self.config_type == "team":
            agents = self.raw_config.get("agents", [])
            if agent_index < len(agents):
                return agents[agent_index].get("prompt_config", {})
        return {}

    def get_memory_config(self, agent_index: int = 0) -> Dict[str, Any]:
        """
        获取记忆配置

        Args:
            agent_index: 智能体索引（用于多智能体配置）

        Returns:
            记忆配置字典
        """
        if self.config_type == "single":
            return self.raw_config.get("memory_config", {})
        elif self.config_type == "team":
            agents = self.raw_config.get("agents", [])
            if agent_index < len(agents):
                return agents[agent_index].get("memory_config", {})
        return {}

    def get_knowledge_config(self, agent_index: int = 0) -> Dict[str, Any]:
        """
        获取知识库配置

        Args:
            agent_index: 智能体索引（用于多智能体配置）

        Returns:
            知识库配置字典
        """
        if self.config_type == "single":
            return self.raw_config.get("knowledge_config", {})
        elif self.config_type == "team":
            agents = self.raw_config.get("agents", [])
            if agent_index < len(agents):
                return agents[agent_index].get("knowledge_config", {})
        return {}

    def get_skills_config(self, agent_index: int = 0) -> Dict[str, Any]:
        """
        获取技能配置

        Args:
            agent_index: 智能体索引（用于多智能体配置）

        Returns:
            技能配置字典
        """
        if self.config_type == "single":
            return self.raw_config.get("skills_config", {})
        elif self.config_type == "team":
            agents = self.raw_config.get("agents", [])
            if agent_index < len(agents):
                return agents[agent_index].get("skills_config", {})
        return {}

    def get_tool_config(self, agent_index: int = 0) -> Dict[str, Any]:
        """
        获取工具配置

        Args:
            agent_index: 智能体索引（用于多智能体配置）

        Returns:
            工具配置字典
        """
        if self.config_type == "single":
            return self.raw_config.get("tool_config", {})
        elif self.config_type == "team":
            agents = self.raw_config.get("agents", [])
            if agent_index < len(agents):
                return agents[agent_index].get("tool_config", {})
        return {}

    def get_behavior_config(self, agent_index: int = 0) -> Dict[str, Any]:
        """
        获取行为控制配置

        Args:
            agent_index: 智能体索引（用于多智能体配置）

        Returns:
            行为控制配置字典
        """
        if self.config_type == "single":
            return self.raw_config.get("behavior_config", {})
        elif self.config_type == "team":
            agents = self.raw_config.get("agents", [])
            if agent_index < len(agents):
                return agents[agent_index].get("behavior_config", {})
        return {}

    def get_agents_list(self) -> List[Dict[str, Any]]:
        """
        获取智能体列表（多智能体配置）

        Returns:
            智能体配置列表
        """
        if self.config_type == "team":
            return self.raw_config.get("agents", [])
        return []

    def get_team_metadata(self) -> Dict[str, Any]:
        """
        获取团队元数据（多智能体配置）

        Returns:
            团队元数据字典
        """
        if self.config_type == "team":
            return self.raw_config.get("team_metadata", {})
        return {}

    def get_collaboration_config(self) -> Dict[str, Any]:
        """
        获取协作配置（多智能体配置）

        Returns:
            协作配置字典
        """
        if self.config_type == "team":
            return self.raw_config.get("collaboration_config", {})
        return {}

    def get_task_context(self) -> Dict[str, Any]:
        """
        获取任务上下文（多智能体配置）

        Returns:
            任务上下文字典
        """
        if self.config_type == "team":
            return self.raw_config.get("task_context", {})
        return {}

    def get_monitoring_config(self, agent_index: int = 0) -> Dict[str, Any]:
        """
        获取监控配置

        Args:
            agent_index: 智能体索引（用于多智能体配置）

        Returns:
            监控配置字典
        """
        if self.config_type == "single":
            return self.raw_config.get("monitoring_config", {})
        elif self.config_type == "team":
            agents = self.raw_config.get("agents", [])
            if agent_index < len(agents):
                return agents[agent_index].get("monitoring_config", {})
            # 团队级别的监控配置
            return self.raw_config.get("logging_config", {})
        return {}

    def get_mcp_config(self, agent_index: int = 0) -> Dict[str, Any]:
        """
        获取MCP配置

        Args:
            agent_index: 智能体索引（用于多智能体配置）

        Returns:
            MCP配置字典
        """
        if self.config_type == "single":
            return self.raw_config.get("mcp_config", {})
        elif self.config_type == "team":
            agents = self.raw_config.get("agents", [])
            if agent_index < len(agents):
                return agents[agent_index].get("mcp_config", {})
            # 团队级别的MCP配置
            return self.raw_config.get("global_mcp_config", {})
        return {}

    def get_built_in_tools_config(self, agent_index: int = 0) -> Dict[str, Any]:
        """
        获取内置工具配置

        Args:
            agent_index: 智能体索引（用于多智能体配置）

        Returns:
            内置工具配置字典
        """
        if self.config_type == "single":
            return self.raw_config.get("built_in_tools_config", {})
        elif self.config_type == "team":
            agents = self.raw_config.get("agents", [])
            if agent_index < len(agents):
                return agents[agent_index].get("built_in_tools_config", {})
            # 团队级别的内置工具配置
            return self.raw_config.get("global_built_in_tools_config", {})
        return {}

    def get_context_compression_config(self, agent_index: int = 0) -> Dict[str, Any]:
        """
        获取上下文压缩配置

        Args:
            agent_index: 智能体索引（用于多智能体配置）

        Returns:
            上下文压缩配置字典
        """
        if self.config_type == "single":
            return self.raw_config.get("context_compression_config", {})
        elif self.config_type == "team":
            agents = self.raw_config.get("agents", [])
            if agent_index < len(agents):
                return agents[agent_index].get("context_compression_config", {})
            # 团队级别的上下文压缩配置
            return self.raw_config.get("global_context_compression_config", {})
        return {}

    def get_warnings(self) -> List[str]:
        """
        获取配置验证警告

        Returns:
            警告信息列表
        """
        return self.validator.get_warnings()

    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要信息

        Returns:
            配置摘要字典
        """
        summary = {
            "config_path": self.config_path,
            "config_type": self.config_type,
            "file_size": os.path.getsize(self.config_path) if os.path.exists(self.config_path) else 0
        }

        if self.config_type == "single":
            metadata = self.get_agent_metadata()
            summary.update({
                "agent_name": metadata.get("agent_name", "Unknown"),
                "agent_type": metadata.get("agent_type", "Unknown"),
                "agent_id": metadata.get("agent_id", "Unknown")
            })
        elif self.config_type == "team":
            team_metadata = self.get_team_metadata()
            agents = self.get_agents_list()
            summary.update({
                "team_name": team_metadata.get("team_name", "Unknown"),
                "team_id": team_metadata.get("team_id", "Unknown"),
                "collaboration_mode": team_metadata.get("collaboration_mode", "Unknown"),
                "agent_count": len(agents)
            })

        return summary


def load_config_from_file(config_path: str) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    便捷函数：从文件加载配置

    Args:
        config_path: 配置文件路径

    Returns:
        (是否成功, 配置字典, 错误列表)
    """
    loader = ConfigLoader(config_path)
    return loader.load()


def load_config_from_string(config_string: str) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    便捷函数：从字符串加载配置

    Args:
        config_string: YAML配置字符串

    Returns:
        (是否成功, 配置字典, 错误列表)
    """
    try:
        config = yaml.safe_load(config_string)
        validator = ConfigValidator()

        if "team_metadata" in config:
            is_valid, errors = validator.validate_team_config(config)
        elif "agent_metadata" in config:
            is_valid, errors = validator.validate_agent_config(config)
        else:
            return False, {}, ["配置必须包含 agent_metadata 或 team_metadata"]

        if is_valid:
            return True, config, []
        else:
            return False, {}, errors

    except Exception as e:
        return False, {}, [f"解析配置字符串失败: {str(e)}"]