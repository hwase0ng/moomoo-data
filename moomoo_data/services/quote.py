"""
Stock quote service for moomoo-data.

Provides real-time quotes with caching, rate limiting, and error handling.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from moomoo_data.core.config import get_config, MoomooConfig
from moomoo_data.core.ticker import fin_genius_to_moomoo
from moomoo_data.infrastructure.rate_limiter import RateLimiter, get_rate_limiter
from moomoo_data.infrastructure.cache import MemoryCache, CacheConfig, get_cache

logger = logging.getLogger(__name__)


def get_stock_quote(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get real-time stock quote.

    Args:
        ticker: FinGenius format ticker (e.g., '0700.HK')

    Returns:
        Dict with quote data, or None on failure

    Example:
        {
            'code': '0700.HK',
            'name': 'Tencent Holdings',
            '最新价': 350.0,
            '涨跌幅': 2.5,
            '成交量': 1000000,
            '成交额': 350000000.0,
        }
    """
    try:
        # Import moomoo SDK
        try:
            from moomoo import OpenQuoteContext, RET_OK
        except ImportError as e:
            logger.error(f"moomoo SDK not available: {e}")
            return None

        config = get_config()

        if not config.enabled:
            logger.warning("Moomoo is disabled")
            return None

        # Rate limiting
        rate_limiter = get_rate_limiter()
        rate_limiter.acquire("stock_quote")

        # Convert ticker format
        moomoo_ticker = fin_genius_to_moomoo(ticker)

        # Create context
        ctx = OpenQuoteContext(host=config.host, port=config.port)
        try:
            ctx.start()

            # Get quote
            ret, data = ctx.get_stock_quote([moomoo_ticker])

            if ret != RET_OK or data is None or len(data) == 0:
                logger.warning(f"get_stock_quote failed for {moomoo_ticker}")
                return None

            # Format result
            row = data.iloc[0]
            result = {
                "code": ticker,
                "name": row.get("name", ""),
                "最新价": float(row.get("last_price", 0)),
                "涨跌幅": float(row.get("change_rate", 0)),
                "涨跌额": float(row.get("change", 0)),
                "成交量": float(row.get("volume", 0)),
                "成交额": float(row.get("turnover", 0)),
                "开盘价": float(row.get("open_price", 0)),
                "最高价": float(row.get("high_price", 0)),
                "最低价": float(row.get("low_price", 0)),
                "昨收价": float(row.get("last_close_price", 0)),
                "amplitude": float(row.get("amplitude", 0)),
                "data_source": "moomoo",
                "update_time": datetime.now(),
            }

            logger.info(f"Retrieved quote for {ticker}: {result['最新价']}")
            return result

        finally:
            ctx.close()

    except Exception as e:
        logger.error(f"Error getting quote for {ticker}: {e}")
        return None


def get_multiple_quotes(tickers: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Get quotes for multiple stocks.

    Args:
        tickers: List of FinGenius format tickers

    Returns:
        Dict mapping ticker to quote data
    """
    results = {}
    for ticker in tickers:
        quote = get_stock_quote(ticker)
        if quote:
            results[ticker] = quote
    return results
