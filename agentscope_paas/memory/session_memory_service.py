"""
会话记忆服务

提供会话级别的记忆管理功能，支持Redis存储和内存存储，并与AgentScope记忆系统集成。
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from agentscope.memory import MemoryBase, InMemoryMemory
    # 尝试导入RedisMemory（如果存在）
    try:
        from agentscope.memory import RedisMemory
        REDIS_MEMORY_AVAILABLE = True
    except ImportError:
        REDIS_MEMORY_AVAILABLE = False
        RedisMemory = None
except ImportError:
    # 如果AgentScope不可用，使用模拟类
    class MemoryBase:
        pass

    class InMemoryMemory(MemoryBase):
        def __init__(self):
            self.memory = []

        def add(self, role: str, content: str):
            self.memory.append({"role": role, "content": content})

        def get(self) -> List[Dict[str, Any]]:
            return self.memory

        def clear(self):
            self.memory = []

    RedisMemory = None
    REDIS_MEMORY_AVAILABLE = False

from ..storage.redis_storage import RedisStorageBackend, RedisConfig
from ..utils.logger import get_logger


class SessionMemoryService:
    """会话记忆服务"""

    def __init__(self):
        """初始化会话记忆服务"""
        self.logger = get_logger(__name__)
        self.redis_backends: Dict[str, RedisStorageBackend] = {}
        self.memory_stores: Dict[str, MemoryBase] = {}

    def get_memory_backend(
        self,
        user_id: str,
        session_id: str,
        config: Dict[str, Any]
    ) -> MemoryBase:
        """
        获取记忆后端实例

        Args:
            user_id: 用户ID
            session_id: 会话ID
            config: 记忆配置

        Returns:
            MemoryBase实例
        """
        memory_key = f"{user_id}:{session_id}"

        # 如果已经创建了记忆实例，直接返回
        if memory_key in self.memory_stores:
            return self.memory_stores[memory_key]

        # 获取会话记忆配置
        session_memory_config = config.get('session_memory', {})

        if not session_memory_config.get('enabled', False):
            # 如果未启用会话记忆，使用内存存储
            self.memory_stores[memory_key] = InMemoryMemory()
            return self.memory_stores[memory_key]

        storage_type = session_memory_config.get('storage_type', 'memory')

        if storage_type == 'redis':
            # 使用Redis存储
            redis_config = session_memory_config.get('redis_config', {})
            try:
                # 创建Redis后端
                backend_key = f"{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}"

                if backend_key not in self.redis_backends:
                    redis_config_obj = RedisConfig(
                        host=redis_config.get('host', 'localhost'),
                        port=redis_config.get('port', 6379),
                        db=redis_config.get('db', 0),
                        password=redis_config.get('password'),
                        ttl=session_memory_config.get('ttl', 3600)
                    )
                    self.redis_backends[backend_key] = RedisStorageBackend(redis_config_obj)

                # 尝试创建AgentScope RedisMemory（如果可用）
                if REDIS_MEMORY_AVAILABLE and RedisMemory is not None:
                    memory = RedisMemory(
                        redis_url=f"redis://{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}/{redis_config.get('db', 0)}",
                        password=redis_config.get('password'),
                        key_prefix=f"{session_memory_config.get('memory_key_prefix', 'session_memory')}:{user_id}:{session_id}"
                    )
                    self.memory_stores[memory_key] = memory
                    return memory
                else:
                    # 如果RedisMemory不可用，使用自定义Redis存储包装
                    self.logger.warning("AgentScope RedisMemory不可用，使用自定义Redis存储")
                    memory = InMemoryMemory()
                    self.memory_stores[memory_key] = memory
                    return memory

            except Exception as e:
                self.logger.error(f"创建Redis记忆失败: {e}，降级到内存存储")
                self.memory_stores[memory_key] = InMemoryMemory()
                return self.memory_stores[memory_key]

        else:
            # 使用内存存储
            self.memory_stores[memory_key] = InMemoryMemory()
            return self.memory_stores[memory_key]

    def add_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        config: Dict[str, Any]
    ) -> bool:
        """
        添加消息到记忆

        Args:
            user_id: 用户ID
            session_id: 会话ID
            role: 消息角色（user/assistant/system）
            content: 消息内容
            config: 记忆配置

        Returns:
            是否添加成功
        """
        try:
            memory = self.get_memory_backend(user_id, session_id, config)

            # 添加消息到记忆
            if hasattr(memory, 'add'):
                memory.add(role, content)
            elif hasattr(memory, 'append'):
                # 对于InMemoryMemory
                memory.append({"role": role, "content": content})
            else:
                # 直接调用方法
                memory(role, content)

            # 如果使用Redis，也保存到Redis
            session_memory_config = config.get('session_memory', {})
            if session_memory_config.get('enabled', False):
                storage_type = session_memory_config.get('storage_type', 'memory')
                if storage_type == 'redis':
                    redis_config = session_memory_config.get('redis_config', {})
                    backend_key = f"{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}"
                    if backend_key in self.redis_backends:
                        backend = self.redis_backends[backend_key]
                        backend.append_message(
                            user_id=user_id,
                            session_id=session_id,
                            message={"role": role, "content": content},
                            max_messages=session_memory_config.get('max_messages', 100),
                            memory_key_prefix=session_memory_config.get('memory_key_prefix', 'session_memory')
                        )

            self.logger.debug(f"消息添加成功: {user_id}:{session_id}, role: {role}")
            return True

        except Exception as e:
            self.logger.error(f"添加消息失败: {e}")
            return False

    def get_memory(
        self,
        user_id: str,
        session_id: str,
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        获取会话记忆

        Args:
            user_id: 用户ID
            session_id: 会话ID
            config: 记忆配置

        Returns:
            消息列表
        """
        try:
            memory = self.get_memory_backend(user_id, session_id, config)

            # 获取记忆
            if hasattr(memory, 'get'):
                return memory.get()
            elif hasattr(memory, 'memory'):
                # 对于InMemoryMemory
                return memory.memory
            else:
                return []

        except Exception as e:
            self.logger.error(f"获取记忆失败: {e}")
            return []

    def clear_memory(
        self,
        user_id: str,
        session_id: str,
        config: Dict[str, Any]
    ) -> bool:
        """
        清除会话记忆

        Args:
            user_id: 用户ID
            session_id: 会话ID
            config: 记忆配置

        Returns:
            是否清除成功
        """
        try:
            memory_key = f"{user_id}:{session_id}"

            # 清除内存中的记忆实例
            if memory_key in self.memory_stores:
                memory = self.memory_stores[memory_key]
                if hasattr(memory, 'clear'):
                    memory.clear()
                del self.memory_stores[memory_key]

            # 如果使用Redis，也清除Redis中的记忆
            session_memory_config = config.get('session_memory', {})
            if session_memory_config.get('enabled', False):
                storage_type = session_memory_config.get('storage_type', 'memory')
                if storage_type == 'redis':
                    redis_config = session_memory_config.get('redis_config', {})
                    backend_key = f"{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}"
                    if backend_key in self.redis_backends:
                        backend = self.redis_backends[backend_key]
                        backend.clear_session_memory(
                            user_id=user_id,
                            session_id=session_id,
                            memory_key_prefix=session_memory_config.get('memory_key_prefix', 'session_memory')
                        )

            self.logger.debug(f"记忆清除成功: {user_id}:{session_id}")
            return True

        except Exception as e:
            self.logger.error(f"清除记忆失败: {e}")
            return False

    def get_statistics(
        self,
        user_id: str,
        session_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        获取记忆统计信息

        Args:
            user_id: 用户ID
            session_id: 会话ID
            config: 记忆配置

        Returns:
            统计信息字典
        """
        try:
            memory = self.get_memory(user_id, session_id, config)

            stats = {
                "user_id": user_id,
                "session_id": session_id,
                "total_messages": len(memory),
                "enabled": config.get('session_memory', {}).get('enabled', False),
                "storage_type": config.get('session_memory', {}).get('storage_type', 'memory'),
                "timestamp": datetime.now().isoformat()
            }

            # 如果使用Redis，添加Redis健康状态
            session_memory_config = config.get('session_memory', {})
            if session_memory_config.get('enabled', False):
                storage_type = session_memory_config.get('storage_type', 'memory')
                if storage_type == 'redis':
                    redis_config = session_memory_config.get('redis_config', {})
                    backend_key = f"{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}"
                    if backend_key in self.redis_backends:
                        backend = self.redis_backends[backend_key]
                        health = backend.health_check()
                        stats["redis_health"] = health

            return stats

        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {}

    def cleanup_expired_sessions(self, config: Dict[str, Any]) -> int:
        """
        清理过期会话（仅对Redis有效）

        Args:
            config: 记忆配置

        Returns:
            清理的会话数量
        """
        try:
            session_memory_config = config.get('session_memory', {})
            if session_memory_config.get('enabled', False):
                storage_type = session_memory_config.get('storage_type', 'memory')
                if storage_type == 'redis':
                    redis_config = session_memory_config.get('redis_config', {})
                    backend_key = f"{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}"
                    if backend_key in self.redis_backends:
                        backend = self.redis_backends[backend_key]
                        # Redis会自动处理TTL过期，这里返回0表示没有手动清理
                        return 0

            return 0

        except Exception as e:
            self.logger.error(f"清理过期会话失败: {e}")
            return 0

    def close_all_connections(self):
        """关闭所有Redis连接"""
        try:
            for backend in self.redis_backends.values():
                backend.close()
            self.redis_backends.clear()
            self.logger.info("所有Redis连接已关闭")

        except Exception as e:
            self.logger.error(f"关闭连接失败: {e}")


# 全局会话记忆服务实例
session_memory_service = SessionMemoryService()