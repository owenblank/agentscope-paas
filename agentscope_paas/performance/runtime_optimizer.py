"""
Runtime Performance Optimization and Analytics Module

Provides performance optimization utilities, caching strategies,
connection pooling, and analytics collection for Runtime operations.
"""

import asyncio
import time
import threading
import logging
from typing import Any, Dict, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict
import hashlib
import json

from ..utils.logger import get_logger


class CacheStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    ttl_seconds: Optional[int] = None


class RuntimeCache:
    """
    Advanced caching system for Runtime operations

    Provides multiple cache strategies, size management, and TTL support.
    """

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        strategy: CacheStrategy = CacheStrategy.LRU
    ):
        """
        Initialize Runtime cache

        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
            strategy: Cache eviction strategy
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy

        self.logger = get_logger(__name__)

        # Cache storage
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()

        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]

            # Check TTL
            if entry.ttl_seconds and self._is_expired(entry):
                self._remove_entry(key)
                self._misses += 1
                return None

            # Update access statistics
            entry.last_accessed = datetime.now()
            entry.access_count += 1

            # Update cache order based on strategy
            if self.strategy == CacheStrategy.LRU:
                self._cache.move_to_end(key)

            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        with self._lock:
            # Check if cache is full
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_entries()

            # Calculate size
            try:
                size_bytes = len(json.dumps(value, default=str))
            except Exception:
                size_bytes = 0

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                size_bytes=size_bytes,
                ttl_seconds=ttl or self.default_ttl
            )

            self._cache[key] = entry

            # Update cache order based on strategy
            if self.strategy == CacheStrategy.LRU:
                self._cache.move_to_end(key)

            return True

    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if entry is expired"""
        if not entry.ttl_seconds:
            return False

        elapsed = (datetime.now() - entry.created_at).total_seconds()
        return elapsed > entry.ttl_seconds

    def _evict_entries(self) -> None:
        """Evict entries based on strategy"""
        if not self._cache:
            return

        if self.strategy == CacheStrategy.LRU:
            # Evict least recently used
            oldest_key = next(iter(self._cache))
            self._remove_entry(oldest_key)

        elif self.strategy == CacheStrategy.LFU:
            # Evict least frequently used
            min_access = min(entry.access_count for entry in self._cache.values())
            for key, entry in self._cache.items():
                if entry.access_count == min_access:
                    self._remove_entry(key)
                    break

        elif self.strategy == CacheStrategy.FIFO:
            # Evict oldest entry
            oldest_key = next(iter(self._cache))
            self._remove_entry(oldest_key)

        elif self.strategy == CacheStrategy.TTL:
            # Evict expired entries first
            for key in list(self._cache.keys()):
                entry = self._cache[key]
                if self._is_expired(entry):
                    self._remove_entry(key)
                    break
            else:
                # If no expired entries, evict oldest
                oldest_key = next(iter(self._cache))
                self._remove_entry(oldest_key)

    def _remove_entry(self, key: str) -> None:
        """Remove entry from cache"""
        if key in self._cache:
            del self._cache[key]
            self._evictions += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests) if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": hit_rate,
                "strategy": self.strategy.value
            }


class ConnectionPool:
    """
    Connection pool for Runtime agent connections

    Manages a pool of connections with automatic creation, cleanup,
    and health monitoring.
    """

    def __init__(
        self,
        max_connections: int = 10,
        idle_timeout: int = 300,
        max_lifetime: int = 3600
    ):
        """
        Initialize connection pool

        Args:
            max_connections: Maximum number of connections
            idle_timeout: Idle timeout in seconds
            max_lifetime: Maximum connection lifetime in seconds
        """
        self.max_connections = max_connections
        self.idle_timeout = idle_timeout
        self.max_lifetime = max_lifetime

        self.logger = get_logger(__name__)

        # Connection storage
        self._connections: Dict[str, Any] = {}
        self._connection_meta: Dict[str, Dict[str, Any]] = {}

        self._lock = threading.Lock()
        self._created_count = 0
        self._reused_count = 0

    def get_connection(self, key: str, creator: Callable[[], Any]) -> Any:
        """Get connection from pool or create new one"""
        with self._lock:
            # Check for existing connection
            if key in self._connections:
                conn = self._connections[key]
                meta = self._connection_meta[key]

                # Check if connection is still valid
                if self._is_connection_valid(meta):
                    meta["last_used"] = datetime.now()
                    meta["use_count"] += 1
                    self._reused_count += 1
                    return conn
                else:
                    # Remove invalid connection
                    self._remove_connection(key)

            # Check pool size limit
            if len(self._connections) >= self.max_connections:
                self._cleanup_idle_connections()

            # Create new connection
            conn = creator()
            self._connections[key] = conn

            self._connection_meta[key] = {
                "created_at": datetime.now(),
                "last_used": datetime.now(),
                "use_count": 1
            }
            self._created_count += 1

            return conn

    def release_connection(self, key: str) -> None:
        """Release connection back to pool"""
        with self._lock:
            if key in self._connection_meta:
                self._connection_meta[key]["last_used"] = datetime.now()

    def remove_connection(self, key: str) -> None:
        """Remove connection from pool"""
        with self._lock:
            self._remove_connection(key)

    def _remove_connection(self, key: str) -> None:
        """Remove connection from pool"""
        if key in self._connections:
            conn = self._connections[key]

            # Close connection if it has a close method
            if hasattr(conn, 'close'):
                try:
                    conn.close()
                except Exception as e:
                    self.logger.error(f"Error closing connection: {str(e)}")

            del self._connections[key]
            del self._connection_meta[key]

    def _is_connection_valid(self, meta: Dict[str, Any]) -> bool:
        """Check if connection is still valid"""
        now = datetime.now()

        # Check lifetime
        age = (now - meta["created_at"]).total_seconds()
        if age > self.max_lifetime:
            return False

        # Check idle timeout
        idle_time = (now - meta["last_used"]).total_seconds()
        if idle_time > self.idle_timeout:
            return False

        return True

    def _cleanup_idle_connections(self) -> None:
        """Remove idle connections"""
        now = datetime.now()
        keys_to_remove = []

        for key, meta in self._connection_meta.items():
            idle_time = (now - meta["last_used"]).total_seconds()
            if idle_time > self.idle_timeout:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            self._remove_connection(key)

    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self._lock:
            return {
                "active_connections": len(self._connections),
                "max_connections": self.max_connections,
                "created_count": self._created_count,
                "reused_count": self._reused_count,
                "reuse_rate": (
                    self._reused_count / (self._created_count + self._reused_count)
                    if (self._created_count + self._reused_count) > 0 else 0
                )
            }


class PerformanceOptimizer:
    """
    Performance optimization utilities for Runtime operations

    Provides caching, connection pooling, and performance enhancement
    strategies for Runtime agent operations.
    """

    def __init__(self):
        """Initialize performance optimizer"""
        self.logger = get_logger(__name__)

        # Components
        self._caches: Dict[str, RuntimeCache] = {}
        self._pools: Dict[str, ConnectionPool] = {}

        # Optimization settings
        self._optimization_enabled = True
        self._performance_tips: List[str] = []

    def create_cache(
        self,
        name: str,
        max_size: int = 1000,
        ttl: int = 3600,
        strategy: CacheStrategy = CacheStrategy.LRU
    ) -> RuntimeCache:
        """Create a new cache instance"""
        cache = RuntimeCache(
            max_size=max_size,
            default_ttl=ttl,
            strategy=strategy
        )
        self._caches[name] = cache
        return cache

    def create_pool(
        self,
        name: str,
        max_connections: int = 10,
        idle_timeout: int = 300,
        max_lifetime: int = 3600
    ) -> ConnectionPool:
        """Create a new connection pool"""
        pool = ConnectionPool(
            max_connections=max_connections,
            idle_timeout=idle_timeout,
            max_lifetime=max_lifetime
        )
        self._pools[name] = pool
        return pool

    def optimize_operation(
        self,
        operation_name: str,
        operation: Callable,
        cache_name: Optional[str] = None,
        cache_key_func: Optional[Callable[..., str]] = None,
        cache_ttl: int = 3600
    ) -> Callable:
        """
        Wrap an operation with performance optimizations

        Args:
            operation_name: Name of the operation
            operation: The operation function to optimize
            cache_name: Name of cache to use
            cache_key_func: Function to generate cache keys
            cache_ttl: Cache time-to-live

        Returns:
            Optimized operation function
        """
        def optimized_operation(*args, **kwargs):
            # Check cache if configured
            if cache_name and cache_key_func and self._optimization_enabled:
                cache = self._caches.get(cache_name)
                if cache:
                    cache_key = cache_key_func(*args, **kwargs)
                    cached_result = cache.get(cache_key)

                    if cached_result is not None:
                        return cached_result

            # Execute operation
            start_time = time.time()
            result = operation(*args, **kwargs)
            duration = time.time() - start_time

            # Cache result if configured
            if cache_name and cache_key_func and self._optimization_enabled:
                cache = self._caches.get(cache_name)
                if cache and result is not None:
                    cache_key = cache_key_func(*args, **kwargs)
                    cache.set(cache_key, result, ttl=cache_ttl)

            # Log performance
            if duration > 1.0:  # Log slow operations
                self.logger.warning(
                    f"Slow operation: {operation_name} took {duration:.2f}s"
                )

            return result

        return optimized_operation

    def batch_operations(
        self,
        operations: List[Tuple[Callable, tuple, dict]],
        max_concurrent: int = 5
    ) -> List[Any]:
        """
        Execute multiple operations with concurrency control

        Args:
            operations: List of (function, args, kwargs) tuples
            max_concurrent: Maximum concurrent operations

        Returns:
            List of results in same order as input
        """
        results = [None] * len(operations)

        def execute_batch(start_idx, end_idx):
            for i in range(start_idx, end_idx):
                func, args, kwargs = operations[i]
                try:
                    results[i] = func(*args, **kwargs)
                except Exception as e:
                    results[i] = e

        # Split into batches
        batch_size = max(1, len(operations) // max_concurrent)

        threads = []
        for i in range(0, len(operations), batch_size):
            end_idx = min(i + batch_size, len(operations))
            thread = threading.Thread(
                target=execute_batch,
                args=(i, end_idx)
            )
            thread.start()
            threads.append(thread)

        # Wait for all threads
        for thread in threads:
            thread.join()

        return results

    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of optimization performance"""
        cache_stats = {}
        for name, cache in self._caches.items():
            cache_stats[name] = cache.get_stats()

        pool_stats = {}
        for name, pool in self._pools.items():
            pool_stats[name] = pool.get_stats()

        return {
            "optimization_enabled": self._optimization_enabled,
            "caches": cache_stats,
            "pools": pool_stats,
            "performance_tips": self._performance_tips
        }

    def enable_optimizations(self) -> None:
        """Enable performance optimizations"""
        self._optimization_enabled = True
        self.logger.info("Performance optimizations enabled")

    def disable_optimizations(self) -> None:
        """Disable performance optimizations"""
        self._optimization_enabled = False
        self.logger.info("Performance optimizations disabled")


def generate_cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_parts = []

    # Add positional args
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif isinstance(arg, (dict, list)):
            key_parts.append(json.dumps(arg, sort_keys=True))
        else:
            key_parts.append(str(hash(str(arg))))

    # Add keyword args (sorted for consistency)
    for k in sorted(kwargs.keys()):
        v = kwargs[k]
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}={v}")
        elif isinstance(v, (dict, list)):
            key_parts.append(f"{k}={json.dumps(v, sort_keys=True)}")
        else:
            key_parts.append(f"{k}={hash(str(v))}")

    key_string = ":".join(key_parts)

    # Hash if key is too long
    if len(key_string) > 100:
        return hashlib.md5(key_string.encode()).hexdigest()

    return key_string


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

# Create default caches
performance_optimizer.create_cache("responses", max_size=500, ttl=1800)
performance_optimizer.create_cache("configurations", max_size=100, ttl=3600)
performance_optimizer.create_cache("agent_data", max_size=200, ttl=7200)

# Create default connection pool
performance_optimizer.create_pool("http_connections", max_connections=20)


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance"""
    return performance_optimizer