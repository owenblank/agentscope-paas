"""
单智能体工厂模块

根据YAML配置文件自动创建AgentScope标准智能体，支持所有智能体类型、
模型配置、记忆模块、工具调用等功能。
"""

import os
from typing import Any, Dict, Optional

try:
    from agentscope import init as agentscope_init
    from agentscope.agent import AgentBase, ReActAgent
    from agentscope.model import DashScopeChatModel, OpenAIChatModel, ChatModelBase
    from agentscope.formatter import DashScopeChatFormatter, OpenAIChatFormatter
    Agent = AgentBase  # 别名，保持向后兼容
except ImportError:
    # 如果没有安装agentscope，提供模拟类
    class AgentBase:
        pass

    class ReActAgent:
        pass

    class ChatModelBase:
        pass

    class DashScopeChatModel:
        pass

    class OpenAIChatModel:
        pass

    class DashScopeChatFormatter:
        pass

    class OpenAIChatFormatter:
        pass

    def agentscope_init(**kwargs):
        pass

    Agent = AgentBase

from ..config.loader import ConfigLoader
from ..utils.logger import get_logger
from ..utils.exceptions import AgentCreationError
from ..memory.session_memory_service import session_memory_service


class AgentFactory:
    """单智能体工厂类"""

    def __init__(self, config_loader: ConfigLoader):
        """
        初始化智能体工厂

        Args:
            config_loader: 配置加载器实例
        """
        self.config_loader = config_loader
        self.logger = get_logger(__name__)

    def create_agent(
        self,
        user_id: str = "default_user",
        session_id: str = "default_session"
    ) -> Optional[Agent]:
        """
        根据配置创建智能体

        Args:
            user_id: 用户ID（用于会话记忆）
            session_id: 会话ID（用于会话记忆）

        Returns:
            创建的智能体实例，失败返回None
        """
        try:
            # 获取配置
            metadata = self.config_loader.get_agent_metadata()
            model_config = self.config_loader.get_model_config()
            prompt_config = self.config_loader.get_prompt_config()

            # 验证必需配置
            if not metadata or not model_config or not prompt_config:
                raise AgentCreationError("缺少必需的配置信息")

            # 根据类型创建智能体 (现在都使用ReActAgent)
            agent_type = metadata.get("agent_type", "DialogAgent")
            agent_name = metadata.get("agent_name", "Unnamed Agent")
            agent_id = metadata.get("agent_id", "unknown")

            self.logger.info(f"开始创建智能体: {agent_name} (ID: {agent_id}, 类型: {agent_type})")

            # 创建模型配置
            model_kwargs = self._prepare_model_config(model_config)

            # 获取完整配置用于记忆初始化
            full_config = self.config_loader.get_full_config()

            # 准备记忆配置
            memory_instance = self._prepare_memory_config(
                full_config,
                user_id,
                session_id
            )

            # 创建智能体 - 统一使用ReActAgent
            if agent_type == "ReActAgent":
                agent = self._create_react_agent(
                    metadata,
                    model_config,
                    prompt_config,
                    memory_instance
                )
            else:
                # 对于DialogAgent和其他类型，都使用ReActAgent
                self.logger.info(f"使用ReActAgent替代 {agent_type}")
                agent = self._create_dialog_agent(
                    metadata,
                    model_config,
                    prompt_config,
                    memory_instance
                )

            if agent:
                self.logger.info(f"智能体创建成功: {agent_name}")
            else:
                self.logger.error(f"智能体创建失败: {agent_name}")

            return agent

        except Exception as e:
            self.logger.error(f"创建智能体时发生异常: {str(e)}")
            raise AgentCreationError(f"智能体创建失败: {str(e)}")

    def _create_react_agent(
        self,
        metadata: Dict[str, Any],
        model_config: Dict[str, Any],
        prompt_config: Dict[str, Any],
        memory_instance: Any = None
    ) -> Optional[AgentBase]:
        """
        创建ReActAgent推理行动智能体

        Args:
            metadata: 智能体元数据
            model_config: 模型配置
            prompt_config: 提示词配置
            memory_instance: 记忆实例（可选）

        Returns:
            AgentBase实例 (实际是ReActAgent)
        """
        try:
            # 初始化AgentScope (如果还没初始化)
            try:
                agentscope_init()
                self.logger.info("AgentScope initialized successfully")
            except Exception as e:
                self.logger.warning(f"AgentScope init warning: {str(e)}")

            system_prompt = prompt_config.get("system_prompt", "")
            agent_name = metadata.get("agent_name", "ReActAgent")

            # 创建模型实例和formatter
            model_instance, formatter_instance = self._create_model_instance(model_config)

            if model_instance is None:
                raise AgentCreationError("Failed to create model instance")

            if formatter_instance is None:
                raise AgentCreationError("Failed to create formatter instance")

            # 构建智能体参数 - 使用ReActAgent的正确参数
            agent_kwargs = {
                "name": agent_name,
                "sys_prompt": system_prompt,
                "model": model_instance,
                "formatter": formatter_instance
            }

            # 如果提供了记忆实例，添加到参数中
            if memory_instance is not None:
                agent_kwargs["memory"] = memory_instance
                self.logger.info(f"为智能体 {agent_name} 添加了记忆实例")

            # 创建ReActAgent
            agent = ReActAgent(**agent_kwargs)

            self.logger.info(f"ReActAgent created successfully: {agent_name}")
            return agent

        except Exception as e:
            self.logger.error(f"Failed to create ReActAgent: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def _create_dialog_agent(
        self,
        metadata: Dict[str, Any],
        model_config: Dict[str, Any],
        prompt_config: Dict[str, Any],
        memory_instance: Any = None
    ) -> Optional[AgentBase]:
        """
        创建对话智能体 (使用ReActAgent实现)

        Args:
            metadata: 智能体元数据
            model_config: 模型配置
            prompt_config: 提示词配置
            memory_instance: 记忆实例（可选）

        Returns:
            AgentBase实例 (实际是ReActAgent)
        """
        try:
            # 初始化AgentScope (如果还没初始化)
            try:
                agentscope_init()
                self.logger.info("AgentScope initialized successfully")
            except Exception as e:
                self.logger.warning(f"AgentScope init warning: {str(e)}")

            system_prompt = prompt_config.get("system_prompt", "")
            agent_name = metadata.get("agent_name", "Agent")

            # 创建模型实例和formatter
            model_instance, formatter_instance = self._create_model_instance(model_config)

            if model_instance is None:
                raise AgentCreationError("Failed to create model instance")

            if formatter_instance is None:
                raise AgentCreationError("Failed to create formatter instance")

            # 构建智能体参数 - 使用ReActAgent的正确参数
            agent_kwargs = {
                "name": agent_name,
                "sys_prompt": system_prompt,
                "model": model_instance,
                "formatter": formatter_instance
            }

            # 如果提供了记忆实例，添加到参数中
            if memory_instance is not None:
                agent_kwargs["memory"] = memory_instance
                self.logger.info(f"为智能体 {agent_name} 添加了记忆实例")

            # 使用ReActAgent创建对话智能体
            agent = ReActAgent(**agent_kwargs)

            self.logger.info(f"ReActAgent created successfully: {agent_name}")
            return agent

        except Exception as e:
            self.logger.error(f"Failed to create ReActAgent: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def _create_model_instance(self, model_config: Dict[str, Any]) -> tuple[Optional[ChatModelBase], Optional[Any]]:
        """
        创建模型实例和对应的formatter

        Args:
            model_config: 模型配置字典

        Returns:
            (ChatModelBase实例, Formatter实例) 的元组
        """
        try:
            model_name = model_config.get("model_name", "")
            api_key = model_config.get("api_key", "")
            base_url = model_config.get("base_url", "")

            # 根据模型名称或base_url判断使用哪个模型类
            if "dashscope" in base_url.lower() or "qwen" in model_name.lower():
                # 使用阿里云百练
                self.logger.info(f"Creating DashScopeChatModel: {model_name}")

                # 构建DashScope模型配置 - 使用正确的参数名
                model_config_dict = {
                    "model_name": model_name,
                    "api_key": api_key
                }

                # 添加可选参数
                if base_url:
                    model_config_dict["base_http_api_url"] = base_url

                # DashScope模型参数 - 使用generate_kwargs
                generate_kwargs = {}
                if "temperature" in model_config:
                    generate_kwargs["temperature"] = model_config["temperature"]
                if "max_tokens" in model_config:
                    generate_kwargs["max_tokens"] = model_config["max_tokens"]
                if "top_p" in model_config:
                    generate_kwargs["top_p"] = model_config["top_p"]

                if generate_kwargs:
                    model_config_dict["generate_kwargs"] = generate_kwargs

                # 创建DashScope模型和formatter
                model_instance = DashScopeChatModel(**model_config_dict)
                formatter_instance = DashScopeChatFormatter()

                self.logger.info("DashScopeChatModel and DashScopeChatFormatter created successfully")
                return model_instance, formatter_instance

            elif "openai" in base_url.lower() or "gpt" in model_name.lower():
                # 使用OpenAI兼容接口
                self.logger.info(f"Creating OpenAIChatModel: {model_name}")

                model_config_dict = {
                    "model_name": model_name,
                    "api_key": api_key
                }

                # OpenAI模型参数 - 使用generate_kwargs
                generate_kwargs = {}
                if "temperature" in model_config:
                    generate_kwargs["temperature"] = model_config["temperature"]
                if "max_tokens" in model_config:
                    generate_kwargs["max_tokens"] = model_config["max_tokens"]
                if "top_p" in model_config:
                    generate_kwargs["top_p"] = model_config["top_p"]

                if generate_kwargs:
                    model_config_dict["generate_kwargs"] = generate_kwargs

                # 设置客户端参数（如果需要自定义base_url）
                if base_url:
                    model_config_dict["client_kwargs"] = {"base_url": base_url}

                # 创建OpenAI模型和formatter
                model_instance = OpenAIChatModel(**model_config_dict)
                formatter_instance = OpenAIChatFormatter()

                self.logger.info("OpenAIChatModel and OpenAIChatFormatter created successfully")
                return model_instance, formatter_instance

            else:
                # 默认使用OpenAI兼容接口
                self.logger.info(f"Creating default OpenAIChatModel: {model_name}")

                model_config_dict = {
                    "model_name": model_name,
                    "api_key": api_key
                }

                # 设置客户端参数（如果需要自定义base_url）
                if base_url:
                    model_config_dict["client_kwargs"] = {"base_url": base_url}

                # 创建OpenAI模型和formatter
                model_instance = OpenAIChatModel(**model_config_dict)
                formatter_instance = OpenAIChatFormatter()

                self.logger.info("Default OpenAIChatModel and OpenAIChatFormatter created successfully")
                return model_instance, formatter_instance

        except Exception as e:
            self.logger.error(f"Failed to create model instance: {str(e)}")
            import traceback
            self.logger.error(f"Model creation traceback: {traceback.format_exc()}")
            return None, None

    def _prepare_model_config(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备模型配置参数 (保留用于兼容性)

        Args:
            model_config: 原始模型配置

        Returns:
            AgentScope格式的模型配置
        """
        # 提取基础模型配置
        config = {
            "model": model_config.get("model_name", "gpt-4"),
            "api_key": model_config.get("api_key", ""),
            "base_url": model_config.get("base_url", "")
        }

        # 添加可选参数
        optional_params = {
            "temperature": "temperature",
            "max_tokens": "max_tokens",
            "top_p": "top_p",
            "frequency_penalty": "frequency_penalty",
            "presence_penalty": "presence_penalty"
        }

        for param, key in optional_params.items():
            if key in model_config and model_config[key] is not None:
                config[param] = model_config[key]

        return config

    def create_agent_with_tools(self, tools: list) -> Optional[Agent]:
        """
        创建带工具调用的智能体

        Args:
            tools: 工具列表

        Returns:
            带工具的智能体实例
        """
        try:
            agent = self.create_agent()
            if agent and hasattr(agent, 'tools'):
                agent.tools = tools
                self.logger.info("智能体工具配置成功")
            return agent
        except Exception as e:
            self.logger.error(f"创建带工具的智能体失败: {str(e)}")
            return None

    def create_agent_with_memory(self, memory_config: Dict[str, Any]) -> Optional[Agent]:
        """
        创建带记忆的智能体

        Args:
            memory_config: 记忆配置

        Returns:
            带记忆的智能体实例
        """
        try:
            agent = self.create_agent()
            # 这里可以根据memory_config配置记忆模块
            # 具体实现依赖于AgentScope的记忆API
            return agent
        except Exception as e:
            self.logger.error(f"创建带记忆的智能体失败: {str(e)}")
            return None

    def _prepare_memory_config(
        self,
        config: Dict[str, Any],
        user_id: str = "default_user",
        session_id: str = "default_session"
    ) -> Any:
        """
        准备记忆配置，创建AgentScope兼容的记忆对象

        Args:
            config: 智能体配置
            user_id: 用户ID
            session_id: 会话ID

        Returns:
            记忆对象实例
        """
        try:
            # 检查是否启用了会话记忆
            session_memory_config = config.get('session_memory_config', {})

            if not session_memory_config or not session_memory_config.get('enabled', False):
                # 默认使用内存记忆
                self.logger.info("使用内存记忆存储")
                if 'InMemoryMemory' in locals():
                    return InMemoryMemory()
                else:
                    # 返回None，让AgentScope使用默认记忆
                    return None

            # 准备记忆配置字典
            memory_config_dict = {
                'session_memory': {
                    'enabled': True,
                    'storage_type': session_memory_config.get('storage_type', 'memory'),
                    'redis_config': session_memory_config.get('redis_config', {}),
                    'ttl': session_memory_config.get('ttl', 3600),
                    'max_messages': session_memory_config.get('max_messages', 100),
                    'memory_key_prefix': session_memory_config.get('memory_key_prefix', 'session_memory')
                }
            }

            # 根据存储类型创建记忆实例
            storage_type = session_memory_config.get('storage_type', 'memory')

            if storage_type == 'redis':
                redis_config = session_memory_config.get('redis_config', {})
                try:
                    # 尝试创建AgentScope RedisMemory（如果可用）
                    if 'RedisMemory' in globals() and RedisMemory is not None:
                        memory = RedisMemory(
                            redis_url=f"redis://{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}/{redis_config.get('db', 0)}",
                            password=redis_config.get('password'),
                            key_prefix=f"{session_memory_config.get('memory_key_prefix', 'session_memory')}:{user_id}:{session_id}"
                        )
                        self.logger.info(f"创建Redis记忆成功: {user_id}:{session_id}")
                        return memory
                    else:
                        self.logger.warning("AgentScope RedisMemory不可用，降级到内存存储")
                        # 初始化会话记忆服务
                        session_memory_service.get_memory_backend(user_id, session_id, memory_config_dict)
                        if 'InMemoryMemory' in locals():
                            return InMemoryMemory()
                        else:
                            return None

                except Exception as e:
                    self.logger.warning(f"Redis记忆创建失败: {e}，降级到内存存储")
                    # 初始化会话记忆服务（使用内存模式）
                    memory_config_dict['session_memory']['storage_type'] = 'memory'
                    session_memory_service.get_memory_backend(user_id, session_id, memory_config_dict)
                    if 'InMemoryMemory' in locals():
                        return InMemoryMemory()
                    else:
                        return None

            else:
                # 使用内存存储
                self.logger.info(f"使用内存存储: {user_id}:{session_id}")
                # 初始化会话记忆服务
                session_memory_service.get_memory_backend(user_id, session_id, memory_config_dict)
                if 'InMemoryMemory' in locals():
                    return InMemoryMemory()
                else:
                    return None

        except Exception as e:
            self.logger.error(f"准备记忆配置失败: {e}")
            # 返回None，让AgentScope使用默认记忆
            return None


def create_agent_from_config(config_path: str) -> Optional[Agent]:
    """
    便捷函数：从配置文件创建智能体

    Args:
        config_path: 配置文件路径

    Returns:
        创建的智能体实例，失败返回None
    """
    try:
        # 加载配置
        loader = ConfigLoader(config_path)
        success, config, errors = loader.load()

        if not success:
            print(f"配置加载失败: {errors}")
            return None

        # 创建智能体
        factory = AgentFactory(loader)
        agent = factory.create_agent()

        return agent

    except Exception as e:
        print(f"从配置创建智能体失败: {str(e)}")
        return None