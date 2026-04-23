"""
Moomoo OpenD data provider for HKSE/KLSE markets.

Provides real-time quotes, K-line data, capital flow analysis,
and chip distribution analysis via Moomoo OpenD API.
"""

from moomoo_data._version import __version__

# Core exports
from moomoo_data.core.ticker import (
    fin_genius_to_moomoo,
    moomoo_to_fin_genius,
    fin_genius_to_akshare,
    akshare_to_fin_genius,
    validate_ticker_format,
    detect_market,
)
from moomoo_data.core.markets import Market
from moomoo_data.core.config import get_config, MoomooConfig

# Infrastructure
from moomoo_data.infrastructure.rate_limiter import (
    get_rate_limiter,
    RateLimiter,
    RateLimitExceededError,
)
from moomoo_data.infrastructure.cache import MemoryCache, CacheConfig

# Services
from moomoo_data.services.quote import get_stock_quote, get_multiple_quotes
from moomoo_data.services.kline import (
    get_daily_kline,
    get_minute_kline,
    get_history_kline,
)
from moomoo_data.services.capital_flow import (
    get_capital_flow,
    get_capital_distribution,
)
from moomoo_data.services.chip_analysis import analyze_chip_distribution

__all__ = [
    # Version
    "__version__",
    # Ticker conversion
    "fin_genius_to_moomoo",
    "moomoo_to_fin_genius",
    "fin_genius_to_akshare",
    "akshare_to_fin_genius",
    "validate_ticker_format",
    "detect_market",
    # Market enum
    "Market",
    # Config
    "get_config",
    "MoomooConfig",
    # Rate limiting
    "get_rate_limiter",
    "RateLimiter",
    "RateLimitExceededError",
    # Cache
    "MemoryCache",
    "CacheConfig",
    # Quote services
    "get_stock_quote",
    "get_multiple_quotes",
    # K-line services
    "get_daily_kline",
    "get_minute_kline",
    "get_history_kline",
    # Capital flow services
    "get_capital_flow",
    "get_capital_distribution",
    # Chip analysis
    "analyze_chip_distribution",
]
