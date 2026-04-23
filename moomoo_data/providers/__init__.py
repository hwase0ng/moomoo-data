"""Provider abstractions for moomoo-data."""

from moomoo_data.providers.base import DataProvider
from moomoo_data.providers.moomoo import MoomooProvider

__all__ = [
    "DataProvider",
    "MoomooProvider",
]
