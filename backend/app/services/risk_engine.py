"""Risk engine for low-capital position sizing."""

from __future__ import annotations

from backend.app.models.schemas import PositionSizing, UserSettings


def calculate_stop_loss(entry_price: float, volatility: float) -> tuple[float, str]:
    """Return default stop and risk label from volatility."""
    if volatility < 0.025:
        pct = 0.05
        risk = "Low"
    elif volatility < 0.045:
        pct = 0.07
        risk = "Medium"
    else:
        pct = 0.10
        risk = "High"
    return round(entry_price * (1 - pct), 2), risk


def calculate_position_size(settings: UserSettings, entry_price: float, stop_loss_price: float) -> PositionSizing:
    """Calculate suggested shares using risk and max-position caps."""
    dollar_risk_allowed = settings.account_size * (settings.risk_per_trade_percent / 100)
    risk_per_share = entry_price - stop_loss_price
    if risk_per_share <= 0:
        return PositionSizing(
            suggested_shares=0,
            suggested_position_value=0,
            dollar_risk_allowed=round(dollar_risk_allowed, 2),
            risk_per_share=round(risk_per_share, 2),
            no_trade_reason="Risk per share is not positive.",
        )
    shares_by_risk = int(dollar_risk_allowed // risk_per_share)
    max_position_value = settings.account_size * (settings.max_position_percent / 100)
    shares_by_position_cap = int(max_position_value // entry_price)
    shares = max(0, min(shares_by_risk, shares_by_position_cap))
    return PositionSizing(
        suggested_shares=shares,
        suggested_position_value=round(shares * entry_price, 2),
        dollar_risk_allowed=round(dollar_risk_allowed, 2),
        risk_per_share=round(risk_per_share, 2),
        no_trade_reason=None if shares > 0 else "Position size rounds to zero for this account.",
    )

