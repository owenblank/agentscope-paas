"""
Runtime Manager Module

Manages AgentScope Runtime lifecycle for deployed agents, including creation,
deployment, execution, health monitoring, and cleanup of AgentApp instances.
"""

from typing import Any, Dict, Optional, Union
from pathlib import Path
import threading
import time
import logging
from datetime import datetime, timedelta

# Optional AgentScope Runtime imports with graceful fallback
RUNTIME_AVAILABLE = False
RUNTIME_IMPORT_ERROR = None

try:
    from agentscope.runtime import (
        AgentApp,
        LocalDeployManager,
        Runner,
        ServiceStatusCode
    )
    RUNTIME_AVAILABLE = True
except ImportError as e:
    RUNTIME_IMPORT_ERROR = str(e)
    # Create dummy classes for type hints if Runtime not available
    class AgentApp:
        pass

    class LocalDeployManager:
        pass

    class Runner:
        pass

    class ServiceStatusCode:
        RUNNING = "running"
        STOPPED = "stopped"
        ERROR = "error"

from ..config.loader import ConfigLoader
from ..factory.agent_factory import AgentFactory
from ..utils.logger import get_logger
from ..utils.exceptions import EngineError


class RuntimeManager:
    """
    Runtime Manager class for managing AgentScope Runtime lifecycle.

    Handles creation, deployment, execution, health monitoring, and cleanup
    of AgentApp instances with optional AgentScope Runtime support.
    """

    def __init__(self, config_loader: ConfigLoader):
        """
        Initialize Runtime Manager

        Args:
            config_loader: Configuration loader instance
        """
        self.config_loader = config_loader
        self.logger = get_logger(__name__)

        # Runtime components
        self.agent_app: Optional[AgentApp] = None
        self.deploy_manager: Optional[LocalDeployManager] = None
        self.runner: Optional[Runner] = None

        # Deployment state
        self.deployment_status = "not_deployed"
        self.deployment_url: Optional[str] = None
        self.deployment_port: Optional[int] = None
        self.health_check_interval = 60  # seconds
        self.last_health_check: Optional[datetime] = None
        self.health_status = "unknown"

        # Lifecycle management
        self.auto_start = False
        self.idle_timeout_minutes = 30
        self.last_activity: Optional[datetime] = None

        # Thread safety
        self._lock = threading.Lock()

        # Check Runtime availability
        self._check_runtime_availability()

    def _check_runtime_availability(self) -> None:
        """Check if AgentScope Runtime is available"""
        if RUNTIME_AVAILABLE:
            self.logger.info("AgentScope Runtime is available")
        else:
            self.logger.warning(
                f"AgentScope Runtime is not available: {RUNTIME_IMPORT_ERROR}. "
                "Runtime features will be disabled. "
                "Install with: pip install agentscope-runtime"
            )

    def is_runtime_available(self) -> bool:
        """
        Check if Runtime is available for use

        Returns:
            True if Runtime is available, False otherwise
        """
        return RUNTIME_AVAILABLE

    def create_and_deploy_agent(
        self,
        host: str = "localhost",
        port: int = 8080,
        max_concurrent_requests: int = 10,
        auto_start: bool = True,
        idle_timeout_minutes: int = 30
    ) -> bool:
        """
        Create and deploy an agent as Runtime service

        Args:
            host: Service host address
            port: Service port
            max_concurrent_requests: Maximum concurrent requests
            auto_start: Auto-start the service
            idle_timeout_minutes: Idle timeout before cleanup

        Returns:
            True if deployment successful, False otherwise
        """
        if not self.is_runtime_available():
            self.logger.error("Cannot deploy: AgentScope Runtime is not available")
            return False

        try:
            with self._lock:
                self.logger.info("Creating and deploying agent as Runtime service")

                # Create AgentApp from configuration
                self.agent_app = self._create_agent_app()

                if not self.agent_app:
                    self.logger.error("Failed to create AgentApp")
                    return False

                # Configure deployment
                self.auto_start = auto_start
                self.idle_timeout_minutes = idle_timeout_minutes

                # Deploy using LocalDeployManager
                self.deploy_manager = LocalDeployManager()

                # Deploy the agent service
                deploy_result = self.deploy_manager.deploy(
                    agent_app=self.agent_app,
                    host=host,
                    port=port,
                    max_concurrent_requests=max_concurrent_requests
                )

                if deploy_result:
                    self.deployment_status = "deployed"
                    self.deployment_url = f"http://{host}:{port}"
                    self.deployment_port = port
                    self.last_activity = datetime.now()

                    self.logger.info(
                        f"Agent deployed successfully at {self.deployment_url}"
                    )

                    # Start health monitoring
                    if auto_start:
                        self._start_health_monitoring()

                    return True
                else:
                    self.logger.error("Agent deployment failed")
                    return False

        except Exception as e:
            self.logger.error(f"Deployment exception: {str(e)}")
            self.deployment_status = "error"
            return False

    def _create_agent_app(self) -> Optional[AgentApp]:
        """
        Create AgentApp from configuration

        Returns:
            AgentApp instance or None if creation fails
        """
        try:
            # Get configuration
            metadata = self.config_loader.get_agent_metadata()
            model_config = self.config_loader.get_model_config()
            prompt_config = self.config_loader.get_prompt_config()

            if not metadata or not model_config or not prompt_config:
                self.logger.error("Missing required configuration for AgentApp")
                return None

            agent_name = metadata.get("agent_name", "RuntimeAgent")
            agent_id = metadata.get("agent_id", "runtime_agent")

            # Use existing AgentFactory to create the base agent
            agent_factory = AgentFactory(self.config_loader)
            base_agent = agent_factory.create_agent()

            if not base_agent:
                self.logger.error("Failed to create base agent")
                return None

            # Create AgentApp wrapper
            agent_app = AgentApp(
                name=agent_name,
                agent_id=agent_id,
                agent=base_agent
            )

            self.logger.info(f"AgentApp created: {agent_name}")
            return agent_app

        except Exception as e:
            self.logger.error(f"AgentApp creation failed: {str(e)}")
            return None

    def get_runner(self) -> Optional[Runner]:
        """
        Get Runner instance for Runtime conversation

        Returns:
            Runner instance or None if not available
        """
        if not self.is_runtime_available():
            self.logger.error("Runtime not available")
            return None

        if self.deployment_status != "deployed":
            self.logger.error("Agent not deployed")
            return None

        try:
            with self._lock:
                if not self.runner:
                    # Create runner from deployment
                    self.runner = self.deploy_manager.get_runner(
                        self.deployment_url
                    )

                    if self.runner:
                        self.logger.info("Runner created successfully")
                    else:
                        self.logger.error("Failed to create Runner")

                # Update last activity
                self.last_activity = datetime.now()

                return self.runner

        except Exception as e:
            self.logger.error(f"Failed to get runner: {str(e)}")
            return None

    async def chat_with_runtime(
        self,
        user_input: str,
        stream: bool = False
    ) -> Optional[Union[str, Any]]:
        """
        Chat with deployed Runtime agent

        Args:
            user_input: User input message
            stream: Enable streaming response

        Returns:
            Agent response or None if failed
        """
        runner = self.get_runner()

        if not runner:
            self.logger.error("Cannot chat: Runner not available")
            return

        try:
            # Update last activity
            self.last_activity = datetime.now()

            if stream:
                # Streaming response
                async for chunk in runner.stream_query(user_input):
                    yield chunk
            else:
                # Single response
                response = await runner.query(user_input)
                yield response

        except Exception as e:
            self.logger.error(f"Runtime chat failed: {str(e)}")
            return

    def stop_agent(self, cleanup: bool = True) -> bool:
        """
        Stop and cleanup the deployed agent

        Args:
            cleanup: Perform full cleanup including resource release

        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            with self._lock:
                self.logger.info("Stopping Runtime agent")

                if self.deploy_manager:
                    # Stop deployment
                    stop_result = self.deploy_manager.stop(self.agent_app)

                    if stop_result:
                        self.deployment_status = "stopped"
                        self.logger.info("Agent stopped successfully")
                    else:
                        self.logger.warning("Agent stop reported failure")

                if cleanup:
                    self._cleanup_resources()

                return True

        except Exception as e:
            self.logger.error(f"Stop agent failed: {str(e)}")
            return False

    def _cleanup_resources(self) -> None:
        """Cleanup Runtime resources"""
        try:
            # Clear runner
            if self.runner:
                self.runner = None

            # Clear deployment manager
            if self.deploy_manager:
                self.deploy_manager = None

            # Clear agent app
            if self.agent_app:
                self.agent_app = None

            # Reset deployment state
            self.deployment_url = None
            self.deployment_port = None
            self.health_status = "unknown"

            self.logger.info("Runtime resources cleaned up")

        except Exception as e:
            self.logger.error(f"Resource cleanup failed: {str(e)}")

    def _start_health_monitoring(self) -> None:
        """Start background health monitoring"""
        def health_monitor():
            while self.deployment_status == "deployed":
                try:
                    self.check_health()
                    time.sleep(self.health_check_interval)
                except Exception as e:
                    self.logger.error(f"Health monitoring error: {str(e)}")
                    break

        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=health_monitor,
            daemon=True,
            name="RuntimeHealthMonitor"
        )
        monitor_thread.start()

    def check_health(self) -> Dict[str, Any]:
        """
        Check health status of deployed agent

        Returns:
            Health status dictionary
        """
        health_info = {
            "status": self.health_status,
            "deployment_status": self.deployment_status,
            "last_check": datetime.now().isoformat(),
            "deployment_url": self.deployment_url,
            "uptime_minutes": None,
            "idle_minutes": None
        }

        if not self.is_runtime_available():
            health_info["status"] = "runtime_unavailable"
            return health_info

        if self.deployment_status != "deployed":
            health_info["status"] = "not_deployed"
            return health_info

        try:
            # Check deployment health via deploy manager
            if self.deploy_manager and self.agent_app:
                service_status = self.deploy_manager.get_status(self.agent_app)

                if service_status == ServiceStatusCode.RUNNING:
                    health_info["status"] = "healthy"
                    self.health_status = "healthy"
                elif service_status == ServiceStatusCode.ERROR:
                    health_info["status"] = "error"
                    self.health_status = "error"
                else:
                    health_info["status"] = "stopped"
                    self.health_status = "stopped"

                # Calculate uptime and idle time
                if self.last_activity:
                    idle_minutes = (datetime.now() - self.last_activity).total_seconds() / 60
                    health_info["idle_minutes"] = round(idle_minutes, 2)

                health_info["uptime_minutes"] = round(
                    (datetime.now() - self.last_activity.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 60, 2
                ) if self.last_activity else 0

            self.last_health_check = datetime.now()

        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            health_info["status"] = "health_check_failed"
            health_info["error"] = str(e)

        return health_info

    def get_deployment_info(self) -> Dict[str, Any]:
        """
        Get deployment information

        Returns:
            Deployment information dictionary
        """
        return {
            "deployment_status": self.deployment_status,
            "deployment_url": self.deployment_url,
            "deployment_port": self.deployment_port,
            "health_status": self.health_status,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "auto_start": self.auto_start,
            "idle_timeout_minutes": self.idle_timeout_minutes,
            "runtime_available": self.is_runtime_available(),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }

    def restart_agent(self) -> bool:
        """
        Restart the deployed agent

        Returns:
            True if restart successful, False otherwise
        """
        try:
            self.logger.info("Restarting Runtime agent")

            # Get deployment parameters
            deployment_info = self.get_deployment_info()

            # Stop current deployment
            if self.deployment_status == "deployed":
                self.stop_agent(cleanup=False)

            # Redeploy with same parameters
            return self.create_and_deploy_agent(
                host=deployment_info.get("deployment_url", "localhost:8080").split(":")[0] if deployment_info.get("deployment_url") else "localhost",
                port=deployment_info.get("deployment_port", 8080),
                auto_start=deployment_info.get("auto_start", True),
                idle_timeout_minutes=deployment_info.get("idle_timeout_minutes", 30)
            )

        except Exception as e:
            self.logger.error(f"Agent restart failed: {str(e)}")
            return False

    def check_idle_timeout(self) -> bool:
        """
        Check if agent has exceeded idle timeout

        Returns:
            True if idle timeout exceeded, False otherwise
        """
        if not self.last_activity:
            return False

        idle_minutes = (datetime.now() - self.last_activity).total_seconds() / 60
        return idle_minutes > self.idle_timeout_minutes


# Singleton instance management
_runtime_managers: Dict[str, RuntimeManager] = {}
_runtime_managers_lock = threading.Lock()


def get_runtime_manager(config_loader: ConfigLoader) -> RuntimeManager:
    """
    Get or create RuntimeManager singleton for configuration

    Args:
        config_loader: Configuration loader instance

    Returns:
        RuntimeManager instance
    """
    config_path = str(config_loader.config_path)

    with _runtime_managers_lock:
        if config_path not in _runtime_managers:
            _runtime_managers[config_path] = RuntimeManager(config_loader)

        return _runtime_managers[config_path]


def cleanup_all_runtime_managers() -> None:
    """Cleanup all RuntimeManager instances"""
    with _runtime_managers_lock:
        for manager in _runtime_managers.values():
            try:
                manager.stop_agent(cleanup=True)
            except Exception as e:
                logging.error(f"RuntimeManager cleanup failed: {str(e)}")

        _runtime_managers.clear()