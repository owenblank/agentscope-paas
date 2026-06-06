"""
Comprehensive Testing and Validation Suite for Runtime Integration

Provides end-to-end tests, performance benchmarks, load testing,
and integration validation for Runtime components.
"""

import pytest
import asyncio
import time
import threading
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from pathlib import Path
import tempfile
import shutil

# Import Runtime components
from agentscope_paas.core.runtime_manager import RuntimeManager, get_runtime_manager
from agentscope_paas.factory.runtime_agent_factory import RuntimeAgentFactory
from agentscope_paas.config.runtime_mapper import RuntimeConfigMapper
from agentscope_paas.monitoring.runtime_monitor import (
    RuntimeMetricsCollector,
    RuntimeAlertManager,
    RuntimePerformanceMonitor,
    create_runtime_monitor
)
from agentscope_paas.performance.runtime_optimizer import (
    RuntimeCache,
    ConnectionPool,
    PerformanceOptimizer,
    get_performance_optimizer
)
from agentscope_paas.lifecycle.advanced_lifecycle import (
    AdvancedLifecycleManager,
    LifecycleConfig,
    LifecycleState,
    create_lifecycle_manager
)
from agentscope_paas.deployment.production_utils import (
    DeploymentValidator,
    DeploymentTemplateManager,
    HealthCheckSystem,
    BackupManager,
    DeploymentConfig,
    DeploymentEnvironment
)

from ..utils.logger import get_logger


# ============================================
# Test Fixtures and Utilities
# ============================================

@pytest.fixture
def mock_config_loader():
    """Mock configuration loader for testing"""
    mock = Mock()
    mock.get_agent_metadata.return_value = {
        "agent_name": "TestAgent",
        "agent_id": "test_agent_001",
        "agent_type": "ReActAgent",
        "description": "Test agent for Runtime integration"
    }
    mock.get_model_config.return_value = {
        "model_name": "gpt-4",
        "api_key": "test_key",
        "base_url": "https://api.openai.com/v1"
    }
    mock.get_prompt_config.return_value = {
        "system_prompt": "You are a helpful assistant"
    }
    mock.get_full_config.return_value = {
        "runtime_config": {
            "deployment_mode": "runtime",
            "service": {
                "host": "localhost",
                "port": 8080
            }
        }
    }
    return mock


@pytest.fixture
def temp_config_dir():
    """Temporary directory for test configurations"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================
# End-to-End Runtime Integration Tests
# ============================================

class TestRuntimeIntegrationE2E:
    """End-to-end integration tests for Runtime components"""

    @pytest.mark.asyncio
    async def test_complete_runtime_workflow(self, mock_config_loader, temp_config_dir):
        """Test complete Runtime workflow from configuration to execution"""
        try:
            # Step 1: Create Runtime Manager
            manager = RuntimeManager(mock_config_loader)
            assert manager is not None
            assert manager.deployment_status == "not_deployed"

            # Step 2: Map configuration
            mapper = RuntimeConfigMapper(mock_config_loader)
            runtime_config = mapper.map_to_runtime_config()
            assert "agent_config" in runtime_config
            assert "service_config" in runtime_config

            # Step 3: Validate configuration
            is_valid, errors = mapper.validate_runtime_config(runtime_config)
            assert is_valid, f"Configuration validation failed: {errors}"

            # Step 4: Create Runtime factory
            factory = RuntimeAgentFactory(mock_config_loader)
            assert factory is not None

            # Step 5: Check Runtime availability
            runtime_available = manager.is_runtime_available()
            # May be False in test environment, which is okay

            # Step 6: Test deployment info retrieval
            deployment_info = manager.get_deployment_info()
            assert "deployment_status" in deployment_info
            assert "runtime_available" in deployment_info

        except Exception as e:
            pytest.fail(f"E2E workflow failed: {str(e)}")

    def test_runtime_configuration_persistence(self, mock_config_loader, temp_config_dir):
        """Test Runtime configuration persistence across instances"""
        try:
            # Create initial configuration
            mapper1 = RuntimeConfigMapper(mock_config_loader)
            config1 = mapper1.map_to_runtime_config()

            # Create new mapper instance
            mapper2 = RuntimeConfigMapper(mock_config_loader)
            config2 = mapper2.map_to_runtime_config()

            # Configurations should be consistent
            assert config1["agent_config"]["name"] == config2["agent_config"]["name"]

        except Exception as e:
            pytest.fail(f"Configuration persistence test failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_runtime_health_check_workflow(self, mock_config_loader):
        """Test health check workflow"""
        try:
            manager = RuntimeManager(mock_config_loader)

            # Perform health check
            health_info = manager.check_health()
            assert health_info is not None
            assert "status" in health_info
            assert "deployment_status" in health_info
            assert "runtime_available" in health_info

            # Health check should not throw errors
            assert isinstance(health_info["status"], str)

        except Exception as e:
            pytest.fail(f"Health check workflow failed: {str(e)}")


# ============================================
# Performance Benchmarking Tests
# ============================================

class TestPerformanceBenchmarks:
    """Performance benchmarking tests for Runtime components"""

    def test_cache_performance_benchmark(self):
        """Benchmark cache performance"""
        cache = RuntimeCache(max_size=10000, ttl=3600)

        # Benchmark write operations
        start_time = time.time()
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        write_time = time.time() - start_time

        # Benchmark read operations
        start_time = time.time()
        for i in range(1000):
            cache.get(f"key_{i}")
        read_time = time.time() - start_time

        # Performance assertions
        assert write_time < 1.0, f"Write operations too slow: {write_time:.3f}s"
        assert read_time < 0.5, f"Read operations too slow: {read_time:.3f}s"

        # Check hit rate
        stats = cache.get_stats()
        assert stats["hits"] > 0, "Cache should have some hits"

    def test_metrics_collection_overhead(self):
        """Benchmark metrics collection overhead"""
        collector = RuntimeMetricsCollector(
            collection_interval=1,
            retention_hours=1
        )

        # Collect metrics without background thread
        collector._collect_metrics()

        start_time = time.time()
        for _ in range(100):
            collector._collect_metrics()
        collection_time = time.time() - start_time

        # Should be fast
        assert collection_time < 2.0, f"Metrics collection too slow: {collection_time:.3f}s"

    def test_lifecycle_scaling_performance(self):
        """Benchmark auto-scaling decision performance"""
        config = LifecycleConfig(
            enable_auto_scaling=True,
            min_instances=1,
            max_instances=10
        )

        lifecycle = AdvancedLifecycleManager(config)

        # Benchmark scaling decisions
        start_time = time.time()
        for _ in range(100):
            lifecycle.check_auto_scaling(lambda: Mock())
        decision_time = time.time() - start_time

        # Should be fast
        assert decision_time < 1.0, f"Scaling decisions too slow: {decision_time:.3f}s"

    @pytest.mark.asyncio
    async def test_concurrent_operations_performance(self):
        """Benchmark concurrent operation handling"""
        optimizer = get_performance_optimizer()

        # Create cache for testing
        cache = optimizer.create_cache("test_cache", max_size=1000)

        async def concurrent_operations():
            """Simulate concurrent operations"""
            tasks = []
            for i in range(100):
                task = asyncio.create_task(asyncio.to_thread(
                    cache.set, f"key_{i}", f"value_{i}"
                ))
                tasks.append(task)

            await asyncio.gather(*tasks)

        start_time = time.time()
        await concurrent_operations()
        operation_time = time.time() - start_time

        # Should handle concurrent operations efficiently
        assert operation_time < 2.0, f"Concurrent operations too slow: {operation_time:.3f}s"


# ============================================
# Load Testing
# ============================================

class TestLoadTesting:
    """Load testing for Runtime components"""

    def test_cache_under_load(self):
        """Test cache performance under high load"""
        cache = RuntimeCache(max_size=10000, ttl=3600)

        # Simulate high load
        start_time = time.time()
        for i in range(10000):
            cache.set(f"key_{i}", f"value_{i}")
            cache.get(f"key_{i % 100}")  # Get from recent keys
        end_time = time.time()

        load_time = end_time - start_time

        # Should handle load efficiently
        assert load_time < 5.0, f"Cache unable to handle load: {load_time:.3f}s"

        # Check cache maintained consistency
        stats = cache.get_stats()
        assert stats["size"] <= 10000

    def test_connection_pool_under_load(self):
        """Test connection pool under high load"""
        pool = ConnectionPool(max_connections=50)

        def simulate_connection_use(i):
            """Simulate connection usage"""
            return pool.get_connection(f"conn_{i}", lambda: Mock())

        # Simulate high connection load
        start_time = time.time()
        connections = []
        for i in range(100):
            conn = simulate_connection_use(i)
            connections.append(conn)
        end_time = time.time()

        load_time = end_time - start_time

        # Should handle load efficiently
        assert load_time < 2.0, f"Connection pool unable to handle load: {load_time:.3f}s"

        # Check pool stats
        stats = pool.get_stats()
        assert stats["active_connections"] <= 50

    def test_metrics_collector_under_load(self):
        """Test metrics collector under high load"""
        collector = RuntimeMetricsCollector(collection_interval=1)

        # Simulate high metric load
        start_time = time.time()
        for i in range(1000):
            collector.set_gauge(f"test_metric_{i % 10}", i)
            collector.increment_counter(f"test_counter_{i % 5}", 1)
            collector.record_histogram(f"test_histogram_{i % 3}", i % 100)
        end_time = time.time()

        load_time = end_time - start_time

        # Should handle load efficiently
        assert load_time < 1.0, f"Metrics collector unable to handle load: {load_time:.3f}s"


# ============================================
# Integration Validation Tests
# ============================================

class TestIntegrationValidation:
    """Integration validation tests"""

    def test_runtime_manager_integration(self, mock_config_loader):
        """Test Runtime Manager integration with other components"""
        manager = RuntimeManager(mock_config_loader)

        # Test basic integration
        assert manager is not None
        assert manager.deployment_status == "not_deployed"

        # Test deployment info
        info = manager.get_deployment_info()
        assert info is not None

    def test_monitoring_integration(self):
        """Test monitoring system integration"""
        # Create monitoring system
        collector = create_runtime_monitor(collection_interval=1)
        alert_manager = RuntimeAlertManager(collector)
        performance_monitor = RuntimePerformanceMonitor(collector)

        # Test integration
        assert collector is not None
        assert alert_manager is not None
        assert performance_monitor is not None

        # Record some metrics
        collector.set_gauge("test_metric", 100)
        performance_monitor.record_request("test_op", 0.5, True)

        # Check integration
        stats = performance_monitor.get_performance_stats("test_op")
        assert stats is not None

        # Cleanup
        collector.stop_collection()

    def test_performance_optimizer_integration(self):
        """Test performance optimizer integration"""
        optimizer = get_performance_optimizer()

        # Test cache integration
        cache = optimizer.create_cache("test_cache")
        assert cache is not None

        # Test pool integration
        pool = optimizer.create_pool("test_pool")
        assert pool is not None

        # Test optimization summary
        summary = optimizer.get_optimization_summary()
        assert summary is not None
        assert "caches" in summary
        assert "pools" in summary

    def test_deployment_validation_integration(self):
        """Test deployment validation integration"""
        validator = create_deployment_validator()
        template_manager = create_template_manager()
        health_system = create_health_check_system()
        backup_manager = create_backup_manager()

        # Test integration
        assert validator is not None
        assert template_manager is not None
        assert health_system is not None
        assert backup_manager is not None

        # Get templates
        templates = template_manager.list_templates()
        assert len(templates) > 0

        # Validate production config
        prod_config = template_manager.get_template("production")
        is_valid, errors = validator.validate_deployment(
            prod_config,
            DeploymentEnvironment.PRODUCTION
        )
        assert is_valid, f"Production config validation failed: {errors}"


# ============================================
# Reliability and Error Handling Tests
# ============================================

class TestReliabilityAndErrorHandling:
    """Reliability and error handling tests"""

    def test_cache_error_handling(self):
        """Test cache error handling"""
        cache = RuntimeCache(max_size=10)

        # Test invalid operations
        cache.get("nonexistent_key")  # Should return None
        cache.delete("nonexistent_key")  # Should return False

        # Test edge cases
        cache.set("", "value")  # Empty key
        cache.set(None, "value")  # None key (if allowed)

        # Cache should remain functional
        cache.set("valid_key", "valid_value")
        assert cache.get("valid_key") == "valid_value"

    def test_connection_pool_error_handling(self):
        """Test connection pool error handling"""
        pool = ConnectionPool(max_connections=5)

        # Test invalid operations
        result = pool.get_connection("test_key", lambda: Mock())
        assert result is not None

        # Test pool overflow
        connections = []
        for i in range(10):  # More than max_connections
            conn = pool.get_connection(f"overflow_{i}", lambda: Mock())
            connections.append(conn)

        # Should still work
        stats = pool.get_stats()
        assert stats["active_connections"] <= 5

    def test_monitoring_error_handling(self):
        """Test monitoring error handling"""
        collector = RuntimeMetricsCollector()

        # Test invalid metrics
        collector.set_gauge("", -100)  # Invalid gauge
        collector.increment_counter("test", -1)  # Negative increment

        # Should still collect metrics
        collector._collect_metrics()

        # Get metrics should work
        metrics = collector.get_all_metrics()
        assert metrics is not None

    def test_lifecycle_error_handling(self):
        """Test lifecycle manager error handling"""
        config = LifecycleConfig(max_instances=1, min_instances=1)
        lifecycle = AdvancedLifecycleManager(config)

        # Test invalid operations
        lifecycle.stop_instance("nonexistent_instance")  # Should not crash

        # Test scaling beyond limits
        result = lifecycle.scale_instances(100, lambda: Mock())  # Way above max
        assert result is False  # Should fail

        # Status should be accessible
        status = lifecycle.get_lifecycle_status()
        assert status is not None

    def test_backup_error_handling(self):
        """Test backup manager error handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_mgr = BackupManager(backup_dir=temp_dir)

            # Test invalid operations
            result = backup_mgr.restore_backup("nonexistent_backup", "/tmp/config.yaml")
            assert result is False

            # Test backup with invalid paths
            result = backup_mgr.create_backup("test", "/nonexistent/path/config.yaml")
            # Should handle gracefully (may return None or succeed with warnings)

            # List backups should work
            backups = backup_mgr.list_backups("test_agent")
            assert isinstance(backups, list)


# ============================================
# Configuration and Compatibility Tests
# ============================================

class TestConfigurationAndCompatibility:
    """Configuration and compatibility tests"""

    def test_runtime_config_compatibility(self, mock_config_loader):
        """Test Runtime configuration compatibility"""
        mapper = RuntimeConfigMapper(mock_config_loader)

        # Test configuration mapping
        config = mapper.map_to_runtime_config()

        # Test required fields
        assert "agent_config" in config
        assert "service_config" in config
        assert "lifecycle_config" in config

        # Test validation
        is_valid, errors = mapper.validate_runtime_config(config)
        assert is_valid, f"Config validation failed: {errors}"

    def test_deployment_config_compatibility(self):
        """Test deployment configuration compatibility"""
        validator = DeploymentValidator()
        template_manager = DeploymentTemplateManager()

        # Test all environment templates
        for env_name in template_manager.list_templates():
            template = template_manager.get_template(env_name)
            assert template is not None

            # Validate for appropriate environment
            env = DeploymentEnvironment[env_name.upper()]
            is_valid, errors = validator.validate_deployment(template, env)

            # Templates should be valid for their environments
            if env_name == "production":
                assert is_valid, f"Production template validation failed: {errors}"

    def test_backward_compatibility(self, mock_config_loader):
        """Test backward compatibility with existing configurations"""
        # Create minimal config
        minimal_config = {
            "agent_metadata": {
                "agent_name": "TestAgent",
                "agent_id": "test_001",
                "agent_type": "ReActAgent",
                "description": "Test"
            },
            "model_config": {
                "model_name": "gpt-4",
                "api_key": "test",
                "base_url": "https://api.openai.com/v1"
            },
            "prompt_config": {
                "system_prompt": "You are helpful"
            }
        }

        # Should work with Runtime mapper
        mapper = RuntimeConfigMapper(mock_config_loader)
        runtime_config = mapper.map_to_runtime_config()

        # Should have default Runtime config
        assert "service_config" in runtime_config
        assert runtime_config["service_config"]["host"] == "localhost"


# ============================================
# Security and Resource Management Tests
# ============================================

class TestSecurityAndResourceManagement:
    """Security and resource management tests"""

    def test_resource_limits(self):
        """Test resource limit enforcement"""
        config = LifecycleConfig(
            max_memory_mb=1024,
            max_cpu_percent=80.0,
            max_instances=5,
            min_instances=1
        )

        lifecycle = AdvancedLifecycleManager(config)

        # Test resource limit validation
        assert config.max_memory_mb == 1024
        assert config.max_cpu_percent == 80.0
        assert config.max_instances == 5

        # Test scaling within limits
        status = lifecycle.get_lifecycle_status()
        assert status["total_capacity"] <= config.max_instances

    def test_security_configuration(self):
        """Test security configuration validation"""
        validator = DeploymentValidator()

        # Test security validation
        secure_config = DeploymentConfig(
            environment=DeploymentEnvironment.PRODUCTION,
            enable_sandbox=True,
            api_key_required=True,
            allowed_hosts=["localhost", "api.example.com"]
        )

        insecure_config = DeploymentConfig(
            environment=DeploymentEnvironment.PRODUCTION,
            enable_sandbox=False,
            api_key_required=False,
            allowed_hosts=[]
        )

        # Secure config should pass
        is_valid, errors = validator.validate_deployment(
            secure_config,
            DeploymentEnvironment.PRODUCTION
        )
        assert is_valid, f"Secure config failed validation: {errors}"

        # Insecure config should fail some validations
        is_valid, errors = validator.validate_deployment(
            insecure_config,
            DeploymentEnvironment.PRODUCTION
        )
        assert not is_valid or len(errors) > 0, "Insecure config should fail validation"


# ============================================
# Test Runners and Utilities
# ============================================

def run_comprehensive_tests():
    """Run comprehensive Runtime integration tests"""
    pytest.main([__file__, "-v", "--tb=short", "-x"])


def run_performance_tests():
    """Run performance benchmark tests only"""
    pytest.main([__file__, "-v", "-k", "performance", "--tb=short"])


def run_load_tests():
    """Run load testing only"""
    pytest.main([__file__, "-v", "-k", "load", "--tb=short"])


def run_integration_tests():
    """Run integration validation tests only"""
    pytest.main([__file__, "-v", "-k", "integration", "--tb=short"])


if __name__ == "__main__":
    # Run all tests
    run_comprehensive_tests()