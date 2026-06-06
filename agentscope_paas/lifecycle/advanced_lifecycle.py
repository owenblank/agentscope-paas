"""
Advanced Lifecycle Management Module

Provides advanced lifecycle management features including auto-scaling,
load balancing, graceful shutdown, and resource management for Runtime agents.
"""

import asyncio
import threading
import time
import logging
import signal
import sys
from typing import Any, Dict, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import psutil

from ..utils.logger import get_logger


class LifecycleState(Enum):
    """Agent lifecycle states"""
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    SCALING = "scaling"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"


class ScalingDirection(Enum):
    """Auto-scaling directions"""
    UP = "up"
    DOWN = "down"
    NONE = "none"


@dataclass
class ScalingEvent:
    """Auto-scaling event information"""
    timestamp: datetime
    direction: ScalingDirection
    from_instances: int
    to_instances: int
    reason: str
    trigger_metric: str
    trigger_value: float
    threshold: float


@dataclass
class LifecycleConfig:
    """Lifecycle management configuration"""
    # Auto-scaling
    enable_auto_scaling: bool = True
    min_instances: int = 1
    max_instances: int = 10
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 20.0
    scale_up_cooldown_seconds: int = 300
    scale_down_cooldown_seconds: int = 600
    scaling_metric: str = "cpu_percent"

    # Load balancing
    enable_load_balancing: bool = True
    load_balancing_strategy: str = "round_robin"  # round_robin, least_connections, weighted
    health_check_interval: int = 30
    max_failures: int = 3

    # Resource management
    memory_limit_mb: int = 2048
    cpu_limit_percent: float = 80.0
    graceful_shutdown_timeout: int = 60
    force_shutdown_timeout: int = 120

    # Monitoring
    enable_monitoring: bool = True
    metrics_collection_interval: int = 60


class AdvancedLifecycleManager:
    """
    Advanced lifecycle management for Runtime agents

    Provides auto-scaling, load balancing, graceful shutdown,
    and resource management capabilities.
    """

    def __init__(self, config: LifecycleConfig):
        """
        Initialize advanced lifecycle manager

        Args:
            config: Lifecycle configuration
        """
        self.config = config
        self.logger = get_logger(__name__)

        # State management
        self._state = LifecycleState.CREATED
        self._instances: Dict[str, Any] = {}
        self._instance_health: Dict[str, bool] = {}
        self._instance_load: Dict[str, float] = {}

        # Scaling management
        self._scaling_events: List[ScalingEvent] = []
        self._last_scale_time: Dict[ScalingDirection, datetime] = defaultdict(
            lambda: datetime.min
        )

        # Load balancing
        self._current_instance_index = 0
        self._request_counts: Dict[str, int] = defaultdict(int)

        # Shutdown management
        self._shutdown_hooks: List[Callable] = []
        self._shutdown initiated = False
        self._graceful_shutdown_complete = False

        # Monitoring
        self._metrics_collector = None
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_running = False

        # Signal handling
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        if sys.platform == "linux":
            signal.signal(signal.SIGUSR1, self._signal_handler)

    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.initiate_graceful_shutdown()

    def start_instance(self, instance_id: str, creator: Callable[[], Any]) -> bool:
        """Start a new agent instance"""
        try:
            if instance_id in self._instances:
                self.logger.warning(f"Instance {instance_id} already exists")
                return False

            self.logger.info(f"Starting instance {instance_id}")

            # Create instance
            instance = creator()
            self._instances[instance_id] = instance

            # Initialize health tracking
            self._instance_health[instance_id] = True
            self._instance_load[instance_id] = 0.0

            # Update state
            if self._state == LifecycleState.CREATED:
                self._state = LifecycleState.RUNNING

            self.logger.info(f"Instance {instance_id} started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start instance {instance_id}: {str(e)}")
            self._instance_health[instance_id] = False
            return False

    def stop_instance(self, instance_id: str, graceful: bool = True) -> bool:
        """Stop an agent instance"""
        try:
            if instance_id not in self._instances:
                self.logger.warning(f"Instance {instance_id} not found")
                return False

            self.logger.info(f"Stopping instance {instance_id}")

            if graceful:
                # Perform graceful shutdown
                self._perform_graceful_shutdown(instance_id)
            else:
                # Force shutdown
                self._perform_force_shutdown(instance_id)

            # Remove from tracking
            del self._instances[instance_id]
            del self._instance_health[instance_id]
            del self._instance_load[instance_id]

            self.logger.info(f"Instance {instance_id} stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop instance {instance_id}: {str(e)}")
            return False

    def _perform_graceful_shutdown(self, instance_id: str) -> None:
        """Perform graceful shutdown for an instance"""
        instance = self._instances[instance_id]

        try:
            # Call shutdown hooks
            for hook in self._shutdown_hooks:
                try:
                    hook(instance_id, instance)
                except Exception as e:
                    self.logger.error(f"Shutdown hook error: {str(e)}")

            # Wait for graceful shutdown timeout
            timeout = self.config.graceful_shutdown_timeout
            start_time = time.time()

            while time.time() - start_time < timeout:
                if self._is_instance_quiet(instance_id):
                    break
                time.sleep(1)

        except Exception as e:
            self.logger.error(f"Graceful shutdown error: {str(e)}")

    def _perform_force_shutdown(self, instance_id: str) -> None:
        """Perform force shutdown for an instance"""
        instance = self._instances[instance_id]

        try:
            # Terminate the instance
            if hasattr(instance, 'terminate'):
                instance.terminate()
            elif hasattr(instance, 'close'):
                instance.close()
            else:
                self.logger.warning(f"Instance {instance_id} has no shutdown method")

        except Exception as e:
            self.logger.error(f"Force shutdown error: {str(e)}")

    def _is_instance_quiet(self, instance_id: str) -> bool:
        """Check if instance is quiet (no active requests)"""
        load = self._instance_load.get(instance_id, 0.0)
        return load < 0.1  # Less than 10% load

    def scale_instances(self, target_count: int, creator: Callable[[], Any]) -> bool:
        """Scale instances to target count"""
        try:
            current_count = len(self._instances)

            if target_count == current_count:
                return True

            if target_count < self.config.min_instances:
                target_count = self.config.min_instances
            if target_count > self.config.max_instances:
                target_count = self.config.max_instances

            self.logger.info(f"Scaling from {current_count} to {target_count} instances")

            if target_count > current_count:
                # Scale up
                return self._scale_up(target_count - current_count, creator)
            else:
                # Scale down
                return self._scale_down(current_count - target_count)

        except Exception as e:
            self.logger.error(f"Scaling error: {str(e)}")
            return False

    def _scale_up(self, count: int, creator: Callable[[], Any]) -> bool:
        """Scale up instances"""
        try:
            self._state = LifecycleState.SCALING

            for i in range(count):
                instance_id = f"instance_{int(time.time())}_{i}"

                if self.start_instance(instance_id, creator):
                    self._scaling_events.append(ScalingEvent(
                        timestamp=datetime.now(),
                        direction=ScalingDirection.UP,
                        from_instances=len(self._instances) - i - 1,
                        to_instances=len(self._instances) - i,
                        reason="Manual scale up",
                        trigger_metric="manual",
                        trigger_value=0.0,
                        threshold=0.0
                    ))

            self._state = LifecycleState.RUNNING
            self._last_scale_time[ScalingDirection.UP] = datetime.now()

            return True

        except Exception as e:
            self.logger.error(f"Scale up error: {str(e)}")
            self._state = LifecycleState.ERROR
            return False

    def _scale_down(self, count: int) -> bool:
        """Scale down instances"""
        try:
            self._state = LifecycleState.SCALING

            # Select instances to remove (least loaded first)
            instance_ids = sorted(
                self._instances.keys(),
                key=lambda iid: self._instance_load.get(iid, 0.0)
            )

            for i in range(min(count, len(instance_ids))):
                instance_id = instance_ids[i]
                if self.stop_instance(instance_id, graceful=True):
                    self._scaling_events.append(ScalingEvent(
                        timestamp=datetime.now(),
                        direction=ScalingDirection.DOWN,
                        from_instances=len(self._instances) + i,
                        to_instances=len(self._instances) + i - 1,
                        reason="Manual scale down",
                        trigger_metric="manual",
                        trigger_value=0.0,
                        threshold=0.0
                    ))

            self._state = LifecycleState.RUNNING
            self._last_scale_time[ScalingDirection.DOWN] = datetime.now()

            return True

        except Exception as e:
            self.logger.error(f"Scale down error: {str(e)}")
            self._state = LifecycleState.ERROR
            return False

    def check_auto_scaling(self, creator: Callable[[], Any]) -> Optional[ScalingEvent]:
        """Check and perform auto-scaling"""
        if not self.config.enable_auto_scaling:
            return None

        current_count = len(self._instances)

        # Calculate aggregate metric
        metric_value = self._calculate_aggregate_metric(self.config.scaling_metric)

        # Check scale up conditions
        if (
            metric_value > self.config.scale_up_threshold
            and current_count < self.config.max_instances
        ):
            # Check cooldown
            cooldown_remaining = self._get_cooldown_remaining(ScalingDirection.UP)
            if cooldown_remaining <= 0:
                self.logger.info(f"Auto-scaling up: {self.config.scaling_metric}={metric_value:.2f}")

                if self.scale_instances(current_count + 1, creator):
                    return ScalingEvent(
                        timestamp=datetime.now(),
                        direction=ScalingDirection.UP,
                        from_instances=current_count,
                        to_instances=current_count + 1,
                        reason=f"Auto-scale up: {self.config.scaling_metric} exceeded threshold",
                        trigger_metric=self.config.scaling_metric,
                        trigger_value=metric_value,
                        threshold=self.config.scale_up_threshold
                    )

        # Check scale down conditions
        elif (
            metric_value < self.config.scale_down_threshold
            and current_count > self.config.min_instances
        ):
            # Check cooldown
            cooldown_remaining = self._get_cooldown_remaining(ScalingDirection.DOWN)
            if cooldown_remaining <= 0:
                self.logger.info(f"Auto-scaling down: {self.config.scaling_metric}={metric_value:.2f}")

                if self.scale_instances(current_count - 1, creator):
                    return ScalingEvent(
                        timestamp=datetime.now(),
                        direction=ScalingDirection.DOWN,
                        from_instances=current_count,
                        to_instances=current_count - 1,
                        reason=f"Auto-scale down: {self.config.scaling_metric} below threshold",
                        trigger_metric=self.config.scaling_metric,
                        trigger_value=metric_value,
                        threshold=self.config.scale_down_threshold
                    )

        return None

    def _calculate_aggregate_metric(self, metric_name: str) -> float:
        """Calculate aggregate metric across all instances"""
        if not self._instances:
            return 0.0

        if metric_name == "cpu_percent":
            # Get CPU usage
            try:
                process = psutil.Process()
                return process.cpu_percent()
            except Exception:
                return 0.0

        elif metric_name == "memory_percent":
            # Get memory usage
            try:
                process = psutil.Process()
                return process.memory_info().rss / psutil.virtual_memory().total * 100
            except Exception:
                return 0.0

        elif metric_name == "load":
            # Calculate based on request counts
            if not self._instance_load:
                return 0.0

            return sum(self._instance_load.values()) / len(self._instance_load)

        else:
            return 0.0

    def _get_cooldown_remaining(self, direction: ScalingDirection) -> float:
        """Get remaining cooldown time in seconds"""
        last_scale = self._last_scale_time[direction]

        if direction == ScalingDirection.UP:
            cooldown = self.config.scale_up_cooldown_seconds
        else:
            cooldown = self.config.scale_down_cooldown_seconds

        elapsed = (datetime.now() - last_scale).total_seconds()
        return max(0, cooldown - elapsed)

    def select_instance_for_request(self) -> Optional[str]:
        """Select instance for request using load balancing"""
        if not self._instances:
            return None

        if not self.config.enable_load_balancing:
            # No load balancing, return first available
            return next(iter(self._instances.keys()))

        strategy = self.config.load_balancing_strategy

        if strategy == "round_robin":
            return self._round_robin_selection()
        elif strategy == "least_connections":
            return self._least_connections_selection()
        elif strategy == "weighted":
            return self._weighted_selection()
        else:
            return self._round_robin_selection()

    def _round_robin_selection(self) -> str:
        """Round-robin instance selection"""
        instance_ids = list(self._instances.keys())
        if not instance_ids:
            raise RuntimeError("No instances available")

        selected_id = instance_ids[self._current_instance_index % len(instance_ids)]
        self._current_instance_index += 1

        return selected_id

    def _least_connections_selection(self) -> str:
        """Select instance with least active connections"""
        min_load = float('inf')
        selected_id = None

        for instance_id, load in self._instance_load.items():
            if load < min_load:
                min_load = load
                selected_id = instance_id

        if selected_id is None:
            # Fallback to first instance
            selected_id = next(iter(self._instances.keys()))

        return selected_id

    def _weighted_selection(self) -> str:
        """Select instance based on weights (inverse load)"""
        # Calculate weights (inverse of load)
        weights = {}
        total_weight = 0.0

        for instance_id, load in self._instance_load.items():
            weight = 1.0 / (load + 0.1)  # Avoid division by zero
            weights[instance_id] = weight
            total_weight += weight

        # Weighted random selection
        import random
        rand_val = random.random() * total_weight

        cumulative = 0.0
        for instance_id, weight in weights.items():
            cumulative += weight
            if rand_val <= cumulative:
                return instance_id

        # Fallback
        return next(iter(self._instances.keys()))

    def record_request_start(self, instance_id: str) -> None:
        """Record request start for an instance"""
        self._request_counts[instance_id] += 1

    def record_request_end(self, instance_id: str) -> None:
        """Record request end for an instance"""
        if instance_id in self._request_counts:
            self._request_counts[instance_id] = max(0, self._request_counts[instance_id] - 1)

    def update_instance_load(self, instance_id: str, load: float) -> None:
        """Update load metric for an instance"""
        self._instance_load[instance_id] = max(0.0, min(1.0, load))

    def initiate_graceful_shutdown(self) -> bool:
        """Initiate graceful shutdown of all instances"""
        if self._shutdown_initiated:
            self.logger.warning("Shutdown already initiated")
            return False

        self.logger.info("Initiating graceful shutdown")
        self._shutdown_initiated = True
        self._state = LifecycleState.STOPPING

        try:
            # Shutdown all instances gracefully
            for instance_id in list(self._instances.keys()):
                self.stop_instance(instance_id, graceful=True)

            self._graceful_shutdown_complete = True
            self._state = LifecycleState.STOPPED

            self.logger.info("Graceful shutdown completed")
            return True

        except Exception as e:
            self.logger.error(f"Graceful shutdown error: {str(e)}")
            self._state = LifecycleState.ERROR
            return False

    def add_shutdown_hook(self, hook: Callable[[str, Any], None]) -> None:
        """Add a shutdown hook to be called during graceful shutdown"""
        self._shutdown_hooks.append(hook)

    def get_lifecycle_status(self) -> Dict[str, Any]:
        """Get current lifecycle status"""
        return {
            "state": self._state.value,
            "instance_count": len(self._instances),
            "healthy_instances": sum(1 for h in self._instance_health.values() if h),
            "total_capacity": len(self._instances),
            "scaling_events": len(self._scaling_events),
            "load_balancing_strategy": self.config.load_balancing_strategy,
            "auto_scaling_enabled": self.config.enable_auto_scaling,
            "instance_load": dict(self._instance_load),
            "last_scale_up": self._last_scale_time[ScalingDirection.UP].isoformat(),
            "last_scale_down": self._last_scale_time[ScalingDirection.DOWN].isoformat()
        }


def create_lifecycle_manager(config: LifecycleConfig) -> AdvancedLifecycleManager:
    """Create and configure an advanced lifecycle manager"""
    manager = AdvancedLifecycleManager(config)
    return manager