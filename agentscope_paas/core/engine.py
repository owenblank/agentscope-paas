"""
核心运行引擎模块

提供统一的智能体运行入口，封装AgentScope原生对话逻辑，支持单智能体对话、
多智能体协作任务的启动和执行。
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import asyncio

try:
    from agentscope import (
        initiate_agent as agentscope_initiate,
        run_agents as agentscope_run
    )
    from agentscope.message import Msg
except ImportError:
    # 如果没有安装agentscope，提供模拟类
    def agentscope_initiate(agent):
        pass

    def agentscope_run(agents, tasks):
        pass

    class Msg:
        def __init__(self, name, content, role, **kwargs):
            self.name = name
            self.content = content
            self.role = role

from ..config.loader import ConfigLoader
from ..factory.agent_factory import AgentFactory
from ..factory.team_factory import TeamFactory
from ..utils.logger import get_logger
from ..utils.exceptions import EngineError


class Engine:
    """智能体运行引擎"""

    def __init__(self, config_path: str):
        """
        初始化引擎

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config_loader = ConfigLoader(config_path)
        self.logger = get_logger(__name__)

        self.agent = None  # 单智能体实例
        self.team = None   # 团队实例
        self.config_type = None  # 配置类型

        # 初始化AgentScope
        self._init_agentscope()

    def _init_agentscope(self) -> None:
        """初始化AgentScope环境"""
        try:
            import agentscope
            self.logger.info("AgentScope环境初始化成功")
        except ImportError:
            self.logger.warning("AgentScope未安装，请运行: pip install agentscope")
            raise EngineError("AgentScope未安装")

    def initialize(self) -> bool:
        """
        初始化引擎，加载配置并创建智能体/团队

        Returns:
            是否初始化成功
        """
        try:
            # 加载配置
            success, config, errors = self.config_loader.load()

            if not success:
                self.logger.error(f"配置加载失败: {errors}")
                return False

            self.config_type = self.config_loader.get_config_type()
            self.logger.info(f"配置类型: {self.config_type}")

            if self.config_type == "single":
                return self._initialize_single_agent()
            elif self.config_type == "team":
                return self._initialize_team()
            else:
                self.logger.error("无法识别的配置类型")
                return False

        except Exception as e:
            self.logger.error(f"初始化引擎失败: {str(e)}")
            return False

    def _initialize_single_agent(self) -> bool:
        """
        初始化单智能体

        Returns:
            是否初始化成功
        """
        try:
            factory = AgentFactory(self.config_loader)
            self.agent = factory.create_agent()

            if self.agent:
                self.logger.info(f"单智能体初始化成功: {self.agent.name}")
                return True
            else:
                self.logger.error("单智能体初始化失败")
                return False

        except Exception as e:
            self.logger.error(f"单智能体初始化异常: {str(e)}")
            return False

    def _initialize_team(self) -> bool:
        """
        初始化多智能体团队

        Returns:
            是否初始化成功
        """
        try:
            factory = TeamFactory(self.config_loader)
            self.team = factory.create_team()

            if self.team:
                team_metadata = self.config_loader.get_team_metadata()
                self.logger.info(f"团队初始化成功: {team_metadata.get('team_name', 'Unknown')}")
                return True
            else:
                self.logger.error("团队初始化失败")
                return False

        except Exception as e:
            self.logger.error(f"团队初始化异常: {str(e)}")
            return False

    async def start_conversation(self, user_input: str) -> Optional[str]:
        """
        开始单智能体对话

        Args:
            user_input: 用户输入

        Returns:
            智能体回复，失败返回None
        """
        try:
            if not self.agent:
                self.logger.error("智能体未初始化，请先调用 initialize() 方法")
                return None

            self.logger.info(f"用户输入: {user_input}")

            # 创建用户消息
            user_msg = Msg(
                name="user",
                content=user_input,
                role="user"
            )

            # 获取智能体回复 - 异步调用
            response = await self.agent(user_msg)

            if response:
                # 处理AgentScope的响应格式
                if isinstance(response, list):
                    # 响应是字典列表，提取文本内容
                    text_contents = []
                    for item in response:
                        if isinstance(item, dict) and 'text' in item:
                            text_contents.append(item['text'])
                        elif isinstance(item, str):
                            text_contents.append(item)
                    reply = ''.join(text_contents) if text_contents else str(response)
                elif hasattr(response, 'content'):
                    # 响应是消息对象，提取内容
                    reply = response.content
                else:
                    # 其他情况，转换为字符串
                    reply = str(response)

                self.logger.info(f"智能体回复: {reply}")
                return reply
            else:
                self.logger.warning("智能体回复为空")
                return None

        except Exception as e:
            self.logger.error(f"对话执行异常: {str(e)}")
            return None

    def run_team_task(self, task: str) -> Optional[Any]:
        """
        执行多智能体团队任务

        Args:
            task: 任务描述

        Returns:
            执行结果，失败返回None
        """
        try:
            if not self.team:
                self.logger.error("团队未初始化，请先调用 initialize() 方法")
                return None

            self.logger.info(f"开始执行团队任务: {task}")

            # 获取任务上下文
            task_context = self.config_loader.get_task_context()
            task_description = task_context.get("task_description", task)

            # 创建初始消息
            initial_msg = Msg(
                name="user",
                content=task_description,
                role="user"
            )

            # 执行团队协作
            result = agentscope_run(
                self.team,
                initial_msg
            )

            self.logger.info("团队任务执行完成")
            return result

        except Exception as e:
            self.logger.error(f"团队任务执行异常: {str(e)}")
            return None

    def chat_loop(self, max_rounds: int = 10) -> None:
        """
        交互式对话循环

        Args:
            max_rounds: 最大对话轮次
        """
        try:
            if not self.agent:
                print("智能体未初始化，请先调用 initialize() 方法")
                return

            print(f"\n=== 与 {self.agent.name} 开始对话 ===")
            print(f"描述: {self.config_loader.get_agent_metadata().get('description', '无描述')}")
            print("输入 'quit' 或 'exit' 退出\n")

            for round_num in range(1, max_rounds + 1):
                try:
                    user_input = input(f"[{round_num}/{max_rounds}] 用户: ")

                    if not user_input.strip():
                        continue

                    if user_input.lower() in ['quit', 'exit', '退出']:
                        print("对话结束")
                        break

                    # 获取回复
                    response = self.start_conversation(user_input)

                    if response:
                        print(f"智能体: {response}\n")
                    else:
                        print("智能体回复为空，请重试\n")

                except KeyboardInterrupt:
                    print("\n对话被用户中断")
                    break
                except Exception as e:
                    print(f"对话异常: {str(e)}\n")

        except Exception as e:
            self.logger.error(f"对话循环异常: {str(e)}")

    def get_agent_info(self) -> Dict[str, Any]:
        """
        获取智能体信息

        Returns:
            智能体信息字典
        """
        info = {
            "config_path": self.config_path,
            "config_type": self.config_type
        }

        if self.agent:
            info["agent_name"] = getattr(self.agent, 'name', 'Unknown')
            info["agent_type"] = type(self.agent).__name__
        elif self.team:
            info["team_name"] = self.config_loader.get_team_metadata().get("team_name", "Unknown")
            info["collaboration_mode"] = self.config_loader.get_team_metadata().get("collaboration_mode", "Unknown")

        return info

    def run_interactive_mode(self) -> None:
        """
        运行交互模式（命令行交互）
        """
        try:
            # 初始化
            if not self.initialize():
                print("引擎初始化失败")
                return

            # 显示配置信息
            info = self.get_agent_info()
            print(f"\n配置类型: {info['config_type']}")
            print(f"配置文件: {info['config_path']}")

            if self.agent:
                self.chat_loop()
            elif self.team:
                # 团队模式下的任务执行
                print("\n=== 团队协作模式 ===")
                task = input("请输入团队任务描述: ")

                if task.strip():
                    result = self.run_team_task(task)
                    if result:
                        print("任务执行完成")
                    else:
                        print("任务执行失败")
                else:
                    print("任务描述为空，退出")

        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            self.logger.error(f"交互模式运行异常: {str(e)}")


def run_agent_from_config(config_path: str, user_input: Optional[str] = None) -> None:
    """
    便捷函数：从配置文件运行智能体

    Args:
        config_path: 配置文件路径
        user_input: 用户输入（可选），如果提供则执行单次对话，否则进入交互模式
    """
    try:
        # 创建引擎
        engine = Engine(config_path)

        if user_input:
            # 单次对话模式
            if engine.initialize():
                response = engine.start_conversation(user_input)
                if response:
                    print(f"回复: {response}")
                else:
                    print("智能体回复失败")
        else:
            # 交互模式
            engine.run_interactive_mode()

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"运行智能体失败: {str(e)}")


def run_team_from_config(config_path: str, task: str) -> None:
    """
    便捷函数：从配置文件运行团队任务

    Args:
        config_path: 配置文件路径
        task: 任务描述
    """
    try:
        # 创建引擎
        engine = Engine(config_path)

        # 执行团队任务
        if engine.initialize():
            result = engine.run_team_task(task)
            if result:
                print("团队任务执行完成")
            else:
                print("团队任务执行失败")
        else:
            print("引擎初始化失败")

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"运行团队失败: {str(e)}")