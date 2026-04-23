"""
Market detection and enumeration.

Determines the target market (HKSE, KLSE) from ticker format.
Only suffix format is supported (e.g., "9868.HK", "5132.KL").

Ticker conventions:
  - HKSE:     Ends with ".HK", e.g. "0700.HK", "9868.HK"
  - KLSE:     Ends with ".KL", e.g. "5132.KL", "1155.KL"

Note: A-share market is NOT supported (only available within China).
      Numeric-only codes without suffix are rejected.
"""

import re
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Market(str, Enum):
    """Supported stock markets."""

    A_SHARE = "A_SHARE"  # Deprecated - not supported outside China
    HKSE = "HKSE"
    KLSE = "KLSE"
    UNKNOWN = "UNKNOWN"


# ------------------------------------------------------------------
# Detection
# ------------------------------------------------------------------

# Strict suffix patterns only - prefix formats and numeric-only are INVALID
_HK_PATTERN = re.compile(r"^(\d{1,5})\.HK$", re.IGNORECASE)
_KL_PATTERN = re.compile(r"^(\d{1,5})\.KL$", re.IGNORECASE)


def detect_market(ticker: str) -> Market:
    """
    Return the :class:`Market` for a given ticker string.

    Only suffix format is valid:
    - "9868.HK" → HKSE ✓
    - "5132.KL" → KLSE ✓
    - "9868" → UNKNOWN ✗ (no suffix)
    - "HK.9868" → UNKNOWN ✗ (prefix, not suffix)
    - "600519" → UNKNOWN ✗ (A-share not supported)

    Examples
    --------
    >>> detect_market("9868.HK")
    <Market.HKSE: 'HKSE'>
    >>> detect_market("5132.KL")
    <Market.KLSE: 'KLSE'>
    >>> detect_market("9868")
    <Market.UNKNOWN: 'UNKNOWN'>
    """
    t = ticker.strip()

    if _HK_PATTERN.match(t):
        logger.info(f"[MarketDetector] '{ticker}' → HKSE (pattern: strict_suffix)")
        return Market.HKSE

    if _KL_PATTERN.match(t):
        logger.info(f"[MarketDetector] '{ticker}' → KLSE (pattern: strict_suffix)")
        return Market.KLSE

    # Log why detection failed
    logger.debug(
        f"[MarketDetector] '{ticker}' → UNKNOWN (invalid format, requires .HK or .KL suffix)"
    )
    return Market.UNKNOWN


def is_a_share(ticker: str) -> bool:
    """
    Return True if *ticker* is a China A-share.

    Deprecated: A-share market is not supported outside China.
    This function always returns False and logs a warning.
    """
    market = detect_market(ticker)
    if market == Market.A_SHARE:
        logger.warning(
            f"[MarketDetector] A-share format detected for '{ticker}' but NOT supported outside China"
        )
    return False


def is_hkse(ticker: str) -> bool:
    """Return True if *ticker* is listed on HKSE."""
    return detect_market(ticker) == Market.HKSE


def is_klse(ticker: str) -> bool:
    """Return True if *ticker* is listed on Bursa Malaysia (KLSE)."""
    return detect_market(ticker) == Market.KLSE


def is_international(ticker: str) -> bool:
    """Return True if *ticker* is HKSE or KLSE (non A-share)."""
    return detect_market(ticker) in (Market.HKSE, Market.KLSE)


# ------------------------------------------------------------------
# Ticker normalisation
# ------------------------------------------------------------------


def normalize_ticker_for_format(ticker: str) -> str:
    """Normalise a ticker for API consumption.

    * HK tickers with 5 digits and leading zeros are stripped to 4 digits.
    * KL tickers are returned as-is.
    """
    t = ticker.strip().upper()

    # 5-digit HK tickers: "09868.HK" -> "9868.HK"
    m = re.match(r"^0+(\d{4})\.HK$", t)
    if m:
        return f"{m.group(1)}.HK"

    return t


def get_market_label(ticker: str) -> str:
    """Return a human-readable market label for *ticker*."""
    m = detect_market(ticker)
    labels = {
        Market.A_SHARE: "China A-Share (Deprecated - Not Supported)",
        Market.HKSE: "Hong Kong (HKSE)",
        Market.KLSE: "Malaysia (KLSE/Bursa)",
        Market.UNKNOWN: "Unknown (Invalid Format)",
    }
    return labels.get(m, "Unknown")


# ------------------------------------------------------------------
# Index tickers
# ------------------------------------------------------------------

# Default index tickers per market
DEFAULT_INDEX = {
    Market.HKSE: "HK_HSImain",  # Hang Seng Index
    Market.KLSE: "KLSE",  # FTSE Bursa Malaysia KLCI
}


def get_default_index(ticker: str) -> str:
    m = detect_market(ticker)
    if m == Market.UNKNOWN:
        logger.error(
            f"[MarketDetector] Cannot get default index for invalid ticker: '{ticker}'"
        )
        return ""
    if m == Market.A_SHARE:
        logger.warning(
            f"[MarketDetector] A-share not supported, returning empty index for '{ticker}'"
        )
        return ""
    return DEFAULT_INDEX.get(m, "")


    Returns empty string for UNKNOWN or A_SHARE (not supported).
    """
    m = detect_market(ticker)
    if m == Market.UNKNOWN:
        logger.error(
            f"[MarketDetector] Cannot get yfinance index for invalid ticker: '{ticker}'"
        )
        return ""
    if m == Market.A_SHARE:
        logger.warning(
            f"[MarketDetector] A-share not supported, returning empty index for '{ticker}'"
        )
        return ""
