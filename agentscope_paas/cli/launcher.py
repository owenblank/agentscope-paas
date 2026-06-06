# agentscope_paas/cli/launcher.py
import logging
from typing import Dict, Any, Optional
from agentscope_paas.cli.interactive import InteractiveSession


class Launcher:
    """Manages agent lifecycle and execution modes"""

    def __init__(self, mode: str = "interactive"):
        self.mode = mode
        self.agents: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

    def launch_agent(self, config: Dict[str, Any], agent_id: str) -> bool:
        """Launch a single agent"""
        try:
            # Import AgentFactory and ConfigLoader
            from agentscope_paas.factory.agent_factory import AgentFactory
            from agentscope_paas.config.loader import ConfigLoader

            self.logger.info(f"Launching agent {agent_id}")

            # Create config loader and load configuration
            config_loader = ConfigLoader()
            config_loader.load_config(config)

            # Create agent using factory
            factory = AgentFactory(config_loader)
            agent = factory.create_agent()

            # Store agent
            self.agents[agent_id] = agent

            self.logger.info(f"Agent {agent_id} launched successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to launch agent {agent_id}: {e}")
            return False

    def launch_interactive_session(self, agents: Optional[Dict[str, Any]] = None) -> None:
        """Launch interactive dialogue session"""
        active_agents = agents or self.agents

        if not active_agents:
            print("没有可用的智能体")
            return

        session = InteractiveSession(active_agents)
        session.run()

    def start_daemon_service(self, config_dir: str, port: int = 8888) -> None:
        """Start background daemon service"""
        print(f"启动守护服务，端口: {port}")
        print(f"配置目录: {config_dir}")
        print("守护服务模式尚未实现")
        # TODO: Implement actual daemon service
