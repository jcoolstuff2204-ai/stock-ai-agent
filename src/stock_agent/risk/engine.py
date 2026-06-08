"""Risk engine and position sizing."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from stock_agent.config import RiskSettings


class RiskEngine:
    """Apply stale-data, sizing, liquidity, and exposure caps before orders."""

    def __init__(self, settings: RiskSettings) -> None:
        self.settings = settings

    def approve_and_size(self, signals: pd.DataFrame, portfolio_state: pd.DataFrame, as_of: datetime) -> pd.DataFrame:
        """Approve candidate signals and compute target shares."""
        del portfolio_state
        approved = signals.copy()
        approved["risk_approved"] = False
        approved["risk_reason"] = "not a buy candidate"
        approved["target_shares"] = 0
        stale = (datetime.now(timezone.utc) - as_of).total_seconds() / 60 > self.settings.stale_data_minutes
        if stale:
            approved["risk_reason"] = "stale data block"
            return approved

        candidates = approved["signal"] == "BUY_CANDIDATE"
        risk_budget = self.settings.account_equity * self.settings.risk_per_trade
        max_position_value = self.settings.account_equity * self.settings.max_single_name_weight
        risk_per_share = approved["atr"].clip(lower=0.01)
        shares_by_risk = (risk_budget / risk_per_share).fillna(0).astype(int)
        shares_by_weight = (max_position_value / approved["close"]).fillna(0).astype(int)
        adv_cap = (approved["avg_volume"] * self.settings.max_adv_participation).fillna(0).astype(int)
        target = pd.concat([shares_by_risk, shares_by_weight, adv_cap], axis=1).min(axis=1)
        approved.loc[candidates, "target_shares"] = target[candidates]
        approved.loc[candidates & (target > 0), "risk_approved"] = True
        approved.loc[candidates & (target > 0), "risk_reason"] = "approved"
        approved.loc[candidates & (target <= 0), "risk_reason"] = "size below minimum"
        return approved

