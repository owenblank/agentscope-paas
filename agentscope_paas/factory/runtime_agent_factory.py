"""
Runtime Agent Factory Module

Factory for creating AgentScope Runtime AgentApps from PaaS configurations.
Wraps the existing AgentFactory and adds Runtime-specific deployment capabilities.
"""

from typing import Any, Dict, Optional, Union
import logging

# Optional AgentScope Runtime imports
RUNTIME_AVAILABLE = False
RUNTIME_IMPORT_ERROR = None

try:
    from agentscope.runtime import AgentApp, LocalDeployManager
    from agentscope.agent import AgentBase
    RUNTIME_AVAILABLE = True
except ImportError as e:
    RUNTIME_IMPORT_ERROR = str(e)
    # Create dummy classes for type hints
    class AgentApp:
        pass

    class LocalDeployManager:
        pass

    class AgentBase:
        pass

from ..config.loader import ConfigLoader
from ..factory.agent_factory import AgentFactory
from ..config.runtime_mapper import RuntimeConfigMapper
from ..utils.logger import get_logger
from ..utils.exceptions import AgentCreationError


class RuntimeAgentFactory:
    """
    Runtime Agent Factory for creating AgentApp instances.

    Wraps the existing AgentFactory and adds Runtime-specific configuration
    mapping and AgentApp creation capabilities.
    """

    def __init__(self, config_loader: ConfigLoader):
        """
        Initialize Runtime Agent Factory

        Args:
            config_loader: Configuration loader instance
        """
        self.config_loader = config_loader
        self.logger = get_logger(__name__)

        # Initialize base agent factory
        self.agent_factory = AgentFactory(config_loader)

        # Runtime configuration mapper
        self.config_mapper = RuntimeConfigMapper(config_loader)

        # Runtime availability check
        self.runtime_available = RUNTIME_AVAILABLE
        if not self.runtime_available:
            self.logger.warning(
                f"AgentScope Runtime not available: {RUNTIME_IMPORT_ERROR}. "
                "Runtime features will be disabled."
            )

    def is_runtime_available(self) -> bool:
        """
        Check if Runtime is available

        Returns:
            True if Runtime available, False otherwise
        """
        return self.runtime_available

    def create_agent_app(
        self,
        user_id: str = "default_user",
        session_id: str = "default_session",
        runtime_config: Optional[Dict[str, Any]] = None
    ) -> Optional[AgentApp]:
        """
        Create AgentApp from PaaS configuration

        Args:
            user_id: User ID for session management
            session_id: Session ID for conversation tracking
            runtime_config: Optional Runtime-specific configuration

        Returns:
            AgentApp instance or None if creation fails
        """
        if not self.is_runtime_available():
            self.logger.error("Cannot create AgentApp: Runtime not available")
            return None

        try:
            self.logger.info("Creating AgentApp from PaaS configuration")

            # Create base agent using existing factory
            base_agent = self.agent_factory.create_agent(user_id, session_id)

            if not base_agent:
                self.logger.error("Failed to create base agent")
                return None

            # Get agent metadata
            metadata = self.config_loader.get_agent_metadata()
            agent_name = metadata.get("agent_name", "RuntimeAgent")
            agent_id = metadata.get("agent_id", "runtime_agent")

            # Prepare Runtime configuration
            runtime_config_dict = self._prepare_runtime_config(
                runtime_config, user_id, session_id
            )

            # Create AgentApp
            agent_app = AgentApp(
                name=agent_name,
                agent_id=agent_id,
                agent=base_agent,
                **runtime_config_dict
            )

            self.logger.info(f"AgentApp created successfully: {agent_name}")
            return agent_app

        except Exception as e:
            self.logger.error(f"AgentApp creation failed: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def _prepare_runtime_config(
        self,
        runtime_config: Optional[Dict[str, Any]],
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Prepare Runtime-specific configuration

        Args:
            runtime_config: Optional Runtime configuration from user
            user_id: User ID
            session_id: Session ID

        Returns:
            Runtime configuration dictionary
        """
        try:
            # Start with mapped configuration from PaaS config
            base_runtime_config = self.config_mapper.map_to_runtime_config()

            # Merge with user-provided Runtime config
            if runtime_config:
                base_runtime_config.update(runtime_config)

            # Add session context
            base_runtime_config.update({
                "user_id": user_id,
                "session_id": session_id,
                "creation_time": logging.LogRecord(
                    name="", level=0, pathname="", lineno=0, msg="", args=None, exc_info=None
                ).created if hasattr(logging.LogRecord, 'created') else None
            })

            return base_runtime_config

        except Exception as e:
            self.logger.error(f"Runtime config preparation failed: {str(e)}")
            # Return minimal config
            return {
                "user_id": user_id,
                "session_id": session_id
            }

    def create_agent_with_runtime_tools(
        self,
        tools: list,
        user_id: str = "default_user",
        session_id: str = "default_session"
    ) -> Optional[AgentApp]:
        """
        Create AgentApp with tool support

        Args:
            tools: List of tools to register
            user_id: User ID
            session_id: Session ID

        Returns:
            AgentApp with tools or None if creation fails
        """
        if not self.is_runtime_available():
            self.logger.error("Cannot create AgentApp with tools: Runtime not available")
            return None

        try:
            self.logger.info("Creating AgentApp with tools")

            # Create base agent with tools
            base_agent = self.agent_factory.create_agent_with_tools(tools)

            if not base_agent:
                self.logger.error("Failed to create base agent with tools")
                return None

            # Get metadata
            metadata = self.config_loader.get_agent_metadata()
            agent_name = metadata.get("agent_name", "RuntimeAgentWithTools")
            agent_id = metadata.get("agent_id", "runtime_agent_with_tools")

            # Create AgentApp
            agent_app = AgentApp(
                name=agent_name,
                agent_id=agent_id,
                agent=base_agent
            )

            self.logger.info(f"AgentApp with tools created: {agent_name}")
            return agent_app

        except Exception as e:
            self.logger.error(f"AgentApp with tools creation failed: {str(e)}")
            return None

    def create_deployment_config(
        self,
        host: str = "localhost",
        port: int = 8080,
        max_concurrent_requests: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create deployment configuration for LocalDeployManager

        Args:
            host: Service host
            port: Service port
            max_concurrent_requests: Maximum concurrent requests
            **kwargs: Additional deployment parameters

        Returns:
            Deployment configuration dictionary
        """
        deployment_config = {
            "host": host,
            "port": port,
            "max_concurrent_requests": max_concurrent_requests
        }

        # Add additional parameters
        deployment_config.update(kwargs)

        # Add Runtime-specific defaults
        deployment_config.setdefault("startup_timeout", 300)  # 5 minutes
        deployment_config.setdefault("health_check_interval", 60)  # 1 minute
        deployment_config.setdefault("shutdown_timeout", 60)  # 1 minute

        return deployment_config

    def validate_runtime_config(self, config: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate Runtime configuration

        Args:
            config: Runtime configuration to validate

        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []

        # Check required Runtime fields
        if "service_config" in config:
            service_config = config["service_config"]

            if "host" in service_config and not isinstance(service_config["host"], str):
                errors.append("service_config.host must be a string")

            if "port" in service_config:
                port = service_config["port"]
                if not isinstance(port, int) or port < 1 or port > 65535:
                    errors.append("service_config.port must be a valid port number (1-65535)")

            if "max_concurrent_requests" in service_config:
                max_req = service_config["max_concurrent_requests"]
                if not isinstance(max_req, int) or max_req < 1:
                    errors.append("service_config.max_concurrent_requests must be a positive integer")

        # Validate lifecycle configuration
        if "lifecycle_config" in config:
            lifecycle_config = config["lifecycle_config"]

            if "idle_timeout_minutes" in lifecycle_config:
                timeout = lifecycle_config["idle_timeout_minutes"]
                if not isinstance(timeout, (int, float)) or timeout < 0:
                    errors.append("lifecycle_config.idle_timeout_minutes must be a positive number")

            if "auto_start" in lifecycle_config:
                auto_start = lifecycle_config["auto_start"]
                if not isinstance(auto_start, bool):
                    errors.append("lifecycle_config.auto_start must be a boolean")

        # Validate health check configuration
        if "health_check_config" in config:
            health_config = config["health_check_config"]

            if "interval_seconds" in health_config:
                interval = health_config["interval_seconds"]
                if not isinstance(interval, (int, float)) or interval < 0:
                    errors.append("health_check_config.interval_seconds must be a positive number")

            if "enabled" in health_config:
                enabled = health_config["enabled"]
                if not isinstance(enabled, bool):
                    errors.append("health_check_config.enabled must be a boolean")

        return (len(errors) == 0, errors)

    def get_runtime_requirements(self) -> Dict[str, Any]:
        """
        Get Runtime requirements and dependencies

        Returns:
            Runtime requirements dictionary
        """
        return {
            "runtime_available": self.runtime_available,
            "runtime_import_error": RUNTIME_IMPORT_ERROR,
            "install_command": "pip install agentscope-runtime",
            "version": ">=1.0.0",
            "optional_features": {
                "streaming": True,
                "health_checks": True,
                "lifecycle_management": True,
                "sandbox_support": True
            }
        }


def create_agent_app_from_config(
    config_path: str,
    user_id: str = "default_user",
    session_id: str = "default_session"
) -> Optional[AgentApp]:
    """
    Convenience function to create AgentApp from config file

    Args:
        config_path: Path to YAML configuration file
        user_id: User ID
        session_id: Session ID

    Returns:
        AgentApp instance or None if creation fails
    """
    try:
        config_loader = ConfigLoader(config_path)
        success, config, errors = config_loader.load()

        if not success:
            logging.error(f"Config loading failed: {errors}")
            return None

        factory = RuntimeAgentFactory(config_loader)
        return factory.create_agent_app(user_id, session_id)

    except Exception as e:
        logging.error(f"AgentApp creation from config failed: {str(e)}")
        return None