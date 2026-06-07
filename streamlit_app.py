import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone

import requests
import streamlit as st


st.set_page_config(
    page_title="Stock AI Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


@dataclass(frozen=True)
class RiskProfile:
    account_size: float
    risk_per_trade_percent: float
    max_position_percent: float
    min_reward_risk: float = 1.8


MOCK_MARKET_DATA = [
    {
        "symbol": "NVDA",
        "name": "NVIDIA Corp.",
        "price": 126.84,
        "previous_close": 123.90,
        "vwap": 125.75,
        "average_volume": 222_000_000,
        "volume": 286_000_000,
        "relative_volume": 1.29,
        "spread_percent": 0.03,
        "sector_trend": "strong",
        "market_alignment": "bullish",
        "news_sentiment": "positive",
        "earnings_risk_days": 24,
        "atr": 4.20,
        "support": 123.40,
        "resistance": 128.50,
        "sma20": 121.70,
        "sma50": 115.20,
    },
    {
        "symbol": "AMD",
        "name": "Advanced Micro Devices",
        "price": 164.15,
        "previous_close": 160.80,
        "vwap": 163.10,
        "average_volume": 65_000_000,
        "volume": 79_000_000,
        "relative_volume": 1.22,
        "spread_percent": 0.04,
        "sector_trend": "strong",
        "market_alignment": "bullish",
        "news_sentiment": "neutral",
        "earnings_risk_days": 18,
        "atr": 5.60,
        "support": 160.90,
        "resistance": 166.20,
        "sma20": 158.30,
        "sma50": 151.40,
    },
    {
        "symbol": "MSFT",
        "name": "Microsoft Corp.",
        "price": 453.20,
        "previous_close": 451.60,
        "vwap": 452.50,
        "average_volume": 22_000_000,
        "volume": 20_300_000,
        "relative_volume": 0.92,
        "spread_percent": 0.02,
        "sector_trend": "neutral",
        "market_alignment": "bullish",
        "news_sentiment": "positive",
        "earnings_risk_days": 10,
        "atr": 8.80,
        "support": 447.40,
        "resistance": 456.90,
        "sma20": 449.80,
        "sma50": 440.50,
    },
    {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "price": 177.55,
        "previous_close": 181.15,
        "vwap": 179.20,
        "average_volume": 98_000_000,
        "volume": 123_000_000,
        "relative_volume": 1.26,
        "spread_percent": 0.05,
        "sector_trend": "weak",
        "market_alignment": "mixed",
        "news_sentiment": "negative",
        "earnings_risk_days": 31,
        "atr": 7.40,
        "support": 174.80,
        "resistance": 182.30,
        "sma20": 184.70,
        "sma50": 190.20,
    },
    {
        "symbol": "PLTR",
        "name": "Palantir Technologies",
        "price": 23.42,
        "previous_close": 22.75,
        "vwap": 23.20,
        "average_volume": 54_000_000,
        "volume": 72_000_000,
        "relative_volume": 1.33,
        "spread_percent": 0.08,
        "sector_trend": "strong",
        "market_alignment": "bullish",
        "news_sentiment": "positive",
        "earnings_risk_days": 6,
        "atr": 1.18,
        "support": 22.68,
        "resistance": 23.90,
        "sma20": 22.10,
        "sma50": 20.80,
    },
]


def money(value):
    return round(float(value), 2)


def get_secret(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


def evaluate_filters(stock):
    checks = [
        ("High liquidity", stock["average_volume"] >= 10_000_000),
        ("Healthy volume confirmation", stock["relative_volume"] >= 1.10),
        ("Tight spread", stock["spread_percent"] <= 0.08),
        ("Not too close to earnings", stock["earnings_risk_days"] >= 7),
        ("Tradable price", stock["price"] >= 10),
    ]
    passed = [name for name, ok in checks if ok]
    failed = [name for name, ok in checks if not ok]
    return {"passed": passed, "failed": failed, "all_passed": len(failed) == 0}


def detect_setup(stock, market_regime):
    above_trend = stock["price"] > stock["sma20"] > stock["sma50"]
    above_vwap = stock["price"] > stock["vwap"]
    near_breakout = stock["price"] >= stock["resistance"] * 0.985
    market_bullish = market_regime["bias"] == "bullish"
    weak_trend = stock["price"] < stock["sma20"] < stock["sma50"]

    if above_trend and above_vwap and near_breakout and market_bullish:
        return {
            "direction": "long",
            "name": "Breakout continuation",
            "entry_type": "breakout confirmation",
            "bias": "bullish",
        }

    if above_trend and above_vwap and market_bullish:
        return {
            "direction": "long",
            "name": "Pullback-to-trend continuation",
            "entry_type": "hold above VWAP/support",
            "bias": "bullish",
        }

    if weak_trend and stock["news_sentiment"] == "negative":
        return {
            "direction": "avoid",
            "name": "Weak trend with negative catalyst",
            "entry_type": "no trade",
            "bias": "bearish",
        }

    return {
        "direction": "watch",
        "name": "Needs confirmation",
        "entry_type": "wait",
        "bias": "neutral",
    }


def score_trade(stock, filters, setup, market_regime):
    score = 45
    score += 12 if filters["all_passed"] else len(filters["passed"]) * 1.5
    score += 12 if setup["direction"] == "long" else -18 if setup["direction"] == "avoid" else 0
    score += 8 if stock["market_alignment"] == "bullish" else 1 if stock["market_alignment"] == "mixed" else -8
    score += 8 if stock["sector_trend"] == "strong" else 2 if stock["sector_trend"] == "neutral" else -8
    score += 6 if stock["news_sentiment"] == "positive" else 1 if stock["news_sentiment"] == "neutral" else -8
    score += 6 if stock["relative_volume"] >= 1.25 else 3 if stock["relative_volume"] >= 1.10 else -5
    score += 5 if stock["price"] > stock["vwap"] else -5
    score += 8 if stock["price"] > stock["sma20"] > stock["sma50"] else -4
    score += 3 if market_regime["volatility"] == "normal" else -4

    if not filters["all_passed"]:
        score = min(score, 79)
    return max(0, min(100, round(score)))


def grade_score(score):
    if score >= 88:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 68:
        return "B"
    if score >= 55:
        return "C"
    return "Skip"


def decide_action(score, filters, setup):
    if setup["direction"] != "long":
        return "watch" if score >= 55 else "skip"
    if not filters["all_passed"]:
        return "watch" if score >= 68 else "skip"
    if score >= 80:
        return "trade_candidate"
    if score >= 68:
        return "watch"
    return "skip"


def calculate_position_size(entry, stop, risk_profile):
    risk_budget = risk_profile.account_size * (risk_profile.risk_per_trade_percent / 100)
    risk_per_share = max(entry - stop, 0)
    if risk_per_share <= 0:
        return {
            "shares": 0,
            "position_value": 0,
            "risk_budget": money(risk_budget),
            "risk_per_share": 0,
            "estimated_max_loss": 0,
        }

    risk_based_shares = int(risk_budget // risk_per_share)
    max_position_value = risk_profile.account_size * (risk_profile.max_position_percent / 100)
    value_based_shares = int(max_position_value // entry)
    shares = max(0, min(risk_based_shares, value_based_shares))

    return {
        "shares": shares,
        "position_value": money(shares * entry),
        "risk_budget": money(risk_budget),
        "risk_per_share": money(risk_per_share),
        "estimated_max_loss": money(shares * risk_per_share),
    }


def calculate_long_entry(stock, setup):
    if "Breakout" in setup["name"]:
        return money(max(stock["price"], stock["resistance"] + 0.05))
    return money(max(stock["price"], stock["vwap"]))


def calculate_long_stop(stock, entry):
    structure_stop = min(stock["support"], stock["vwap"] - stock["atr"] * 0.25)
    volatility_stop = entry - stock["atr"] * 0.70
    return money(min(structure_stop, volatility_stop))


def build_evidence(stock):
    evidence = []
    if stock["price"] > stock["vwap"]:
        evidence.append("Trading above VWAP")
    if stock["price"] > stock["sma20"] > stock["sma50"]:
        evidence.append("Short-term trend is above longer trend")
    if stock["relative_volume"] >= 1.10:
        evidence.append(f"Relative volume is {stock['relative_volume']}x")
    if stock["sector_trend"] == "strong":
        evidence.append("Sector trend is strong")
    if stock["market_alignment"] == "bullish":
        evidence.append("Market alignment is bullish")
    if stock["news_sentiment"] == "positive":
        evidence.append("News sentiment is positive")
    return evidence


def build_trade_plan(candidate, risk_profile):
    setup = candidate["setup"]
    is_long = setup["direction"] == "long"

    if not is_long:
        return {
            "symbol": candidate["symbol"],
            "company": candidate["name"],
            "decision": "Watch only" if candidate["action"] == "watch" else "Skip",
            "grade": candidate["grade"],
            "score": candidate["score"],
            "setup": setup["name"],
            "reason_to_wait": candidate["filters"]["failed"],
            "invalidation": "No trade until price action, market alignment, and risk filters improve.",
        }

    entry = calculate_long_entry(candidate, setup)
    stop = calculate_long_stop(candidate, entry)
    risk_per_share = entry - stop
    target1 = money(entry + risk_per_share * 1.8)
    target2 = money(entry + risk_per_share * 2.8)
    sizing = calculate_position_size(entry, stop, risk_profile)

    return {
        "symbol": candidate["symbol"],
        "company": candidate["name"],
        "decision": "Trade candidate" if candidate["action"] == "trade_candidate" else "Watch only",
        "direction": "Long",
        "grade": candidate["grade"],
        "score": candidate["score"],
        "setup": setup["name"],
        "time_horizon": "Intraday to 3 trading days",
        "entry": {
            "type": setup["entry_type"],
            "trigger": f"Buy only if {candidate['symbol']} holds above ${entry} with volume confirmation.",
            "price": entry,
            "chase_limit": money(entry + candidate["atr"] * 0.35),
        },
        "exit": {
            "stop_loss": stop,
            "target1": target1,
            "target1_action": "Sell 50% and move stop near breakeven.",
            "target2": target2,
            "target2_action": "Sell remaining or trail below VWAP/20 EMA.",
            "time_stop": "Exit if the setup does not progress within 3 trading days.",
        },
        "sizing": sizing,
        "invalidation": f"Skip or exit if price loses VWAP near ${money(candidate['vwap'])} with heavy selling volume.",
        "evidence": build_evidence(candidate),
        "warnings": candidate["filters"]["failed"],
    }


def scan_market(risk_profile):
    market_regime = {
        "bias": "bullish",
        "volatility": "normal",
        "note": "Mock regime for deployment setup. Connect live data before real trading decisions.",
    }
    candidates = []
    for stock in MOCK_MARKET_DATA:
        filters = evaluate_filters(stock)
        setup = detect_setup(stock, market_regime)
        score = score_trade(stock, filters, setup, market_regime)
        candidate = {
            **stock,
            "filters": filters,
            "setup": setup,
            "score": score,
            "grade": grade_score(score),
            "action": decide_action(score, filters, setup),
        }
        candidates.append(candidate)

    candidates.sort(key=lambda item: item["score"], reverse=True)
    plans = [build_trade_plan(candidate, risk_profile) for candidate in candidates[:5]]
    return market_regime, plans


def generate_coach_notes(plan):
    api_key = get_secret("OPENAI_API_KEY")
    model = get_secret("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key or plan["decision"] != "Trade candidate":
        return fallback_coach_notes(plan)

    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "input": [
                    {
                        "role": "system",
                        "content": (
                            "You are a cautious stock-trading assistant. You do not give guarantees. "
                            "Explain trade plans with risk first, concise wording, and clear invalidation."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "Explain this short-term trade plan in under 120 words. "
                            "Include one reason to skip if conditions weaken.\n"
                            f"{json.dumps(plan, indent=2)}"
                        ),
                    },
                ],
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("output_text") or fallback_coach_notes(plan)
    except Exception:
        return fallback_coach_notes(plan)


def fallback_coach_notes(plan):
    if plan["decision"] != "Trade candidate":
        return "No high-quality trade yet. Keep this on watch and wait for stronger confirmation."

    return (
        f"{plan['symbol']} is a {plan['grade']} setup, but only if the entry trigger confirms. "
        f"Keep risk capped near ${plan['sizing']['estimated_max_loss']}, take partial profit at target 1, "
        "and skip the trade if it loses VWAP with volume."
    )


def render_plan(plan):
    badge_color = "green" if plan["decision"] == "Trade candidate" else "orange" if plan["decision"] == "Watch only" else "red"

    with st.container(border=True):
        left, right = st.columns([3, 1])
        with left:
            st.subheader(f"{plan['symbol']} · {plan['company']}")
            st.caption(f"{plan['decision']} · {plan['setup']}")
        with right:
            st.metric("Trade Quality", f"{plan['score']}/100", plan["grade"])

        st.markdown(f":{badge_color}[{plan['decision']}]")
        st.write(generate_coach_notes(plan))

        if plan["decision"] == "Skip":
            st.warning(plan["invalidation"])
            return

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Entry", f"${plan['entry']['price']}")
        col2.metric("Stop", f"${plan['exit']['stop_loss']}")
        col3.metric("Target 1", f"${plan['exit']['target1']}")
        col4.metric("Target 2", f"${plan['exit']['target2']}")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Shares", plan["sizing"]["shares"])
        col2.metric("Position", f"${plan['sizing']['position_value']}")
        col3.metric("Max Loss", f"${plan['sizing']['estimated_max_loss']}")
        col4.metric("Risk / Share", f"${plan['sizing']['risk_per_share']}")

        st.write(plan["entry"]["trigger"])
        st.write(plan["invalidation"])

        if plan.get("evidence"):
            st.markdown("**Evidence**")
            st.write(", ".join(plan["evidence"]))

        if plan.get("warnings"):
            st.warning("Watch-only warning: " + ", ".join(plan["warnings"]))


def main():
    st.title("Stock AI Agent")
    st.caption("Short-term scanner, trade planner, risk manager, and AI trading assistant.")
    st.info("For research and paper-trading support only. This is not financial advice.")

    with st.sidebar:
        st.header("Risk Settings")
        account_size = st.number_input("Account size", min_value=1000.0, value=10000.0, step=500.0)
        risk_percent = st.number_input("Risk per trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
        max_position_percent = st.number_input("Max position size (%)", min_value=1.0, max_value=100.0, value=25.0, step=1.0)
        st.divider()
        st.caption("Deployment mode: mock market data")
        st.caption("Add live data next: Alpaca or Polygon")

    risk_profile = RiskProfile(
        account_size=account_size,
        risk_per_trade_percent=risk_percent,
        max_position_percent=max_position_percent,
    )
    market_regime, plans = scan_market(risk_profile)

    trade_candidates = sum(1 for plan in plans if plan["decision"] == "Trade candidate")
    watch_only = sum(1 for plan in plans if plan["decision"] == "Watch only")
    average_score = round(sum(plan["score"] for plan in plans) / len(plans), 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Scanned", len(MOCK_MARKET_DATA))
    c2.metric("Trade Ideas", trade_candidates)
    c3.metric("Watchlist", watch_only)
    c4.metric("Avg Score", average_score)

    st.caption(
        f"Market regime: {market_regime['bias']} · Volatility: {market_regime['volatility']} · "
        f"Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )

    for plan in plans:
        render_plan(plan)


if __name__ == "__main__":
    main()
