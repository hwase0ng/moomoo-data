"""
Configuration for moomoo-data.

Uses pydantic-settings for environment variable and .env file support.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for a rate limit."""

    limit: int  # Max requests
    window_seconds: int  # Time window
    name: str = ""  # Human-readable name


@dataclass
class CacheConfig:
    """Configuration for cache."""

    enabled: bool = True
    backend: str = "memory"  # "memory", "sqlite", or "redis"
    default_ttl_seconds: int = 300  # 5 minutes
    max_size: int = 10000  # Max entries for memory cache
    sqlite_path: str = "~/.cache/moomoo-data/cache.db"

    # TTLs for specific data types
    quotes_ttl: int = 900  # 15 minutes
    kline_daily_ttl: int = 86400  # 24 hours
    kline_intraday_ttl: int = 3600  # 1 hour
    capital_flow_ttl: int = 3600  # 1 hour
    order_book_ttl: int = 300  # 5 minutes
    fundamentals_ttl: int = 604800  # 7 days

    # Redis config (if used)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_prefix: str = "moomoo:"


class MoomooConfig(BaseSettings):
    """
    Moomoo configuration with environment variable support.

    Environment variables:
        MOOMOO_HOST: OpenD gateway host (default: 127.0.0.1)
        MOOMOO_PORT: OpenD gateway port (default: 11111)
        MOOMOO_ENABLED: Enable moomoo integration (default: true)
        MOOMOO_PERMISSION_LEVEL: LV1 or LV2 (default: LV1)
        MOOMOO_TIMEOUT_SECONDS: Connection timeout (default: 30)
        MOOMOO_MAX_RETRIES: Max retry attempts (default: 3)
        MOOMOO_POOL_SIZE: Connection pool size (default: 3)
        MOOMOO_CACHE_ENABLED: Enable caching (default: true)
        MOOMOO_CACHE_PATH: SQLite cache path (default: ~/.cache/moomoo-data/cache.db)
        MOOMOO_RATE_LIMIT_QUOTE: Quote rate limit (default: 30)
        MOOMOO_RATE_LIMIT_KLINE: K-line rate limit (default: 20)
        MOOMOO_RATE_LIMIT_CAPITAL_FLOW: Capital flow rate limit (default: 20)
    """

    model_config = SettingsConfigDict(
        env_prefix="MOOMOO_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Connection settings
    enabled: bool = True
    host: str = "127.0.0.1"
    port: int = 11111
    permission_level: str = "LV1"
    timeout_seconds: int = 30
    max_retries: int = 3
    pool_size: int = 3

    # Rate limits (requests per 30 seconds)
    rate_limit_market_state: int = 8
    rate_limit_stock_quote: int = 30
    rate_limit_kline: int = 20
    rate_limit_capital_flow: int = 20
    rate_limit_order_book: int = 15

    # Cache settings
    cache_enabled: bool = True
    cache_backend: str = "sqlite"  # "memory", "sqlite", "redis"
    cache_path: str = "~/.cache/moomoo-data/cache.db"

    # Cache TTLs
    quotes_ttl_seconds: int = 900  # 15 minutes
    kline_daily_ttl_seconds: int = 86400  # 24 hours
    kline_intraday_ttl_seconds: int = 3600  # 1 hour
    capital_flow_ttl_seconds: int = 3600  # 1 hour
    order_book_ttl_seconds: int = 300  # 5 minutes
    fundamentals_ttl_seconds: int = 604800  # 7 days

    # Feature flags
    enable_broker_queue: bool = False  # Requires LV2
    enable_full_orderbook: bool = False  # Requires LV2

    def to_rate_limit_configs(self) -> Dict[str, RateLimitConfig]:
        """Convert to rate limiter config format."""
        return {
            "market_state": RateLimitConfig(
                limit=self.rate_limit_market_state,
                window_seconds=30,
                name="get_market_state()",
            ),
            "stock_quote": RateLimitConfig(
                limit=self.rate_limit_stock_quote,
                window_seconds=30,
                name="get_stock_quote()",
            ),
            "kline": RateLimitConfig(
                limit=self.rate_limit_kline,
                window_seconds=30,
                name="get_cur_kline()",
            ),
            "capital_flow": RateLimitConfig(
                limit=self.rate_limit_capital_flow,
                window_seconds=30,
                name="get_capital_flow()",
            ),
            "order_book": RateLimitConfig(
                limit=self.rate_limit_order_book,
                window_seconds=30,
                name="get_order_book()",
            ),
        }

    def to_cache_config(self) -> CacheConfig:
        """Convert to cache config format."""
        return CacheConfig(
            enabled=self.cache_enabled,
            backend=self.cache_backend,
            default_ttl_seconds=self.quotes_ttl_seconds,
            quotes_ttl=self.quotes_ttl_seconds,
            kline_daily_ttl=self.kline_daily_ttl_seconds,
            kline_intraday_ttl=self.kline_intraday_ttl_seconds,
            capital_flow_ttl=self.capital_flow_ttl_seconds,
            order_book_ttl=self.order_book_ttl_seconds,
            fundamentals_ttl=self.fundamentals_ttl_seconds,
            sqlite_path=self.cache_path,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MoomooConfig":
        """Create config from dictionary."""
        return cls(
            enabled=data.get("enabled", True),
            host=data.get("host", "127.0.0.1"),
            port=data.get("port", 11111),
            permission_level=data.get("permission_level", "LV1"),
            timeout_seconds=data.get("timeout_seconds", 30),
            max_retries=data.get("max_retries", 3),
            pool_size=data.get("pool_size", 3),
            rate_limit_market_state=data.get("rate_limit_market_state", 8),
            rate_limit_stock_quote=data.get("rate_limit_stock_quote", 30),
            rate_limit_kline=data.get("rate_limit_kline", 20),
            rate_limit_capital_flow=data.get("rate_limit_capital_flow", 20),
            rate_limit_order_book=data.get("rate_limit_order_book", 15),
            cache_enabled=data.get("cache_enabled", True),
            cache_backend=data.get("cache_backend", "sqlite"),
            cache_path=data.get("cache_path", "~/.cache/moomoo-data/cache.db"),
            quotes_ttl_seconds=data.get("quotes_ttl_seconds", 900),
            kline_daily_ttl_seconds=data.get("kline_daily_ttl_seconds", 86400),
            kline_intraday_ttl_seconds=data.get("kline_intraday_ttl_seconds", 3600),
            capital_flow_ttl_seconds=data.get("capital_flow_ttl_seconds", 3600),
            order_book_ttl_seconds=data.get("order_book_ttl_seconds", 300),
            fundamentals_ttl_seconds=data.get("fundamentals_ttl_seconds", 604800),
            enable_broker_queue=data.get("enable_broker_queue", False),
            enable_full_orderbook=data.get("enable_full_orderbook", False),
        )


# Global config instance
_global_config: Optional[MoomooConfig] = None


def get_config() -> MoomooConfig:
    """
    Get or create Moomoo config.

    Loads from environment variables or .env file on first call.

    Returns:
        MoomooConfig instance
    """
    global _global_config

    if _global_config is None:
        try:
            _global_config = MoomooConfig()
            logger.info(
                f"Loaded Moomoo config: host={_global_config.host}:{_global_config.port}"
            )
        except Exception as e:
            logger.warning(f"Failed to load Moomoo config: {e}, using defaults")
            _global_config = MoomooConfig()

    return _global_config


def reset_config() -> None:
    """Reset global config (useful for testing)."""
    global _global_config
    _global_config = None
