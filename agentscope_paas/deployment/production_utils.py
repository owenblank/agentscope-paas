"""
Production Deployment Utilities Module

Provides production deployment utilities including configuration templates,
deployment validators, health check systems, and backup/restore functionality.
"""

import os
import yaml
import json
import shutil
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import threading

from ..utils.logger import get_logger


class DeploymentEnvironment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class DeploymentStatus(Enum):
    """Deployment status types"""
    PENDING = "pending"
    VALIDATING = "validating"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentConfig:
    """Production deployment configuration"""
    environment: DeploymentEnvironment
    runtime_enabled: bool = True
    monitoring_enabled: bool = True
    health_checks_enabled: bool = True
    auto_scaling_enabled: bool = False

    # Resource limits
    max_memory_mb: int = 2048
    max_cpu_percent: float = 80.0
    max_instances: int = 5
    min_instances: int = 1

    # Performance settings
    cache_enabled: bool = True
    connection_pool_size: int = 20
    request_timeout: int = 120
    graceful_shutdown_timeout: int = 60

    # Security settings
    enable_sandbox: bool = True
    sandbox_type: str = "docker"
    allowed_hosts: List[str] = field(default_factory=list)
    api_key_required: bool = True

    # Backup settings
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    backup_retention_days: int = 7

    # Monitoring settings
    metrics_enabled: bool = True
    log_level: str = "INFO"
    alert_on_errors: bool = True


class DeploymentValidator:
    """
    Deployment configuration and environment validator

    Validates deployment configurations and environments before deployment.
    """

    def __init__(self):
        """Initialize deployment validator"""
        self.logger = get_logger(__name__)
        self._validation_rules: List[Callable] = []

    def add_validation_rule(self, rule: Callable) -> None:
        """Add a custom validation rule"""
        self._validation_rules.append(rule)

    def validate_deployment(
        self,
        config: DeploymentConfig,
        environment: DeploymentEnvironment
    ) -> Tuple[bool, List[str]]:
        """
        Validate deployment configuration and environment

        Args:
            config: Deployment configuration
            environment: Target environment

        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []

        # Environment-specific validation
        if environment == DeploymentEnvironment.PRODUCTION:
            errors.extend(self._validate_production(config))

        # Resource validation
        errors.extend(self._validate_resources(config))

        # Security validation
        errors.extend(self._validate_security(config))

        # Runtime availability
        errors.extend(self._validate_runtime_availability(config))

        # Custom validation rules
        for rule in self._validation_rules:
            try:
                rule_errors = rule(config, environment)
                errors.extend(rule_errors)
            except Exception as e:
                self.logger.error(f"Validation rule error: {str(e)}")

        return (len(errors) == 0, errors)

    def _validate_production(self, config: DeploymentConfig) -> List[str]:
        """Validate production-specific requirements"""
        errors = []

        if not config.monitoring_enabled:
            errors.append("Monitoring must be enabled in production")

        if not config.health_checks_enabled:
            errors.append("Health checks must be enabled in production")

        if not config.backup_enabled:
            errors.append("Backups must be enabled in production")

        if config.max_instances < 2:
            errors.append("Production should have at least 2 instances for high availability")

        if config.api_key_required is False:
            errors.append("API key authentication should be required in production")

        return errors

    def _validate_resources(self, config: DeploymentConfig) -> List[str]:
        """Validate resource configuration"""
        errors = []

        if config.max_memory_mb < 512:
            errors.append("Max memory must be at least 512MB")

        if config.max_memory_mb > 16384:
            errors.append("Max memory cannot exceed 16GB")

        if config.max_cpu_percent < 10 or config.max_cpu_percent > 100:
            errors.append("Max CPU percent must be between 10 and 100")

        if config.min_instances < 1:
            errors.append("Min instances must be at least 1")

        if config.max_instances < config.min_instances:
            errors.append("Max instances must be >= min instances")

        if config.max_instances > 20:
            errors.append("Max instances cannot exceed 20")

        return errors

    def _validate_security(self, config: DeploymentConfig) -> List[str]:
        """Validate security configuration"""
        errors = []

        if config.enable_sandbox and config.sandbox_type not in ["docker", "process", "thread"]:
            errors.append(f"Invalid sandbox type: {config.sandbox_type}")

        if config.api_key_required and not config.allowed_hosts:
            errors.append("Allowed hosts must be specified when API key is required")

        return errors

    def _validate_runtime_availability(self, config: DeploymentConfig) -> List[str]:
        """Validate Runtime availability if enabled"""
        errors = []

        if config.runtime_enabled:
            try:
                from agentscope_paas.utils.runtime_validator import check_runtime_availability
                if not check_runtime_availability():
                    errors.append("AgentScope Runtime is enabled but not available")
            except ImportError:
                errors.append("Runtime validation failed: runtime_validator not available")

        return errors


class DeploymentTemplateManager:
    """
    Deployment template manager

    Provides pre-configured templates for different deployment scenarios.
    """

    def __init__(self):
        """Initialize template manager"""
        self.logger = get_logger(__name__)
        self._templates: Dict[str, DeploymentConfig] = {}
        self._load_default_templates()

    def _load_default_templates(self) -> None:
        """Load default deployment templates"""
        self._templates = {
            "development": DeploymentConfig(
                environment=DeploymentEnvironment.DEVELOPMENT,
                runtime_enabled=False,
                monitoring_enabled=True,
                health_checks_enabled=True,
                auto_scaling_enabled=False,
                max_memory_mb=1024,
                max_cpu_percent=80.0,
                max_instances=1,
                min_instances=1,
                cache_enabled=True,
                connection_pool_size=10,
                api_key_required=False,
                backup_enabled=False,
                metrics_enabled=True,
                log_level="DEBUG"
            ),
            "staging": DeploymentConfig(
                environment=DeploymentEnvironment.STAGING,
                runtime_enabled=True,
                monitoring_enabled=True,
                health_checks_enabled=True,
                auto_scaling_enabled=False,
                max_memory_mb=1536,
                max_cpu_percent=70.0,
                max_instances=3,
                min_instances=1,
                cache_enabled=True,
                connection_pool_size=15,
                api_key_required=True,
                backup_enabled=True,
                backup_interval_hours=12,
                backup_retention_days=3,
                metrics_enabled=True,
                log_level="INFO"
            ),
            "production": DeploymentConfig(
                environment=DeploymentEnvironment.PRODUCTION,
                runtime_enabled=True,
                monitoring_enabled=True,
                health_checks_enabled=True,
                auto_scaling_enabled=True,
                max_memory_mb=2048,
                max_cpu_percent=80.0,
                max_instances=10,
                min_instances=2,
                cache_enabled=True,
                connection_pool_size=20,
                graceful_shutdown_timeout=60,
                enable_sandbox=True,
                sandbox_type="docker",
                api_key_required=True,
                backup_enabled=True,
                backup_interval_hours=24,
                backup_retention_days=7,
                metrics_enabled=True,
                log_level="INFO",
                alert_on_errors=True
            ),
            "high_performance": DeploymentConfig(
                environment=DeploymentEnvironment.PRODUCTION,
                runtime_enabled=True,
                monitoring_enabled=True,
                health_checks_enabled=True,
                auto_scaling_enabled=True,
                max_memory_mb=4096,
                max_cpu_percent=90.0,
                max_instances=15,
                min_instances=3,
                cache_enabled=True,
                connection_pool_size=30,
                request_timeout=180,
                graceful_shutdown_timeout=90,
                enable_sandbox=True,
                sandbox_type="docker",
                api_key_required=True,
                backup_enabled=True,
                backup_interval_hours=12,
                backup_retention_days=14,
                metrics_enabled=True,
                log_level="WARNING",
                alert_on_errors=True
            )
        }

    def get_template(self, name: str) -> Optional[DeploymentConfig]:
        """Get deployment template by name"""
        return self._templates.get(name)

    def list_templates(self) -> List[str]:
        """List available template names"""
        return list(self._templates.keys())

    def save_template(self, name: str, config: DeploymentConfig) -> None:
        """Save a custom template"""
        self._templates[name] = config
        self.logger.info(f"Saved custom template: {name}")

    def delete_template(self, name: str) -> bool:
        """Delete a custom template"""
        if name in self._templates:
            del self._templates[name]
            self.logger.info(f"Deleted template: {name}")
            return True
        return False


class HealthCheckSystem:
    """
    Comprehensive health check system

    Provides health monitoring, dependency checking, and
    automated health status reporting.
    """

    def __init__(self, check_interval: int = 30):
        """
        Initialize health check system

        Args:
            check_interval: Seconds between health checks
        """
        self.check_interval = check_interval
        self.logger = get_logger(__name__)

        # Health status tracking
        self._health_status: Dict[str, bool] = {}
        self._last_check: Dict[str, datetime] = {}
        self._check_history: List[Dict[str, Any]] = []

        # Background checking
        self._check_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()

        # Health check functions
        self._health_checks: Dict[str, Callable] = {}

        # Setup default health checks
        self._setup_default_checks()

    def _setup_default_checks(self) -> None:
        """Setup default health check functions"""
        self._health_checks = {
            "runtime_available": self._check_runtime_available,
            "memory_usage": self._check_memory_usage,
            "cpu_usage": self._check_cpu_usage,
            "disk_space": self._check_disk_space,
            "dependencies": self._check_dependencies
        }

    def register_health_check(self, name: str, check_func: Callable) -> None:
        """Register a custom health check"""
        self._health_checks[name] = check_func
        self.logger.info(f"Registered health check: {name}")

    async def check_health(self, checks: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform health checks

        Args:
            checks: List of specific checks to perform (None = all)

        Returns:
            Health status dictionary
        """
        if checks is None:
            checks = list(self._health_checks.keys())

        results = {}
        overall_healthy = True

        for check_name in checks:
            if check_name not in self._health_checks:
                continue

            try:
                check_func = self._health_checks[check_name]
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()

                results[check_name] = {
                    "healthy": result,
                    "timestamp": datetime.now().isoformat()
                }

                with self._lock:
                    self._health_status[check_name] = result
                    self._last_check[check_name] = datetime.now()

                if not result:
                    overall_healthy = False

            except Exception as e:
                self.logger.error(f"Health check {check_name} failed: {str(e)}")
                results[check_name] = {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                overall_healthy = False

        # Add overall status
        results["overall"] = {
            "healthy": overall_healthy,
            "timestamp": datetime.now().isoformat(),
            "checks_performed": len(checks)
        }

        # Store check history
        with self._lock:
            self._check_history.append({
                "timestamp": datetime.now().isoformat(),
                "overall_healthy": overall_healthy,
                "results": results
            })

            # Keep last 100 checks
            if len(self._check_history) > 100:
                self._check_history.pop(0)

        return results

    def _check_runtime_available(self) -> bool:
        """Check if AgentScope Runtime is available"""
        try:
            from agentscope_paas.utils.runtime_validator import check_runtime_availability
            return check_runtime_availability()
        except ImportError:
            return False

    def _check_memory_usage(self) -> bool:
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.percent < 90
        except Exception:
            return True

    def _check_cpu_usage(self) -> bool:
        """Check CPU usage"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            return cpu_percent < 85
        except Exception:
            return True

    def _check_disk_space(self) -> bool:
        """Check disk space"""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return disk.percent < 90
        except Exception:
            return True

    def _check_dependencies(self) -> bool:
        """Check critical dependencies"""
        try:
            import agentscope
            return True
        except ImportError:
            return False

    def start_monitoring(self) -> None:
        """Start background health monitoring"""
        if self._running:
            return

        self._running = True
        self._check_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="HealthMonitor"
        )
        self._check_thread.start()
        self.logger.info("Health monitoring started")

    def stop_monitoring(self) -> None:
        """Stop background health monitoring"""
        if not self._running:
            return

        self._running = False
        if self._check_thread:
            self._check_thread.join(timeout=5)

        self.logger.info("Health monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while self._running:
            try:
                asyncio.run(self.check_health())
            except Exception as e:
                self.logger.error(f"Health monitoring error: {str(e)}")

            # Sleep for check interval
            for _ in range(self.check_interval):
                if not self._running:
                    break
                time.sleep(1)

    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of health status"""
        with self._lock:
            return {
                "health_status": dict(self._health_status),
                "last_checks": {
                    k: v.isoformat() if v else None
                    for k, v in self._last_check.items()
                },
                "check_count": len(self._check_history),
                "monitoring_active": self._running
            }


class BackupManager:
    """
    Backup and restore manager for Runtime deployments

    Provides automated backup, restore, and rollback capabilities.
    """

    def __init__(self, backup_dir: str = "backups"):
        """
        Initialize backup manager

        Args:
            backup_dir: Directory for backup storage
        """
        self.backup_dir = Path(backup_dir)
        self.logger = get_logger(__name__)

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup tracking
        self._backup_registry: Dict[str, List[Dict]] = {}

    def create_backup(
        self,
        agent_id: str,
        config_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create backup of agent configuration and data

        Args:
            agent_id: Agent identifier
            config_path: Path to agent configuration
            metadata: Optional metadata for the backup

        Returns:
            Backup ID or None if backup failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"{agent_id}_{timestamp}"
            backup_path = self.backup_dir / backup_id

            self.logger.info(f"Creating backup: {backup_id}")

            # Create backup directory
            backup_path.mkdir(parents=True, exist_ok=True)

            # Backup configuration file
            config_file = Path(config_path)
            if config_file.exists():
                shutil.copy2(config_file, backup_path / "config.yaml")

            # Backup metadata
            backup_metadata = {
                "backup_id": backup_id,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "config_path": config_path,
                "metadata": metadata or {}
            }

            metadata_file = backup_path / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(backup_metadata, f, indent=2)

            # Register backup
            if agent_id not in self._backup_registry:
                self._backup_registry[agent_id] = []

            self._backup_registry[agent_id].append({
                "backup_id": backup_id,
                "timestamp": datetime.now(),
                "path": str(backup_path)
            })

            self.logger.info(f"Backup created successfully: {backup_id}")
            return backup_id

        except Exception as e:
            self.logger.error(f"Backup creation failed: {str(e)}")
            return None

    def restore_backup(
        self,
        backup_id: str,
        restore_path: str
    ) -> bool:
        """
        Restore agent from backup

        Args:
            backup_id: Backup identifier
            restore_path: Path to restore configuration

        Returns:
            True if restore successful
        """
        try:
            backup_path = self.backup_dir / backup_id

            if not backup_path.exists():
                self.logger.error(f"Backup not found: {backup_id}")
                return False

            self.logger.info(f"Restoring backup: {backup_id}")

            # Restore configuration
            config_backup = backup_path / "config.yaml"
            if config_backup.exists():
                shutil.copy2(config_backup, restore_path)

            self.logger.info(f"Backup restored successfully: {backup_id}")
            return True

        except Exception as e:
            self.logger.error(f"Backup restore failed: {str(e)}")
            return False

    def list_backups(self, agent_id: str) -> List[Dict[str, Any]]:
        """List available backups for an agent"""
        if agent_id not in self._backup_registry:
            return []

        return [
            {
                "backup_id": backup["backup_id"],
                "timestamp": backup["timestamp"].isoformat(),
                "path": backup["path"]
            }
            for backup in self._backup_registry[agent_id]
        ]

    def cleanup_old_backups(self, agent_id: str, retention_days: int = 7) -> int:
        """
        Clean up old backups beyond retention period

        Args:
            agent_id: Agent identifier
            retention_days: Days to retain backups

        Returns:
            Number of backups cleaned up
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cleaned_count = 0

            if agent_id not in self._backup_registry:
                return 0

            # Filter backups to keep
            self._backup_registry[agent_id] = [
                backup for backup in self._backup_registry[agent_id]
                if backup["timestamp"] >= cutoff_date
            ]

            # Calculate removed count
            original_count = len(self._backup_registry[agent_id])
            cleaned_count = original_count - len(self._backup_registry[agent_id])

            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old backups for {agent_id}")

            return cleaned_count

        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {str(e)}")
            return 0


def create_deployment_validator() -> DeploymentValidator:
    """Create deployment validator with default rules"""
    return DeploymentValidator()


def create_template_manager() -> DeploymentTemplateManager:
    """Create deployment template manager"""
    return DeploymentTemplateManager()


def create_health_check_system(check_interval: int = 30) -> HealthCheckSystem:
    """Create health check system"""
    return HealthCheckSystem(check_interval)


def create_backup_manager(backup_dir: str = "backups") -> BackupManager:
    """Create backup manager"""
    return BackupManager(backup_dir)