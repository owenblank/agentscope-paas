#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的异步对话处理器，用于API服务器
"""

import asyncio
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from agentscope import init as agentscope_init
from agentscope.agent import ReActAgent
from agentscope.model import DashScopeChatModel, OpenAIChatModel
from agentscope.formatter import DashScopeChatFormatter, OpenAIChatFormatter
from agentscope.message import Msg

class AsyncChatProcessor:
    """简化的异步对话处理器"""

    def __init__(self):
        self.agents_cache = {}  # 缓存已创建的智能体实例

    async def process_message(
        self,
        agent_id: str,
        agent_config: Dict[str, Any],
        user_message: str
    ) -> Optional[str]:
        """
        异步处理用户消息

        Args:
            agent_id: 智能体ID
            agent_config: 智能体配置
            user_message: 用户消息

        Returns:
            智能体回复
        """
        try:
            # 初始化AgentScope
            agentscope_init()

            # 检查缓存中是否有智能体实例
            if agent_id in self.agents_cache:
                agent = self.agents_cache[agent_id]
                print(f"Using cached agent for {agent_id}")
            else:
                # 创建新的智能体实例
                print(f"Creating new agent instance for {agent_id}")

                # 提取配置
                metadata = agent_config["agent_metadata"]
                llm_config = agent_config["llm_config"]
                prompt_config = agent_config["prompt_config"]

                # 创建模型和formatter
                if "dashscope" in llm_config["base_url"].lower() or "qwen" in llm_config["model_name"].lower():
                    model = DashScopeChatModel(
                        model_name=llm_config["model_name"],
                        api_key=llm_config["api_key"],
                        base_http_api_url=llm_config["base_url"]
                    )
                    formatter = DashScopeChatFormatter()
                else:
                    model = OpenAIChatModel(
                        model_name=llm_config["model_name"],
                        api_key=llm_config["api_key"]
                    )
                    if "base_url" in llm_config:
                        model = OpenAIChatModel(
                            model_name=llm_config["model_name"],
                            api_key=llm_config["api_key"],
                            client_kwargs={"base_url": llm_config["base_url"]}
                        )
                    formatter = OpenAIChatFormatter()

                # 创建智能体
                agent = ReActAgent(
                    name=metadata["agent_name"],
                    sys_prompt=prompt_config["system_prompt"],
                    model=model,
                    formatter=formatter
                )

                # 缓存智能体实例
                self.agents_cache[agent_id] = agent

            # 创建用户消息
            user_msg = Msg(
                name="user",
                content=user_message,
                role="user"
            )

            # 异步调用智能体
            print(f"Processing message for {agent_id}")
            response = await agent(user_msg)

            # 处理响应
            if isinstance(response, list):
                # AgentScope返回的是字典列表
                text_parts = []
                for item in response:
                    if isinstance(item, dict):
                        if 'text' in item:
                            text_parts.append(item['text'])
                        elif 'content' in item:
                            text_parts.append(item['content'])
                    elif isinstance(item, str):
                        text_parts.append(item)
                return ''.join(text_parts)
            elif hasattr(response, 'content'):
                return response.content
            else:
                return str(response)

        except Exception as e:
            print(f"Error in async processing: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"处理异常: {str(e)}"

    def clear_agent_cache(self, agent_id: Optional[str] = None):
        """清除智能体缓存"""
        if agent_id:
            if agent_id in self.agents_cache:
                del self.agents_cache[agent_id]
        else:
            self.agents_cache.clear()

# 全局对话处理器实例
chat_processor = AsyncChatProcessor()