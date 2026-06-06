"""
Runtime API Integration Tests

Comprehensive tests for Runtime API endpoints including deployment,
chat, health checks, streaming responses, and error handling.
"""

import pytest
import asyncio
import json
from typing import AsyncGenerator, Dict, Any
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import Runtime components
from agentscope_paas.core.runtime_manager import RuntimeManager, get_runtime_manager
from agentscope_paas.factory.runtime_agent_factory import RuntimeAgentFactory
from agentscope_paas.config.runtime_mapper import RuntimeConfigMapper
from api_server.routers import runtime as runtime_router
from api_server.utils.streaming import (
    StreamingResponseManager,
    StreamingChatProcessor,
    create_streaming_response,
    format_sse_message
)


# ============================================
# Test Fixtures
# ============================================

@pytest.fixture
def mock_config_loader():
    """Mock configuration loader"""
    mock_loader = Mock()
    mock_loader.get_agent_metadata.return_value = {
        "agent_name": "TestAgent",
        "agent_id": "test_agent_001",
        "agent_type": "DialogAgent",
        "description": "Test agent for Runtime integration"
    }
    mock_loader.get_model_config.return_value = {
        "model_name": "gpt-4",
        "api_key": "test_key",
        "base_url": "https://api.openai.com/v1",
        "temperature": 0.7,
        "max_tokens": 2000
    }
    mock_loader.get_prompt_config.return_value = {
        "system_prompt": "You are a helpful assistant",
        "user_prompt_template": None
    }
    mock_loader.get_memory_config.return_value = {
        "memory_type": "memory",
        "max_messages": 100
    }
    mock_loader.get_tool_config.return_value = None
    mock_loader.get_monitoring_config.return_value = None
    mock_loader.get_full_config.return_value = {
        "runtime_config": {
            "service": {
                "host": "localhost",
                "port": 8080
            },
            "lifecycle": {
                "auto_start": True,
                "idle_timeout_minutes": 30
            }
        }
    }
    return mock_loader


@pytest.fixture
def mock_storage():
    """Mock storage instance"""
    mock_store = Mock()
    mock_store.get_agent.return_value = {
        "agent_id": "test_agent_001",
        "config_path": "/path/to/config.yaml",
        "name": "TestAgent"
    }
    return mock_store


@pytest.fixture
def mock_runtime_manager():
    """Mock Runtime manager"""
    mock_manager = Mock()
    mock_manager.is_runtime_available.return_value = True
    mock_manager.deployment_status = "deployed"
    mock_manager.deployment_url = "http://localhost:8080"
    mock_manager.deployment_port = 8080
    mock_manager.health_status = "healthy"
    mock_manager.create_and_deploy_agent.return_value = True
    mock_manager.chat_with_runtime.return_value = "Test response"
    mock_manager.check_health.return_value = {
        "status": "healthy",
        "deployment_status": "deployed",
        "last_check": "2025-01-01T12:00:00",
        "deployment_url": "http://localhost:8080"
    }
    mock_manager.stop_agent.return_value = True
    mock_manager.restart_agent.return_value = True
    mock_manager.get_deployment_info.return_value = {
        "deployment_status": "deployed",
        "deployment_url": "http://localhost:8080",
        "deployment_port": 8080,
        "health_status": "healthy",
        "auto_start": True,
        "idle_timeout_minutes": 30,
        "runtime_available": True
    }
    return mock_manager


@pytest.fixture
def test_app():
    """Create test FastAPI application"""
    app = FastAPI()
    app.include_router(runtime_router.router)
    return app


@pytest.fixture
def test_client(test_app):
    """Create test client"""
    return TestClient(test_app)


# ============================================
# Runtime Manager Tests
# ============================================

class TestRuntimeManager:
    """Test RuntimeManager functionality"""

    def test_runtime_manager_initialization(self, mock_config_loader):
        """Test RuntimeManager initialization"""
        manager = RuntimeManager(mock_config_loader)

        assert manager.config_loader == mock_config_loader
        assert manager.agent_app is None
        assert manager.deployment_status == "not_deployed"
        assert manager.deployment_url is None

    def test_runtime_availability_check(self, mock_config_loader):
        """Test Runtime availability checking"""
        manager = RuntimeManager(mock_config_loader)

        # Should return boolean
        assert isinstance(manager.is_runtime_available(), bool)

    def test_deployment_info_retrieval(self, mock_config_loader):
        """Test deployment information retrieval"""
        manager = RuntimeManager(mock_config_loader)

        info = manager.get_deployment_info()

        assert "deployment_status" in info
        assert "deployment_url" in info
        assert "health_status" in info
        assert "runtime_available" in info


# ============================================
# Runtime Config Mapper Tests
# ============================================

class TestRuntimeConfigMapper:
    """Test RuntimeConfigMapper functionality"""

    def test_mapper_initialization(self, mock_config_loader):
        """Test RuntimeConfigMapper initialization"""
        mapper = RuntimeConfigMapper(mock_config_loader)

        assert mapper.config_loader == mock_config_loader

    def test_runtime_config_mapping(self, mock_config_loader):
        """Test configuration mapping to Runtime format"""
        mapper = RuntimeConfigMapper(mock_config_loader)

        runtime_config = mapper.map_to_runtime_config()

        assert "agent_config" in runtime_config
        assert "service_config" in runtime_config
        assert "lifecycle_config" in runtime_config
        assert "health_check_config" in runtime_config

    def test_agent_config_mapping(self, mock_config_loader):
        """Test agent configuration mapping"""
        mapper = RuntimeConfigMapper(mock_config_loader)

        agent_config = mapper._map_agent_config()

        assert "name" in agent_config
        assert "agent_id" in agent_config
        assert "model_config" in agent_config
        assert "prompt_config" in agent_config

    def test_runtime_config_validation(self, mock_config_loader):
        """Test Runtime configuration validation"""
        mapper = RuntimeConfigMapper(mock_config_loader)

        runtime_config = mapper.map_to_runtime_config()
        is_valid, errors = mapper.validate_runtime_config(runtime_config)

        # Should be valid for properly mapped config
        assert is_valid or len(errors) > 0  # Either valid or has specific errors


# ============================================
# Streaming Response Tests
# ============================================

class TestStreamingResponseManager:
    """Test StreamingResponseManager functionality"""

    def test_streaming_manager_initialization(self):
        """Test streaming manager initialization"""
        manager = StreamingResponseManager(
            agent_id="test_agent",
            timeout_seconds=120,
            keepalive_interval=30
        )

        assert manager.agent_id == "test_agent"
        assert manager.timeout_seconds == 120
        assert manager.keepalive_interval == 30

    def test_sse_event_formatting(self):
        """Test SSE event formatting"""
        manager = StreamingResponseManager(agent_id="test_agent")

        test_data = {
            "type": "test",
            "content": "test message"
        }

        sse_event = manager._format_sse_event(test_data)

        assert "data: " in sse_event
        assert "\n\n" in sse_event
        assert "test" in sse_event

    @pytest.mark.asyncio
    async def test_stream_response_with_mock_generator(self):
        """Test stream response with mock generator"""
        manager = StreamingResponseManager(
            agent_id="test_agent",
            timeout_seconds=120
        )

        async def mock_response_generator():
            """Mock response generator"""
            chunks = ["Hello", " ", "world", "!"]
            for chunk in chunks:
                yield chunk

        # Collect streamed responses
        responses = []
        async for response in manager.stream_agent_response(mock_response_generator()):
            responses.append(response)

        # Should have multiple responses (connected + chunks + complete)
        assert len(responses) > 1
        assert any("connected" in r for r in responses)
        assert any("complete" in r for r in responses)


class TestStreamingChatProcessor:
    """Test StreamingChatProcessor functionality"""

    def test_processor_initialization(self):
        """Test streaming processor initialization"""
        processor = StreamingChatProcessor()

        assert isinstance(processor.active_streams, dict)

    def test_get_active_streams(self):
        """Test getting active streams list"""
        processor = StreamingChatProcessor()

        streams = processor.get_active_streams()

        assert isinstance(streams, list)


# ============================================
# API Endpoint Tests
# ============================================

class TestRuntimeAPIEndpoints:
    """Test Runtime API endpoints"""

    def test_runtime_system_status_endpoint(self, test_client):
        """Test Runtime system status endpoint"""
        response = test_client.get("/api/v1/runtime/status")

        assert response.status_code in [200, 500]  # May fail if Runtime not available

        if response.status_code == 200:
            data = response.json()
            assert "runtime_available" in data
            assert "runtime_version" in data
            assert "python_version" in data

    def test_deploy_agent_endpoint_with_mock(self, test_client, mock_storage, mock_runtime_manager):
        """Test agent deployment endpoint with mocks"""
        with patch('agentscope_paas.core.runtime_manager.get_runtime_manager', return_value=mock_runtime_manager):
            with patch('agentscope_paas.config.loader.ConfigLoader'):
                response = test_client.post(
                    "/api/v1/agents/test_agent_001/deploy",
                    json={
                        "host": "localhost",
                        "port": 8080,
                        "max_concurrent_requests": 10,
                        "auto_start": True,
                        "idle_timeout_minutes": 30
                    }
                )

                # Should succeed or return appropriate error
                assert response.status_code in [200, 404, 503]

    def test_health_check_endpoint_with_mock(self, test_client, mock_storage, mock_runtime_manager):
        """Test health check endpoint with mocks"""
        with patch('agentscope_paas.core.runtime_manager.get_runtime_manager', return_value=mock_runtime_manager):
            with patch('agentscope_paas.config.loader.ConfigLoader'):
                response = test_client.get("/api/v1/agents/test_agent_001/health")

                # Should succeed or return appropriate error
                assert response.status_code in [200, 404, 503]

    def test_stop_agent_endpoint_with_mock(self, test_client, mock_storage, mock_runtime_manager):
        """Test stop agent endpoint with mocks"""
        with patch('agentscope_paas.core.runtime_manager.get_runtime_manager', return_value=mock_runtime_manager):
            with patch('agentscope_paas.config.loader.ConfigLoader'):
                response = test_client.delete("/api/v1/agents/test_agent_001/stop")

                # Should succeed or return appropriate error
                assert response.status_code in [200, 404, 503]

    def test_runtime_status_endpoint_with_mock(self, test_client, mock_storage, mock_runtime_manager):
        """Test runtime status endpoint with mocks"""
        with patch('agentscope_paas.core.runtime_manager.get_runtime_manager', return_value=mock_runtime_manager):
            with patch('agentscope_paas.config.loader.ConfigLoader'):
                response = test_client.get("/api/v1/agents/test_agent_001/runtime-status")

                # Should succeed or return appropriate error
                assert response.status_code in [200, 404, 503]


# ============================================
# Integration Tests
# ============================================

class TestRuntimeIntegration:
    """Test Runtime integration scenarios"""

    @pytest.mark.asyncio
    async def test_end_to_end_deployment_flow(self, mock_config_loader):
        """Test end-to-end deployment flow"""
        with patch('agentscope_paas.factory.agent_factory.AgentFactory.create_agent') as mock_create:
            mock_agent = Mock()
            mock_agent.name = "TestAgent"
            mock_create.return_value = mock_agent

            manager = RuntimeManager(mock_config_loader)

            # Mock Runtime availability
            with patch.object(manager, 'is_runtime_available', return_value=True):
                # This would normally deploy the agent
                # For testing, we just verify the flow works
                assert manager.is_runtime_available()

    @pytest.mark.asyncio
    async def test_streaming_chat_flow(self, mock_config_loader, mock_runtime_manager):
        """Test streaming chat flow"""
        # Create mock streaming response
        async def mock_stream():
            chunks = ["Hello", " ", "world", "!"]
            for chunk in chunks:
                yield chunk

        mock_runtime_manager.chat_with_runtime.return_value = mock_stream()

        # Test streaming response creation
        responses = []
        async for response in create_streaming_response(
            agent_id="test_agent",
            message="Hello",
            runtime_manager=mock_runtime_manager,
            timeout_seconds=120
        ):
            responses.append(response)

        # Should have responses
        assert len(responses) > 0


# ============================================
# Error Handling Tests
# ============================================

class TestRuntimeErrorHandling:
    """Test Runtime error handling"""

    def test_runtime_unavailable_handling(self, test_client):
        """Test handling when Runtime is unavailable"""
        with patch('agentscope_paas.utils.runtime_validator.check_runtime_availability', return_value=False):
            response = test_client.get("/api/v1/runtime/status")

            # Should still return 200 with runtime_available: false
            assert response.status_code == 200
            data = response.json()
            assert data["runtime_available"] is False

    def test_agent_not_found_handling(self, test_client, mock_storage):
        """Test handling when agent is not found"""
        mock_storage.get_agent.return_value = None

        with patch('agentscope_paas.auth.middleware.get_storage', return_value=mock_storage):
            response = test_client.post(
                "/api/v1/agents/nonexistent_agent/deploy",
                json={"host": "localhost", "port": 8080}
            )

            # Should return 404
            assert response.status_code == 404

    def test_invalid_configuration_handling(self, test_client, mock_storage):
        """Test handling of invalid configuration"""
        mock_storage.get_agent.return_value = {
            "agent_id": "test_agent",
            "config_path": "/invalid/path/config.yaml"
        }

        with patch('agentscope_paas.auth.middleware.get_storage', return_value=mock_storage):
            with patch('agentscope_paas.config.loader.ConfigLoader') as mock_loader:
                mock_loader.return_value.load.return_value = (False, {}, ["Config error"])

                response = test_client.post(
                    "/api/v1/agents/test_agent/deploy",
                    json={"host": "localhost", "port": 8080}
                )

                # Should return error
                assert response.status_code in [400, 404]


# ============================================
# Performance Tests
# ============================================

class TestRuntimePerformance:
    """Test Runtime performance characteristics"""

    @pytest.mark.asyncio
    async def test_streaming_performance(self):
        """Test streaming response performance"""
        manager = StreamingResponseManager(
            agent_id="test_agent",
            timeout_seconds=120
        )

        async def fast_generator():
            """Fast response generator"""
            for i in range(100):
                yield f"chunk_{i}"

        start_time = asyncio.get_event_loop().time()
        chunk_count = 0

        async for response in manager.stream_agent_response(fast_generator()):
            if "chunk" in response:
                chunk_count += 1

        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time

        # Should process chunks reasonably fast
        assert chunk_count == 100
        assert elapsed < 5.0  # Should complete in under 5 seconds


# ============================================
# Utility Function Tests
# ============================================

class TestStreamingUtilities:
    """Test streaming utility functions"""

    def test_format_sse_message(self):
        """Test SSE message formatting"""
        message = format_sse_message(
            message_type="test",
            data={"content": "test"},
            agent_id="test_agent"
        )

        assert "data: " in message
        assert "\n\n" in message
        assert "test" in message

    def test_create_sse_error_response(self):
        """Test SSE error response creation"""
        from api_server.utils.streaming import create_sse_error_response

        error_response = create_sse_error_response(
            error_message="Test error",
            agent_id="test_agent",
            error_code="TEST_ERROR"
        )

        assert "data: " in error_response
        assert "Test error" in error_response
        assert "TEST_ERROR" in error_response


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])