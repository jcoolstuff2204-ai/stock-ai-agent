import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone

import requests
import streamlit as st

try:
    import pandas as pd
    import yfinance as yf
except Exception:
    pd = None
    yf = None


st.set_page_config(
    page_title="QuanTrade AI Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)


BRAND_CSS = """
<style>
:root {
  --rh-bg: #F7F8F6;
  --rh-card: #FFFFFF;
  --rh-ink: #0B0F0E;
  --rh-muted: #6B7280;
  --rh-line: #E5E7EB;
  --rh-green: #00C805;
  --rh-red: #FF5000;
  --rh-yellow: #F4C430;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background: var(--rh-bg) !important;
}

[data-testid="stSidebar"] {
  background: var(--rh-card) !important;
  border-right: 1px solid var(--rh-line);
}

.block-container {
  max-width: 1160px;
  padding-top: 1.35rem;
  padding-bottom: 4rem;
}

h1, h2, h3, h4, p, label, span, div {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
}

h1, h2, h3, h4 {
  color: var(--rh-ink) !important;
  letter-spacing: 0 !important;
}

p, .stCaption, [data-testid="stMarkdownContainer"] {
  color: var(--rh-muted);
}

[data-testid="stMetric"] {
  background: var(--rh-card);
  border: 1px solid var(--rh-line);
  border-radius: 14px;
  padding: 1rem;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

[data-testid="stMetricValue"] {
  color: var(--rh-ink);
  font-variant-numeric: tabular-nums;
}

button[kind="primary"], .stButton > button {
  background: var(--rh-green) !important;
  color: var(--rh-ink) !important;
  border: 0 !important;
  border-radius: 999px !important;
  font-weight: 850 !important;
  min-height: 2.8rem;
}

button[kind="primary"] *, .stButton > button * {
  color: var(--rh-ink) !important;
  font-weight: 850 !important;
}

[data-baseweb="tab"] {
  color: var(--rh-muted) !important;
  font-weight: 750 !important;
}

[data-baseweb="tab"][aria-selected="true"] {
  color: var(--rh-ink) !important;
}

[data-testid="stSidebar"] input,
[data-testid="stSidebar"] [data-baseweb="input"] {
  background: #F3F4F6 !important;
  color: var(--rh-ink) !important;
  border-color: var(--rh-line) !important;
}

[data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] {
  border-color: var(--rh-line) !important;
  border-radius: 16px !important;
  background: var(--rh-card) !important;
}

[data-testid="stDataFrame"] {
  border: 1px solid var(--rh-line);
  border-radius: 16px;
  overflow: hidden;
}

.qt-screener-note {
  background: #ECFDF3;
  border: 1px solid #BBF7D0;
  border-radius: 16px;
  color: #14532D;
  padding: 0.85rem 1rem;
  margin: 0.65rem 0 1rem;
  font-weight: 650;
}

.qt-section-kicker {
  color: var(--rh-muted);
  font-size: 0.78rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.qt-rating-buy {
  color: #087B2F;
  font-weight: 850;
}

.qt-rating-wait {
  color: #8A6500;
  font-weight: 850;
}

.qt-rating-sell {
  color: #B42318;
  font-weight: 850;
}

.qt-action-buy {
  border-left: 5px solid var(--rh-green) !important;
}

.qt-action-wait {
  border-left: 5px solid var(--rh-yellow) !important;
}

.qt-action-sell {
  border-left: 5px solid var(--rh-red) !important;
}
</style>
"""


DEFAULT_UNIVERSES = {
    "Auto: Market leaders": [
        "NVDA", "AMD", "AAPL", "MSFT", "META", "AMZN", "GOOGL", "AVGO", "TSLA", "NFLX",
        "COIN", "MSTR", "PLTR", "SMCI", "JPM", "XOM", "SPY", "QQQ", "IWM", "MARA",
    ],
    "Auto: Broad opportunity scan": [
        "NVDA", "AMD", "AAPL", "MSFT", "META", "AMZN", "GOOGL", "AVGO", "TSLA", "NFLX",
        "COIN", "MSTR", "PLTR", "SMCI", "JPM", "XOM", "SPY", "QQQ", "IWM", "MARA",
        "TSM", "MU", "ARM", "INTC", "ORCL", "CRM", "NOW", "UBER", "SHOP", "SNOW",
        "PANW", "CRWD", "NET", "DDOG", "HOOD", "SQ", "PYPL", "RBLX", "ROKU", "DKNG",
        "NKE", "DIS", "COST", "WMT", "HD", "LLY", "UNH", "JPM", "BAC", "GS",
    ],
    "Auto: AI and semiconductors": [
        "NVDA", "AMD", "AVGO", "SMCI", "ARM", "TSM", "MU", "PLTR", "SOUN", "AI",
    ],
    "Auto: Future potential": [
        "RXRX", "IONQ", "SOUN", "ASTS", "RKLB", "ENVX", "CRSP", "JOBY", "HIMS", "PLTR",
    ],
    "Auto: Small-cap momentum": [
        "RXRX", "IONQ", "SOUN", "ASTS", "RKLB", "ENVX", "JOBY", "HIMS", "ACHR", "CLSK",
        "RIOT", "MARA", "UPST", "AFRM", "SOFI", "LMND", "DNA", "OUST", "WULF", "QBTS",
    ],
    "Auto: ETFs and index pulse": [
        "SPY", "QQQ", "IWM", "DIA", "XLK", "XLF", "XLE", "SMH", "ARKK", "IBB",
    ],
}


SAMPLE_QUOTES = {
    "NVDA": (126.84, 125.75, 222_000_000, 1.29, 4.20, 123.40, 128.50, 121.70, 115.20, "strong", "positive"),
    "AMD": (164.15, 163.10, 65_000_000, 1.22, 5.60, 160.90, 166.20, 158.30, 151.40, "strong", "neutral"),
    "AAPL": (212.40, 211.80, 58_000_000, 1.08, 3.10, 207.80, 214.20, 209.60, 205.70, "neutral", "neutral"),
    "MSFT": (453.20, 452.50, 22_000_000, 0.92, 8.80, 447.40, 456.90, 449.80, 440.50, "neutral", "positive"),
    "META": (514.70, 511.90, 17_000_000, 1.18, 10.40, 502.20, 518.80, 500.30, 486.90, "strong", "positive"),
    "AMZN": (186.30, 185.50, 39_000_000, 1.15, 4.60, 181.40, 188.20, 181.10, 176.50, "strong", "positive"),
    "GOOGL": (176.80, 176.10, 27_000_000, 0.98, 3.50, 173.20, 179.40, 174.60, 169.70, "neutral", "neutral"),
    "AVGO": (143.60, 142.10, 33_000_000, 1.31, 5.20, 137.90, 144.80, 136.50, 130.40, "strong", "positive"),
    "TSLA": (177.55, 179.20, 98_000_000, 1.26, 7.40, 174.80, 182.30, 184.70, 190.20, "weak", "negative"),
    "PLTR": (23.42, 23.20, 54_000_000, 1.33, 1.18, 22.68, 23.90, 22.10, 20.80, "strong", "positive"),
    "COIN": (244.20, 241.80, 12_000_000, 1.52, 12.70, 231.50, 247.60, 232.40, 219.80, "strong", "positive"),
    "MSTR": (156.10, 154.60, 18_000_000, 1.43, 10.90, 147.20, 158.00, 146.70, 137.50, "strong", "positive"),
    "SMCI": (48.90, 49.70, 44_000_000, 1.41, 4.40, 46.10, 52.20, 51.80, 55.40, "mixed", "neutral"),
    "SPY": (537.60, 536.90, 74_000_000, 1.06, 4.80, 531.80, 539.40, 532.70, 524.10, "neutral", "neutral"),
    "QQQ": (462.20, 461.00, 49_000_000, 1.12, 5.70, 454.30, 464.60, 455.10, 445.20, "strong", "positive"),
}


FUTURE_COMPANIES = [
    ("RXRX", "Recursion Pharmaceuticals", "AI biotech", "Small cap", 42, 74, 24, "medium", 92, 78, 72, 76, 84, "AI drug-discovery pipeline and pharma partnerships"),
    ("IONQ", "IonQ", "Quantum computing", "Small cap", 78, 58, 30, "low", 88, 74, 64, 88, 90, "Enterprise quantum adoption and government demand"),
    ("SOUN", "SoundHound AI", "AI software", "Small cap", 54, 62, 18, "medium", 86, 58, 52, 82, 88, "Voice AI adoption across auto and enterprise channels"),
    ("ASTS", "AST SpaceMobile", "Space connectivity", "Small cap", 20, 35, 16, "high", 84, 83, 57, 86, 92, "Satellite-to-phone milestones and telecom partnerships"),
    ("RKLB", "Rocket Lab", "Space infrastructure", "Small cap", 31, 28, 22, "medium", 80, 76, 61, 72, 79, "Launch cadence, backlog, and Neutron development"),
    ("ENVX", "Enovix", "Battery technology", "Small cap", 65, 22, 20, "medium", 78, 70, 55, 80, 82, "Advanced battery commercialization"),
    ("CRSP", "CRISPR Therapeutics", "Biotech", "Mid cap", 36, 68, 36, "low", 75, 86, 73, 66, 70, "Gene-editing therapies and pipeline execution"),
    ("JOBY", "Joby Aviation", "Electric aviation", "Small cap", 12, 18, 28, "low", 72, 67, 54, 78, 83, "Certification progress and early air taxi operations"),
    ("HIMS", "Hims & Hers Health", "Digital health", "Mid cap", 47, 80, 42, "low", 74, 62, 69, 62, 66, "Subscription health growth and margin expansion"),
]


@dataclass(frozen=True)
class RiskProfile:
    account_size: float
    risk_per_trade_percent: float
    max_position_percent: float
    max_daily_loss_percent: float


def money(value):
    return round(float(value), 2)


def clean_tickers(text):
    return [part.strip().upper() for part in text.replace("\n", ",").split(",") if part.strip()]


def get_secret(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


def fallback_quote(symbol):
    price, vwap, avg_volume, rvol, atr, support, resistance, sma20, sma50, sector, sentiment = SAMPLE_QUOTES.get(
        symbol, (50.0, 49.7, 8_000_000, 1.0, 2.0, 47.5, 52.5, 49.0, 48.0, "neutral", "neutral")
    )
    return {
        "symbol": symbol,
        "name": symbol,
        "price": price,
        "vwap": vwap,
        "average_volume": avg_volume,
        "relative_volume": rvol,
        "spread_percent": 0.04,
        "sector_trend": sector,
        "market_alignment": "bullish",
        "news_sentiment": sentiment,
        "atr": atr,
        "support": support,
        "resistance": resistance,
        "sma20": sma20,
        "sma50": sma50,
        "source": "sample fallback",
    }


@st.cache_data(ttl=900, show_spinner=False)
def fetch_live_quote(symbol):
    if yf is None or pd is None:
        return None
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="6mo", interval="1d", auto_adjust=False)
        if history is None or history.empty or len(history) < 55:
            return None

        close = history["Close"]
        high = history["High"]
        low = history["Low"]
        volume = history["Volume"]
        price = float(close.iloc[-1])
        sma20 = float(close.rolling(20).mean().iloc[-1])
        sma50 = float(close.rolling(50).mean().iloc[-1])
        support = float(low.tail(20).min())
        resistance = float(high.tail(20).max())
        true_range = (high - low).rolling(14).mean()
        atr = float(true_range.iloc[-1]) if not true_range.empty else price * 0.03
        avg_volume = float(volume.tail(30).mean())
        relative_volume = float(volume.iloc[-1] / avg_volume) if avg_volume else 1
        vwap = float(((high + low + close) / 3).tail(5).mean())
        info = {}
        try:
            info = ticker.fast_info or {}
        except Exception:
            info = {}

        return {
            "symbol": symbol,
            "name": str(info.get("longName") or info.get("shortName") or symbol),
            "price": money(price),
            "vwap": money(vwap),
            "average_volume": int(avg_volume),
            "relative_volume": round(relative_volume, 2),
            "spread_percent": 0.04,
            "sector_trend": "strong" if price > sma20 > sma50 else "weak" if price < sma20 < sma50 else "neutral",
            "market_alignment": "neutral",
            "news_sentiment": "neutral",
            "atr": money(max(atr, price * 0.01)),
            "support": money(support),
            "resistance": money(resistance),
            "sma20": money(sma20),
            "sma50": money(sma50),
            "source": "live yfinance",
        }
    except Exception:
        return None


def get_quote(symbol, use_live_data):
    if use_live_data:
        quote = fetch_live_quote(symbol)
        if quote:
            return quote
    return fallback_quote(symbol)


def market_regime(use_live_data):
    spy = get_quote("SPY", use_live_data)
    qqq = get_quote("QQQ", use_live_data)
    bullish_count = sum(1 for item in [spy, qqq] if item["price"] > item["sma20"] > item["sma50"])
    weak_count = sum(1 for item in [spy, qqq] if item["price"] < item["sma20"])
    if bullish_count == 2:
        bias = "bullish"
    elif weak_count >= 1:
        bias = "mixed"
    else:
        bias = "neutral"
    return {
        "bias": bias,
        "participation": "active" if bias == "bullish" else "selective" if bias == "neutral" else "defensive",
        "rule": "Trade only A/B setups" if bias == "bullish" else "Reduce size and wait for confirmation" if bias == "neutral" else "Avoid weak setups and protect capital",
        "spy": spy,
        "qqq": qqq,
        "source": spy["source"],
    }


def score_trade(quote, regime):
    score = 45
    score += 12 if quote["average_volume"] >= 10_000_000 else -6
    score += 8 if quote["relative_volume"] >= 1.2 else 3 if quote["relative_volume"] >= 1.0 else -5
    score += 14 if quote["price"] > quote["sma20"] > quote["sma50"] else -10 if quote["price"] < quote["sma20"] else 0
    score += 8 if quote["price"] > quote["vwap"] else -5
    score += 8 if quote["sector_trend"] == "strong" else -6 if quote["sector_trend"] == "weak" else 1
    score += 7 if regime["bias"] == "bullish" else -6 if regime["bias"] == "mixed" else 0
    score += 4 if quote["news_sentiment"] == "positive" else -5 if quote["news_sentiment"] == "negative" else 0
    return max(0, min(100, round(score)))


def trade_grade(score):
    if score >= 88:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 68:
        return "B"
    if score >= 55:
        return "C"
    return "Avoid"


def trade_decision(score, quote):
    if quote["average_volume"] < 3_000_000:
        return "SELL / AVOID"
    if quote["relative_volume"] < 0.85 and quote["price"] < quote["resistance"]:
        return "HOLD / WATCH"
    if quote["price"] < quote["sma20"] and quote["sector_trend"] == "weak":
        return "SELL / AVOID"
    if score >= 80:
        return "BUY SETUP"
    if score >= 68:
        return "WAIT FOR TRIGGER"
    if score >= 55:
        return "HOLD / WATCH"
    return "SELL / AVOID"


def factor_grade(value):
    if value >= 94:
        return "A+"
    if value >= 88:
        return "A"
    if value >= 82:
        return "A-"
    if value >= 76:
        return "B+"
    if value >= 70:
        return "B"
    if value >= 63:
        return "B-"
    if value >= 55:
        return "C"
    if value >= 45:
        return "D"
    return "F"


def quan_rating(score, decision):
    if decision == "SELL / AVOID" or score < 55:
        return "Sell / Avoid"
    if score >= 88:
        return "Strong Buy"
    if score >= 78:
        return "Buy"
    if score >= 65:
        return "Hold"
    return "Watch"


def clamp_score(value):
    return max(0, min(100, round(value)))


def score_factors(quote, regime):
    atr_percent = quote["atr"] / max(quote["price"], 0.01)
    distance_to_resistance = (quote["resistance"] - quote["price"]) / max(quote["price"], 0.01)
    distance_to_support = (quote["price"] - quote["support"]) / max(quote["price"], 0.01)

    momentum = 50
    momentum += 18 if quote["price"] > quote["sma20"] > quote["sma50"] else -16 if quote["price"] < quote["sma20"] else 2
    momentum += 14 if quote["relative_volume"] >= 1.3 else 8 if quote["relative_volume"] >= 1.0 else -8
    momentum += 8 if quote["sector_trend"] == "strong" else -10 if quote["sector_trend"] == "weak" else 0

    technical = 50
    technical += 14 if quote["price"] > quote["vwap"] else -10
    technical += 12 if 0 <= distance_to_resistance <= 0.04 else 5 if distance_to_resistance > 0.04 else -5
    technical += 10 if distance_to_support >= 0.02 else -8
    technical += 7 if quote["price"] > quote["sma20"] else -7

    liquidity = 50
    liquidity += 24 if quote["average_volume"] >= 20_000_000 else 16 if quote["average_volume"] >= 8_000_000 else 4 if quote["average_volume"] >= 3_000_000 else -18
    liquidity += 8 if quote["spread_percent"] <= 0.08 else -8
    liquidity += 7 if quote["relative_volume"] >= 1.0 else -4

    risk_quality = 72
    risk_quality -= 22 if atr_percent > 0.08 else 12 if atr_percent > 0.05 else 2 if atr_percent > 0.03 else 0
    risk_quality -= 12 if quote["price"] < quote["sma20"] else 0
    risk_quality += 6 if distance_to_support >= 0.03 else -6

    market_timing = 55
    market_timing += 18 if regime["bias"] == "bullish" else -8 if regime["bias"] == "mixed" else 4
    market_timing += 8 if quote["market_alignment"] == "bullish" else 0
    market_timing += 6 if quote["news_sentiment"] == "positive" else -8 if quote["news_sentiment"] == "negative" else 0

    return {
        "Momentum": clamp_score(momentum),
        "Technical": clamp_score(technical),
        "Liquidity": clamp_score(liquidity),
        "Risk": clamp_score(risk_quality),
        "Timing": clamp_score(market_timing),
    }


def position_size(entry, stop, risk_profile):
    risk_budget = risk_profile.account_size * risk_profile.risk_per_trade_percent / 100
    risk_per_share = max(entry - stop, 0.01)
    shares_by_risk = int(risk_budget // risk_per_share)
    max_position_value = risk_profile.account_size * risk_profile.max_position_percent / 100
    shares_by_value = int(max_position_value // entry)
    shares = max(0, min(shares_by_risk, shares_by_value))
    return {
        "shares": shares,
        "position_value": money(shares * entry),
        "risk_per_share": money(risk_per_share),
        "max_loss": money(shares * risk_per_share),
        "risk_budget": money(risk_budget),
    }


def build_trade_plan(quote, regime, risk_profile):
    score = score_trade(quote, regime)
    factors = score_factors(quote, regime)
    entry = money(max(quote["price"], quote["resistance"] + 0.03)) if quote["price"] > quote["sma20"] else quote["price"]
    stop = money(min(quote["support"], entry - quote["atr"] * 0.7))
    risk = entry - stop
    target1 = money(entry + risk * 1.8)
    target2 = money(entry + risk * 2.8)
    sizing = position_size(entry, stop, risk_profile)
    decision = trade_decision(score, quote)
    setup = "Breakout continuation" if quote["price"] >= quote["resistance"] * 0.985 else "Trend pullback" if quote["price"] > quote["sma20"] else "Needs confirmation"

    return {
        **quote,
        "score": score,
        "grade": trade_grade(score),
        "decision": decision,
        "rating": quan_rating(score, decision),
        "factor_scores": factors,
        "factor_grades": {name: factor_grade(value) for name, value in factors.items()},
        "action_note": action_note(decision, quote),
        "setup": setup,
        "entry": entry,
        "stop": stop,
        "target1": target1,
        "target2": target2,
        "sizing": sizing,
        "regime_rule": regime["rule"],
        "invalidation": f"Skip or exit if {quote['symbol']} loses VWAP near ${quote['vwap']} with heavy selling volume.",
    }


def action_note(decision, quote):
    if decision == "BUY SETUP":
        return "Consider only if the entry trigger confirms. Do not chase above the chase zone."
    if decision == "WAIT FOR TRIGGER":
        return "Promising, but not ready. Wait for confirmation above VWAP/resistance with volume."
    if decision == "HOLD / WATCH":
        return "No fresh buy signal. If already holding, monitor trend and risk levels."
    return "Avoid new buying. If already holding, review whether the position still fits your plan."


def scan_trades(tickers, risk_profile, use_live_data, max_results):
    regime = market_regime(use_live_data)
    plans = []
    for symbol in tickers:
        quote = get_quote(symbol, use_live_data)
        plans.append(build_trade_plan(quote, regime, risk_profile))
    plans.sort(key=lambda item: item["score"], reverse=True)
    return regime, plans[:max_results]


def future_score(item, risk_tolerance):
    symbol, name, sector, market_cap, growth, margin, runway, debt, tailwind, moat, inst, valuation_risk, volatility_risk, catalyst = item
    debt_penalty = {"low": 4, "medium": 10, "high": 18}[debt]
    risk_adjust = {"Conservative": 10, "Balanced": 4, "Aggressive": 0}[risk_tolerance]
    financial = min(100, runway * 2.3) * 0.45 + margin * 0.25 + (90 - debt_penalty * 3) * 0.30
    score = growth * 0.24 + financial * 0.22 + tailwind * 0.21 + moat * 0.18 + inst * 0.15 - valuation_risk * 0.12 - volatility_risk * 0.10 - risk_adjust + 24
    action = "Starter candidate" if score >= 80 and debt != "high" else "Watchlist only" if score >= 66 else "Too speculative"
    return {
        "symbol": symbol,
        "name": name,
        "sector": sector,
        "market_cap": market_cap,
        "growth": growth,
        "financial": round(financial),
        "runway": runway,
        "debt": debt,
        "tailwind": tailwind,
        "moat": moat,
        "valuation_risk": valuation_risk,
        "volatility_risk": volatility_risk,
        "catalyst": catalyst,
        "score": max(0, min(100, round(score))),
        "action": action,
    }


def scan_future(risk_tolerance, sectors, max_results):
    selected = []
    for item in FUTURE_COMPANIES:
        if "All" in sectors or item[2] in sectors:
            selected.append(future_score(item, risk_tolerance))
    return sorted(selected, key=lambda item: item["score"], reverse=True)[:max_results]


def openai_brief(prompt):
    api_key = get_secret("OPENAI_API_KEY")
    model = get_secret("OPENAI_MODEL", "gpt-4.1-mini")
    if not api_key:
        return "AI brief unavailable until OPENAI_API_KEY is configured in Streamlit secrets."
    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "input": [
                    {
                        "role": "system",
                        "content": "You are QuanTrade, a cautious market-analysis assistant. Give concise, risk-aware insight. Never promise profit.",
                    },
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=25,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("output_text", "No AI text returned.")
    except Exception as exc:
        return f"AI brief unavailable right now: {exc}"


def render_logo():
    st.markdown("## QuanTrade")
    st.caption("AI signals for calmer trading.")


def render_header():
    with st.container(border=True):
        left, right = st.columns([0.72, 0.28], vertical_alignment="center")
        with left:
            st.caption("AI stock picker · smart signals · portfolio guard")
            st.title("Discover trade candidates before you trade.")
            st.subheader("QuanTrade scans, ranks, explains, and controls risk.")
            st.write(
                "Inspired by professional AI research tools, the agent starts with market discovery, then turns the best "
                "setups into entry triggers, stop levels, targets, and position sizes."
            )
            st.caption("For informational purposes only. Not financial advice.")
        with right:
            st.metric("Agent Mode", "Scan first")
            st.metric("Risk Posture", "No overtrade")


def render_screener_table(plans):
    rows = []
    for index, plan in enumerate(plans, start=1):
        factors = plan["factor_grades"]
        rows.append(
            {
                "Rank": index,
                "Ticker": plan["symbol"],
                "Rating": plan["rating"],
                "QuanScore": plan["score"],
                "Action": plan["decision"],
                "Momentum": factors["Momentum"],
                "Technical": factors["Technical"],
                "Liquidity": factors["Liquidity"],
                "Risk": factors["Risk"],
                "Timing": factors["Timing"],
                "Buy Above": f"${plan['entry']}",
                "Stop": f"${plan['stop']}",
                "Target 1": f"${plan['target1']}",
                "Shares": plan["sizing"]["shares"],
                "Max Loss": f"${plan['sizing']['max_loss']}",
            }
        )

    st.markdown('<div class="qt-section-kicker">Ranked Screener</div>', unsafe_allow_html=True)
    st.subheader("Top Rated Stock Setups")
    st.markdown(
        '<div class="qt-screener-note">Start here: QuanTrade scans the universe for you, ranks the best setups, '
        "and separates buy candidates from wait and sell/avoid names.</div>",
        unsafe_allow_html=True,
    )

    if pd is not None:
        frame = pd.DataFrame(rows)
        st.dataframe(frame, use_container_width=True, hide_index=True)
    else:
        for row in rows:
            st.write(row)


def passes_rating_filter(plan, rating_filter):
    if rating_filter == "All ratings":
        return True
    if rating_filter == "Buy or better":
        return plan["rating"] in ["Strong Buy", "Buy"]
    if rating_filter == "Strong Buy only":
        return plan["rating"] == "Strong Buy"
    return True


def plan_reasons(plan):
    reasons = []
    factors = plan["factor_grades"]
    if factors["Momentum"] in ["A+", "A", "A-", "B+"]:
        reasons.append("Momentum is expanding")
    if factors["Technical"] in ["A+", "A", "A-", "B+"]:
        reasons.append("Price structure is near a usable trigger")
    if factors["Liquidity"] in ["A+", "A", "A-", "B+"]:
        reasons.append("Liquidity supports execution")
    if factors["Risk"] in ["A+", "A", "A-", "B+"]:
        reasons.append("Volatility is acceptable for sizing")
    if not reasons:
        reasons.append("Signal needs cleaner confirmation")
    return reasons[:3]


def participation_label(plan):
    if plan["decision"] == "BUY SETUP":
        return "Ready only above trigger"
    if plan["decision"] == "WAIT FOR TRIGGER":
        return "Watch for confirmation"
    if plan["decision"] == "HOLD / WATCH":
        return "Do not force a trade"
    return "Avoid or reduce exposure"


def render_agent_console(regime, plans, risk_profile):
    buy_count = sum(1 for plan in plans if plan["decision"] == "BUY SETUP")
    wait_count = sum(1 for plan in plans if plan["decision"] in ["WAIT FOR TRIGGER", "HOLD / WATCH"])
    sell_count = sum(1 for plan in plans if plan["decision"] == "SELL / AVOID")
    risk_budget = money(risk_profile.account_size * risk_profile.risk_per_trade_percent / 100)
    daily_stop = money(risk_profile.account_size * risk_profile.max_daily_loss_percent / 100)
    max_new_trades = max(1, int(daily_stop // max(risk_budget, 1)))

    st.markdown('<div class="qt-section-kicker">Agent Console</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Market Regime", regime["bias"].title())
    c2.metric("Participation", regime["participation"].title())
    c3.metric("Buy Setups", buy_count)
    c4.metric("Max New Trades", max_new_trades)

    if regime["participation"] == "defensive":
        st.warning("Market is mixed/weak. The agent is in defensive mode: protect capital and ignore low-grade signals.")
    elif wait_count > buy_count * 2 and buy_count <= 1:
        st.info("Most names are not clean buy setups. Waiting is the recommended workflow until confirmation improves.")
    else:
        st.success("The scan found usable candidates. Trade only at the trigger and respect the stop.")

    st.caption(
        f"Rule: {regime['rule']} · Sell/Avoid names: {sell_count} · Risk per trade: about ${risk_budget} · "
        "The agent is designed to reduce overtrading, not maximize clicks."
    )


def render_market_movers(plans):
    rows = []
    for plan in sorted(plans, key=lambda item: item["relative_volume"], reverse=True):
        distance_from_sma20 = ((plan["price"] - plan["sma20"]) / max(plan["sma20"], 0.01)) * 100
        rows.append(
            {
                "Ticker": plan["symbol"],
                "Price": f"${plan['price']}",
                "RVOL": plan["relative_volume"],
                "Vs 20D": f"{round(distance_from_sma20, 1)}%",
                "Momentum": plan["factor_grades"]["Momentum"],
                "Rating": plan["rating"],
                "Action": plan["decision"],
            }
        )
    if pd is not None:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        for row in rows:
            st.write(row)


def render_smart_signals(plans):
    st.subheader("Smart Signals")
    st.caption("This view turns the ranked list into a short execution checklist.")
    for plan in plans[:6]:
        with st.container(border=True):
            left, right = st.columns([0.68, 0.32])
            with left:
                st.markdown(f"### {plan['symbol']} · {plan['rating']}")
                st.write(participation_label(plan))
                st.caption(" · ".join(plan_reasons(plan)))
            with right:
                st.metric("QuanScore", f"{plan['score']}/100")
            c1, c2, c3 = st.columns(3)
            c1.metric("Trigger", f"${plan['entry']}")
            c2.metric("Stop", f"${plan['stop']}")
            c3.metric("Target", f"${plan['target1']}")
            st.caption(f"Invalidation: {plan['invalidation']}")


def render_portfolio_guard(risk_profile, buy_plans):
    risk_budget = money(risk_profile.account_size * risk_profile.risk_per_trade_percent / 100)
    daily_stop = money(risk_profile.account_size * risk_profile.max_daily_loss_percent / 100)
    planned_risk = money(sum(plan["sizing"]["max_loss"] for plan in buy_plans))
    allowed = planned_risk <= daily_stop

    st.subheader("Portfolio Guard")
    c1, c2, c3 = st.columns(3)
    c1.metric("Risk Per Trade", f"${risk_budget}")
    c2.metric("Daily Stop", f"${daily_stop}")
    c3.metric("Risk If All Buys Trigger", f"${planned_risk}")
    if allowed:
        st.success("Planned buy setups fit inside the daily risk limit.")
    else:
        st.error("Too much combined risk. Reduce size or choose fewer setups before trading.")
    st.write("Execution rules:")
    st.write("- Only trade names that trigger above the entry level.")
    st.write("- Skip trades if the market regime turns defensive.")
    st.write("- Stop after the daily loss limit is reached.")
    st.write("- Exit logic matters more than entry logic: respect invalidation levels.")


def render_plan(plan):
    is_buy = plan["decision"] == "BUY SETUP"
    is_sell = plan["decision"] == "SELL / AVOID"
    with st.container(border=True):
        top_left, top_right = st.columns([0.70, 0.30])
        with top_left:
            st.subheader(f"{plan['symbol']}")
            st.markdown(f"**{plan['rating']} · {plan['decision']}**")
            st.caption(f"{plan['setup']} · QuanGrade {plan['grade']} · Data: {plan['source']}")
            if is_buy:
                st.success(plan["action_note"])
            elif is_sell:
                st.error(plan["action_note"])
            else:
                st.info(plan["action_note"])
        with top_right:
            st.metric("Trade Quality", f"{plan['score']}/100")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Buy above", f"${plan['entry']}")
        c2.metric("Stop", f"${plan['stop']}")
        c3.metric("Target 1", f"${plan['target1']}")
        c4.metric("Target 2", f"${plan['target2']}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Shares", plan["sizing"]["shares"])
        c2.metric("Position", f"${plan['sizing']['position_value']}")
        c3.metric("Max loss", f"${plan['sizing']['max_loss']}")
        c4.metric("Risk/share", f"${plan['sizing']['risk_per_share']}")

        f1, f2, f3, f4, f5 = st.columns(5)
        grades = plan["factor_grades"]
        f1.metric("Momentum", grades["Momentum"])
        f2.metric("Technical", grades["Technical"])
        f3.metric("Liquidity", grades["Liquidity"])
        f4.metric("Risk", grades["Risk"])
        f5.metric("Timing", grades["Timing"])

        if is_sell:
            st.write("Sell/Avoid logic: trend is weak, quality score is low, or liquidity/risk does not justify a fresh entry.")
        else:
            st.write(plan["invalidation"])
        st.caption("Trade with data, not emotion. Signals are informational, not financial advice.")


def render_future_card(item):
    with st.container(border=True):
        left, right = st.columns([0.70, 0.30])
        with left:
            st.subheader(f"{item['symbol']} · {item['name']}")
            st.caption(f"{item['market_cap']} · {item['sector']} · {item['action']}")
        with right:
            st.metric("Future Potential", f"{item['score']}/100")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Growth", f"{item['growth']}/100")
        c2.metric("Financial", f"{item['financial']}/100")
        c3.metric("Tailwind", f"{item['tailwind']}/100")
        c4.metric("Moat", f"{item['moat']}/100")

        st.write(f"Main catalyst: {item['catalyst']}.")
        st.caption(
            f"Risks to monitor: valuation risk {item['valuation_risk']}/100, volatility risk {item['volatility_risk']}/100, "
            f"debt risk {item['debt']}, cash runway {item['runway']} months."
        )
        st.caption("Smaller-market stocks are usually watchlist-first. Not financial advice.")


def main():
    st.markdown(BRAND_CSS, unsafe_allow_html=True)

    with st.sidebar:
        render_logo()
        st.divider()
        st.subheader("1. Run Screener")
        universe_name = st.selectbox("Market to scan", list(DEFAULT_UNIVERSES.keys()))
        st.caption(f"The agent will scan {len(DEFAULT_UNIVERSES[universe_name])} symbols from this market group.")
        use_live_data = st.toggle("Use live Yahoo Finance data when available", value=True)
        max_results = st.slider("Ranked results to show", 5, 40, 15)
        rating_filter = st.selectbox("Minimum rating", ["All ratings", "Buy or better", "Strong Buy only"])
        show_avoid = st.toggle("Show sell/avoid names", value=True)
        with st.expander("Advanced: scan my own tickers"):
            use_custom_tickers = st.checkbox("Override market scan with custom tickers", value=False)
            custom = st.text_area("Custom tickers", value=", ".join(DEFAULT_UNIVERSES[universe_name]), height=90)
        st.divider()
        st.subheader("2. Set Risk")
        account_size = st.number_input("Account size", min_value=1000.0, value=10000.0, step=500.0)
        risk_percent = st.number_input("Risk per trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
        max_position_percent = st.number_input("Max position size (%)", min_value=1.0, max_value=100.0, value=25.0, step=1.0)
        max_daily_loss_percent = st.number_input("Max daily loss (%)", min_value=0.5, max_value=10.0, value=3.0, step=0.5)
        st.divider()
        st.subheader("Optional: Future Watchlist")
        future_risk = st.selectbox("Future risk tolerance", ["Balanced", "Conservative", "Aggressive"])
        future_results = st.slider("Future names to show", 3, 9, 6)
        future_sectors = st.multiselect("Future sectors", ["All"] + sorted({item[2] for item in FUTURE_COMPANIES}), default=["All"])

    render_header()
    run_scan = st.button("Run Top-Rated Stock Scan", type="primary")

    if not run_scan and "plans" not in st.session_state:
        st.info("Choose a market universe and risk settings, then click Run Top-Rated Stock Scan.")
        st.caption("QuanTrade is a decision-support assistant. It does not guarantee outcomes.")
        return

    if run_scan:
        tickers = clean_tickers(custom) if use_custom_tickers else DEFAULT_UNIVERSES[universe_name]
        risk_profile = RiskProfile(account_size, risk_percent, max_position_percent, max_daily_loss_percent)
        with st.spinner("Scanning market, scoring setups, and building risk-aware plans..."):
            regime, plans = scan_trades(tickers, risk_profile, use_live_data, max_results)
            futures = scan_future(future_risk, future_sectors, future_results)
        st.session_state["regime"] = regime
        st.session_state["plans"] = plans
        st.session_state["futures"] = futures
        st.session_state["risk_profile"] = risk_profile
        st.session_state["last_scan"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        st.session_state["scan_universe"] = "Custom tickers" if use_custom_tickers else universe_name
        st.session_state["scanned_count"] = len(tickers)

    regime = st.session_state["regime"]
    raw_plans = st.session_state["plans"]
    plans = [plan for plan in raw_plans if passes_rating_filter(plan, rating_filter)]
    if not show_avoid:
        plans = [plan for plan in plans if plan["decision"] != "SELL / AVOID"]
    futures = st.session_state["futures"]
    risk_profile = st.session_state["risk_profile"]

    avg_score = round(sum(plan["score"] for plan in plans) / len(plans), 1) if plans else 0

    st.caption(
        f"Scanned: {st.session_state.get('scan_universe', universe_name)} · "
        f"{st.session_state.get('scanned_count', len(raw_plans))} symbols · Average QuanScore: {avg_score}/100 · "
        f"Last scan: {st.session_state['last_scan']} · Data mode: {regime['source']}"
    )

    if not plans:
        st.warning("No names match the current rating filter. Change Minimum rating or show sell/avoid names.")
        return

    render_agent_console(regime, plans, risk_profile)
    render_screener_table(plans)

    buy_plans = [plan for plan in plans if plan["decision"] == "BUY SETUP"]
    wait_plans = [plan for plan in plans if plan["decision"] in ["WAIT FOR TRIGGER", "HOLD / WATCH"]]
    sell_plans = [plan for plan in plans if plan["decision"] == "SELL / AVOID"]

    st.subheader("Trade Plan Details")
    if buy_plans:
        with st.expander("Buy-rated setups", expanded=True):
            for plan in buy_plans:
                render_plan(plan)
    else:
        st.warning("No clean buy setup found from this scan. Waiting is a valid trading decision.")

    with st.expander("Wait / Hold candidates", expanded=True):
        if wait_plans:
            for plan in wait_plans:
                render_plan(plan)
        else:
            st.caption("No wait/hold names in this scan.")

    with st.expander("Sell / Avoid candidates", expanded=show_avoid):
        if sell_plans:
            for plan in sell_plans:
                render_plan(plan)
        else:
            st.caption("No sell/avoid names in this scan.")

    st.divider()
    movers_tab, signals_tab, guard_tab, future_tab, assistant_tab = st.tabs(
        ["Market Movers", "Smart Signals", "Portfolio Guard", "Future Watchlist", "Ask AI"]
    )

    with movers_tab:
        st.subheader("Market Movers")
        st.caption("High activity names from the current scan, ranked by relative volume.")
        render_market_movers(plans)

    with signals_tab:
        render_smart_signals(plans)

    with guard_tab:
        render_portfolio_guard(risk_profile, buy_plans)

    with future_tab:
        st.subheader("Future Watchlist")
        st.caption("Longer-term opportunities are watchlist-first. They are not urgent buy/sell signals.")
        for item in futures:
            render_future_card(item)

    with assistant_tab:
        st.subheader("Ask QuanTrade")
        question = st.text_area(
            "Question",
            placeholder="Ask if a ticker is buy, sell/avoid, or wait based on this scan...",
            height=120,
        )
        if st.button("Ask AI Assistant", type="primary"):
            context = {
                "market_regime": regime["bias"],
                "participation": regime["participation"],
                "rule": regime["rule"],
                "buy_setups": [
                    {
                        "symbol": p["symbol"],
                        "rating": p["rating"],
                        "score": p["score"],
                        "factor_grades": p["factor_grades"],
                        "entry": p["entry"],
                        "stop": p["stop"],
                    }
                    for p in buy_plans
                ],
                "wait": [
                    {
                        "symbol": p["symbol"],
                        "rating": p["rating"],
                        "decision": p["decision"],
                        "score": p["score"],
                        "factor_grades": p["factor_grades"],
                    }
                    for p in wait_plans[:5]
                ],
                "sell_avoid": [
                    {
                        "symbol": p["symbol"],
                        "rating": p["rating"],
                        "score": p["score"],
                        "factor_grades": p["factor_grades"],
                    }
                    for p in sell_plans[:5]
                ],
            }
            prompt = f"User question: {question}\n\nCurrent QuanTrade buy/sell scan:\n{json.dumps(context, indent=2)}"
            st.write(openai_brief(prompt))
        st.caption("AI responses are informational and may be wrong. Verify before acting.")

    return


if __name__ == "__main__":
    main()
