"""Signal policy turns ranks into candidate ideas."""

from __future__ import annotations

from datetime import datetime

import pandas as pd


class SignalPolicy:
    """Generate long and sell/avoid ideas from ranked scores."""

    def __init__(self, long_threshold: float = 68.0, avoid_threshold: float = 45.0) -> None:
        self.long_threshold = long_threshold
        self.avoid_threshold = avoid_threshold

    def generate(self, ranked: pd.DataFrame, as_of: datetime) -> pd.DataFrame:
        """Create candidate signal rows."""
        signals = ranked.copy()
        signals["as_of"] = as_of
        signals["signal"] = "WATCH"
        signals.loc[signals["long_score"] >= self.long_threshold, "signal"] = "BUY_CANDIDATE"
        signals.loc[signals["long_score"] <= self.avoid_threshold, "signal"] = "SELL_AVOID"
        signals["rationale"] = signals.apply(self._rationale, axis=1)
        return signals

    @staticmethod
    def _rationale(row: pd.Series) -> str:
        reasons: list[str] = []
        if row["momentum_score"] >= 65:
            reasons.append("positive momentum")
        if row["quality_score"] >= 65:
            reasons.append("strong quality")
        if row["risk_score"] < 50:
            reasons.append("elevated risk")
        if row["liquidity_score"] < 50:
            reasons.append("liquidity caution")
        return ", ".join(reasons) or "mixed evidence"

