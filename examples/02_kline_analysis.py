"""
Example: Get K-line (candlestick) data.

This example demonstrates how to retrieve historical
daily and intraday K-line data.
"""

from moomoo_data import get_daily_kline, get_history_kline


def main():
    """Run example."""
    print("=" * 60)
    print("Moomoo-Data Example: K-line Data")
    print("=" * 60)

    # Example 1: Daily K-line (last 30 days)
    print("\n1. Getting daily K-line for Tencent (0700.HK)...")
    kline = get_daily_kline("0700.HK", count=30)

    if kline is not None and len(kline) > 0:
        print(f"   Retrieved {len(kline)} days of data")
        print(f"   Latest close: HK$ {kline.iloc[-1]['close']:.2f}")
        print(f"   Latest volume: {kline.iloc[-1]['volume']:,.0f}")
        print(f"\n   Last 5 days:")
        print(kline[["time_key", "open", "high", "low", "close", "volume"]].tail())
    else:
        print("   Failed to retrieve K-line data")

    # Example 2: Historical K-line with date range
    print("\n2. Getting historical K-line with date range...")
    hist_kline = get_history_kline(
        "0700.HK",
        interval="daily",
        start_date="2024-01-01",
        end_date="2024-12-31",
    )

    if hist_kline is not None and len(hist_kline) > 0:
        print(f"   Retrieved {len(hist_kline)} days of historical data")
        print(f"   Date range: {hist_kline.iloc[0]['time_key']} to {hist_kline.iloc[-1]['time_key']}")
        print(f"   Price range: HK$ {hist_kline['low'].min():.2f} - HK$ {hist_kline['high'].max():.2f}")
    else:
        print("   Failed to retrieve historical K-line data")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
