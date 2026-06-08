"""Universe selection and liquidity filters."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class UniverseConfig:
    """Eligibility thresholds for the tradable universe."""

    min_price: float = 5.0
    min_avg_volume: int = 1_000_000
    max_spread_pct: float = 0.25
    allow_etfs: bool = True


class UniverseSelector:
    """Select symbols that are liquid enough to scan and paper trade."""

    def __init__(self, config: UniverseConfig | None = None) -> None:
        self.config = config or UniverseConfig()

    def filter(self, market_df: pd.DataFrame) -> pd.DataFrame:
        """Filter by price, volume, and spread constraints."""
        eligible = market_df[
            (market_df["close"] >= self.config.min_price)
            & (market_df["avg_volume"] >= self.config.min_avg_volume)
            & (market_df["spread_pct"] <= self.config.max_spread_pct)
        ].copy()
        if not self.config.allow_etfs:
            eligible = eligible[eligible["sector"] != "ETF"]
        return eligible.reset_index(drop=True)

