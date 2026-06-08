"""Feature generation pipeline."""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd


class FeaturePipeline:
    """Compute technical, liquidity, quality, and regime features."""

    feature_version = "features.v1"

    def transform(
        self,
        market_df: pd.DataFrame,
        fundamentals_df: pd.DataFrame,
        macro_df: pd.DataFrame,
        eligible_symbols: list[str],
        as_of: datetime,
    ) -> pd.DataFrame:
        """Build a point-in-time feature matrix."""
        del as_of
        features = market_df[market_df["symbol"].isin(eligible_symbols)].merge(
            fundamentals_df, on="symbol", how="left"
        )
        macro = macro_df.iloc[0].to_dict()
        features["above_sma20"] = (features["close"] > features["sma20"]).astype(float)
        features["above_sma50"] = (features["close"] > features["sma50"]).astype(float)
        features["momentum_score"] = (
            features["above_sma20"] * 30
            + features["above_sma50"] * 25
            + np.clip(features["relative_volume"], 0, 2) * 15
        )
        features["liquidity_score"] = np.clip(np.log10(features["avg_volume"]) * 12 - features["spread_pct"] * 30, 0, 100)
        features["quality_score"] = np.clip(
            features["revenue_growth"] * 0.4
            + features["net_margin"] * 1.2
            + features["fcf_margin"] * 0.9
            + features["roe"] * 0.35
            - features["debt_to_equity"] * 10,
            0,
            100,
        )
        features["valuation_score"] = np.where(features["pe"] <= 0, 45, np.clip(100 - features["pe"], 0, 100))
        features["risk_score"] = np.clip(90 - (features["atr"] / features["close"]) * 350 - features["spread_pct"] * 40, 0, 100)
        features["market_regime"] = macro.get("market_regime", "neutral")
        features["as_of_regime_score"] = 10 if features["market_regime"].iloc[0] == "bullish" else -5
        return features.reset_index(drop=True)

