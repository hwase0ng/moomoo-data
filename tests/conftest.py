"""
Pytest configuration and fixtures.
"""

import pytest


@pytest.fixture
def sample_tickers():
    """Sample stock tickers for testing."""
    return {
        "hk": ["0700.HK", "9868.HK", "9988.HK"],
        "kl": ["7088.KL", "5132.KL"],
        "cn": ["600519", "000001"],
    }


@pytest.fixture
def sample_hk_ticker():
    """Sample HK ticker."""
    return "0700.HK"


@pytest.fixture
def sample_kl_ticker():
    """Sample KL ticker."""
    return "7088.KL"


@pytest.fixture
def mock_moomoo_config():
    """Mock Moomoo configuration."""
    return {
        "enabled": True,
        "host": "127.0.0.1",
        "port": 11111,
        "cache_enabled": False,
    }
