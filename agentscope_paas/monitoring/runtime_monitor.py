"""
Runtime Monitoring and Metrics Collection Module

Provides comprehensive monitoring, metrics collection, performance tracking,
and analytics for AgentScope Runtime deployments.
"""

import time
import threading
import logging
import json
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import psutil
import asyncio

from ..utils.logger import get_logger


class MetricType(Enum):
    """Types of metrics that can be collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertLevel(Enum):
    """Severity levels for monitoring alerts"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class Alert:
    """Monitoring alert information"""
    level: AlertLevel
    message: str
    timestamp: datetime
    metric_name: str
    current_value: float
    threshold_value: float
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class RuntimeMetricsCollector:
    """
    Comprehensive metrics collection for Runtime operations

    Collects system metrics, application metrics, and performance indicators
    with configurable sampling intervals and retention policies.
    """

    def __init__(
        self,
        collection_interval: int = 60,
        retention_hours: int = 24,
        enable_system_metrics: bool = True,
        enable_app_metrics: bool = True
    ):
        """
        Initialize metrics collector

        Args:
            collection_interval: Seconds between metric collections
            retention_hours: Hours to retain metric data
            enable_system_metrics: Enable system resource monitoring
            enable_app_metrics: Enable application-level metrics
        """
        self.collection_interval = collection_interval
        self.retention_hours = retention_hours
        self.enable_system_metrics = enable_system_metrics
        self.enable_app_metrics = enable_app_metrics

        self.logger = get_logger(__name__)

        # Metric storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: deque = deque(maxlen=1000)

        # Counters and gauges
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)

        # Histogram data
        self._histograms: Dict[str, List[float]] = defaultdict(list)

        # Background collection thread
        self._collection_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()

        # Metric callbacks
        self._metric_callbacks: List[Callable[[Metric], None]] = []

    def start_collection(self) -> None:
        """Start background metrics collection"""
        if self._running:
            self.logger.warning("Metrics collection already running")
            return

        self._running = True
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True,
            name="MetricsCollector"
        )
        self._collection_thread.start()
        self.logger.info("Metrics collection started")

    def stop_collection(self) -> None:
        """Stop background metrics collection"""
        if not self._running:
            return

        self._running = False
        if self._collection_thread:
            self._collection_thread.join(timeout=5)

        self.logger.info("Metrics collection stopped")

    def _collection_loop(self) -> None:
        """Background loop for metric collection"""
        while self._running:
            try:
                self._collect_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error(f"Metrics collection error: {str(e)}")
                time.sleep(self.collection_interval)

    def _collect_metrics(self) -> None:
        """Collect all configured metrics"""
        timestamp = datetime.now()

        with self._lock:
            # System metrics
            if self.enable_system_metrics:
                self._collect_system_metrics(timestamp)

            # Application metrics
            if self.enable_app_metrics:
                self._collect_app_metrics(timestamp)

    def _collect_system_metrics(self, timestamp: datetime) -> None:
        """Collect system resource metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self._add_metric("system_cpu_percent", cpu_percent, timestamp)

            # Memory metrics
            memory = psutil.virtual_memory()
            self._add_metric("system_memory_percent", memory.percent, timestamp)
            self._add_metric("system_memory_available_gb", memory.available / (1024**3), timestamp)

            # Disk metrics
            disk = psutil.disk_usage('/')
            self._add_metric("system_disk_percent", disk.percent, timestamp)
            self._add_metric("system_disk_free_gb", disk.free / (1024**3), timestamp)

            # Network metrics
            network = psutil.net_io_counters()
            self._add_metric("system_network_bytes_sent", network.bytes_sent, timestamp)
            self._add_metric("system_network_bytes_recv", network.bytes_recv, timestamp)

        except Exception as e:
            self.logger.error(f"System metrics collection failed: {str(e)}")

    def _collect_app_metrics(self, timestamp: datetime) -> None:
        """Collect application-level metrics"""
        try:
            # Process metrics
            process = psutil.Process()

            self._add_metric("app_cpu_percent", process.cpu_percent(), timestamp)
            self._add_metric("app_memory_mb", process.memory_info().rss / (1024**2), timestamp)
            self._add_metric("app_num_threads", process.num_threads(), timestamp)
            self._add_metric("app_num_fds", process.num_fds(), timestamp)

            # Custom counters and gauges
            for name, value in self._counters.items():
                self._add_metric(f"counter_{name}", value, timestamp, MetricType.COUNTER)

            for name, value in self._gauges.items():
                self._add_metric(f"gauge_{name}", value, timestamp, MetricType.GAUGE)

        except Exception as e:
            self.logger.error(f"Application metrics collection failed: {str(e)}")

    def _add_metric(
        self,
        name: str,
        value: float,
        timestamp: datetime,
        metric_type: MetricType = MetricType.GAUGE,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Add a metric to storage"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=timestamp,
            labels=labels or {},
            metric_type=metric_type
        )

        self.metrics[name].append(metric)

        # Notify callbacks
        for callback in self._metric_callbacks:
            try:
                callback(metric)
            except Exception as e:
                self.logger.error(f"Metric callback error: {str(e)}")

    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric"""
        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] += value
            self._add_metric(name, self._counters[key], datetime.now(), MetricType.COUNTER, labels)

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric value"""
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value
            self._add_metric(name, value, datetime.now(), MetricType.GAUGE, labels)

    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a value in a histogram"""
        with self._lock:
            key = self._make_key(name, labels)
            self._histograms[key].append(value)
            self._add_metric(name, value, datetime.now(), MetricType.HISTOGRAM, labels)

    def get_metrics(self, name: str, since: Optional[datetime] = None) -> List[Metric]:
        """Get metrics for a specific name"""
        if since is None:
            since = datetime.now() - timedelta(hours=self.retention_hours)

        metrics = self.metrics.get(name, deque())
        return [m for m in metrics if m.timestamp >= since]

    def get_all_metrics(self, since: Optional[datetime] = None) -> Dict[str, List[Metric]]:
        """Get all collected metrics"""
        if since is None:
            since = datetime.now() - timedelta(hours=self.retention_hours)

        result = {}
        for name, metric_deque in self.metrics.items():
            result[name] = [m for m in metric_deque if m.timestamp >= since]

        return result

    def get_metric_summary(self, name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        metrics = self.get_metrics(name)

        if not metrics:
            return {}

        values = [m.value for m in metrics]

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None,
            "first_timestamp": metrics[0].timestamp.isoformat() if metrics else None,
            "last_timestamp": metrics[-1].timestamp.isoformat() if metrics else None
        }

    def add_callback(self, callback: Callable[[Metric], None]) -> None:
        """Add a callback to be called for each new metric"""
        self._metric_callbacks.append(callback)

    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create a unique key for labeled metrics"""
        if not labels:
            return name

        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []

        for name, metric_deque in self.metrics.items():
            if not metric_deque:
                continue

            latest_metric = metric_deque[-1]
            labels_str = ""

            if latest_metric.labels:
                labels_str = "{" + ",".join(
                    f'{k}="{v}"' for k, v in latest_metric.labels.items()
                ) + "}"

            # Metric type help
            metric_type = latest_metric.metric_type.value
            lines.append(f"# HELP {name} {name} metric")
            lines.append(f"# TYPE {name} {metric_type}")

            # Metric value
            lines.append(f"{name}{labels_str} {latest_metric.value}")

        return "\n".join(lines)

    def get_metrics_json(self) -> str:
        """Export metrics as JSON"""
        metrics_data = {}

        for name, metric_deque in self.metrics.items():
            if not metric_deque:
                continue

            latest_metric = metric_deque[-1]
            metrics_data[name] = {
                "value": latest_metric.value,
                "timestamp": latest_metric.timestamp.isoformat(),
                "type": latest_metric.metric_type.value,
                "labels": latest_metric.labels
            }

        return json.dumps(metrics_data, indent=2)


class RuntimeAlertManager:
    """
    Alert management for monitoring thresholds

    Monitors metrics and generates alerts when thresholds are exceeded.
    """

    def __init__(self, metrics_collector: RuntimeMetricsCollector):
        """
        Initialize alert manager

        Args:
            metrics_collector: Metrics collector instance
        """
        self.metrics_collector = metrics_collector
        self.logger = get_logger(__name__)

        # Alert rules
        self.alert_rules: Dict[str, Dict[str, Any]] = {}

        # Alert history
        self.alerts: deque = deque(maxlen=1000)

    def add_alert_rule(
        self,
        name: str,
        metric_name: str,
        condition: str,  # "greater_than", "less_than", "equals"
        threshold: float,
        level: AlertLevel = AlertLevel.WARNING,
        message_template: Optional[str] = None
    ) -> None:
        """Add an alert rule"""
        self.alert_rules[name] = {
            "metric_name": metric_name,
            "condition": condition,
            "threshold": threshold,
            "level": level,
            "message_template": message_template or f"{metric_name} {condition} {threshold}"
        }

        self.logger.info(f"Added alert rule: {name}")

    def check_alerts(self) -> List[Alert]:
        """Check all alert rules and generate alerts"""
        new_alerts = []

        for rule_name, rule in self.alert_rules.items():
            try:
                alert = self._check_rule(rule_name, rule)
                if alert:
                    new_alerts.append(alert)
                    self.alerts.append(alert)
            except Exception as e:
                self.logger.error(f"Alert check failed for {rule_name}: {str(e)}")

        return new_alerts

    def _check_rule(self, rule_name: str, rule: Dict[str, Any]) -> Optional[Alert]:
        """Check a single alert rule"""
        metric_name = rule["metric_name"]
        condition = rule["condition"]
        threshold = rule["threshold"]
        level = rule["level"]
        message_template = rule["message_template"]

        # Get latest metric value
        metrics = self.metrics_collector.get_metrics(metric_name)
        if not metrics:
            return None

        latest_metric = metrics[-1]
        current_value = latest_metric.value

        # Check condition
        triggered = False

        if condition == "greater_than" and current_value > threshold:
            triggered = True
        elif condition == "less_than" and current_value < threshold:
            triggered = True
        elif condition == "equals" and current_value == threshold:
            triggered = True

        if triggered:
            message = message_template.format(
                metric_name=metric_name,
                current_value=current_value,
                threshold=threshold
            )

            return Alert(
                level=level,
                message=message,
                timestamp=datetime.now(),
                metric_name=metric_name,
                current_value=current_value,
                threshold_value=threshold
            )

        return None

    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get recent alerts"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp >= cutoff]

    def get_active_alerts(self) -> List[Alert]:
        """Get currently active (unresolved) alerts"""
        return [alert for alert in self.alerts if not alert.resolved]


class RuntimePerformanceMonitor:
    """
    Performance monitoring for Runtime operations

    Tracks response times, throughput, error rates, and performance patterns.
    """

    def __init__(self, metrics_collector: RuntimeMetricsCollector):
        """
        Initialize performance monitor

        Args:
            metrics_collector: Metrics collector instance
        """
        self.metrics_collector = metrics_collector
        self.logger = get_logger(__name__)

        # Performance tracking
        self._request_timings: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._request_counts: Dict[str, int] = defaultdict(int)

        # Performance baselines
        self._baselines: Dict[str, float] = {}

    def record_request(
        self,
        operation: str,
        duration: float,
        success: bool = True,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a request performance"""
        self._request_timings[operation].append({
            "duration": duration,
            "timestamp": datetime.now(),
            "success": success,
            "labels": labels or {}
        })

        self._request_counts[operation] += 1

        if not success:
            self._error_counts[operation] += 1

        # Update metrics
        self.metrics_collector.record_histogram(
            f"request_duration_{operation}",
            duration,
            labels
        )

        if success:
            self.metrics_collector.increment_counter(
                f"requests_success_{operation}",
                1.0,
                labels
            )
        else:
            self.metrics_collector.increment_counter(
                f"requests_error_{operation}",
                1.0,
                labels
            )

    def get_performance_stats(self, operation: str) -> Dict[str, Any]:
        """Get performance statistics for an operation"""
        timings = self._request_timings.get(operation, deque())

        if not timings:
            return {}

        durations = [t["duration"] for t in timings if t["success"]]
        errors = [t for t in timings if not t["success"]]

        success_rate = (len(durations) / len(timings)) * 100 if timings else 0

        return {
            "operation": operation,
            "total_requests": len(timings),
            "successful_requests": len(durations),
            "error_requests": len(errors),
            "success_rate": success_rate,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "p50_duration": self._percentile(durations, 50) if durations else 0,
            "p95_duration": self._percentile(durations, 95) if durations else 0,
            "p99_duration": self._percentile(durations, 99) if durations else 0
        }

    def _percentile(self, data: List[float], p: int) -> float:
        """Calculate percentile value"""
        if not data:
            return 0

        sorted_data = sorted(data)
        index = (p / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_data) - 1)

        if upper == lower:
            return sorted_data[lower]

        return sorted_data[lower] * (upper - index) + sorted_data[upper] * (index - lower)

    def set_baseline(self, operation: str, duration: float) -> None:
        """Set performance baseline for an operation"""
        self._baselines[operation] = duration
        self.logger.info(f"Set baseline for {operation}: {duration}s")

    def check_baseline_drift(self, operation: str, threshold: float = 2.0) -> Optional[Dict[str, Any]]:
        """Check if performance has drifted from baseline"""
        if operation not in self._baselines:
            return None

        baseline = self._baselines[operation]
        stats = self.get_performance_stats(operation)
        current_avg = stats.get("avg_duration", 0)

        if current_avg == 0:
            return None

        drift_ratio = current_avg / baseline

        if drift_ratio > threshold:
            return {
                "operation": operation,
                "baseline": baseline,
                "current": current_avg,
                "drift_ratio": drift_ratio,
                "threshold": threshold,
                "drift_detected": True
            }

        return None


def create_runtime_monitor(
    collection_interval: int = 60,
    retention_hours: int = 24
) -> RuntimeMetricsCollector:
    """
    Create and configure Runtime monitoring system

    Args:
        collection_interval: Seconds between metric collections
        retention_hours: Hours to retain metrics

    Returns:
        Configured RuntimeMetricsCollector instance
    """
    collector = RuntimeMetricsCollector(
        collection_interval=collection_interval,
        retention_hours=retention_hours,
        enable_system_metrics=True,
        enable_app_metrics=True
    )

    # Set up default alert rules
    alert_manager = RuntimeAlertManager(collector)

    alert_manager.add_alert_rule(
        "high_cpu",
        "system_cpu_percent",
        "greater_than",
        80.0,
        AlertLevel.WARNING
    )

    alert_manager.add_alert_rule(
        "high_memory",
        "system_memory_percent",
        "greater_than",
        85.0,
        AlertLevel.CRITICAL
    )

    alert_manager.add_alert_rule(
        "high_disk",
        "system_disk_percent",
        "greater_than",
        90.0,
        AlertLevel.CRITICAL
    )

    collector.start_collection()

    return collector