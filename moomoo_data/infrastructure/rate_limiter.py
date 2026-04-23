"""
Rate limiter for Moomoo API calls.

Implements sliding window rate limiting with:
- Per-API limits
- Automatic retry with backoff
- Thread-safe operation
"""

import time
import asyncio
import logging
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for a rate limit."""

    limit: int  # Max requests
    window_seconds: int  # Time window
    name: str = ""  # Human-readable name


# Default rate limits (conservative settings)
DEFAULT_RATE_LIMITS = {
    "market_state": RateLimitConfig(
        limit=8, window_seconds=30, name="get_market_state()"
    ),
    "stock_quote": RateLimitConfig(
        limit=30, window_seconds=30, name="get_stock_quote()"
    ),
    "kline": RateLimitConfig(limit=20, window_seconds=30, name="get_cur_kline()"),
    "capital_flow": RateLimitConfig(
        limit=20, window_seconds=30, name="get_capital_flow()"
    ),
    "capital_distribution": RateLimitConfig(
        limit=20, window_seconds=30, name="get_capital_distribution()"
    ),
    "order_book": RateLimitConfig(limit=15, window_seconds=30, name="get_order_book()"),
    "broker_queue": RateLimitConfig(
        limit=15, window_seconds=30, name="get_broker_queue()"
    ),
    "subscribe": RateLimitConfig(limit=5, window_seconds=30, name="subscribe()"),
}


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, api_name: str, retry_after: float):
        self.api_name = api_name
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded for {api_name}. Retry after {retry_after:.2f}s"
        )


class RateLimiter:
    """
    Thread-safe sliding window rate limiter.

    Tracks request timestamps per API endpoint and enforces rate limits
    using a sliding window algorithm.
    """

    def __init__(self, configs: Optional[Dict[str, RateLimitConfig]] = None):
        """
        Initialize rate limiter.

        Args:
            configs: Rate limit configurations. Uses defaults if not provided.
        """
        self.configs = configs or DEFAULT_RATE_LIMITS
        self._request_times: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def _cleanup_old_requests(self, api_name: str, window_seconds: int) -> None:
        """Remove requests outside the current window."""
        now = time.time()
        cutoff = now - window_seconds
        self._request_times[api_name] = [
            t for t in self._request_times[api_name] if t > cutoff
        ]

    def can_request(self, api_name: str) -> bool:
        """
        Check if a request is allowed.

        Args:
            api_name: Name of the API endpoint

        Returns:
            True if request is allowed, False if rate limited
        """
        if api_name not in self.configs:
            return True  # No limit configured

        config = self.configs[api_name]

        with self._lock:
            self._cleanup_old_requests(api_name, config.window_seconds)
            return len(self._request_times[api_name]) < config.limit

    def record_request(self, api_name: str) -> None:
        """
        Record a request timestamp.

        Args:
            api_name: Name of the API endpoint
        """
        with self._lock:
            self._request_times[api_name].append(time.time())

    def acquire(self, api_name: str, blocking: bool = True) -> bool:
        """
        Acquire permission to make a request.

        Args:
            api_name: Name of the API endpoint
            blocking: If True, wait until permission is granted.
                     If False, raise immediately if rate limited.

        Returns:
            True if permission granted

        Raises:
            RateLimitExceededError: If blocking=False and rate limited
        """
        if api_name not in self.configs:
            self.record_request(api_name)
            return True

        config = self.configs[api_name]

        while True:
            with self._lock:
                self._cleanup_old_requests(api_name, config.window_seconds)

                if len(self._request_times[api_name]) < config.limit:
                    self.record_request(api_name)
                    return True

                # Calculate wait time
                oldest = min(self._request_times[api_name])
                wait_time = (oldest + config.window_seconds) - time.time()

            if not blocking:
                raise RateLimitExceededError(api_name, max(0, wait_time))

            if wait_time > 0:
                logger.debug(f"Rate limited for {api_name}, waiting {wait_time:.2f}s")
                time.sleep(min(wait_time, 1.0))  # Sleep in 1s increments
            else:
                # Shouldn't happen, but safety check
                time.sleep(0.1)

    async def acquire_async(self, api_name: str, blocking: bool = True) -> bool:
        """
        Acquire permission to make a request (async version).

        Args:
            api_name: Name of the API endpoint
            blocking: If True, wait until permission is granted.

        Returns:
            True if permission granted

        Raises:
            RateLimitExceededError: If blocking=False and rate limited
        """
        if api_name not in self.configs:
            self.record_request(api_name)
            return True

        config = self.configs[api_name]

        while True:
            with self._lock:
                self._cleanup_old_requests(api_name, config.window_seconds)

                if len(self._request_times[api_name]) < config.limit:
                    self.record_request(api_name)
                    return True

                # Calculate wait time
                oldest = min(self._request_times[api_name])
                wait_time = (oldest + config.window_seconds) - time.time()

            if not blocking:
                raise RateLimitExceededError(api_name, max(0, wait_time))

            if wait_time > 0:
                logger.debug(f"Rate limited for {api_name}, waiting {wait_time:.2f}s")
                await asyncio.sleep(min(wait_time, 1.0))
            else:
                await asyncio.sleep(0.1)

    def get_status(self, api_name: str) -> Dict[str, Any]:
        """
        Get rate limit status for an API.

        Args:
            api_name: Name of the API endpoint

        Returns:
            Dict with current usage info
        """
        from typing import Any

        if api_name not in self.configs:
            return {"configured": False}

        config = self.configs[api_name]

        with self._lock:
            self._cleanup_old_requests(api_name, config.window_seconds)
            current = len(self._request_times[api_name])

        return {
            "configured": True,
            "api_name": api_name,
            "limit": config.limit,
            "window_seconds": config.window_seconds,
            "current": current,
            "remaining": max(0, config.limit - current),
            "utilization": current / config.limit if config.limit > 0 else 0,
        }


# Global rate limiter instance
_global_limiter: Optional[RateLimiter] = None


def get_rate_limiter(
    configs: Optional[Dict[str, RateLimitConfig]] = None,
) -> RateLimiter:
    """
    Get or create global rate limiter.

    Args:
        configs: Optional custom rate limit configurations

    Returns:
        RateLimiter instance
    """
    global _global_limiter

    if _global_limiter is None:
        _global_limiter = RateLimiter(configs)

    return _global_limiter


def reset_rate_limiter() -> None:
    """Reset global rate limiter (useful for testing)."""
    global _global_limiter
    _global_limiter = None
