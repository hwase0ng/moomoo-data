"""
Example: Capital flow analysis.

This example demonstrates how to retrieve capital flow
and capital distribution data.
"""

from moomoo_data import get_capital_flow, get_capital_distribution


def main():
    """Run example."""
    print("=" * 60)
    print("Moomoo-Data Example: Capital Flow Analysis")
    print("=" * 60)

    # Example 1: Capital distribution
    print("\n1. Getting capital distribution for Tencent (0700.HK)...")
    dist = get_capital_distribution("0700.HK")

    if dist:
        print("   Capital Inflow:")
        print(f"      Super: HK$ {dist.get('capital_in_super', 0):,.0f}")
        print(f"      Big:   HK$ {dist.get('capital_in_big', 0):,.0f}")
        print(f"      Mid:   HK$ {dist.get('capital_in_mid', 0):,.0f}")
        print(f"      Small: HK$ {dist.get('capital_in_small', 0):,.0f}")
        print("\n   Capital Outflow:")
        print(f"      Super: HK$ {dist.get('capital_out_super', 0):,.0f}")
        print(f"      Big:   HK$ {dist.get('capital_out_big', 0):,.0f}")
        print(f"      Mid:   HK$ {dist.get('capital_out_mid', 0):,.0f}")
        print(f"      Small: HK$ {dist.get('capital_out_small', 0):,.0f}")

        # Calculate net flow
        net_super = dist.get('capital_in_super', 0) - dist.get('capital_out_super', 0)
        net_big = dist.get('capital_in_big', 0) - dist.get('capital_out_big', 0)
        print(f"\n   Net Super+Big Flow: HK$ {net_super + net_big:,.0f}")
    else:
        print("   Failed to retrieve capital distribution")

    # Example 2: Capital flow
    print("\n2. Getting capital flow for Tencent (0700.HK)...")
    flow = get_capital_flow("0700.HK")

    if flow:
        print(f"   Net Inflow: HK$ {flow.get('net_inflow', 0):,.0f}")
        print(f"   Large Order Inflow: HK$ {flow.get('large_order_inflow', 0):,.0f}")
        print(f"   Large Order Outflow: HK$ {flow.get('large_order_outflow', 0):,.0f}")
    else:
        print("   Failed to retrieve capital flow")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
