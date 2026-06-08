"""Deterministic local provider used for development, tests, and Streamlit demos."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from stock_agent.data.base import DataProvider


class MockDataProvider(DataProvider):
    """Small point-in-time market dataset with liquid and avoid candidates."""

    def load_market_snapshot(self, as_of: datetime, mode: str) -> pd.DataFrame:
        """Return a deterministic market snapshot."""
        del as_of, mode
        rows = [
            ("NVDA", "NVIDIA", "Technology", 126.84, 121.7, 115.2, 128.5, 1.29, 222_000_000, 4.2, 0.04),
            ("AMD", "Advanced Micro Devices", "Technology", 164.15, 158.3, 151.4, 166.2, 1.22, 65_000_000, 5.6, 0.05),
            ("MSFT", "Microsoft", "Technology", 453.2, 449.8, 440.5, 456.9, 0.92, 22_000_000, 8.8, 0.03),
            ("AAPL", "Apple", "Technology", 212.4, 209.6, 205.7, 214.2, 1.08, 58_000_000, 3.1, 0.03),
            ("TSLA", "Tesla", "Consumer Discretionary", 177.55, 184.7, 190.2, 182.3, 1.26, 98_000_000, 7.4, 0.06),
            ("PLTR", "Palantir", "Technology", 23.42, 22.1, 20.8, 23.9, 1.33, 54_000_000, 1.18, 0.08),
            ("SPY", "SPDR S&P 500 ETF", "ETF", 537.6, 532.7, 524.1, 539.4, 1.06, 74_000_000, 4.8, 0.01),
            ("SMALL", "Small Example Co", "Industrials", 4.8, 4.6, 4.4, 5.1, 1.8, 600_000, 0.5, 0.45),
        ]
        columns = [
            "symbol",
            "name",
            "sector",
            "close",
            "sma20",
            "sma50",
            "resistance",
            "relative_volume",
            "avg_volume",
            "atr",
            "spread_pct",
        ]
        return pd.DataFrame(rows, columns=columns)

    def load_fundamentals(self, symbols: list[str], as_of: datetime) -> pd.DataFrame:
        """Return point-in-time-style fundamentals."""
        del as_of
        data = {
            "NVDA": (126.0, 53.0, 43.0, 0.2, 91.0, 43.0),
            "AMD": (13.7, 5.0, 8.0, 0.05, 3.0, 49.0),
            "MSFT": (15.0, 36.0, 31.0, 0.3, 37.0, 34.0),
            "AAPL": (2.0, 26.0, 24.0, 1.7, 154.0, 30.0),
            "TSLA": (1.0, 7.0, 3.0, 0.2, 12.0, 62.0),
            "PLTR": (21.0, 16.0, 34.0, 0.05, 12.0, 85.0),
            "SPY": (0.0, 0.0, 0.0, 0.0, 0.0, 22.0),
            "SMALL": (18.0, -12.0, -20.0, 2.1, -8.0, 0.0),
        }
        rows = [(s, *data.get(s, (5.0, 8.0, 5.0, 0.7, 10.0, 28.0))) for s in symbols]
        return pd.DataFrame(
            rows,
            columns=["symbol", "revenue_growth", "net_margin", "fcf_margin", "debt_to_equity", "roe", "pe"],
        )

    def load_macro(self, as_of: datetime) -> pd.DataFrame:
        """Return a simple macro/regime row."""
        del as_of
        return pd.DataFrame([{"market_regime": "bullish", "risk_free_rate": 0.045, "vix_proxy": 15.2}])

