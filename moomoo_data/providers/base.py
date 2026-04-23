"""
Abstract base class for data providers.

Provides abstraction for multiple data providers with fallback routing.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class DataProvider(ABC):
    """Abstract base class for data providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @abstractmethod
    def get_capital_distribution(
        self,
        stock_code: str,
    ) -> Dict[str, Any]:
        """
        Get capital distribution (super/big/mid/small order flow).

        Args:
            stock_code: Stock code in any common format.

        Returns:
            Dict with capital distribution data.
        """
        pass

    @abstractmethod
    def get_capital_flow_intraday(
        self,
        stock_code: str,
    ) -> Dict[str, Any]:
        """
        Get intraday capital flow (by minute).

        Args:
            stock_code: Stock code in any common format.

        Returns:
            Dict with capital flow data.
        """
        pass

    @abstractmethod
    def get_historical_kline(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        """
        Get historical K-line (OHLCV) data.

        Args:
            stock_code: Stock code in any common format.
            start_date: Start date (YYYY-MM-DD).
            end_date: End date (YYYY-MM-DD).

        Returns:
            List of K-line data with OHLCV columns.
        """
        pass

    def is_available(self) -> bool:
        """Check if provider is available."""
        return True
