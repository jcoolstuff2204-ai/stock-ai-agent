"""Rule-based and optional AI explanations."""

from __future__ import annotations

from typing import Any

from backend.app.config import OPENAI_API_KEY


def build_rule_based_explanation(data: dict[str, Any]) -> dict[str, Any]:
    """Generate a transparent explanation from computed metrics."""
    bullish: list[str] = []
    bearish: list[str] = []
    if data["price_above_ma20"]:
        bullish.append("Price is above the 20-day moving average.")
    else:
        bearish.append("Price is below the 20-day moving average.")
    if data["price_above_ma50"]:
        bullish.append("Price is above the 50-day moving average.")
    else:
        bearish.append("Price is below the 50-day moving average.")
    if data["relative_strength_score"] >= 60:
        bullish.append("Recent momentum is stronger than SPY.")
    if data["volume_score"] >= 60:
        bullish.append("Recent volume is above its normal average.")
    if data["risk_level"] == "High":
        bearish.append("Volatility is elevated, so position sizing should be smaller.")
    if data["liquidity_score"] < 50:
        bearish.append("Liquidity is weak for a low-capital account.")

    summary = (
        f"{data['ticker']} is classified as {data['action_label']} with a "
        f"{data['promising_score']:.1f}/100 Promising Stock Score."
    )
    return {
        "summary": summary,
        "bullish_factors": bullish,
        "bearish_or_risk_factors": bearish,
        "risk_management_note": (
            f"Suggested size is {data['suggested_shares']} shares with stop near ${data['stop_loss']}. "
            "This protects the account from oversized single-stock risk."
        ),
        "suggested_next_action": data["next_action"],
        "warning": "This is a research signal. No outcome is guaranteed. Review before trading.",
    }


def generate_ai_explanation(signal_data: dict[str, Any]) -> dict[str, Any]:
    """Optional OpenAI placeholder. Falls back to rule-based explanations."""
    if not OPENAI_API_KEY:
        return build_rule_based_explanation(signal_data)
    # Placeholder for a future OpenAI call. The prompt must only explain computed metrics.
    return build_rule_based_explanation(signal_data)
