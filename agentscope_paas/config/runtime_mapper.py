"""
Runtime Config Mapper Module

Maps AgentScope PaaS YAML configurations to AgentScope Runtime configurations
while preserving backward compatibility and adding Runtime-specific features.
"""

from typing import Any, Dict, Optional, Union
import logging
from datetime import timedelta

from ..config.loader import ConfigLoader
from ..utils.logger import get_logger


class RuntimeConfigMapper:
    """
    Runtime Configuration Mapper

    Converts PaaS configurations to Runtime configurations with support for:
    - Model configuration mapping
    - Memory configuration adaptation
    - Tool configuration translation
    - Monitoring configuration setup
    - Runtime-specific extensions
    """

    def __init__(self, config_loader: ConfigLoader):
        """
        Initialize Runtime Config Mapper

        Args:
            config_loader: Configuration loader instance
        """
        self.config_loader = config_loader
        self.logger = get_logger(__name__)

    def map_to_runtime_config(self) -> Dict[str, Any]:
        """
        Map PaaS configuration to Runtime configuration

        Returns:
            Runtime configuration dictionary
        """
        try:
            runtime_config = {
                "agent_config": self._map_agent_config(),
                "service_config": self._map_service_config(),
                "lifecycle_config": self._map_lifecycle_config(),
                "health_check_config": self._map_health_check_config(),
                "monitoring_config": self._map_monitoring_config(),
                "runtime_extensions": self._map_runtime_extensions()
            }

            self.logger.info("PaaS configuration mapped to Runtime configuration")
            return runtime_config

        except Exception as e:
            self.logger.error(f"Runtime config mapping failed: {str(e)}")
            return {}

    def _map_agent_config(self) -> Dict[str, Any]:
        """
        Map agent configuration

        Returns:
            Agent configuration for Runtime
        """
        try:
            # Get PaaS agent configuration
            metadata = self.config_loader.get_agent_metadata()
            model_config = self.config_loader.get_model_config()
            prompt_config = self.config_loader.get_prompt_config()
            memory_config = self.config_loader.get_memory_config()

            # Map to Runtime format
            agent_config = {
                "name": metadata.get("agent_name", "RuntimeAgent"),
                "agent_id": metadata.get("agent_id", "runtime_agent"),
                "agent_type": metadata.get("agent_type", "DialogAgent"),
                "description": metadata.get("description", ""),
                "version": metadata.get("version", "1.0.0"),
                "model_config": self._map_model_config(model_config),
                "prompt_config": self._map_prompt_config(prompt_config)
            }

            # Add optional configurations
            if memory_config:
                agent_config["memory_config"] = self._map_memory_config(memory_config)

            # Add tool configuration if present
            tool_config = self.config_loader.get_tool_config()
            if tool_config:
                agent_config["tool_config"] = self._map_tool_config(tool_config)

            return agent_config

        except Exception as e:
            self.logger.error(f"Agent config mapping failed: {str(e)}")
            return {}

    def _map_model_config(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map model configuration to Runtime format

        Args:
            model_config: PaaS model configuration

        Returns:
            Runtime model configuration
        """
        try:
            # Direct mapping for most fields
            runtime_model_config = {
                "model_name": model_config.get("model_name", "gpt-4"),
                "api_key": model_config.get("api_key", ""),
                "base_url": model_config.get("base_url", "https://api.openai.com/v1"),
                "temperature": model_config.get("temperature", 0.7),
                "max_tokens": model_config.get("max_tokens", 2000),
                "top_p": model_config.get("top_p", 1.0),
                "frequency_penalty": model_config.get("frequency_penalty", 0.0),
                "presence_penalty": model_config.get("presence_penalty", 0.0)
            }

            # Add Runtime-specific extensions
            runtime_model_config["streaming"] = model_config.get("streaming", False)
            runtime_model_config["timeout"] = model_config.get("timeout", 60)

            return runtime_model_config

        except Exception as e:
            self.logger.error(f"Model config mapping failed: {str(e)}")
            return {}

    def _map_prompt_config(self, prompt_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map prompt configuration to Runtime format

        Args:
            prompt_config: PaaS prompt configuration

        Returns:
            Runtime prompt configuration
        """
        try:
            runtime_prompt_config = {
                "system_prompt": prompt_config.get("system_prompt", ""),
                "user_prompt_template": prompt_config.get("user_prompt_template", None)
            }

            # Add Runtime-specific prompt enhancements
            runtime_prompt_config["max_prompt_length"] = prompt_config.get(
                "max_prompt_length", 4000
            )

            return runtime_prompt_config

        except Exception as e:
            self.logger.error(f"Prompt config mapping failed: {str(e)}")
            return {}

    def _map_memory_config(self, memory_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map memory configuration to Runtime format

        Args:
            memory_config: PaaS memory configuration

        Returns:
            Runtime memory configuration
        """
        try:
            runtime_memory_config = {
                "memory_type": memory_config.get("memory_type", "memory"),
                "max_messages": memory_config.get("max_messages", 100),
                "memory_window_size": memory_config.get("memory_window_size", 10),
                "persistent": memory_config.get("persistent", False)
            }

            # Add session memory support
            if "session_memory_config" in memory_config:
                session_config = memory_config["session_memory_config"]
                runtime_memory_config["session_memory"] = {
                    "enabled": session_config.get("enabled", False),
                    "storage_type": session_config.get("storage_type", "memory"),
                    "ttl": session_config.get("ttl", 3600),
                    "max_messages": session_config.get("max_messages", 100)
                }

            # Add context compression support
            if "context_compression_config" in memory_config:
                compression_config = memory_config["context_compression_config"]
                runtime_memory_config["context_compression"] = {
                    "enabled": compression_config.get("enabled", False),
                    "compression_threshold": compression_config.get("compression_threshold", 3000),
                    "compression_strategy": compression_config.get("compression_strategy", "recent")
                }

            return runtime_memory_config

        except Exception as e:
            self.logger.error(f"Memory config mapping failed: {str(e)}")
            return {}

    def _map_tool_config(self, tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map tool configuration to Runtime format

        Args:
            tool_config: PaaS tool configuration

        Returns:
            Runtime tool configuration
        """
        try:
            runtime_tool_config = {
                "tools_enabled": tool_config.get("tools_enabled", False),
                "tool_timeout": tool_config.get("tool_timeout", 30),
                "max_tool_calls": tool_config.get("max_tool_calls", 10)
            }

            # Add tool list if present
            if "tools" in tool_config:
                runtime_tool_config["tools"] = tool_config["tools"]

            # Add MCP configuration
            if "mcp_config" in tool_config:
                mcp_config = tool_config["mcp_config"]
                runtime_tool_config["mcp"] = {
                    "enabled": mcp_config.get("enabled", False),
                    "servers": mcp_config.get("servers", [])
                }

            return runtime_tool_config

        except Exception as e:
            self.logger.error(f"Tool config mapping failed: {str(e)}")
            return {}

    def _map_service_config(self) -> Dict[str, Any]:
        """
        Map service configuration for Runtime deployment

        Returns:
            Runtime service configuration
        """
        try:
            # Get Runtime-specific service config from PaaS config
            full_config = self.config_loader.get_full_config()
            runtime_section = full_config.get("runtime_config", {})

            service_config = {
                "host": runtime_section.get("service", {}).get("host", "localhost"),
                "port": runtime_section.get("service", {}).get("port", 8080),
                "max_concurrent_requests": runtime_section.get("service", {}).get(
                    "max_concurrent_requests", 10
                ),
                "startup_timeout": runtime_section.get("service", {}).get(
                    "startup_timeout", 300
                ),
                "request_timeout": runtime_section.get("service", {}).get(
                    "request_timeout", 120
                )
            }

            return service_config

        except Exception as e:
            self.logger.error(f"Service config mapping failed: {str(e)}")
            return {
                "host": "localhost",
                "port": 8080,
                "max_concurrent_requests": 10
            }

    def _map_lifecycle_config(self) -> Dict[str, Any]:
        """
        Map lifecycle configuration for Runtime management

        Returns:
            Runtime lifecycle configuration
        """
        try:
            # Get Runtime-specific lifecycle config
            full_config = self.config_loader.get_full_config()
            runtime_section = full_config.get("runtime_config", {})

            lifecycle_config = {
                "auto_start": runtime_section.get("lifecycle", {}).get("auto_start", True),
                "auto_stop": runtime_section.get("lifecycle", {}).get("auto_stop", False),
                "idle_timeout_minutes": runtime_section.get("lifecycle", {}).get(
                    "idle_timeout_minutes", 30
                ),
                "graceful_shutdown_timeout": runtime_section.get("lifecycle", {}).get(
                    "graceful_shutdown_timeout", 60
                ),
                "max_retries": runtime_section.get("lifecycle", {}).get("max_retries", 3),
                "retry_delay_seconds": runtime_section.get("lifecycle", {}).get(
                    "retry_delay_seconds", 5
                )
            }

            return lifecycle_config

        except Exception as e:
            self.logger.error(f"Lifecycle config mapping failed: {str(e)}")
            return {
                "auto_start": True,
                "auto_stop": False,
                "idle_timeout_minutes": 30
            }

    def _map_health_check_config(self) -> Dict[str, Any]:
        """
        Map health check configuration for Runtime monitoring

        Returns:
            Runtime health check configuration
        """
        try:
            # Get Runtime-specific health check config
            full_config = self.config_loader.get_full_config()
            runtime_section = full_config.get("runtime_config", {})

            health_check_config = {
                "enabled": runtime_section.get("health_check", {}).get("enabled", True),
                "interval_seconds": runtime_section.get("health_check", {}).get(
                    "interval_seconds", 60
                ),
                "timeout_seconds": runtime_section.get("health_check", {}).get(
                    "timeout_seconds", 10
                ),
                "failure_threshold": runtime_section.get("health_check", {}).get(
                    "failure_threshold", 3
                ),
                "success_threshold": runtime_section.get("health_check", {}).get(
                    "success_threshold", 1
                )
            }

            return health_check_config

        except Exception as e:
            self.logger.error(f"Health check config mapping failed: {str(e)}")
            return {
                "enabled": True,
                "interval_seconds": 60
            }

    def _map_monitoring_config(self) -> Dict[str, Any]:
        """
        Map monitoring configuration for Runtime observability

        Returns:
            Runtime monitoring configuration
        """
        try:
            # Get PaaS monitoring config
            monitoring_config = self.config_loader.get_monitoring_config()

            runtime_monitoring_config = {
                "enabled": monitoring_config.get("enabled", False) if monitoring_config else False,
                "metrics_collection": monitoring_config.get("metrics_collection", True) if monitoring_config else True,
                "log_level": monitoring_config.get("log_level", "INFO") if monitoring_config else "INFO",
                "performance_tracking": monitoring_config.get("performance_tracking", True) if monitoring_config else True,
                "error_tracking": monitoring_config.get("error_tracking", True) if monitoring_config else True
            }

            # Add Runtime-specific monitoring
            runtime_monitoring_config["resource_monitoring"] = {
                "enabled": monitoring_config.get("resource_monitoring", {}).get("enabled", True) if monitoring_config else True,
                "memory_threshold_mb": monitoring_config.get("resource_monitoring", {}).get("memory_threshold_mb", 1024) if monitoring_config else 1024,
                "cpu_threshold_percent": monitoring_config.get("resource_monitoring", {}).get("cpu_threshold_percent", 80) if monitoring_config else 80
            }

            return runtime_monitoring_config

        except Exception as e:
            self.logger.error(f"Monitoring config mapping failed: {str(e)}")
            return {
                "enabled": False,
                "metrics_collection": True
            }

    def _map_runtime_extensions(self) -> Dict[str, Any]:
        """
        Map Runtime-specific extensions and features

        Returns:
            Runtime extensions configuration
        """
        try:
            # Get Runtime-specific extensions from config
            full_config = self.config_loader.get_full_config()
            runtime_section = full_config.get("runtime_config", {})

            extensions = {
                "streaming_enabled": runtime_section.get("streaming", {}).get("enabled", True),
                "sandbox_enabled": runtime_section.get("sandbox", {}).get("enabled", False),
                "sandbox_type": runtime_section.get("sandbox", {}).get("type", "docker"),
                "custom_decorators": runtime_section.get("custom_decorators", []),
                "middleware": runtime_section.get("middleware", []),
                "environment_variables": runtime_section.get("environment_variables", {})
            }

            return extensions

        except Exception as e:
            self.logger.error(f"Runtime extensions mapping failed: {str(e)}")
            return {
                "streaming_enabled": True,
                "sandbox_enabled": False
            }

    def validate_runtime_config(self, runtime_config: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate mapped Runtime configuration

        Args:
            runtime_config: Runtime configuration to validate

        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []

        # Validate agent config
        if "agent_config" not in runtime_config:
            errors.append("Missing agent_config in Runtime configuration")
        else:
            agent_config = runtime_config["agent_config"]
            if "name" not in agent_config or not agent_config["name"]:
                errors.append("agent_config.name is required")
            if "agent_id" not in agent_config or not agent_config["agent_id"]:
                errors.append("agent_config.agent_id is required")

        # Validate service config
        if "service_config" not in runtime_config:
            errors.append("Missing service_config in Runtime configuration")
        else:
            service_config = runtime_config["service_config"]
            if "port" in service_config:
                port = service_config["port"]
                if not isinstance(port, int) or port < 1 or port > 65535:
                    errors.append("service_config.port must be a valid port (1-65535)")

        # Validate lifecycle config
        if "lifecycle_config" in runtime_config:
            lifecycle_config = runtime_config["lifecycle_config"]
            if "idle_timeout_minutes" in lifecycle_config:
                timeout = lifecycle_config["idle_timeout_minutes"]
                if not isinstance(timeout, (int, float)) or timeout < 0:
                    errors.append("lifecycle_config.idle_timeout_minutes must be positive")

        return (len(errors) == 0, errors)

    def get_runtime_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the mapped Runtime configuration

        Returns:
            Runtime configuration summary
        """
        try:
            runtime_config = self.map_to_runtime_config()

            summary = {
                "agent_name": runtime_config.get("agent_config", {}).get("name", "Unknown"),
                "agent_type": runtime_config.get("agent_config", {}).get("agent_type", "Unknown"),
                "service_host": runtime_config.get("service_config", {}).get("host", "localhost"),
                "service_port": runtime_config.get("service_config", {}).get("port", 8080),
                "auto_start": runtime_config.get("lifecycle_config", {}).get("auto_start", True),
                "health_check_enabled": runtime_config.get("health_check_config", {}).get("enabled", True),
                "streaming_enabled": runtime_config.get("runtime_extensions", {}).get("streaming_enabled", True),
                "sandbox_enabled": runtime_config.get("runtime_extensions", {}).get("sandbox_enabled", False)
            }

            return summary

        except Exception as e:
            self.logger.error(f"Runtime config summary failed: {str(e)}")
            return {}


def map_config_to_runtime(config_path: str) -> Dict[str, Any]:
    """
    Convenience function to map configuration file to Runtime format

    Args:
        config_path: Path to PaaS YAML configuration file

    Returns:
        Runtime configuration dictionary
    """
    try:
        config_loader = ConfigLoader(config_path)
        success, config, errors = config_loader.load()

        if not success:
            logging.error(f"Config loading failed: {errors}")
            return {}

        mapper = RuntimeConfigMapper(config_loader)
        return mapper.map_to_runtime_config()

    except Exception as e:
        logging.error(f"Config to Runtime mapping failed: {str(e)}")
        return {}