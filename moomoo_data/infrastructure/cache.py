"""
Caching layer for moomoo-data.

Provides TTL-based caching with:
- In-memory cache (default)
- Automatic invalidation
- Thread-safe operation
"""

import time
import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """A cached item with metadata."""

    value: Any
    created_at: float
    ttl_seconds: int
    key: str

    @property
    def expires_at(self) -> float:
        """Get expiration timestamp."""
        return self.created_at + self.ttl_seconds

    @property
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        return time.time() > self.expires_at

    @property
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return time.time() - self.created_at

    @property
    def ttl_remaining(self) -> float:
        """Get remaining TTL in seconds."""
        return max(0, self.expires_at - time.time())


@dataclass
class CacheConfig:
    """Configuration for cache."""

    enabled: bool = True
    backend: str = "memory"  # "memory" or "redis"
    default_ttl_seconds: int = 300  # 5 minutes
    max_size: int = 10000  # Max entries for memory cache

    # TTLs for specific data types
    quotes_ttl: int = 900  # 15 minutes
    kline_daily_ttl: int = 86400  # 24 hours
    kline_intraday_ttl: int = 3600  # 1 hour
    capital_flow_ttl: int = 3600  # 1 hour
    order_book_ttl: int = 300  # 5 minutes
    fundamentals_ttl: int = 604800  # 7 days


class MemoryCache:
    """Thread-safe in-memory cache."""

    def __init__(self, config: CacheConfig):
        """Initialize memory cache."""
        self.config = config
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired:
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache miss (expired): {key}")
                return None

            self._hits += 1
            logger.debug(f"Cache hit: {key} (age={entry.age_seconds:.1f}s)")
            return entry.value

    def set(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: TTL in seconds (uses default if not provided)
        """
        if not self.config.enabled:
            return

        with self._lock:
            # Evict oldest if at capacity
            if len(self._cache) >= self.config.max_size:
                self._evict_oldest()

            ttl = ttl_seconds or self.config.default_ttl_seconds
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                ttl_seconds=ttl,
                key=key,
            )
            self._cache[key] = entry
            logger.debug(f"Cached: {key} (ttl={ttl}s)")

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache deleted: {key}")
                return True
            return False

    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")

    def _evict_oldest(self) -> None:
        """Evict the oldest entry."""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(), key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]
        logger.debug(f"Evicted oldest: {oldest_key}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0

            return {
                "enabled": self.config.enabled,
                "backend": "memory",
                "size": len(self._cache),
                "max_size": self.config.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
            }

    def get_ttl_for_type(self, data_type: str) -> int:
        """
        Get TTL for a specific data type.

        Args:
            data_type: Type of data ('quotes', 'kline_daily', etc.)

        Returns:
            TTL in seconds
        """
        ttl_map = {
            "quotes": self.config.quotes_ttl,
            "kline_daily": self.config.kline_daily_ttl,
            "kline_intraday": self.config.kline_intraday_ttl,
            "capital_flow": self.config.capital_flow_ttl,
            "order_book": self.config.order_book_ttl,
            "fundamentals": self.config.fundamentals_ttl,
        }
        return ttl_map.get(data_type, self.config.default_ttl_seconds)


# Global cache instance
_global_cache: Optional[MemoryCache] = None


def get_cache(config: Optional[CacheConfig] = None) -> MemoryCache:
    """
    Get or create global cache.

    Args:
        config: Optional cache configuration

    Returns:
        MemoryCache instance
    """
    global _global_cache

    if _global_cache is None:
        _global_cache = MemoryCache(config or CacheConfig())

    return _global_cache


def reset_cache() -> None:
    """Reset global cache (useful for testing)."""
    global _global_cache
    _global_cache = None
