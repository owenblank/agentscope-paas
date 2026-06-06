"""
Advanced Lifecycle Management Module

Provides advanced lifecycle management features including auto-scaling,
load balancing, graceful shutdown, and resource management for Runtime agents.
"""

from .advanced_lifecycle import (
    AdvancedLifecycleManager,
    LifecycleState,
    ScalingDirection,
    ScalingEvent,
    LifecycleConfig,
    create_lifecycle_manager
)

__all__ = [
    'AdvancedLifecycleManager',
    'LifecycleState',
    'ScalingDirection',
    'ScalingEvent',
    'LifecycleConfig',
    'create_lifecycle_manager'
]