# agentscope_paas/cli/interactive.py
import logging
from typing import Dict, Any


class InteractiveSession:
    """Manages interactive dialogue sessions with agents"""

    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.running = False
        self.logger = logging.getLogger(__name__)
        self.current_agent = list(agents.keys())[0] if agents else None

    def display_welcome(self) -> None:
        """Display welcome message"""
        print("💬 交互模式已启动")
        print(f"可用智能体: {', '.join(self.agents.keys())}")
        print(f"当前智能体: {self.current_agent}")
        print("输入 'exit' 退出，'switch <agent>' 切换智能体")
        print("-" * 50)

    def get_user_input(self) -> str:
        """Get input from user"""
        try:
            user_input = input(f"{self.current_agent}> ")
            return user_input.strip()
        except EOFError:
            return "exit"
        except KeyboardInterrupt:
            return "exit"

    def process_command(self, user_input: str) -> bool:
        """Process user command, returns False to exit"""
        if not user_input:
            return True

        if user_input.lower() in ['exit', 'quit', 'q']:
            print("再见！")
            return False

        if user_input.startswith('switch '):
            agent_name = user_input[7:].strip()
            if agent_name in self.agents:
                self.current_agent = agent_name
                print(f"已切换到智能体: {agent_name}")
            else:
                print(f"智能体不存在: {agent_name}")
            return True

        # Send to agent for processing
        response = self.send_to_agent(user_input)
        print(f"{self.current_agent}: {response}")

        return True

    def send_to_agent(self, message: str) -> str:
        """Send message to current agent"""
        if self.current_agent not in self.agents:
            return "错误: 当前智能体不可用"

        agent = self.agents[self.current_agent]
        try:
            # Call agent's chat method
            if hasattr(agent, 'chat'):
                return agent.chat(message)
            else:
                return f"收到消息: {message}"
        except Exception as e:
            self.logger.error(f"Agent error: {e}")
            return f"错误: {str(e)}"

    def run(self) -> None:
        """Run interactive session"""
        self.running = True
        self.display_welcome()

        while self.running:
            try:
                user_input = self.get_user_input()
                self.running = self.process_command(user_input)
            except Exception as e:
                print(f"错误: {e}")
                self.logger.error(f"Session error: {e}")
