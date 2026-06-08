"""Transparent rules-based stock signal engine."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from backend.app.models.schemas import StockSignal, UserSettings
from backend.app.services.data_provider import StockDataProvider
from backend.app.services.explanation_engine import generate_ai_explanation
from backend.app.services.risk_engine import calculate_position_size, calculate_stop_loss


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    """Clamp a score."""
    return max(low, min(high, value))


def action_from_score(score: float) -> str:
    """Map score to user-safe action label."""
    if score >= 85:
        return "Strong Buy Candidate"
    if score >= 70:
        return "Buy Small / Watch"
    if score >= 55:
        return "Watchlist"
    if score >= 40:
        return "Neutral / Hold"
    return "Avoid / Sell Candidate"


class SignalEngine:
    """Compute features, scores, action labels, and rationales."""

    def __init__(self, provider: StockDataProvider | None = None) -> None:
        self.provider = provider or StockDataProvider()

    def scan(self, settings: UserSettings) -> tuple[list[StockSignal], bool]:
        """Scan a universe and return sorted signals plus demo-data mode."""
        universe = settings.universe or []
        if not universe:
            raise ValueError("Stock universe cannot be empty.")
        histories = self.provider.get_batch_price_history(universe)
        spy = self.provider.get_spy_benchmark().history
        results: list[StockSignal] = []
        demo_mode = any(item.demo_data for item in histories)
        for item in histories:
            try:
                results.append(self._analyze_one(item.ticker, item.company_name, item.history, spy, settings, item.demo_data))
            except Exception:
                continue
        return sorted(results, key=lambda row: row.promising_score, reverse=True), demo_mode

    def _analyze_one(
        self,
        ticker: str,
        company_name: str,
        history: pd.DataFrame,
        spy_history: pd.DataFrame,
        settings: UserSettings,
        demo_data: bool,
    ) -> StockSignal:
        if len(history) < 60:
            raise ValueError(f"Not enough historical data for {ticker}.")
        close = history["Close"].astype(float)
        volume = history["Volume"].astype(float)
        price = float(close.iloc[-1])
        ma20 = float(close.rolling(20).mean().iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else ma50
        ret5 = float(close.pct_change(5).iloc[-1])
        ret20 = float(close.pct_change(20).iloc[-1])
        ret60 = float(close.pct_change(60).iloc[-1])
        avg_volume = float(volume.rolling(30).mean().iloc[-1])
        recent_volume_ratio = float(volume.tail(5).mean() / avg_volume) if avg_volume else 0
        volatility = float(close.pct_change().tail(20).std() or 0)
        spy_close = spy_history["Close"].astype(float)
        spy_ret20 = float(spy_close.pct_change(20).iloc[-1]) if len(spy_close) >= 21 else 0

        momentum_score = clamp((ret5 * 180) + (ret20 * 160) + (ret60 * 80) + 45)
        volume_score = clamp(40 + recent_volume_ratio * 28)
        trend_quality = clamp((price > ma20) * 25 + (price > ma50) * 30 + (price > ma200) * 25 + 10)
        relative_strength = clamp(50 + ((ret20 - spy_ret20) * 220))
        risk_control = clamp(100 - volatility * 1250)
        liquidity_quality = clamp((math.log10(max(avg_volume, 1)) - 5.5) * 35 - max(0, settings.min_price - price) * 10)

        promising_score = (
            momentum_score * 0.30
            + volume_score * 0.20
            + trend_quality * 0.15
            + relative_strength * 0.15
            + risk_control * 0.10
            + liquidity_quality * 0.10
        )

        stop_loss, risk_level = calculate_stop_loss(price, volatility)
        sizing = calculate_position_size(settings, price, stop_loss)
        do_not_trade = False
        warnings: list[str] = []
        if settings.avoid_penny_stocks and price < max(5, settings.min_price):
            do_not_trade = True
            warnings.append("Stock is below the low-capital minimum price rule.")
        if avg_volume < settings.min_avg_volume:
            do_not_trade = True
            warnings.append("Average volume is below the liquidity rule.")
        if volatility > 0.075:
            do_not_trade = True
            warnings.append("Volatility is too high for this low-capital risk profile.")
        if sizing.suggested_shares <= 0:
            do_not_trade = True
            warnings.append(sizing.no_trade_reason or "No safe position size.")

        if do_not_trade:
            action = "Watchlist" if promising_score >= 70 else "Avoid / Sell Candidate"
        else:
            action = action_from_score(promising_score)
        entry_low = round(price * 0.995, 2)
        entry_high = round(price * 1.015, 2)
        target_price = round(price + (price - stop_loss) * 1.8, 2)
        main_reason = self._main_reason(momentum_score, volume_score, trend_quality, relative_strength, risk_level, warnings)
        next_action = "Do not trade" if do_not_trade else ("Review, then paper trade small size" if promising_score >= 70 else "Watch only")
        metrics = {
            "ticker": ticker,
            "action_label": action,
            "promising_score": round(promising_score, 1),
            "risk_level": risk_level,
            "price_above_ma20": price > ma20,
            "price_above_ma50": price > ma50,
            "volume_score": volume_score,
            "relative_strength_score": relative_strength,
            "liquidity_score": liquidity_quality,
            "suggested_shares": sizing.suggested_shares,
            "stop_loss": stop_loss,
            "next_action": next_action,
        }
        explanation = generate_ai_explanation(metrics)
        if warnings:
            explanation["warnings"] = warnings

        return StockSignal(
            ticker=ticker,
            company_name=company_name,
            price=round(price, 2),
            action_label=action,
            confidence_score=round(np.mean([trend_quality, liquidity_quality, risk_control]), 1),
            promising_score=round(promising_score, 1),
            risk_level=risk_level,
            entry_low=entry_low,
            entry_high=entry_high,
            stop_loss=stop_loss,
            target_price=target_price,
            suggested_shares=sizing.suggested_shares,
            suggested_position_value=sizing.suggested_position_value,
            main_reason=main_reason,
            explanation=explanation,
            demo_data=demo_data,
            do_not_trade=do_not_trade,
        )

    @staticmethod
    def _main_reason(
        momentum_score: float,
        volume_score: float,
        trend_quality: float,
        relative_strength: float,
        risk_level: str,
        warnings: list[str],
    ) -> str:
        if warnings:
            return warnings[0]
        reasons = []
        if momentum_score >= 65:
            reasons.append("momentum")
        if volume_score >= 65:
            reasons.append("volume")
        if trend_quality >= 65:
            reasons.append("trend")
        if relative_strength >= 60:
            reasons.append("relative strength")
        if not reasons:
            reasons.append("mixed setup")
        return f"Strongest factors: {', '.join(reasons)}. Risk: {risk_level}."
