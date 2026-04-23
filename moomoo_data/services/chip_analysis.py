"""
Chip distribution analysis for moomoo-data.

Uses historical K-line data with turnover_rate to estimate chip distribution
using triangular distribution model with psychological decay (L-Curve).
"""

import logging
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd

from moomoo_data.core.config import get_config
from moomoo_data.core.ticker import fin_genius_to_moomoo
from moomoo_data.core.markets import Market
from moomoo_data.services.kline import get_history_kline

logger = logging.getLogger(__name__)


class ChipAnalyzer:
    """
    Professional-grade chip analyzer.

    Algorithm:
    1. Pre-determine global price range and create fixed-size NumPy array
    2. For each trading day:
       a. Apply L-Curve psychological decay to existing chips
       b. Distribute new turnover across [low, high] range
       c. Normalize to ensure total chips = 1.0 (100%)
    """

    def calculate_chips(
        self,
        df: pd.DataFrame,
        periods: int = 100,
        ticker: Optional[str] = None,
    ) -> pd.Series:
        """
        Calculate chip distribution using vectorized NumPy operations.

        Args:
            df: DataFrame with 'close', 'high', 'low', 'turnover_rate', 'volume' columns
            periods: Number of periods to analyze (default 100 trading days)
            ticker: Stock ticker for market detection

        Returns:
            pd.Series with price bins as index, chip concentration (0-1) as values
        """
        if df is None or len(df) == 0:
            logger.warning("Empty DataFrame provided")
            return pd.Series(dtype=float)

        # Use only last 'periods' rows
        analysis_df = df.tail(periods).copy()

        # Determine dynamic bin size based on market and price range
        avg_price = analysis_df["close"].mean()
        bin_size = self._get_bin_size(ticker, avg_price)

        logger.debug(
            f"Using bin_size={bin_size} for {ticker} (avg_price={avg_price:.2f})"
        )

        # Pre-determine global price range for fixed-size array
        min_price = np.floor(analysis_df["low"].min() / bin_size) * bin_size
        max_price = np.ceil(analysis_df["high"].max() / bin_size) * bin_size
        bins = np.arange(min_price, max_price + bin_size, bin_size)

        # Initialize chips array
        chips = np.zeros(len(bins))

        for _, row in analysis_df.iterrows():
            try:
                high = row.get("high", row["close"])
                low = row.get("low", row["close"])

                # Normalize turnover rate
                t_rate = row.get("turnover_rate", 0)

                # Convert percentage to decimal if needed
                if isinstance(t_rate, (int, float)) and t_rate > 1.0:
                    t_rate = t_rate / 100.0
                elif not isinstance(t_rate, (int, float)):
                    logger.warning(f"Invalid turnover_rate type: {type(t_rate)}")
                    continue

                if t_rate <= 0:
                    continue

                # L-Curve psychological decay
                price_levels = bins
                current_price = row["close"]
                dist = np.abs(price_levels - current_price) / current_price

                # L-Curve decay: within 5% = full decay, beyond 5% = reduced decay
                decay_weights = np.where(dist < 0.05, t_rate, t_rate * 0.7)
                chips *= 1 - decay_weights

                # Distribute turnover across price range
                mask = (bins >= low) & (bins <= high)
                active_bins_count = np.sum(mask)

                if active_bins_count > 0:
                    chips[mask] += t_rate / active_bins_count
                else:
                    idx = np.abs(bins - current_price).argmin()
                    chips[idx] += t_rate

                # Normalize
                total = chips.sum()
                if total > 0:
                    chips /= total
                else:
                    chips[:] = 1.0 / len(chips)

            except Exception as e:
                logger.warning(f"Error processing row: {e}")
                continue

        # Final normalization
        total = chips.sum()
        if total > 0:
            chips /= total

        return pd.Series(chips, index=np.round(bins, 2))

    def _get_bin_size(self, ticker: Optional[str], avg_price: float) -> float:
        """
        Dynamic bin size based on market and price tier.

        Market-specific granularity:
        - HK penny stocks (HKD 0.005-1): 0.005 bins
        - HK mid-cap (HKD 1-100): 0.10 bins
        - HK high-cap (HKD 100+): 0.50 bins
        - KL penny stocks (MYR 0.005-0.50): 0.01 bins
        - KL mid-cap (MYR 0.50-50): 0.05 bins
        """
        if not ticker:
            return self._get_bin_size_for_price(avg_price)

        try:
            # Simple market detection from ticker format
            if ticker.endswith(".HK"):
                market = Market.HKSE
            elif ticker.endswith(".KL"):
                market = Market.KLSE
            else:
                return self._get_bin_size_for_price(avg_price)

            if market == Market.HKSE:
                if avg_price < 1.0:
                    return 0.005
                elif avg_price < 100.0:
                    return 0.10
                else:
                    return 0.50

            elif market == Market.KLSE:
                if avg_price < 0.50:
                    return 0.01
                elif avg_price < 50.0:
                    return 0.05
                else:
                    return 0.50

            else:
                return self._get_bin_size_for_price(avg_price)

        except Exception as e:
            logger.warning(f"Market detection failed for {ticker}: {e}")
            return self._get_bin_size_for_price(avg_price)

    def _get_bin_size_for_price(self, avg_price: float) -> float:
        """Fallback bin size based on price alone."""
        if avg_price < 1.0:
            return 0.01
        elif avg_price < 10.0:
            return 0.05
        elif avg_price < 100.0:
            return 0.10
        else:
            return 0.50

    def analyze_distribution(
        self, chip_dist: Dict[float, float], current_price: float
    ) -> Dict[str, Any]:
        """
        Analyze chip distribution to extract key metrics.

        Args:
            chip_dist: Price -> concentration mapping
            current_price: Current stock price

        Returns:
            Dict with analysis metrics
        """
        if not chip_dist:
            return {}

        # Sort by price
        sorted_chips = sorted(chip_dist.items(), key=lambda x: x[0])
        prices = [p for p, _ in sorted_chips]
        concentrations = [c for _, c in sorted_chips]

        # Calculate weighted average cost
        avg_cost = sum(p * c for p, c in zip(prices, concentrations))

        # Calculate profit ratio
        profitable_chips = sum(
            c for p, c in zip(prices, concentrations) if p < current_price
        )
        profit_ratio = profitable_chips * 100  # As percentage

        # Calculate concentration metrics
        conc_90 = self._calculate_concentration(sorted_chips, 0.90)
        conc_70 = self._calculate_concentration(sorted_chips, 0.70)

        # Determine concentration level
        if conc_90 < 15:
            concentration_level = "高度集中"
        elif conc_90 < 25:
            concentration_level = "中度集中"
        elif conc_90 < 35:
            concentration_level = "较为分散"
        else:
            concentration_level = "高度分散"

        # Cost deviation from current price
        cost_deviation = (
            ((current_price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0
        )

        return {
            "avg_cost": round(avg_cost, 2),
            "concentration_90": round(conc_90, 2),
            "concentration_70": round(conc_70, 2),
            "profit_ratio": round(profit_ratio, 2),
            "cost_deviation": round(cost_deviation, 2),
            "concentration_level": concentration_level,
            "chip_count": len(chip_dist),
        }

    def _calculate_concentration(
        self, sorted_chips: list, target_pct: float
    ) -> float:
        """
        Calculate the price range (as percentage) containing target_pct of chips.

        Args:
            sorted_chips: List of (price, concentration) sorted by price
            target_pct: Target percentage (e.g., 0.90 for 90%)

        Returns:
            Concentration as percentage (lower = more concentrated)
        """
        if not sorted_chips:
            return 0.0

        total = sum(c for _, c in sorted_chips)
        target = total * target_pct

        min_range = float("inf")
        n = len(sorted_chips)

        for i in range(n):
            cumsum = 0
            for j in range(i, n):
                cumsum += sorted_chips[j][1]
                if cumsum >= target:
                    price_range = sorted_chips[j][0] - sorted_chips[i][0]
                    mid_price = (sorted_chips[j][0] + sorted_chips[i][0]) / 2
                    range_pct = (price_range / mid_price * 100) if mid_price > 0 else 0
                    min_range = min(min_range, range_pct)
                    break

        return min_range if min_range != float("inf") else 0.0


# Global analyzer instance
_global_analyzer = None


def get_analyzer() -> ChipAnalyzer:
    """Get or create global chip analyzer."""
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = ChipAnalyzer()
    return _global_analyzer


def analyze_chip_distribution(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get chip analysis for a stock using Moomoo data.

    Args:
        ticker: FinGenius format ticker (e.g., '0700.HK', '7088.KL')

    Returns:
        Dict with chip analysis results:
        {
            'code': '0700.HK',
            'chip_distribution': {price: concentration, ...},
            'avg_cost': float,
            'concentration_90': float,
            'concentration_70': float,
            'profit_ratio': float,
            'current_price': float,
            'data_source': 'moomoo',
            'analysis_days': int,
            'peak_prices': [list of top 3 chip peak prices]
        }
    """
    try:
        # Get historical K-line data
        df = get_history_kline(
            ticker,
            interval="daily",
            start_date=None,  # Defaults to 3 years ago
            end_date=None,  # Defaults to today
            autype="qfq",  # Forward adjusted
        )

        if df is None or len(df) == 0:
            logger.warning(f"No K-line data available for {ticker}")
            return None

        # Validate required columns
        required_cols = ["close", "turnover_rate"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            # Try to estimate turnover rate from volume
            logger.warning(f"Missing columns: {missing_cols}")
            if "volume" in df.columns:
                # Estimate turnover rate as volume / avg_volume * 0.01
                avg_volume = df["volume"].mean()
                df["turnover_rate"] = (df["volume"] / avg_volume * 0.01).clip(0, 1)
            else:
                logger.error(f"Cannot calculate turnover rate for {ticker}")
                return None

        # Get current price
        current_price = float(df["close"].iloc[-1])

        # Calculate chip distribution
        analyzer = get_analyzer()
        chips_series = analyzer.calculate_chips(df, periods=100, ticker=ticker)

        if chips_series.empty or chips_series.sum() == 0:
            logger.warning(f"Chip calculation resulted in empty distribution for {ticker}")
            return None

        # Convert to dict
        chip_dist = chips_series.to_dict()

        # Analyze distribution
        analysis = analyzer.analyze_distribution(chip_dist, current_price)

        # Identify peak prices
        peak_prices = chips_series.nlargest(3).index.tolist()

        result = {
            "code": ticker,
            "chip_distribution": chip_dist,
            "chip_series": chips_series,
            "current_price": current_price,
            "data_source": "moomoo",
            "analysis_days": min(100, len(df)),
            "peak_prices": peak_prices,
            **analysis,
        }

        logger.info(
            f"Chip analysis completed for {ticker}: "
            f"avg_cost={analysis.get('avg_cost', 0):.2f}, "
            f"current_price={current_price:.2f}, "
            f"peaks={peak_prices}"
        )

        return result

    except Exception as e:
        logger.error(f"Error in chip analysis for {ticker}: {e}")
        return None
