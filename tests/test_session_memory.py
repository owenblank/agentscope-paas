"""
Unit tests for session memory functionality

Tests for Redis storage backend, session memory service, and configuration models.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Test configuration models
def test_session_memory_config_creation():
    """Test creating valid session memory configuration"""
    from api_server.main import SessionMemoryConfig, RedisConnectionConfig

    # Test basic configuration
    config = SessionMemoryConfig(
        enabled=True,
        storage_type="redis",
        redis_config=RedisConnectionConfig(
            host="localhost",
            port=6379,
            db=0
        ),
        ttl=3600,
        max_messages=100,
        memory_key_prefix="session_memory"
    )

    assert config.enabled == True
    assert config.storage_type == "redis"
    assert config.redis_config.host == "localhost"
    assert config.redis_config.port == 6379
    assert config.ttl == 3600
    assert config.max_messages == 100
    assert config.memory_key_prefix == "session_memory"


def test_session_memory_config_defaults():
    """Test session memory configuration with defaults"""
    from api_server.main import SessionMemoryConfig

    config = SessionMemoryConfig()

    assert config.enabled == False
    assert config.storage_type == "redis"
    assert config.ttl == 3600
    assert config.max_messages == 100
    assert config.memory_key_prefix == "session_memory"


def test_redis_connection_config():
    """Test Redis connection configuration"""
    from api_server.main import RedisConnectionConfig

    config = RedisConnectionConfig(
        host="192.168.1.100",
        port=6380,
        db=1,
        password="secure_password",
        connection_pool_size=20,
        socket_timeout=10,
        socket_connect_timeout=10
    )

    assert config.host == "192.168.1.100"
    assert config.port == 6380
    assert config.db == 1
    assert config.password == "secure_password"
    assert config.connection_pool_size == 20
    assert config.socket_timeout == 10
    assert config.socket_connect_timeout == 10


class TestRedisStorageBackend:
    """Test Redis storage backend functionality"""

    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client"""
        with patch('agentscope_paas.storage.redis_storage.redis') as mock_redis:
            mock_pool = Mock()
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            mock_client.setex.return_value = True
            mock_client.delete.return_value = True
            mock_client.keys.return_value = []
            mock_client.info.return_value = {
                "used_memory_human": "1.5M",
                "connected_clients": 5
            }

            mock_redis.ConnectionPool.return_value = mock_pool
            mock_redis.Redis.return_value = mock_client

            yield mock_client

    def test_redis_backend_initialization(self, mock_redis_client):
        """Test Redis backend initialization"""
        from agentscope_paas.storage.redis_storage import RedisStorageBackend, RedisConfig

        config = RedisConfig(host="localhost", port=6379, db=0)
        backend = RedisStorageBackend(config)

        assert backend.client is not None
        assert backend.config.host == "localhost"
        assert backend.config.port == 6379
        mock_redis_client.ping.assert_called_once()

    def test_save_session_memory(self, mock_redis_client):
        """Test saving session memory to Redis"""
        from agentscope_paas.storage.redis_storage import RedisStorageBackend, RedisConfig

        config = RedisConfig(host="localhost", port=6379, db=0)
        backend = RedisStorageBackend(config)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]

        result = backend.save_session_memory("user1", "session1", messages)

        assert result == True
        mock_redis_client.setex.assert_called_once()

        # Verify the key format
        call_args = mock_redis_client.setex.call_args
        key = call_args[0][0]
        assert "session_memory:user1:session1" in key

    def test_get_session_memory(self, mock_redis_client):
        """Test getting session memory from Redis"""
        from agentscope_paas.storage.redis_storage import RedisStorageBackend, RedisConfig

        config = RedisConfig(host="localhost", port=6379, db=0)
        backend = RedisStorageBackend(config)

        # Mock return data
        messages = [{"role": "user", "content": "Test message"}]
        mock_redis_client.get.return_value = json.dumps(messages)

        result = backend.get_session_memory("user1", "session1")

        assert len(result) == 1
        assert result[0]["content"] == "Test message"

    def test_get_empty_session_memory(self, mock_redis_client):
        """Test getting non-existent session memory"""
        from agentscope_paas.storage.redis_storage import RedisStorageBackend, RedisConfig

        config = RedisConfig(host="localhost", port=6379, db=0)
        backend = RedisStorageBackend(config)

        mock_redis_client.get.return_value = None

        result = backend.get_session_memory("user1", "nonexistent_session")

        assert result == []

    def test_clear_session_memory(self, mock_redis_client):
        """Test clearing session memory"""
        from agentscope_paas.storage.redis_storage import RedisStorageBackend, RedisConfig

        config = RedisConfig(host="localhost", port=6379, db=0)
        backend = RedisStorageBackend(config)

        result = backend.clear_session_memory("user1", "session1")

        assert result == True
        mock_redis_client.delete.assert_called_once()

    def test_append_message(self, mock_redis_client):
        """Test appending a message to session memory"""
        from agentscope_paas.storage.redis_storage import RedisStorageBackend, RedisConfig

        config = RedisConfig(host="localhost", port=6379, db=0)
        backend = RedisStorageBackend(config)

        # Mock existing messages
        existing_messages = [{"role": "user", "content": "First message"}]
        mock_redis_client.get.return_value = json.dumps(existing_messages)

        # Append new message
        new_message = {"role": "assistant", "content": "Second message"}
        result = backend.append_message("user1", "session1", new_message, max_messages=100)

        assert result == True
        # Should call get then set
        mock_redis_client.get.assert_called_once()
        mock_redis_client.setex.assert_called_once()

    def test_health_check(self, mock_redis_client):
        """Test Redis health check"""
        from agentscope_paas.storage.redis_storage import RedisStorageBackend, RedisConfig

        config = RedisConfig(host="localhost", port=6379, db=0)
        backend = RedisStorageBackend(config)

        health = backend.health_check()

        assert health["status"] == "healthy"
        assert health["host"] == "localhost"
        assert health["port"] == 6379
        assert "response_time" in health


class TestSessionMemoryService:
    """Test session memory service functionality"""

    @pytest.fixture
    def memory_service(self):
        """Get session memory service instance"""
        from agentscope_paas.memory.session_memory_service import session_memory_service
        return session_memory_service

    def test_get_memory_backend_memory_storage(self, memory_service):
        """Test getting memory backend with memory storage"""
        config = {
            'session_memory': {
                'enabled': False,
                'storage_type': 'memory'
            }
        }

        memory = memory_service.get_memory_backend("user1", "session1", config)

        assert memory is not None
        # Should return an InMemoryMemory instance
        assert hasattr(memory, 'memory') or hasattr(memory, 'get')

    @patch('agentscope_paas.memory.session_memory_service.REDIS_MEMORY_AVAILABLE', False)
    def test_get_memory_backend_redis_unavailable(self, memory_service):
        """Test fallback when RedisMemory is unavailable"""
        config = {
            'session_memory': {
                'enabled': True,
                'storage_type': 'redis',
                'redis_config': {
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0
                }
            }
        }

        # Should not raise exception, should fallback to memory
        memory = memory_service.get_memory_backend("user1", "session1", config)

        assert memory is not None

    def test_add_and_get_message(self, memory_service):
        """Test adding and retrieving messages"""
        config = {
            'session_memory': {
                'enabled': True,
                'storage_type': 'memory'
            }
        }

        # Add a message
        result = memory_service.add_message(
            user_id="user1",
            session_id="session1",
            role="user",
            content="Hello, this is a test message",
            config=config
        )

        assert result == True

        # Get messages
        messages = memory_service.get_memory("user1", "session1", config)

        assert len(messages) >= 1
        assert messages[-1]["content"] == "Hello, this is a test message"

    def test_clear_memory(self, memory_service):
        """Test clearing session memory"""
        config = {
            'session_memory': {
                'enabled': True,
                'storage_type': 'memory'
            }
        }

        # Add some messages first
        memory_service.add_message("user1", "session1", "user", "Message 1", config)
        memory_service.add_message("user1", "session1", "assistant", "Response 1", config)

        # Clear memory
        result = memory_service.clear_memory("user1", "session1", config)

        assert result == True

        # Verify memory is cleared
        messages = memory_service.get_memory("user1", "session1", config)
        assert len(messages) == 0

    def test_get_statistics(self, memory_service):
        """Test getting memory statistics"""
        config = {
            'session_memory': {
                'enabled': True,
                'storage_type': 'memory',
                'max_messages': 100
            }
        }

        # Add some messages
        memory_service.add_message("user1", "session1", "user", "Test message", config)

        # Get statistics
        stats = memory_service.get_statistics("user1", "session1", config)

        assert "user_id" in stats
        assert "session_id" in stats
        assert "total_messages" in stats
        assert stats["user_id"] == "user1"
        assert stats["session_id"] == "session1"
        assert stats["total_messages"] >= 1


class TestAgentFactoryMemoryIntegration:
    """Test AgentFactory memory integration"""

    @pytest.fixture
    def config_loader(self):
        """Create a mock config loader"""
        with patch('agentscope_paas.config.loader.ConfigLoader') as mock:
            loader = Mock()
            loader.get_agent_metadata.return_value = {
                "agent_id": "test_agent",
                "agent_name": "Test Agent",
                "agent_type": "ReActAgent"
            }
            loader.get_model_config.return_value = {
                "model_name": "gpt-4",
                "api_key": "test_key",
                "base_url": "https://api.openai.com/v1"
            }
            loader.get_prompt_config.return_value = {
                "system_prompt": "You are a helpful assistant."
            }
            loader.get_full_config.return_value = {
                "session_memory_config": {
                    "enabled": True,
                    "storage_type": "memory"
                }
            }
            yield loader

    def test_prepare_memory_config_disabled(self, config_loader):
        """Test memory config preparation when disabled"""
        from agentscope_paas.factory.agent_factory import AgentFactory

        factory = AgentFactory(config_loader)
        config = {
            "session_memory_config": {
                "enabled": False
            }
        }

        memory = factory._prepare_memory_config(config, "user1", "session1")

        # Should return None or InMemoryMemory when disabled
        assert memory is None or hasattr(memory, 'memory')

    @patch('agentscope_paas.factory.agent_factory.InMemoryMemory')
    def test_prepare_memory_config_enabled(self, mock_memory, config_loader):
        """Test memory config preparation when enabled"""
        from agentscope_paas.factory.agent_factory import AgentFactory

        factory = AgentFactory(config_loader)
        config = {
            "session_memory_config": {
                "enabled": True,
                "storage_type": "memory"
            }
        }

        # Create a mock memory instance
        mock_mem_instance = Mock()
        mock_memory.return_value = mock_mem_instance

        memory = factory._prepare_memory_config(config, "user1", "session1")

        assert memory is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])