"""
Capital flow data service for moomoo-data.

Provides:
- Capital flow analysis (inflow/outflow by order size)
- Capital distribution (super/big/mid/small orders)
"""

import logging
from typing import Dict, Any, Optional

from moomoo_data.core.config import get_config
from moomoo_data.core.ticker import fin_genius_to_moomoo
from moomoo_data.infrastructure.rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)


def get_capital_flow(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get capital flow data for a stock.

    Args:
        ticker: FinGenius format ticker (e.g., '0700.HK')

    Returns:
        Dict with capital flow data or None on failure

    Example:
        {
            'code': '0700.HK',
            'net_inflow': 1000000.0,
            'large_order_inflow': 5000000.0,
            'large_order_outflow': 4000000.0,
            'medium_order_inflow': 3000000.0,
            'medium_order_outflow': 3500000.0,
            'small_order_inflow': 2000000.0,
            'small_order_outflow': 2500000.0,
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
        rate_limiter.acquire("capital_flow")

        # Convert ticker format
        moomoo_ticker = fin_genius_to_moomoo(ticker)

        # Create context
        ctx = OpenQuoteContext(host=config.host, port=config.port)
        try:
            ctx.start()

            # Get capital flow
            ret, data = ctx.get_capital_flow(moomoo_ticker)

            if ret != RET_OK or data is None:
                logger.warning(f"get_capital_flow failed for {moomoo_ticker}")
                return None

            # Parse response
            if len(data) > 0:
                row = data.iloc[-1]
                result = {
                    "code": ticker,
                    "net_inflow": float(row.get("net_inflow", 0)),
                    "large_order_inflow": float(row.get("large_inflow", 0)),
                    "large_order_outflow": float(row.get("large_outflow", 0)),
                    "medium_order_inflow": float(row.get("medium_inflow", 0)),
                    "medium_order_outflow": float(row.get("medium_outflow", 0)),
                    "small_order_inflow": float(row.get("small_inflow", 0)),
                    "small_order_outflow": float(row.get("small_outflow", 0)),
                    "update_time": row.get("update_time"),
                    "data_source": "moomoo",
                }
                return result

            return {"code": ticker, "net_inflow": 0}

        finally:
            ctx.close()

    except Exception as e:
        logger.error(f"Error getting capital flow for {ticker}: {e}")
        return None


def get_capital_distribution(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get capital distribution data (super/big/mid/small order flow).

    Args:
        ticker: FinGenius format ticker (e.g., '0700.HK')

    Returns:
        Dict with capital distribution data or None on failure

    Example:
        {
            'code': '0700.HK',
            'capital_in_super': 1000000.0,
            'capital_in_big': 2000000.0,
            'capital_in_mid': 1500000.0,
            'capital_in_small': 500000.0,
            'capital_out_super': 800000.0,
            'capital_out_big': 1800000.0,
            'capital_out_mid': 1200000.0,
            'capital_out_small': 400000.0,
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
        rate_limiter.acquire("capital_distribution")

        # Convert ticker format
        moomoo_ticker = fin_genius_to_moomoo(ticker)

        # Create context
        ctx = OpenQuoteContext(host=config.host, port=config.port)
        try:
            ctx.start()

            # Get capital distribution
            ret, data = ctx.get_capital_distribution(moomoo_ticker)

            if ret != RET_OK or data is None or len(data) == 0:
                logger.warning(f"get_capital_distribution failed for {moomoo_ticker}")
                return None

            # Parse response
            row = data.iloc[0]
            result = {
                "code": ticker,
                "capital_in_super": float(row.get("capital_in_super", 0)),
                "capital_in_big": float(row.get("capital_in_big", 0)),
                "capital_in_mid": float(row.get("capital_in_mid", 0)),
                "capital_in_small": float(row.get("capital_in_small", 0)),
                "capital_out_super": float(row.get("capital_out_super", 0)),
                "capital_out_big": float(row.get("capital_out_big", 0)),
                "capital_out_mid": float(row.get("capital_out_mid", 0)),
                "capital_out_small": float(row.get("capital_out_small", 0)),
                "update_time": row.get("update_time"),
                "data_source": "moomoo",
            }
            return result

        finally:
            ctx.close()

    except Exception as e:
        logger.error(f"Error getting capital distribution for {ticker}: {e}")
        return None
