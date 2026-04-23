"""
Ticker format conversion utilities.

Supports bidirectional conversion between:
- FinGenius format (internal standard): 0700.HK, 7088.KL
- Moomoo format: HK.00700, MY.07088
- akshare format: 00700, sh600000
- yfinance format: 0700.HK, 7088.KL

Examples:
    >>> fin_genius_to_moomoo('0700.HK')
    'HK.00700'
    >>> moomoo_to_fin_genius('HK.00700')
    '0700.HK'
"""

import re
from typing import Optional


def fin_genius_to_moomoo(ticker: str) -> str:
    """
    Convert FinGenius ticker to Moomoo format.

    Args:
        ticker: FinGenius format ticker (e.g., '0700.HK', '7088.KL')

    Returns:
        Moomoo format ticker (e.g., 'HK.00700', 'MY.07088')

    Examples:
        '0700.HK' → 'HK.00700'
        '7088.KL' → 'MY.07088'
        '600000' → 'SH.600000'
        '000001' → 'SZ.000001'
    """
    # HK stocks
    if ticker.endswith(".HK"):
        code = ticker.replace(".HK", "").zfill(5)
        return f"HK.{code}"

    # KL/MY stocks
    elif ticker.endswith(".KL"):
        code = ticker.replace(".KL", "").zfill(5)
        return f"MY.{code}"

    # A-shares (6-digit codes)
    elif len(ticker) == 6 and ticker.isdigit():
        if ticker.startswith("6"):  # Shanghai
            return f"SH.{ticker}"
        else:  # Shenzhen
            return f"SZ.{ticker}"

    # Already in Moomoo format
    elif ticker.startswith(("HK.", "MY.", "SH.", "SZ.", "US.")):
        return ticker

    # Assume US stock or other
    else:
        return f"US.{ticker}"


def moomoo_to_fin_genius(ticker: str) -> str:
    """
    Convert Moomoo ticker to FinGenius format.

    Args:
        ticker: Moomoo format ticker (e.g., 'HK.00700', 'MY.07088')

    Returns:
        FinGenius format ticker (e.g., '0700.HK', '7088.KL')

    Examples:
        'HK.00700' → '0700.HK'
        'MY.07088' → '7088.KL'
        'SH.600000' → '600000'
        'SZ.000001' → '000001'
    """
    parts = ticker.split(".")
    if len(parts) != 2:
        return ticker  # Return as-is if unexpected format

    market, code = parts

    if market == "HK":
        # Strip leading zeros for FinGenius format (but keep at least 4 digits)
        code_clean = code.lstrip("0") or "0"
        # Pad to at least 4 digits for HK stocks
        code_clean = code_clean.zfill(4)
        return f"{code_clean}.HK"
    elif market == "MY":
        # Strip leading zeros for FinGenius format (but keep at least 4 digits)
        code_clean = code.lstrip("0") or "0"
        # Pad to at least 4 digits for KL stocks
        code_clean = code_clean.zfill(4)
        return f"{code_clean}.KL"
    elif market in ("SH", "SZ"):
        return code  # A-shares without prefix
    elif market == "US":
        return code
    else:
        return ticker


def fin_genius_to_akshare(ticker: str) -> str:
    """
    Convert FinGenius ticker to akshare format.

    Args:
        ticker: FinGenius format ticker

    Returns:
        akshare format ticker

    Examples:
        '0700.HK' → '00700'
        '600000' → 'sh600000'
        '000001' → 'sz000001'
    """
    # HK stocks (akshare uses 5-digit code without suffix)
    if ticker.endswith(".HK"):
        return ticker.replace(".HK", "").zfill(5)

    # A-shares (akshare uses lowercase prefix)
    elif len(ticker) == 6 and ticker.isdigit():
        if ticker.startswith("6"):
            return f"sh{ticker}"
        else:
            return f"sz{ticker}"

    else:
        return ticker


def akshare_to_fin_genius(code: str, market_hint: Optional[str] = None) -> str:
    """
    Convert akshare format to FinGenius.

    Args:
        code: akshare format code
        market_hint: Optional hint for ambiguous cases ('hk', 'cn')

    Returns:
        FinGenius format ticker

    Examples:
        '00700' (HK) → '0700.HK'
        'sh600000' → '600000'
        'sz000001' → '000001'
    """
    # A-shares with prefix
    if code.startswith(("sh", "sz")):
        return code[2:]  # Remove prefix

    # HK stocks (5-digit code)
    elif code.isdigit() and len(code) == 5:
        return f"{code}.HK"

    # Need market hint for ambiguous cases
    elif market_hint == "hk":
        return f"{code}.HK"
    else:
        return code


def validate_ticker_format(ticker: str, expected_source: str) -> bool:
    """
    Validate ticker format based on expected source.

    Args:
        ticker: Ticker string to validate
        expected_source: Expected source ('fin_genius', 'moomoo', 'akshare', 'yfinance')

    Returns:
        True if format is valid, False otherwise

    Examples:
        >>> validate_ticker_format('0700.HK', 'fin_genius')
        True
        >>> validate_ticker_format('HK.00700', 'moomoo')
        True
    """
    if expected_source == "fin_genius":
        # HK: 4-5 digits + .HK, KL: 4-5 digits + .KL, CN: 6 digits
        patterns = [r"^\d{4,5}\.HK$", r"^\d{4,5}\.KL$", r"^\d{6}$"]
        return any(re.match(p, ticker) for p in patterns)

    elif expected_source == "moomoo":
        # Market.Code format
        patterns = [r"^(HK|MY|SH|SZ|US|SG|JP|AU)\..+$"]
        return any(re.match(p, ticker) for p in patterns)

    elif expected_source == "akshare":
        # 5-digit HK or sh/sz + 6 digits
        patterns = [
            r"^\d{5}$",  # HK
            r"^sh\d{6}$",  # SH
            r"^sz\d{6}$",  # SZ
        ]
        return any(re.match(p, ticker) for p in patterns)

    elif expected_source == "yfinance":
        # Similar to FinGenius
        patterns = [
            r"^\d{4,5}\.HK$",
            r"^\d{4,5}\.KL$",
            r"^[A-Z\.]+$",  # US stocks
        ]
        return any(re.match(p, ticker) for p in patterns)

    return False


def detect_market(ticker: str) -> str:
    """
    Detect market from ticker format.

    Args:
        ticker: Ticker in any supported format

    Returns:
        Market code ('HK', 'MY', 'SH', 'SZ', 'US', 'UNKNOWN')

    Examples:
        >>> detect_market('0700.HK')
        'HK'
        >>> detect_market('HK.00700')
        'HK'
        >>> detect_market('7088.KL')
        'MY'
    """
    # FinGenius format
    if ticker.endswith(".HK"):
        return "HK"
    elif ticker.endswith(".KL"):
        return "MY"

    # Moomoo format
    elif ticker.startswith("HK."):
        return "HK"
    elif ticker.startswith("MY."):
        return "MY"
    elif ticker.startswith("SH."):
        return "SH"
    elif ticker.startswith("SZ."):
        return "SZ"
    elif ticker.startswith("US."):
        return "US"

    # A-share detection
    elif len(ticker) == 6 and ticker.isdigit():
        if ticker.startswith("6"):
            return "SH"
        else:
            return "SZ"

    # akshare format
    elif ticker.startswith("sh"):
        return "SH"
    elif ticker.startswith("sz"):
        return "SZ"

    return "UNKNOWN"
