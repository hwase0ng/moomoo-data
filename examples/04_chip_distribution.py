"""
Example: Chip distribution analysis.

This example demonstrates the chip distribution analysis
feature using triangular distribution model.
"""

from moomoo_data import analyze_chip_distribution


def main():
    """Run example."""
    print("=" * 60)
    print("Moomoo-Data Example: Chip Distribution Analysis")
    print("=" * 60)

    # Example: Chip analysis for Tencent
    print("\nAnalyzing chip distribution for Tencent (0700.HK)...")
    result = analyze_chip_distribution("0700.HK")

    if result:
        print(f"\n   Current Price: HK$ {result['current_price']:.2f}")
        print(f"   Average Cost:  HK$ {result['avg_cost']:.2f}")
        print(f"\n   Concentration Metrics:")
        print(f"      90% Concentration: {result['concentration_90']:.2f}%")
        print(f"      70% Concentration: {result['concentration_70']:.2f}%")
        print(f"      Level: {result['concentration_level']}")
        print(f"\n   Profit Ratio: {result['profit_ratio']:.2f}%")
        print(f"   Cost Deviation: {result['cost_deviation']:.2f}%")
        print(f"\n   Peak Prices (top 3 chip concentrations):")
        for i, price in enumerate(result['peak_prices'], 1):
            print(f"      {i}. HK$ {price:.2f}")
        print(f"\n   Analysis Period: {result['analysis_days']} days")
        print(f"   Data Source: {result['data_source']}")
    else:
        print("   Failed to analyze chip distribution")
        print("   (Requires Moomoo OpenD with historical data access)")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
