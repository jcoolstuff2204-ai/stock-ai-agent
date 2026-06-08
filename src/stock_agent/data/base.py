"""Data-provider interfaces."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

import pandas as pd


class DataProvider(Protocol):
    """Provider for market, fundamental, and macro data."""

    def load_market_snapshot(self, as_of: datetime, mode: str) -> pd.DataFrame:
        """Return one point-in-time tradable market snapshot."""

    def load_fundamentals(self, symbols: list[str], as_of: datetime) -> pd.DataFrame:
        """Return point-in-time fundamental metrics."""

    def load_macro(self, as_of: datetime) -> pd.DataFrame:
        """Return macro/regime features available as of the timestamp."""

