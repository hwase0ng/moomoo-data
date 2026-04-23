"""
Example: Get stock quote using moomoo-data.

This example demonstrates how to retrieve real-time quotes
for HKSE and KLSE stocks.
"""

from moomoo_data import get_stock_quote, get_multiple_quotes


def main():
    """Run example."""
    print("=" * 60)
    print("Moomoo-Data Example: Stock Quotes")
    print("=" * 60)

    # Example 1: Single stock quote (Tencent)
    print("\n1. Getting quote for Tencent (0700.HK)...")
    quote = get_stock_quote("0700.HK")

    if quote:
        print(f"   Name: {quote.get('name', 'N/A')}")
        print(f"   Price: HK$ {quote.get('最新价', 0):.2f}")
        print(f"   Change: {quote.get('涨跌幅', 0):.2f}%")
        print(f"   Volume: {quote.get('成交量', 0):,.0f}")
        print(f"   Turnover: HK$ {quote.get('成交额', 0):,.0f}")
        print(f"   Data source: {quote.get('data_source', 'unknown')}")
    else:
        print("   Failed to retrieve quote (Moomoo OpenD may not be running)")

    # Example 2: Multiple stock quotes
    print("\n2. Getting quotes for multiple stocks...")
    tickers = ["0700.HK", "9868.HK", "9988.HK"]  # Tencent, Xpeng, Alibaba
    quotes = get_multiple_quotes(tickers)

    for ticker, data in quotes.items():
        print(f"   {ticker}: HK$ {data.get('最新价', 0):.2f} ({data.get('涨跌幅', 0):.2f}%)")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)

    # Note: If Moomoo OpenD is not running, quotes will return None
    # The library gracefully handles this and logs warnings


if __name__ == "__main__":
    main()
