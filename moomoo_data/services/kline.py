"""
K-line (candlestick) data service for moomoo-data.

Provides historical and real-time K-line data with caching and rate limiting.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd

from moomoo_data.core.config import get_config, MoomooConfig
from moomoo_data.core.ticker import fin_genius_to_moomoo
from moomoo_data.infrastructure.rate_limiter import RateLimiter, get_rate_limiter
from moomoo_data.infrastructure.cache import MemoryCache, CacheConfig, get_cache

logger = logging.getLogger(__name__)

# Map interval names to Moomoo KLType
KLTYPE_MAP = {
    "1m": "K_1M",
    "5m": "K_5M",
    "15m": "K_15M",
    "30m": "K_30M",
    "60m": "K_60M",
    "daily": "K_DAY",
    "weekly": "K_WEEK",
    "monthly": "K_MON",
}


def get_daily_kline(
    ticker: str,
    count: int = 100,
    autype: str = "qfq",
) -> Optional[pd.DataFrame]:
    """
    Get daily K-line data.

    Args:
        ticker: FinGenius format ticker (e.g., '0700.HK')
        count: Number of candles to retrieve
        autype: Adjustment type - 'qfq' (forward), 'hfq' (backward), '' (none)

    Returns:
        DataFrame with OHLCV data, or None on failure
    """
    return get_cur_kline(ticker, interval="daily", count=count, autype=autype)


def get_minute_kline(
    ticker: str,
    minutes: int = 1,
    count: int = 100,
    autype: str = "qfq",
) -> Optional[pd.DataFrame]:
    """
    Get minute-level K-line data.

    Args:
        ticker: FinGenius format ticker
        minutes: Minute interval (1, 5, 15, 30, 60)
        count: Number of candles
        autype: Adjustment type

    Returns:
        DataFrame with OHLCV data
    """
    interval_map = {
        1: "1m",
        5: "5m",
        15: "15m",
        30: "30m",
        60: "60m",
    }
    interval = interval_map.get(minutes, "1m")
    return get_cur_kline(ticker, interval=interval, count=count, autype=autype)


def get_cur_kline(
    ticker: str,
    interval: str = "daily",
    count: int = 100,
    autype: str = "qfw",
) -> Optional[pd.DataFrame]:
    """
    Get current K-line data.

    Args:
        ticker: FinGenius format ticker
        interval: K-line interval
        count: Number of candles
        autype: Adjustment type - 'qfq', 'hfq', or ''

    Returns:
        DataFrame with OHLCV data
    """
    try:
        # Import moomoo SDK
        try:
            from moomoo import OpenQuoteContext, RET_OK, KLType, AuType
        except ImportError as e:
            logger.error(f"moomoo SDK not available: {e}")
            return None

        config = get_config()

        if not config.enabled:
            logger.warning("Moomoo is disabled")
            return None

        # Validate interval
        if interval not in KLTYPE_MAP:
            logger.error(f"Invalid interval: {interval}")
            return None

        # Rate limiting
        rate_limiter = get_rate_limiter()
        rate_limiter.acquire("kline")

        # Convert ticker format
        moomoo_ticker = fin_genius_to_moomoo(ticker)

        # Map interval to KLType
        kltype_map = {
            "1m": KLType.K_1M,
            "5m": KLType.K_5M,
            "15m": KLType.K_15M,
            "30m": KLType.K_30M,
            "60m": KLType.K_60M,
            "daily": KLType.K_DAY,
            "weekly": KLType.K_WEEK,
            "monthly": KLType.K_MON,
        }
        kl_type = kltype_map[interval]

        # Map autype
        autype_map = {
            "qfq": AuType.QFQ,  # Forward adjusted
            "hfq": AuType.HFQ,  # Backward adjusted
            "": AuType.NONE,
        }
        au_type = autype_map.get(autype, AuType.QFQ)

        # Create context
        ctx = OpenQuoteContext(host=config.host, port=config.port)
        try:
            ctx.start()

            # Subscribe (required before getting data)
            ret_sub, _ = ctx.subscribe([moomoo_ticker], [kl_type], subscribe_push=False)

            if ret_sub != RET_OK:
                logger.warning(f"Subscription failed for {moomoo_ticker}")
                return None

            # Get K-line data
            ret, data = ctx.get_cur_kline(
                moomoo_ticker, num=count, ktype=kl_type, autype=au_type
            )

            if ret != RET_OK or data is None or len(data) == 0:
                logger.warning(f"get_cur_kline failed for {moomoo_ticker}")
                return None

            # Format result
            df = _format_kline(data, ticker, interval)

            logger.info(
                f"Retrieved {len(df)} {interval} candles for {ticker}, "
                f"latest: {df.iloc[-1]['close'] if len(df) > 0 else 'N/A'}"
            )
            return df

        finally:
            ctx.close()

    except Exception as e:
        logger.error(f"Error getting K-line for {ticker}: {e}")
        return None


def get_history_kline(
    ticker: str,
    interval: str = "daily",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    autype: str = "qfq",
) -> Optional[pd.DataFrame]:
    """
    Get historical K-line data.

    Args:
        ticker: FinGenius format ticker
        interval: K-line interval
        start_date: Start date in 'YYYY-MM-DD' format (defaults to 3 years ago)
        end_date: End date in 'YYYY-MM-DD' format (defaults to today)
        autype: Adjustment type

    Returns:
        DataFrame with historical OHLCV data
    """
    try:
        # Import moomoo SDK
        try:
            from moomoo import OpenQuoteContext, RET_OK, KLType, AuType
        except ImportError as e:
            logger.error(f"moomoo SDK not available: {e}")
            return None

        config = get_config()

        if not config.enabled:
            logger.warning("Moomoo is disabled")
            return None

        # Set default date range (3 years)
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=3 * 365)).strftime(
                "%Y-%m-%d"
            )

        # Validate interval
        if interval not in KLTYPE_MAP:
            logger.error(f"Invalid interval: {interval}")
            return None

        # Rate limiting
        rate_limiter = get_rate_limiter()
        rate_limiter.acquire("kline")

        # Convert ticker
        moomoo_ticker = fin_genius_to_moomoo(ticker)

        # Map interval to KLType
        kltype_map = {
            "1m": KLType.K_1M,
            "5m": KLType.K_5M,
            "15m": KLType.K_15M,
            "30m": KLType.K_30M,
            "60m": KLType.K_60M,
            "daily": KLType.K_DAY,
            "weekly": KLType.K_WEEK,
            "monthly": KLType.K_MON,
        }
        kl_type = kltype_map[interval]

        # Map autype
        autype_map = {
            "qfq": AuType.QFQ,
            "hfq": AuType.HFQ,
            "": AuType.NONE,
        }
        au_type = autype_map.get(autype, AuType.QFQ)

        # Create context
        ctx = OpenQuoteContext(host=config.host, port=config.port)
        try:
            ctx.start()

            # Subscribe
            ret_sub, _ = ctx.subscribe([moomoo_ticker], [kl_type], subscribe_push=False)

            if ret_sub != RET_OK:
                logger.warning(f"Historical subscription failed for {moomoo_ticker}")
                return None

            # Get historical data
            ret, data = ctx.request_history_kline(
                moomoo_ticker,
                ktype=kl_type,
                start_time=start_date,
                end_time=end_date,
                autype=au_type,
            )

            if ret != RET_OK or data is None or len(data) == 0:
                logger.warning(f"request_history_kline failed for {moomoo_ticker}")
                return None

            # Format result
            df = _format_kline(data, ticker, interval)

            logger.info(
                f"Retrieved {len(df)} historical {interval} candles for {ticker} "
                f"({start_date} to {end_date})"
            )
            return df

        finally:
            ctx.close()

    except Exception as e:
        logger.error(f"Error getting historical K-line for {ticker}: {e}")
        return None


def _format_kline(data: pd.DataFrame, ticker: str, interval: str) -> pd.DataFrame:
    """
    Format K-line data to standard format.

    Args:
        data: Raw DataFrame from Moomoo API
        ticker: Original FinGenius ticker
        interval: Interval string

    Returns:
        Formatted DataFrame
    """
    if len(data) == 0:
        return pd.DataFrame()

    df = data.copy()

    # Ensure time_key is properly formatted
    if "time_key" in df.columns:
        df["time_key"] = pd.to_datetime(df["time_key"])

    # Add ticker column
    df["code"] = ticker

    # Sort by time
    if "time_key" in df.columns:
        df = df.sort_values("time_key").reset_index(drop=True)

    # Standardize column names
    column_map = {
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume",
        "turnover": "amount",
        "pe_ratio": "pe_ratio",
        "turnover_rate": "turnover_rate",
        "change_rate": "change_rate",
        "last_close": "last_close",
    }

    for src, dst in column_map.items():
        if src in df.columns and dst not in df.columns:
            df[dst] = df[src]

    return df
