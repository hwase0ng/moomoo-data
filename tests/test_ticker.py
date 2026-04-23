"""
Tests for ticker conversion utilities.
"""

import pytest
from moomoo_data.core.ticker import (
    fin_genius_to_moomoo,
    moomoo_to_fin_genius,
    validate_ticker_format,
    detect_market,
)


class TestFinGeniusToMoomoo:
    """Tests for fin_genius_to_moomoo conversion."""

    def test_hk_standard(self):
        """Test HK stock conversion."""
        assert fin_genius_to_moomoo("0700.HK") == "HK.00700"
        assert fin_genius_to_moomoo("9868.HK") == "HK.09868"

    def test_kl_standard(self):
        """Test KL stock conversion."""
        assert fin_genius_to_moomoo("7088.KL") == "MY.07088"
        assert fin_genius_to_moomoo("5132.KL") == "MY.05132"

    def test_a_share_shanghai(self):
        """Test Shanghai A-share conversion."""
        assert fin_genius_to_moomoo("600519") == "SH.600519"

    def test_a_share_shenzhen(self):
        """Test Shenzhen A-share conversion."""
        assert fin_genius_to_moomoo("000001") == "SZ.000001"

    def test_already_moomoo_format(self):
        """Test already in Moomoo format."""
        assert fin_genius_to_moomoo("HK.00700") == "HK.00700"
        assert fin_genius_to_moomoo("MY.07088") == "MY.07088"

    def test_us_stock(self):
        """Test US stock conversion."""
        assert fin_genius_to_moomoo("AAPL") == "US.AAPL"


class TestMoomooToFinGenius:
    """Tests for moomoo_to_fin_genius conversion."""

    def test_hk_standard(self):
        """Test HK stock conversion."""
        assert moomoo_to_fin_genius("HK.00700") == "0700.HK"
        assert moomoo_to_fin_genius("HK.09868") == "9868.HK"

    def test_kl_standard(self):
        """Test KL stock conversion."""
        assert moomoo_to_fin_genius("MY.07088") == "7088.KL"
        assert moomoo_to_fin_genius("MY.05132") == "5132.KL"

    def test_a_share(self):
        """Test A-share conversion."""
        assert moomoo_to_fin_genius("SH.600519") == "600519"
        assert moomoo_to_fin_genius("SZ.000001") == "000001"


class TestValidateTickerFormat:
    """Tests for ticker format validation."""

    def test_fin_genius_hk(self):
        """Test FinGenius HK format."""
        assert validate_ticker_format("0700.HK", "fin_genius") is True
        assert validate_ticker_format("9868.HK", "fin_genius") is True

    def test_fin_genius_kl(self):
        """Test FinGenius KL format."""
        assert validate_ticker_format("7088.KL", "fin_genius") is True

    def test_moomoo_format(self):
        """Test Moomoo format."""
        assert validate_ticker_format("HK.00700", "moomoo") is True
        assert validate_ticker_format("MY.07088", "moomoo") is True

    def test_fin_genius_format(self):
        """Test FinGenius format."""
        assert validate_ticker_format("0700.HK", "fin_genius") is True
        assert validate_ticker_format("7088.KL", "fin_genius") is True

    def test_invalid_format(self):
        """Test invalid format."""
        assert validate_ticker_format("invalid", "fin_genius") is False


class TestDetectMarket:
    """Tests for market detection."""

    def test_hk_suffix(self):
        """Test HK market detection from suffix."""
        assert detect_market("0700.HK") == "HK"
        assert detect_market("9868.HK") == "HK"

    def test_kl_suffix(self):
        """Test KL market detection from suffix."""
        assert detect_market("7088.KL") == "MY"
        assert detect_market("5132.KL") == "MY"

    def test_moomoo_hk(self):
        """Test HK market detection from Moomoo format."""
        assert detect_market("HK.00700") == "HK"

    def test_moomoo_my(self):
        """Test MY market detection from Moomoo format."""
        assert detect_market("MY.07088") == "MY"

    def test_a_share_shanghai(self):
        """Test Shanghai A-share detection."""
        assert detect_market("600519") == "SH"

    def test_a_share_shenzhen(self):
        """Test Shenzhen A-share detection."""
        assert detect_market("000001") == "SZ"

    def test_unknown(self):
        """Test unknown market."""
        assert detect_market("UNKNOWN") == "UNKNOWN"
