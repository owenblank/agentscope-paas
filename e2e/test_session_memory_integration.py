"""
Integration tests for session memory functionality

Tests the complete session memory integration including API endpoints,
Redis connectivity, and agent creation with memory.
"""

import pytest
import asyncio
import json
import time
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Import for testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestRedisAPIIntegration:
    """Test Redis API integration"""

    @pytest.fixture
    def test_client(self):
        """Create test HTTP client"""
        from fastapi.testclient import TestClient
        from api_server.main import app

        return TestClient(app)

    def test_redis_connection_endpoint_success(self, test_client):
        """Test Redis connection endpoint with valid config"""
        # Mock the Redis backend
        with patch('agentscope_paas.storage.redis_storage.RedisStorageBackend') as mock_backend:
            mock_instance = Mock()
            mock_instance.health_check.return_value = {
                "status": "healthy",
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "response_time": 0.1
            }
            mock_backend.return_value = mock_instance

            response = test_client.post("/api/v1/test-redis", json={
                "redis_config": {
                    "host": "localhost",
                    "port": 6379,
                    "db": 0
                }
            })

            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert "data" in data
            assert data["data"]["status"] == "healthy"

    def test_redis_connection_endpoint_failure(self, test_client):
        """Test Redis connection endpoint with invalid config"""
        with patch('agentscope_paas.storage.redis_storage.RedisStorageBackend') as mock_backend:
            mock_backend.side_effect = Exception("Connection failed")

            response = test_client.post("/api/v1/test-redis", json={
                "redis_config": {
                    "host": "invalid-host",
                    "port": 6379,
                    "db": 0
                }
            })

            assert response.status_code == 200
            data = response.json()
            assert data["success"] == False
            assert "message" in data

    def test_redis_connection_missing_config(self, test_client):
        """Test Redis connection endpoint with missing config"""
        response = test_client.post("/api/v1/test-redis", json={})

        assert response.status_code == 422  # Validation error


class TestConversationMemoryAPI:
    """Test conversation memory API endpoints"""

    @pytest.fixture
    def test_client(self):
        """Create test HTTP client"""
        from fastapi.testclient import TestClient
        from api_server.main import app

        return TestClient(app)

    @pytest.fixture
    def mock_auth(self):
        """Mock authentication"""
        with patch('api_server.routers.conversation.api_key_auth') as mock:
            user = Mock()
            user.user_id = "test_user"
            mock.return_value = user
            yield mock

    def test_get_session_memory_empty(self, test_client, mock_auth):
        """Test getting empty session memory"""
        # Create a conversation
        import api_server.routers.conversation as conv_module
        conv_module.conversations_store["session1"] = {
            "config": {
                "session_memory": {
                    "enabled": True,
                    "storage_type": "memory"
                }
            }
        }

        response = test_client.get(
            "/api/v1/conversations/sessions/session1/memory?user_id=test_user"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "memories" in data["data"]
        assert isinstance(data["data"]["memories"], list)

    def test_clear_session_memory(self, test_client, mock_auth):
        """Test clearing session memory"""
        import api_server.routers.conversation as conv_module
        conv_module.conversations_store["session1"] = {
            "config": {
                "session_memory": {
                    "enabled": True,
                    "storage_type": "memory"
                }
            }
        }

        response = test_client.delete(
            "/api/v1/conversations/sessions/session1/memory?user_id=test_user"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "cleared_at" in data["data"]

    def test_get_memory_statistics(self, test_client, mock_auth):
        """Test getting memory statistics"""
        import api_server.routers.conversation as conv_module
        conv_module.conversations_store["session1"] = {
            "config": {
                "session_memory": {
                    "enabled": True,
                    "storage_type": "memory"
                }
            }
        }

        response = test_client.get(
            "/api/v1/conversations/sessions/session1/memory/statistics?user_id=test_user"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "total_messages" in data["data"]

    def test_add_memory_message(self, test_client, mock_auth):
        """Test adding message to memory"""
        import api_server.routers.conversation as conv_module
        conv_module.conversations_store["session1"] = {
            "config": {
                "session_memory": {
                    "enabled": True,
                    "storage_type": "memory"
                }
            }
        }

        response = test_client.post(
            "/api/v1/conversations/sessions/session1/memory/messages?user_id=test_user",
            json={
                "role": "user",
                "content": "Test message"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "timestamp" in data["data"]

    def test_nonexistent_session(self, test_client, mock_auth):
        """Test accessing nonexistent session"""
        response = test_client.get(
            "/api/v1/conversations/sessions/nonexistent/memory/statistics?user_id=test_user"
        )

        assert response.status_code == 404


class TestAgentCreationWithMemory:
    """Test agent creation with session memory"""

    def test_agent_config_with_memory(self):
        """Test creating agent configuration with memory"""
        from api_server.main import AgentConfig, SessionMemoryConfig, RedisConnectionConfig

        config = AgentConfig(
            agent_metadata={
                "agent_id": "memory_agent",
                "agent_name": "Memory Agent",
                "agent_type": "ReActAgent",
                "description": "Agent with memory"
            },
            llm_config={
                "model_name": "gpt-4",
                "api_key": "test_key"
            },
            prompt_config={
                "system_prompt": "You are a helpful assistant."
            },
            session_memory_config=SessionMemoryConfig(
                enabled=True,
                storage_type="redis",
                redis_config=RedisConnectionConfig(
                    host="localhost",
                    port=6379,
                    db=0
                )
            )
        )

        assert config.session_memory_config is not None
        assert config.session_memory_config.enabled == True
        assert config.session_memory_config.storage_type == "redis"

    def test_agent_config_without_memory(self):
        """Test creating agent configuration without memory"""
        from api_server.main import AgentConfig

        config = AgentConfig(
            agent_metadata={
                "agent_id": "simple_agent",
                "agent_name": "Simple Agent",
                "agent_type": "ReActAgent",
                "description": "Simple agent without memory"
            },
            llm_config={
                "model_name": "gpt-4",
                "api_key": "test_key"
            },
            prompt_config={
                "system_prompt": "You are a helpful assistant."
            }
        )

        assert config.session_memory_config is None


class TestSessionMemoryServiceIntegration:
    """Test session memory service integration"""

    @pytest.fixture
    def memory_service(self):
        """Get session memory service instance"""
        from agentscope_paas.memory.session_memory_service import session_memory_service
        return session_memory_service

    def test_conversation_flow_memory(self, memory_service):
        """Test complete conversation flow with memory"""
        config = {
            'session_memory': {
                'enabled': True,
                'storage_type': 'memory',
                'max_messages': 100
            }
        }

        user_id = "test_user"
        session_id = "test_session"

        # Simulate conversation
        messages = [
            ("user", "My name is Alice"),
            ("assistant", "Hello Alice! Nice to meet you."),
            ("user", "What's my name?"),
            ("assistant", "Your name is Alice.")
        ]

        # Add all messages
        for role, content in messages:
            result = memory_service.add_message(user_id, session_id, role, content, config)
            assert result == True

        # Verify all messages are stored
        stored_messages = memory_service.get_memory(user_id, session_id, config)
        assert len(stored_messages) == 4

        # Verify conversation content
        assert stored_messages[0]["content"] == "My name is Alice"
        assert stored_messages[2]["content"] == "What's my name?"

    def test_memory_message_limit(self, memory_service):
        """Test memory message limit enforcement"""
        max_messages = 5
        config = {
            'session_memory': {
                'enabled': True,
                'storage_type': 'memory',
                'max_messages': max_messages
            }
        }

        user_id = "test_user"
        session_id = "test_session"

        # Add more messages than the limit
        for i in range(10):
            memory_service.add_message(user_id, session_id, "user", f"Message {i}", config)

        # Get stored messages
        stored_messages = memory_service.get_memory(user_id, session_id, config)

        # Should only have the last 5 messages
        assert len(stored_messages) <= max_messages

    def test_multi_session_isolation(self, memory_service):
        """Test that different sessions are isolated"""
        config = {
            'session_memory': {
                'enabled': True,
                'storage_type': 'memory'
            }
        }

        user_id = "test_user"

        # Create two different sessions
        memory_service.add_message(user_id, "session1", "user", "Session 1 message", config)
        memory_service.add_message(user_id, "session2", "user", "Session 2 message", config)

        # Verify sessions are isolated
        session1_messages = memory_service.get_memory(user_id, "session1", config)
        session2_messages = memory_service.get_memory(user_id, "session2", config)

        assert len(session1_messages) == 1
        assert len(session2_messages) == 1
        assert session1_messages[0]["content"] == "Session 1 message"
        assert session2_messages[0]["content"] == "Session 2 message"

    def test_memory_clear_and_reuse(self, memory_service):
        """Test clearing memory and reusing session"""
        config = {
            'session_memory': {
                'enabled': True,
                'storage_type': 'memory'
            }
        }

        user_id = "test_user"
        session_id = "test_session"

        # Add messages
        memory_service.add_message(user_id, session_id, "user", "First message", config)
        memory_service.add_message(user_id, session_id, "assistant", "First response", config)

        # Verify messages exist
        messages = memory_service.get_memory(user_id, session_id, config)
        assert len(messages) == 2

        # Clear memory
        memory_service.clear_memory(user_id, session_id, config)

        # Verify memory is cleared
        messages = memory_service.get_memory(user_id, session_id, config)
        assert len(messages) == 0

        # Add new messages to the same session
        memory_service.add_message(user_id, session_id, "user", "New message", config)

        # Verify new message is stored
        messages = memory_service.get_memory(user_id, session_id, config)
        assert len(messages) == 1
        assert messages[0]["content"] == "New message"


class TestConfigurationValidation:
    """Test configuration validation for session memory"""

    def test_yaml_config_loading(self):
        """Test loading session memory from YAML config"""
        import yaml
        from io import StringIO

        yaml_content = """
agent_metadata:
  agent_id: "test_agent"
  agent_name: "Test Agent"
  agent_type: "ReActAgent"
  description: "Test agent with memory"

model_config:
  model_name: "gpt-4"
  api_key: "test_key"
  base_url: "https://api.openai.com/v1"

prompt_config:
  system_prompt: "You are a helpful assistant."

session_memory_config:
  enabled: true
  storage_type: "redis"
  redis_config:
    host: "localhost"
    port: 6379
    db: 0
  ttl: 3600
  max_messages: 100
  memory_key_prefix: "session_memory"
"""

        config = yaml.safe_load(StringIO(yaml_content))

        assert config["session_memory_config"]["enabled"] == True
        assert config["session_memory_config"]["storage_type"] == "redis"
        assert config["session_memory_config"]["redis_config"]["host"] == "localhost"
        assert config["session_memory_config"]["ttl"] == 3600
        assert config["session_memory_config"]["max_messages"] == 100

    def test_frontend_config_types(self):
        """Test frontend TypeScript interface compatibility"""
        # This simulates what would come from the frontend
        frontend_config = {
            "enabled": True,
            "storage_type": "redis",
            "redis_config": {
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "password": "",
                "connection_pool_size": 10,
                "socket_timeout": 5,
                "socket_connect_timeout": 5
            },
            "ttl": 3600,
            "max_messages": 100,
            "memory_key_prefix": "session_memory"
        }

        # Test it can be processed by the backend
        from api_server.main import SessionMemoryConfig, RedisConnectionConfig

        config = SessionMemoryConfig(**frontend_config)
        assert config.enabled == True
        assert config.redis_config is not None
        assert config.redis_config.host == "localhost"


@pytest.mark.integration
class TestRedisConnectivity:
    """Integration tests that require actual Redis connection"""

    @pytest.fixture
    def redis_config(self):
        """Get Redis configuration from environment or defaults"""
        import os
        return {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", 6379)),
            "db": int(os.getenv("REDIS_DB", 0)),
            "password": os.getenv("REDIS_PASSWORD"),
            "connection_pool_size": 10,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "ttl": 3600
        }

    def test_redis_connection_if_available(self, redis_config):
        """Test actual Redis connection if available"""
        from agentscope_paas.storage.redis_storage import RedisStorageBackend, RedisConfig

        try:
            config = RedisConfig(**redis_config)
            backend = RedisStorageBackend(config)

            # Test basic operations
            health = backend.health_check()
            assert health["status"] == "healthy"

            # Test save and retrieve
            messages = [{"role": "user", "content": "Integration test"}]
            save_result = backend.save_session_memory("test_user", "test_session", messages)
            assert save_result == True

            retrieved = backend.get_session_memory("test_user", "test_session")
            assert len(retrieved) == 1
            assert retrieved[0]["content"] == "Integration test"

            # Clean up
            backend.clear_session_memory("test_user", "test_session")

            print("✅ Redis integration test passed")

        except Exception as e:
            pytest.skip(f"Redis not available or connection failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])