"""
Redis存储后端实现

提供Redis连接管理、会话记忆存储和检索功能，支持连接池、TTL管理和错误处理。
"""

try:
    import redis
    from redis import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    ConnectionPool = None
    REDIS_AVAILABLE = False
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class RedisConfig:
    """Redis连接配置"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        connection_pool_size: int = 10,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
        ttl: int = 3600  # 会话记忆过期时间（秒）
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.connection_pool_size = connection_pool_size
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.ttl = ttl


class RedisStorageBackend:
    """Redis存储后端"""

    def __init__(self, config: RedisConfig):
        """
        初始化Redis存储后端

        Args:
            config: Redis连接配置
        """
        self.config = config
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
        self._initialize_connection()

    def _initialize_connection(self):
        """初始化Redis连接"""
        try:
            self.pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.connection_pool_size,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                decode_responses=True  # 自动解码为字符串
            )
            self.client = redis.Redis(connection_pool=self.pool)

            # 测试连接
            self.client.ping()
            logger.info(f"Redis连接成功: {self.config.host}:{self.config.port}")

        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise

    def save_session_memory(
        self,
        user_id: str,
        session_id: str,
        messages: List[Dict[str, Any]],
        memory_key_prefix: str = "session_memory"
    ) -> bool:
        """
        保存会话记忆到Redis

        Args:
            user_id: 用户ID
            session_id: 会话ID
            messages: 消息列表
            memory_key_prefix: 记忆键前缀

        Returns:
            是否保存成功
        """
        if not self.client:
            logger.error("Redis客户端未初始化")
            return False

        key = f"{memory_key_prefix}:{user_id}:{session_id}"

        try:
            # 序列化消息列表
            messages_json = json.dumps(messages, ensure_ascii=False)

            # 保存到Redis，设置TTL
            self.client.setex(
                key,
                self.config.ttl,
                messages_json
            )

            logger.debug(f"会话记忆保存成功: {key}, 消息数: {len(messages)}")
            return True

        except Exception as e:
            logger.error(f"保存会话记忆失败: {e}")
            return False

    def get_session_memory(
        self,
        user_id: str,
        session_id: str,
        memory_key_prefix: str = "session_memory"
    ) -> List[Dict[str, Any]]:
        """
        从Redis获取会话记忆

        Args:
            user_id: 用户ID
            session_id: 会话ID
            memory_key_prefix: 记忆键前缀

        Returns:
            消息列表，如果不存在或出错返回空列表
        """
        if not self.client:
            logger.error("Redis客户端未初始化")
            return []

        key = f"{memory_key_prefix}:{user_id}:{session_id}"

        try:
            data = self.client.get(key)

            if not data:
                logger.debug(f"会话记忆不存在: {key}")
                return []

            messages = json.loads(data)
            logger.debug(f"会话记忆获取成功: {key}, 消息数: {len(messages)}")
            return messages

        except Exception as e:
            logger.error(f"获取会话记忆失败: {e}")
            return []

    def clear_session_memory(
        self,
        user_id: str,
        session_id: str,
        memory_key_prefix: str = "session_memory"
    ) -> bool:
        """
        清除会话记忆

        Args:
            user_id: 用户ID
            session_id: 会话ID
            memory_key_prefix: 记忆键前缀

        Returns:
            是否清除成功
        """
        if not self.client:
            logger.error("Redis客户端未初始化")
            return False

        key = f"{memory_key_prefix}:{user_id}:{session_id}"

        try:
            self.client.delete(key)
            logger.debug(f"会话记忆清除成功: {key}")
            return True

        except Exception as e:
            logger.error(f"清除会话记忆失败: {e}")
            return False

    def append_message(
        self,
        user_id: str,
        session_id: str,
        message: Dict[str, Any],
        max_messages: int = 100,
        memory_key_prefix: str = "session_memory"
    ) -> bool:
        """
        向会话记忆追加单条消息

        Args:
            user_id: 用户ID
            session_id: 会话ID
            message: 要追加的消息
            max_messages: 最大保存消息数
            memory_key_prefix: 记忆键前缀

        Returns:
            是否追加成功
        """
        # 获取现有消息
        messages = self.get_session_memory(user_id, session_id, memory_key_prefix)

        # 追加新消息
        messages.append(message)

        # 限制消息数量
        if len(messages) > max_messages:
            messages = messages[-max_messages:]

        # 保存更新后的消息列表
        return self.save_session_memory(user_id, session_id, messages, memory_key_prefix)

    def get_all_session_keys(
        self,
        user_id: str,
        memory_key_prefix: str = "session_memory"
    ) -> List[str]:
        """
        获取用户所有会话的键

        Args:
            user_id: 用户ID
            memory_key_prefix: 记忆键前缀

        Returns:
            会话键列表
        """
        if not self.client:
            logger.error("Redis客户端未初始化")
            return []

        pattern = f"{memory_key_prefix}:{user_id}:*"

        try:
            keys = self.client.keys(pattern)
            return keys

        except Exception as e:
            logger.error(f"获取会话键失败: {e}")
            return []

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            健康状态信息
        """
        try:
            if not self.client:
                return {
                    "status": "error",
                    "message": "Redis客户端未初始化"
                }

            # 测试连接
            start_time = __import__('time').time()
            self.client.ping()
            response_time = __import__('time').time() - start_time

            # 获取基本信息
            info = self.client.info()

            return {
                "status": "healthy",
                "host": self.config.host,
                "port": self.config.port,
                "db": self.config.db,
                "response_time": response_time,
                "memory_usage": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients")
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def close(self):
        """关闭连接"""
        try:
            if self.pool:
                self.pool.disconnect()
                logger.info("Redis连接池已关闭")
        except Exception as e:
            logger.error(f"关闭Redis连接失败: {e}")


# 便捷函数
def create_redis_backend(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None,
    **kwargs
) -> RedisStorageBackend:
    """
    创建Redis存储后端的便捷函数

    Args:
        host: Redis主机地址
        port: Redis端口
        db: Redis数据库编号
        password: Redis密码
        **kwargs: 其他配置参数

    Returns:
        RedisStorageBackend实例
    """
    config = RedisConfig(
        host=host,
        port=port,
        db=db,
        password=password,
        **kwargs
    )
    return RedisStorageBackend(config)