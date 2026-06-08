"""Baseline ranking model."""

from __future__ import annotations

import pandas as pd


class BaselineRanker:
    """Interpretable factor ranker with hooks for future ML models."""

    model_version = "baseline.factor_ranker.v1"

    def rank(self, features: pd.DataFrame, horizon: str = "swing") -> pd.DataFrame:
        """Return ranked symbols with long and sell/avoid scores."""
        weights = {
            "day": {"momentum_score": 0.45, "liquidity_score": 0.25, "risk_score": 0.20, "quality_score": 0.10},
            "swing": {"momentum_score": 0.35, "quality_score": 0.25, "risk_score": 0.25, "liquidity_score": 0.15},
            "long": {"quality_score": 0.45, "valuation_score": 0.20, "risk_score": 0.20, "momentum_score": 0.15},
        }
        selected = weights.get(horizon, weights["swing"])
        ranked = features.copy()
        ranked["long_score"] = sum(ranked[col] * weight for col, weight in selected.items())
        ranked["long_score"] = (ranked["long_score"] + ranked["as_of_regime_score"]).clip(0, 100).round(1)
        ranked["avoid_score"] = (100 - ranked["long_score"]).clip(0, 100).round(1)
        ranked["confidence"] = (ranked[["momentum_score", "quality_score", "risk_score"]].mean(axis=1)).round(1)
        return ranked.sort_values("long_score", ascending=False).reset_index(drop=True)

