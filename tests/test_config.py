"""
Tests for configuration loading.
"""

import os
import pytest
from moomoo_data.core.config import get_config, reset_config, MoomooConfig


class TestMoomooConfig:
    """Tests for MoomooConfig."""

    def teardown_method(self):
        """Reset config after each test."""
        reset_config()

    def test_default_values(self):
        """Test default configuration values."""
        config = get_config()

        assert config.enabled is True
        assert config.host == "127.0.0.1"
        assert config.port == 11111
        assert config.permission_level == "LV1"
        assert config.timeout_seconds == 30
        assert config.max_retries == 3
        assert config.pool_size == 3

    def test_cache_defaults(self):
        """Test cache default values."""
        config = get_config()

        assert config.cache_enabled is True
        assert config.cache_backend == "sqlite"
        assert config.cache_path == "~/.cache/moomoo-data/cache.db"

    def test_rate_limit_defaults(self):
        """Test rate limit default values."""
        config = get_config()

        assert config.rate_limit_stock_quote == 30
        assert config.rate_limit_kline == 20
        assert config.rate_limit_capital_flow == 20

    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "host": "192.168.1.100",
            "port": 22222,
            "enabled": False,
        }
        config = MoomooConfig.from_dict(data)

        assert config.host == "192.168.1.100"
        assert config.port == 22222
        assert config.enabled is False

    def test_to_rate_limit_configs(self):
        """Test converting to rate limit configs."""
        config = get_config()
        rate_limits = config.to_rate_limit_configs()

        assert "stock_quote" in rate_limits
        assert "kline" in rate_limits
        assert "capital_flow" in rate_limits

        assert rate_limits["stock_quote"].limit == 30
        assert rate_limits["stock_quote"].window_seconds == 30

    def test_to_cache_config(self):
        """Test converting to cache config."""
        config = get_config()
        cache_config = config.to_cache_config()

        assert cache_config.enabled is True
        assert cache_config.backend == "sqlite"
        assert cache_config.quotes_ttl == 900


class TestConfigFromEnv:
    """Tests for environment variable configuration."""

    def teardown_method(self):
        """Clean up environment variables."""
        reset_config()
        for key in ["MOOMOO_HOST", "MOOMOO_PORT", "MOOMOO_ENABLED"]:
            if key in os.environ:
                del os.environ[key]

    def test_env_host(self):
        """Test host from environment variable."""
        os.environ["MOOMOO_HOST"] = "192.168.1.50"
        reset_config()

        config = get_config()
        assert config.host == "192.168.1.50"

    def test_env_port(self):
        """Test port from environment variable."""
        os.environ["MOOMOO_PORT"] = "22222"
        reset_config()

        config = get_config()
        assert config.port == 22222

    def test_env_enabled(self):
        """Test enabled from environment variable."""
        os.environ["MOOMOO_ENABLED"] = "false"
        reset_config()

        config = get_config()
        assert config.enabled is False
