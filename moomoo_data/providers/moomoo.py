"""
Moomoo provider implementation.

Provides data via Moomoo OpenD API.
"""

import logging
from typing import Dict, Any, List, Optional

from moomoo_data.providers.base import DataProvider
from moomoo_data.core.config import get_config

logger = logging.getLogger(__name__)


class MoomooProvider(DataProvider):
    """Data provider using Moomoo OpenD API."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Moomoo provider.

        Args:
            config: Optional configuration dict.
        """
        self._config = config or {}
        self._enabled = self._config.get("enabled", True)

    @property
    def name(self) -> str:
        return "moomoo"

    def is_available(self) -> bool:
        """Check if Moomoo is available."""
        if not self._enabled:
            return False

        # Try to test connection
        try:
            from moomoo import OpenQuoteContext
            return True
        except ImportError:
            return False

    def get_capital_distribution(
        self,
        stock_code: str,
    ) -> Dict[str, Any]:
        """Get capital distribution from Moomoo."""
        from moomoo_data.services.capital_flow import get_capital_distribution

        result = get_capital_distribution(stock_code)
        if result:
            result["_provider"] = "moomoo"
        return result or {"error": "No data available"}

    def get_capital_flow_intraday(
        self,
        stock_code: str,
    ) -> Dict[str, Any]:
        """Get intraday capital flow from Moomoo."""
        from moomoo_data.services.capital_flow import get_capital_flow

        result = get_capital_flow(stock_code)
        if result:
            result["_provider"] = "moomoo"
        return result or {"error": "No data available"}

    def get_historical_kline(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        """Get historical K-line from Moomoo."""
        from moomoo_data.services.kline import get_history_kline

        df = get_history_kline(stock_code, start_date=start_date, end_date=end_date)
        if df is not None and len(df) > 0:
            result = df.to_dict("records")
            if result:
                result[0]["_provider"] = "moomoo"
            return result
        return []
