# moomoo-data

[![PyPI version](https://img.shields.io/pypi/v/moomoo-data.svg)](https://pypi.org/project/moomoo-data/)
[![Python versions](https://img.shields.io/pypi/pyversions/moomoo-data.svg)](https://pypi.org/project/moomoo-data/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Moomoo OpenD data provider for HKSE/KLSE markets with capital flow analysis**

A comprehensive Python library for accessing Moomoo OpenD API data, featuring:

- 📈 **Real-time quotes** for HKSE and KLSE stocks
- 📊 **K-line data** (daily, weekly, monthly, intraday)
- 💰 **Capital flow analysis** (super/big/mid/small order tracking)
- 🎯 **Chip distribution analysis** (triangular distribution model)
- 🔄 **Automatic fallback** to yfinance/akshare when Moomoo unavailable
- 💾 **Built-in caching** (memory + SQLite)
- ⚡ **Rate limiting** with configurable limits

## Installation

```bash
pip install moomoo-data
```

### Optional dependencies

```bash
# Full installation with all features
pip install moomoo-data[all]

# SQLite caching
pip install moomoo-data[cache]

# Fallback providers
pip install moomoo-data[yfinance,akshare]
```

## Requirements

- Python 3.10+
- Moomoo OpenD gateway running locally (default: `127.0.0.1:11111`)
- `moomoo-api` package (`pip install moomoo-api`)

## Quick Start

```python
from moomoo_data import get_stock_quote, get_daily_kline, get_capital_flow

# Get real-time quote
quote = get_stock_quote("0700.HK")
print(f"Price: {quote['最新价']}, Change: {quote['涨跌幅']}%")

# Get daily K-line
kline = get_daily_kline("0700.HK", count=100)
print(f"Retrieved {len(kline)} days of data")

# Get capital flow
flow = get_capital_flow("0700.HK")
print(f"Net inflow: {flow['net_inflow']}")
```

## Configuration

Configure via environment variables or `.env` file:

```bash
# Moomoo OpenD connection
MOOMOO_HOST=127.0.0.1
MOOMOO_PORT=11111
MOOMOO_ENABLED=true

# Cache settings
MOOMOO_CACHE_PATH=~/.cache/moomoo-data/cache.db
MOOMOO_CACHE_ENABLED=true

# Rate limits (requests per 30 seconds)
MOOMOO_RATE_LIMIT_QUOTE=30
MOOMOO_RATE_LIMIT_KLINE=20
```

## API Reference

### Core Functions

| Function | Description | Returns |
|----------|-------------|---------|
| `get_stock_quote(ticker)` | Real-time stock quote | Dict with OHLCV + changes |
| `get_daily_kline(ticker, count)` | Daily K-line data | pandas DataFrame |
| `get_history_kline(ticker, start, end)` | Historical K-line | pandas DataFrame |
| `get_capital_flow(ticker)` | Capital flow by order size | Dict with inflow/outflow |
| `get_capital_distribution(ticker)` | Current capital distribution | Dict with super/big/mid/small |
| `analyze_chip_distribution(ticker)` | Chip distribution analysis | Dict with avg_cost, concentration |

### Ticker Formats

Supported formats:
- **FinGenius**: `0700.HK`, `7088.KL`
- **Moomoo**: `HK.00700`, `MY.07088`
- **yfinance**: `0700.HK`, `7088.KL`
- **akshare**: `00700`, `sh600000`

The library automatically converts between formats.

## Markets Supported

| Market | Ticker Suffix | Example |
|--------|---------------|---------|
| HKSE | `.HK` | `0700.HK` (Tencent) |
| KLSE | `.KL` | `7088.KL` (Yinson) |
| A-Share | 6-digit code | `600519` (Kweichow Moutai) |

## Chip Analysis

The library includes a professional-grade chip distribution analyzer using:

- **Triangular distribution**: Spreads turnover across price range
- **L-Curve decay**: Models psychological selling behavior
- **Dynamic bin sizing**: Market-aware granularity
- **NumPy vectorization**: 100x faster than loops

```python
from moomoo_data import analyze_chip_distribution

result = analyze_chip_distribution("0700.HK")
print(f"Average cost: {result['avg_cost']}")
print(f"Concentration (90%): {result['concentration_90']}%")
print(f"Profit ratio: {result['profit_ratio']}%")
```

## Provider Fallback

When Moomoo is unavailable, the library automatically falls back to:

1. **yfinance** - Institutional holders, historical data
2. **akshare** - A-share capital flow, K-lines

```python
from moomoo_data.providers import ProviderRouter, MoomooProvider, YFinanceProvider

router = ProviderRouter([
    MoomooProvider(),
    YFinanceProvider(),
])

# Automatically uses first available provider
quote = router.get_capital_distribution("0700.HK")
print(f"Data source: {quote['_provider']}")
```

## Examples

See the `examples/` directory for:

- `01_basic_quote.py` - Real-time quotes
- `02_kline_analysis.py` - K-line data retrieval
- `03_capital_flow.py` - Capital flow analysis
- `04_chip_distribution.py` - Chip distribution visualization
- `05_provider_fallback.py` - Provider fallback demo

## Documentation

Full API documentation: [GitHub](https://github.com/hwase0ng/moomoo-data)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
