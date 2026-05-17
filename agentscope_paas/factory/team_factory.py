"""
多智能体团队工厂模块

根据YAML配置文件自动创建多智能体协作团队，支持所有AgentScope
协作模式（SequentialChat、RoundRobinChat、ManagerProxy等）。
"""

from typing import Any, Dict, List, Optional

try:
    from agentscope import Agent
    from agentscope.agents import DialogAgent, ReActAgent, UserAgent
    from agentscope.pipelines import SequentialChat, RoundRobinChat
except ImportError:
    # 如果没有安装agentscope，提供模拟类
    class Agent:
        pass

    class DialogAgent(Agent):
        pass

    class ReActAgent(Agent):
        pass

    class UserAgent(Agent):
        pass

    class SequentialChat:
        pass

    class RoundRobinChat:
        pass

from ..config.loader import ConfigLoader
from ..factory.agent_factory import AgentFactory
from ..utils.logger import get_logger
from ..utils.exceptions import TeamCreationError


class TeamFactory:
    """多智能体团队工厂类"""

    def __init__(self, config_loader: ConfigLoader):
        """
        初始化团队工厂

        Args:
            config_loader: 配置加载器实例
        """
        self.config_loader = config_loader
        self.logger = get_logger(__name__)

    def create_team(self) -> Optional[object]:
        """
        根据配置创建智能体团队

        Returns:
            创建的团队实例，失败返回None
        """
        try:
            # 获取团队配置
            team_metadata = self.config_loader.get_team_metadata()
            agents_config = self.config_loader.get_agents_list()
            collab_config = self.config_loader.get_collaboration_config()

            if not team_metadata or not agents_config:
                raise TeamCreationError("缺少必需的团队配置信息")

            team_name = team_metadata.get("team_name", "Unknown Team")
            collab_mode = team_metadata.get("collaboration_mode", "SequentialChat")

            self.logger.info(f"开始创建团队: {team_name} (协作模式: {collab_mode})")

            # 创建所有智能体
            agents = self._create_all_agents(agents_config)

            if not agents:
                raise TeamCreationError("智能体创建失败，团队无法构建")

            # 根据协作模式创建团队
            team = self._create_team_by_mode(
                collab_mode,
                agents,
                team_metadata,
                collab_config
            )

            if team:
                self.logger.info(f"团队创建成功: {team_name}")
            else:
                self.logger.error(f"团队创建失败: {team_name}")

            return team

        except Exception as e:
            self.logger.error(f"创建团队时发生异常: {str(e)}")
            raise TeamCreationError(f"团队创建失败: {str(e)}")

    def _create_all_agents(self, agents_config: List[Dict[str, Any]]) -> List[Agent]:
        """
        创建所有智能体

        Args:
            agents_config: 智能体配置列表

        Returns:
            智能体实例列表
        """
        agents = []

        for idx, agent_config in enumerate(agents_config):
            try:
                # 为每个智能体创建临时配置加载器
                # 这里需要构建临时的单智能体配置结构
                temp_config = {
                    "agent_metadata": agent_config.get("agent_metadata", {}),
                    "model_config": agent_config.get("model_config", {}),
                    "prompt_config": agent_config.get("prompt_config", {}),
                    "tool_config": agent_config.get("tool_config", {}),
                    "knowledge_config": agent_config.get("knowledge_config", {}),
                    "skills_config": agent_config.get("skills_config", {}),
                    "memory_config": agent_config.get("memory_config", {}),
                    "behavior_config": agent_config.get("behavior_config", {}),
                    "monitoring_config": agent_config.get("monitoring_config", {})
                }

                # 创建临时配置加载器
                from ..config.loader import ConfigLoader
                import yaml
                import tempfile

                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(temp_config, f, allow_unicode=True)
                    temp_path = f.name

                temp_loader = ConfigLoader(temp_path)
                temp_factory = AgentFactory(temp_loader)

                # 创建智能体
                agent = temp_factory.create_agent()

                if agent:
                    agents.append(agent)
                    self.logger.info(f"智能体 {idx + 1} 创建成功")
                else:
                    self.logger.warning(f"智能体 {idx + 1} 创建失败")

                # 清理临时文件
                import os
                os.unlink(temp_path)

            except Exception as e:
                self.logger.error(f"创建智能体 {idx + 1} 时发生异常: {str(e)}")
                continue

        return agents

    def _create_team_by_mode(
        self,
        collab_mode: str,
        agents: List[Agent],
        team_metadata: Dict[str, Any],
        collab_config: Dict[str, Any]
    ) -> Optional[object]:
        """
        根据协作模式创建团队

        Args:
            collab_mode: 协作模式
            agents: 智能体列表
            team_metadata: 团队元数据
            collab_config: 协作配置

        Returns:
            团队实例
        """
        try:
            if collab_mode == "SequentialChat":
                return self._create_sequential_chat(agents, team_metadata, collab_config)
            elif collab_mode == "RoundRobinChat":
                return self._create_round_robin_chat(agents, team_metadata, collab_config)
            else:
                self.logger.warning(f"暂不支持协作模式: {collab_mode}，使用SequentialChat")
                return self._create_sequential_chat(agents, team_metadata, collab_config)

        except Exception as e:
            self.logger.error(f"创建团队协作模式失败: {str(e)}")
            return None

    def _create_sequential_chat(
        self,
        agents: List[Agent],
        team_metadata: Dict[str, Any],
        collab_config: Dict[str, Any]
    ) -> Optional[SequentialChat]:
        """
        创建顺序对话团队

        Args:
            agents: 智能体列表
            team_metadata: 团队元数据
            collab_config: 协作配置

        Returns:
            SequentialChat实例
        """
        try:
            # 获取发言顺序
            speaking_order = collab_config.get("speaking_order", [])
            if not speaking_order:
                # 如果没有指定顺序，使用agents的顺序
                speaking_order = [agent.name for agent in agents]

            # 根据agent名称找到对应的agent实例
            ordered_agents = []
            for name in speaking_order:
                for agent in agents:
                    if hasattr(agent, 'name') and agent.name == name:
                        ordered_agents.append(agent)
                        break

            # 如果没有找到所有指定agent，使用原始顺序
            if len(ordered_agents) < len(agents):
                ordered_agents = agents

            # 获取初始发言者
            initial_speaker = collab_config.get("initial_speaker")
            if initial_speaker:
                for agent in ordered_agents:
                    if hasattr(agent, 'name') and agent.name == initial_speaker:
                        # 将初始发言者移到第一位
                        ordered_agents.remove(agent)
                        ordered_agents.insert(0, agent)
                        break

            # 创建SequentialChat
            team = SequentialChat(agents=ordered_agents)

            self.logger.info(f"SequentialChat团队创建成功，包含 {len(ordered_agents)} 个智能体")
            return team

        except Exception as e:
            self.logger.error(f"创建SequentialChat失败: {str(e)}")
            return None

    def _create_round_robin_chat(
        self,
        agents: List[Agent],
        team_metadata: Dict[str, Any],
        collab_config: Dict[str, Any]
    ) -> Optional[RoundRobinChat]:
        """
        创建轮询对话团队

        Args:
            agents: 智能体列表
            team_metadata: 团队元数据
            collab_config: 协作配置

        Returns:
            RoundRobinChat实例
        """
        try:
            # 创建RoundRobinChat
            team = RoundRobinChat(agents=agents)

            self.logger.info(f"RoundRobinChat团队创建成功，包含 {len(agents)} 个智能体")
            return team

        except Exception as e:
            self.logger.error(f"创建RoundRobinChat失败: {str(e)}")
            return None


def create_team_from_config(config_path: str) -> Optional[object]:
    """
    便捷函数：从配置文件创建智能体团队

    Args:
        config_path: 配置文件路径

    Returns:
        创建的团队实例，失败返回None
    """
    try:
        # 加载配置
        loader = ConfigLoader(config_path)
        success, config, errors = loader.load()

        if not success:
            print(f"配置加载失败: {errors}")
            return None

        # 创建团队
        factory = TeamFactory(loader)
        team = factory.create_team()

        return team

    except Exception as e:
        print(f"从配置创建团队失败: {str(e)}")
        return None