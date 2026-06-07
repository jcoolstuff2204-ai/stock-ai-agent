import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from textwrap import dedent

import requests
import streamlit as st


st.set_page_config(
    page_title="QuanTrade AI Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)


BRAND_CSS = """
<style>
:root {
  --midnight-navy: #0B1020;
  --card-dark: #111827;
  --electric-cyan: #00E5FF;
  --ai-purple: #7C3AED;
  --profit-green: #22C55E;
  --risk-red: #EF4444;
  --soft-gray: #CBD5E1;
  --deep-border: #334155;
  --muted-panel: #0F172A;
  --brand-gradient: linear-gradient(135deg, #00E5FF 0%, #7C3AED 100%);
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background: radial-gradient(circle at top left, rgba(0, 229, 255, 0.10), transparent 30%),
    radial-gradient(circle at top right, rgba(124, 58, 237, 0.12), transparent 34%),
    var(--midnight-navy) !important;
}

[data-testid="stSidebar"] {
  background: #080D1B !important;
  border-right: 1px solid var(--deep-border);
}

[data-testid="stSidebar"] * {
  color: var(--soft-gray);
}

.block-container {
  max-width: 1220px;
  padding-top: 2.2rem;
  padding-bottom: 4rem;
}

h1, h2, h3, h4, p, label, span, div {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
}

h1, h2, h3 {
  color: #FFFFFF !important;
  font-weight: 800 !important;
  letter-spacing: 0 !important;
}

p, .stCaption, [data-testid="stMarkdownContainer"] {
  color: var(--soft-gray);
}

button[kind="primary"], .stButton > button {
  background: var(--electric-cyan) !important;
  color: var(--midnight-navy) !important;
  border: 0 !important;
  border-radius: 14px !important;
  font-weight: 800 !important;
  min-height: 2.8rem;
  box-shadow: 0 0 22px rgba(0, 229, 255, 0.24);
}

button[kind="primary"] *, .stButton > button * {
  color: var(--midnight-navy) !important;
  font-weight: 850 !important;
}

button[kind="secondary"] {
  background: var(--card-dark) !important;
  color: var(--soft-gray) !important;
  border: 1px solid var(--deep-border) !important;
  border-radius: 14px !important;
  font-weight: 700 !important;
}

[data-testid="stMetric"] {
  background: var(--card-dark);
  border: 1px solid var(--deep-border);
  border-radius: 20px;
  padding: 1rem;
}

[data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
  font-variant-numeric: tabular-nums;
}

.qt-hero {
  position: relative;
  overflow: hidden;
  padding: 2rem;
  border: 1px solid rgba(0, 229, 255, 0.28);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(17, 24, 39, 0.96), rgba(11, 16, 32, 0.92)),
    radial-gradient(circle at 85% 20%, rgba(124, 58, 237, 0.28), transparent 30%);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.30);
}

.qt-hero::after {
  content: "";
  position: absolute;
  inset: auto -10% -38% 52%;
  height: 260px;
  background: var(--brand-gradient);
  filter: blur(70px);
  opacity: 0.22;
}

.qt-brand-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.qt-logo {
  width: 64px;
  height: 64px;
  flex: 0 0 auto;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: #0B1020;
  border: 1px solid rgba(0, 229, 255, 0.32);
  box-shadow: 0 0 28px rgba(0, 229, 255, 0.18);
}

.qt-logo svg {
  width: 42px;
  height: 42px;
}

.qt-eyebrow {
  color: var(--electric-cyan);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.qt-title {
  margin: 0.6rem 0 0.3rem;
  color: #FFFFFF;
  font-size: clamp(2.1rem, 4vw, 4.4rem);
  line-height: 0.98;
  font-weight: 850;
  letter-spacing: 0;
}

.qt-tagline {
  color: #FFFFFF;
  font-size: clamp(1.15rem, 2vw, 1.6rem);
  font-weight: 720;
}

.qt-subcopy {
  max-width: 680px;
  margin-top: 0.9rem;
  color: var(--soft-gray);
  font-size: 1rem;
  line-height: 1.7;
}

.qt-disclaimer {
  margin-top: 1rem;
  color: #94A3B8;
  font-size: 0.82rem;
}

.qt-card {
  height: 100%;
  padding: 1.25rem;
  border: 1px solid var(--deep-border);
  border-radius: 22px;
  background: rgba(17, 24, 39, 0.94);
  box-shadow: 0 16px 46px rgba(0, 0, 0, 0.24);
}

.qt-card-gradient {
  border: 1px solid rgba(0, 229, 255, 0.34);
  background:
    linear-gradient(#111827, #111827) padding-box,
    var(--brand-gradient) border-box;
}

.qt-card-label {
  color: #94A3B8;
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.qt-card-value {
  margin-top: 0.35rem;
  color: #FFFFFF;
  font-size: 1.7rem;
  font-weight: 820;
  font-variant-numeric: tabular-nums;
}

.qt-card-copy {
  margin-top: 0.55rem;
  color: var(--soft-gray);
  line-height: 1.55;
}

.qt-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.8rem;
}

.qt-chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0.28rem 0.65rem;
  border: 1px solid var(--deep-border);
  border-radius: 999px;
  background: #0F172A;
  color: var(--soft-gray);
  font-size: 0.78rem;
  font-weight: 700;
}

.qt-signal {
  padding: 1.25rem;
  border: 1px solid var(--deep-border);
  border-radius: 22px;
  background: var(--card-dark);
}

.qt-signal-buy {
  border-color: rgba(34, 197, 94, 0.48);
  box-shadow: 0 0 28px rgba(34, 197, 94, 0.08);
}

.qt-signal-hold {
  border-color: rgba(0, 229, 255, 0.38);
}

.qt-signal-sell {
  border-color: rgba(239, 68, 68, 0.45);
}

.qt-signal-pill {
  display: inline-flex;
  padding: 0.32rem 0.68rem;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 850;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.qt-signal-buy .qt-signal-pill {
  background: rgba(34, 197, 94, 0.14);
  color: var(--profit-green);
}

.qt-signal-hold .qt-signal-pill {
  background: rgba(0, 229, 255, 0.12);
  color: var(--electric-cyan);
}

.qt-signal-sell .qt-signal-pill {
  background: rgba(239, 68, 68, 0.13);
  color: var(--risk-red);
}

.qt-signal-title {
  margin-top: 0.85rem;
  color: #FFFFFF;
  font-size: 1.35rem;
  font-weight: 820;
}

.qt-levels {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
  margin-top: 1rem;
}

.qt-level {
  padding: 0.8rem;
  border: 1px solid var(--deep-border);
  border-radius: 16px;
  background: #0F172A;
}

.qt-level span {
  display: block;
  color: #94A3B8;
  font-size: 0.72rem;
  font-weight: 780;
  text-transform: uppercase;
}

.qt-level strong {
  display: block;
  margin-top: 0.28rem;
  color: #FFFFFF;
  font-size: 1.02rem;
  font-variant-numeric: tabular-nums;
}

.qt-assistant {
  padding: 1.35rem;
  border: 1px solid rgba(124, 58, 237, 0.42);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(17, 24, 39, 0.98), rgba(15, 23, 42, 0.96)),
    radial-gradient(circle at 90% 10%, rgba(124, 58, 237, 0.26), transparent 28%);
}

.qt-input-placeholder {
  padding: 1rem;
  border: 1px solid var(--deep-border);
  border-radius: 16px;
  background: #0B1020;
  color: #94A3B8;
}

.qt-muted {
  color: #94A3B8;
}

@media (max-width: 760px) {
  .qt-hero {
    padding: 1.35rem;
  }
  .qt-levels {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
"""


def render_html(markup):
    st.markdown(dedent(markup).strip(), unsafe_allow_html=True)


@dataclass(frozen=True)
class RiskProfile:
    account_size: float
    risk_per_trade_percent: float
    max_position_percent: float
    min_reward_risk: float = 1.8


@dataclass(frozen=True)
class FuturePotentialProfile:
    risk_tolerance: str
    time_horizon: str
    max_results: int
    sectors: list[str]


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


def stock(
    symbol,
    name,
    price,
    vwap,
    average_volume,
    relative_volume,
    spread_percent,
    sector_trend,
    market_alignment,
    news_sentiment,
    earnings_risk_days,
    atr,
    support,
    resistance,
    sma20,
    sma50,
):
    return {
        "symbol": symbol,
        "name": name,
        "price": price,
        "previous_close": money(price * 0.992),
        "vwap": vwap,
        "average_volume": average_volume,
        "volume": int(average_volume * relative_volume),
        "relative_volume": relative_volume,
        "spread_percent": spread_percent,
        "sector_trend": sector_trend,
        "market_alignment": market_alignment,
        "news_sentiment": news_sentiment,
        "earnings_risk_days": earnings_risk_days,
        "atr": atr,
        "support": support,
        "resistance": resistance,
        "sma20": sma20,
        "sma50": sma50,
    }


def get_market_universe():
    return MOCK_MARKET_DATA + [
        stock("AAPL", "Apple Inc.", 212.4, 211.8, 58_000_000, 1.08, 0.02, "neutral", "bullish", "neutral", 16, 3.1, 207.8, 214.2, 209.6, 205.7),
        stock("META", "Meta Platforms", 514.7, 511.9, 17_000_000, 1.18, 0.03, "strong", "bullish", "positive", 21, 10.4, 502.2, 518.8, 500.3, 486.9),
        stock("AMZN", "Amazon.com", 186.3, 185.5, 39_000_000, 1.15, 0.03, "strong", "bullish", "positive", 28, 4.6, 181.4, 188.2, 181.1, 176.5),
        stock("GOOGL", "Alphabet Inc.", 176.8, 176.1, 27_000_000, 0.98, 0.02, "neutral", "bullish", "neutral", 13, 3.5, 173.2, 179.4, 174.6, 169.7),
        stock("AVGO", "Broadcom Inc.", 143.6, 142.1, 33_000_000, 1.31, 0.04, "strong", "bullish", "positive", 9, 5.2, 137.9, 144.8, 136.5, 130.4),
        stock("SMCI", "Super Micro Computer", 48.9, 49.7, 44_000_000, 1.41, 0.09, "mixed", "mixed", "neutral", 19, 4.4, 46.1, 52.2, 51.8, 55.4),
        stock("COIN", "Coinbase Global", 244.2, 241.8, 12_000_000, 1.52, 0.05, "strong", "bullish", "positive", 34, 12.7, 231.5, 247.6, 232.4, 219.8),
        stock("MSTR", "MicroStrategy", 156.1, 154.6, 18_000_000, 1.43, 0.06, "strong", "bullish", "positive", 40, 10.9, 147.2, 158.0, 146.7, 137.5),
        stock("NFLX", "Netflix Inc.", 641.0, 638.2, 4_600_000, 1.02, 0.04, "neutral", "bullish", "positive", 12, 13.2, 624.5, 649.8, 629.6, 610.1),
        stock("JPM", "JPMorgan Chase", 198.7, 198.1, 9_800_000, 0.95, 0.03, "neutral", "mixed", "neutral", 25, 2.9, 195.3, 201.2, 197.4, 194.8),
        stock("XOM", "Exxon Mobil", 113.4, 114.0, 16_000_000, 0.88, 0.03, "weak", "mixed", "neutral", 22, 2.2, 111.2, 116.4, 115.6, 116.1),
        stock("SPY", "SPDR S&P 500 ETF", 537.6, 536.9, 74_000_000, 1.06, 0.01, "neutral", "bullish", "neutral", 365, 4.8, 531.8, 539.4, 532.7, 524.1),
        stock("QQQ", "Invesco QQQ Trust", 462.2, 461.0, 49_000_000, 1.12, 0.01, "strong", "bullish", "positive", 365, 5.7, 454.3, 464.6, 455.1, 445.2),
        stock("IWM", "iShares Russell 2000 ETF", 203.5, 204.2, 31_000_000, 0.91, 0.02, "weak", "mixed", "neutral", 365, 2.8, 200.7, 207.1, 205.3, 206.0),
        stock("MARA", "MARA Holdings", 19.6, 19.2, 52_000_000, 1.66, 0.11, "strong", "bullish", "positive", 37, 1.9, 18.1, 20.4, 18.8, 17.1),
    ]


FUTURE_POTENTIAL_UNIVERSE = [
    {
        "symbol": "RXRX",
        "name": "Recursion Pharmaceuticals",
        "sector": "AI biotech",
        "market_cap": "Small cap",
        "price": 8.42,
        "average_volume": 9_800_000,
        "revenue_growth": 42,
        "gross_margin": 74,
        "cash_runway_months": 24,
        "debt_risk": "medium",
        "sector_tailwind": 92,
        "moat": 78,
        "institutional_interest": 72,
        "valuation_risk": 76,
        "volatility_risk": 84,
        "liquidity_risk": "medium",
        "catalyst": "AI drug-discovery pipeline progress and pharma partnerships",
    },
    {
        "symbol": "IONQ",
        "name": "IonQ",
        "sector": "Quantum computing",
        "market_cap": "Small cap",
        "price": 10.18,
        "average_volume": 14_500_000,
        "revenue_growth": 78,
        "gross_margin": 58,
        "cash_runway_months": 30,
        "debt_risk": "low",
        "sector_tailwind": 88,
        "moat": 74,
        "institutional_interest": 64,
        "valuation_risk": 88,
        "volatility_risk": 90,
        "liquidity_risk": "medium",
        "catalyst": "Enterprise quantum adoption and government research demand",
    },
    {
        "symbol": "SOUN",
        "name": "SoundHound AI",
        "sector": "AI software",
        "market_cap": "Small cap",
        "price": 4.91,
        "average_volume": 33_000_000,
        "revenue_growth": 54,
        "gross_margin": 62,
        "cash_runway_months": 18,
        "debt_risk": "medium",
        "sector_tailwind": 86,
        "moat": 58,
        "institutional_interest": 52,
        "valuation_risk": 82,
        "volatility_risk": 88,
        "liquidity_risk": "medium",
        "catalyst": "Voice AI adoption across auto, restaurant, and enterprise channels",
    },
    {
        "symbol": "ASTS",
        "name": "AST SpaceMobile",
        "sector": "Space connectivity",
        "market_cap": "Small cap",
        "price": 9.74,
        "average_volume": 18_800_000,
        "revenue_growth": 20,
        "gross_margin": 35,
        "cash_runway_months": 16,
        "debt_risk": "high",
        "sector_tailwind": 84,
        "moat": 83,
        "institutional_interest": 57,
        "valuation_risk": 86,
        "volatility_risk": 92,
        "liquidity_risk": "medium",
        "catalyst": "Satellite-to-phone network milestones and telecom partnerships",
    },
    {
        "symbol": "RKLB",
        "name": "Rocket Lab",
        "sector": "Space infrastructure",
        "market_cap": "Small cap",
        "price": 5.63,
        "average_volume": 11_400_000,
        "revenue_growth": 31,
        "gross_margin": 28,
        "cash_runway_months": 22,
        "debt_risk": "medium",
        "sector_tailwind": 80,
        "moat": 76,
        "institutional_interest": 61,
        "valuation_risk": 72,
        "volatility_risk": 79,
        "liquidity_risk": "medium",
        "catalyst": "Launch cadence, space systems backlog, and Neutron development",
    },
    {
        "symbol": "ENVX",
        "name": "Enovix",
        "sector": "Battery technology",
        "market_cap": "Small cap",
        "price": 11.38,
        "average_volume": 7_200_000,
        "revenue_growth": 65,
        "gross_margin": 22,
        "cash_runway_months": 20,
        "debt_risk": "medium",
        "sector_tailwind": 78,
        "moat": 70,
        "institutional_interest": 55,
        "valuation_risk": 80,
        "volatility_risk": 82,
        "liquidity_risk": "medium",
        "catalyst": "Advanced battery commercialization and manufacturing scale-up",
    },
    {
        "symbol": "CRSP",
        "name": "CRISPR Therapeutics",
        "sector": "Biotech",
        "market_cap": "Mid cap",
        "price": 54.72,
        "average_volume": 1_900_000,
        "revenue_growth": 36,
        "gross_margin": 68,
        "cash_runway_months": 36,
        "debt_risk": "low",
        "sector_tailwind": 75,
        "moat": 86,
        "institutional_interest": 73,
        "valuation_risk": 66,
        "volatility_risk": 70,
        "liquidity_risk": "medium",
        "catalyst": "Gene-editing therapies and pipeline execution",
    },
    {
        "symbol": "JOBY",
        "name": "Joby Aviation",
        "sector": "Electric aviation",
        "market_cap": "Small cap",
        "price": 5.12,
        "average_volume": 8_600_000,
        "revenue_growth": 12,
        "gross_margin": 18,
        "cash_runway_months": 28,
        "debt_risk": "low",
        "sector_tailwind": 72,
        "moat": 67,
        "institutional_interest": 54,
        "valuation_risk": 78,
        "volatility_risk": 83,
        "liquidity_risk": "medium",
        "catalyst": "Certification progress and early commercial air taxi operations",
    },
    {
        "symbol": "HIMS",
        "name": "Hims & Hers Health",
        "sector": "Digital health",
        "market_cap": "Mid cap",
        "price": 18.84,
        "average_volume": 12_300_000,
        "revenue_growth": 47,
        "gross_margin": 80,
        "cash_runway_months": 42,
        "debt_risk": "low",
        "sector_tailwind": 74,
        "moat": 62,
        "institutional_interest": 69,
        "valuation_risk": 62,
        "volatility_risk": 66,
        "liquidity_risk": "low",
        "catalyst": "Subscription health growth and margin expansion",
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


def scan_market(risk_profile, max_results):
    market_regime = {
        "bias": "bullish",
        "volatility": "normal",
        "note": "Mock regime for deployment setup. Connect live data before real trading decisions.",
    }
    candidates = []
    universe = get_market_universe()
    for stock in universe:
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
    plans = [build_trade_plan(candidate, risk_profile) for candidate in candidates[:max_results]]
    return market_regime, plans


def risk_penalty(value):
    return {
        "low": 4,
        "medium": 10,
        "high": 18,
    }.get(value, 10)


def financial_health_score(company):
    runway_score = min(100, company["cash_runway_months"] * 2.5)
    debt_score = {"low": 88, "medium": 64, "high": 38}.get(company["debt_risk"], 55)
    return round((runway_score * 0.42) + (company["gross_margin"] * 0.28) + (debt_score * 0.30))


def future_action(score, company, profile):
    if company["liquidity_risk"] == "high" or company["debt_risk"] == "high":
        return "Watchlist only"
    if profile.risk_tolerance == "Conservative":
        if score >= 78 and company["market_cap"] == "Mid cap":
            return "Starter candidate"
        return "Watchlist only"
    if profile.risk_tolerance == "Balanced":
        if score >= 82:
            return "Starter candidate"
        if score >= 70:
            return "Watchlist only"
        return "Too speculative"
    if score >= 78:
        return "Starter candidate"
    if score >= 66:
        return "Watchlist only"
    return "Too speculative"


def scan_future_potential(profile):
    allowed_sectors = set(profile.sectors)
    results = []

    for company in FUTURE_POTENTIAL_UNIVERSE:
        if allowed_sectors and "All" not in allowed_sectors and company["sector"] not in allowed_sectors:
            continue

        growth = min(100, company["revenue_growth"])
        financial = financial_health_score(company)
        tailwind = company["sector_tailwind"]
        moat = company["moat"]
        institutional = company["institutional_interest"]
        penalty = (
            company["valuation_risk"] * 0.13
            + company["volatility_risk"] * 0.12
            + risk_penalty(company["liquidity_risk"])
            + risk_penalty(company["debt_risk"])
        )
        score = round(
            growth * 0.24
            + financial * 0.22
            + tailwind * 0.21
            + moat * 0.18
            + institutional * 0.15
            - penalty
            + 28
        )
        score = max(0, min(100, score))

        results.append(
            {
                **company,
                "score": score,
                "growth_score": growth,
                "financial_health": financial,
                "action": future_action(score, company, profile),
                "suggested_plan": future_plan(company, score, profile),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[: profile.max_results]


def future_plan(company, score, profile):
    if score >= 82 and company["debt_risk"] != "high":
        sizing = "Small starter size only, such as 0.5%-1% portfolio risk."
    elif score >= 70:
        sizing = "Watchlist first. Wait for earnings, volume, or breakout confirmation."
    else:
        sizing = "Avoid new exposure until financial or execution risk improves."

    return (
        f"{profile.time_horizon} horizon. {sizing} Main catalyst: {company['catalyst']}. "
        "Review liquidity, cash runway, and earnings updates before acting."
    )


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
        return "No high-quality signal yet. Keep this on watch and wait for stronger confirmation before making a decision."

    return (
        f"{plan['symbol']} is a {plan['grade']} setup, but only if the entry trigger confirms. "
        f"Keep risk capped near ${plan['sizing']['estimated_max_loss']}, take partial profit at target 1, "
        "and skip the trade if it loses VWAP with volume."
    )


def logo_svg():
    return """
    <div class="qt-logo" aria-label="QuanTrade AI Agent logo">
      <svg viewBox="0 0 64 64" role="img">
        <defs>
          <linearGradient id="qtGradient" x1="10" y1="54" x2="54" y2="10" gradientUnits="userSpaceOnUse">
            <stop offset="0" stop-color="#00E5FF"/>
            <stop offset="1" stop-color="#7C3AED"/>
          </linearGradient>
          <filter id="qtGlow">
            <feGaussianBlur stdDeviation="2.6" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <rect x="4" y="4" width="56" height="56" rx="16" fill="#0B1020" stroke="#334155"/>
        <path d="M15 42 L25 32 L33 37 L49 18" fill="none" stroke="url(#qtGradient)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" filter="url(#qtGlow)"/>
        <path d="M39 18 H49 V28" fill="none" stroke="url(#qtGradient)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M18 20 H23 M18 27 H21 M42 43 H47 M39 49 H47" stroke="#00E5FF" stroke-width="2" stroke-linecap="round" opacity="0.55"/>
      </svg>
    </div>
    """


def apply_brand_theme():
    render_html(BRAND_CSS)


def render_onboarding():
    with st.container(border=True):
        logo_col, copy_col = st.columns([0.14, 0.86], vertical_alignment="center")
        with logo_col:
            render_html(logo_svg())
        with copy_col:
            st.caption("AI-powered market analysis assistant")
            st.markdown("# QuanTrade AI Agent")
            st.markdown("### Smarter signals. Calmer trading.")
            st.write(
                "AI-powered market insights for risk-aware decisions. Understand stocks, crypto, "
                "market signals, risk, and portfolio opportunities before you trade."
            )
            st.caption("Trade with data, not emotion. Analyze risk before chasing reward.")
            st.caption("For informational purposes only. Not financial advice.")
    return st.button("Start Analyzing", type="primary", use_container_width=False)


def metric_card(label, value, copy, gradient=False):
    class_name = "qt-card qt-card-gradient" if gradient else "qt-card"
    return f"""
    <div class="{class_name}">
      <div class="qt-card-label">{label}</div>
      <div class="qt-card-value">{value}</div>
      <div class="qt-card-copy">{copy}</div>
    </div>
    """


def signal_state(plan):
    if plan["decision"] == "Trade candidate":
        return "buy", "Bullish / Buy setup"
    if plan["decision"] == "Watch only":
        return "hold", "Hold / Neutral watch"
    return "sell", "Bearish / Avoid"


def render_dashboard(plans, market_regime, average_score, trade_candidates, watch_only):
    c1, c2, c3 = st.columns([1.25, 1, 1])
    with c1:
        render_html(
            metric_card(
                "AI Market Signal",
                market_regime["bias"].title(),
                "From market noise to clear insights. Current sample regime supports selective setups.",
                True,
            )
        )
    with c2:
        render_html(
            metric_card(
                "Risk Score",
                f"{average_score}/100",
                "Risk-aware trading support based on filters, trend, volume, and invalidation levels.",
            )
        )
    with c3:
        render_html(
            metric_card(
                "Top Opportunities",
                str(trade_candidates),
                f"{watch_only} additional names are watch-only until confirmation improves.",
            )
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        render_html(
            metric_card(
                "Portfolio Snapshot",
                "Risk-first",
                "Position size is calculated from account risk, not emotion.",
            )
        )
    with c2:
        render_html(
            metric_card(
                "Watchlist",
                ", ".join(plan["symbol"] for plan in plans if plan["decision"] != "Skip") or "None",
                "Understand the signal before the trade.",
            )
        )
    with c3:
        render_html(
            metric_card(
                "Market News Summary",
                "AI-ready",
                "News and live catalysts are prepared for the next data integration stage.",
            )
        )


def render_assistant_panel():
    render_html(
        """
        <div class="qt-assistant">
          <div class="qt-card-label">AI Assistant</div>
          <div class="qt-card-value">Your AI co-pilot for market decisions.</div>
          <p class="qt-card-copy">
            Ask QuanTrade about a stock, crypto, risk, or market trend. The assistant is designed
            to help analyze before you trade, not promise outcomes.
          </p>
          <div class="qt-input-placeholder">
            Ask QuanTrade about a stock, crypto, risk, or market trend...
          </div>
          <p class="qt-disclaimer">For informational purposes only. Not financial advice.</p>
        </div>
        """
    )
    question = st.text_input(
        "Ask QuanTrade",
        placeholder="Ask QuanTrade about a stock, crypto, risk, or market trend...",
        label_visibility="collapsed",
    )
    if question:
        st.info("Assistant chat wiring is ready for the next step. Market analysis responses will use your OpenAI key and live data adapters.")


def render_future_card(item):
    action_class = "qt-signal-buy" if item["action"] == "Starter candidate" else "qt-signal-hold"
    if item["action"] == "Too speculative":
        action_class = "qt-signal-sell"

    render_html(
        f"""
        <div class="qt-signal {action_class}">
          <span class="qt-signal-pill">{item['action']}</span>
          <div class="qt-signal-title">{item['symbol']} · {item['name']}</div>
          <p class="qt-card-copy">{item['market_cap']} · {item['sector']} · Future Potential {item['score']}/100</p>
          <div class="qt-levels">
            <div class="qt-level"><span>Growth</span><strong>{item['growth_score']}/100</strong></div>
            <div class="qt-level"><span>Financial Health</span><strong>{item['financial_health']}/100</strong></div>
            <div class="qt-level"><span>Sector Tailwind</span><strong>{item['sector_tailwind']}/100</strong></div>
            <div class="qt-level"><span>Moat</span><strong>{item['moat']}/100</strong></div>
            <div class="qt-level"><span>Valuation Risk</span><strong>{item['valuation_risk']}/100</strong></div>
            <div class="qt-level"><span>Volatility Risk</span><strong>{item['volatility_risk']}/100</strong></div>
            <div class="qt-level"><span>Cash Runway</span><strong>{item['cash_runway_months']} mo</strong></div>
            <div class="qt-level"><span>Liquidity</span><strong>{item['liquidity_risk'].title()}</strong></div>
          </div>
          <p class="qt-card-copy">{item['suggested_plan']}</p>
          <div class="qt-chip-row">
            <span class="qt-chip">Catalyst: {item['catalyst']}</span>
            <span class="qt-chip">Debt risk: {item['debt_risk'].title()}</span>
            <span class="qt-chip">Avg volume: {item['average_volume']:,}</span>
          </div>
          <p class="qt-disclaimer">For informational purposes only. Not financial advice.</p>
        </div>
        """
    )


def render_future_potential_panel(profile):
    results = scan_future_potential(profile)
    starter_count = sum(1 for item in results if item["action"] == "Starter candidate")
    watch_count = sum(1 for item in results if item["action"] == "Watchlist only")
    average_score = round(sum(item["score"] for item in results) / len(results), 1) if results else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        render_html(metric_card("Future Potential", f"{average_score}/100", "Growth, financial health, tailwinds, moat, and risk are scored separately.", True))
    with c2:
        render_html(metric_card("Starter Candidates", str(starter_count), "Small starter size only. This mode is for opportunity scouting, not urgent trades."))
    with c3:
        render_html(metric_card("Watchlist", str(watch_count), "Track execution, earnings, cash runway, and liquidity before acting."))

    st.caption("Smaller-market stocks can move fast, but they also carry higher liquidity, dilution, and execution risk.")
    if not results:
        st.warning("No future-potential names matched the selected sector filters.")
        return

    for item in results:
        render_future_card(item)


def render_plan(plan):
    state, state_label = signal_state(plan)
    state_class = f"qt-signal qt-signal-{state}"
    coach_notes = generate_coach_notes(plan)

    if plan["decision"] == "Skip":
        render_html(
            f"""
            <div class="{state_class}">
              <span class="qt-signal-pill">{state_label}</span>
              <div class="qt-signal-title">{plan['symbol']} · {plan['company']}</div>
              <p class="qt-card-copy">{plan['decision']} · {plan['setup']} · Trade Quality {plan['score']}/100 · Grade {plan['grade']}</p>
              <p class="qt-card-copy">{coach_notes}</p>
              <div class="qt-chip-row">
                <span class="qt-chip">{plan['invalidation']}</span>
              </div>
              <p class="qt-disclaimer">For informational purposes only. Not financial advice.</p>
            </div>
            """
        )
        return

    warning_html = ""
    if plan.get("warnings"):
        warning_html = f"""<span class="qt-chip">Watch-only warning: {", ".join(plan["warnings"])}</span>"""

    evidence_html = "".join(f"""<span class="qt-chip">{item}</span>""" for item in plan.get("evidence", []))
    render_html(
        f"""
        <div class="{state_class}">
          <span class="qt-signal-pill">{state_label}</span>
          <div class="qt-signal-title">{plan['symbol']} · {plan['company']}</div>
          <p class="qt-card-copy">{plan['decision']} · {plan['setup']} · Trade Quality {plan['score']}/100 · Grade {plan['grade']}</p>
          <p class="qt-card-copy">{coach_notes}</p>
          <div class="qt-levels">
            <div class="qt-level"><span>Entry</span><strong>${plan['entry']['price']}</strong></div>
            <div class="qt-level"><span>Stop</span><strong>${plan['exit']['stop_loss']}</strong></div>
            <div class="qt-level"><span>Target 1</span><strong>${plan['exit']['target1']}</strong></div>
            <div class="qt-level"><span>Target 2</span><strong>${plan['exit']['target2']}</strong></div>
            <div class="qt-level"><span>Shares</span><strong>{plan['sizing']['shares']}</strong></div>
            <div class="qt-level"><span>Position</span><strong>${plan['sizing']['position_value']}</strong></div>
            <div class="qt-level"><span>Max Loss</span><strong>${plan['sizing']['estimated_max_loss']}</strong></div>
            <div class="qt-level"><span>Risk / Share</span><strong>${plan['sizing']['risk_per_share']}</strong></div>
          </div>
          <p class="qt-card-copy">{plan['entry']['trigger']}</p>
          <p class="qt-card-copy">{plan['invalidation']}</p>
          <div class="qt-chip-row">{evidence_html}{warning_html}</div>
          <p class="qt-disclaimer">For informational purposes only. Not financial advice.</p>
        </div>
        """
    )


def main():
    apply_brand_theme()

    with st.sidebar:
        render_html(logo_svg())
        st.header("QuanTrade AI Agent")
        st.caption("Smarter signals. Calmer trading.")
        st.divider()
        st.subheader("Risk Settings")
        account_size = st.number_input("Account size", min_value=1000.0, value=10000.0, step=500.0)
        risk_percent = st.number_input("Risk per trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
        max_position_percent = st.number_input("Max position size (%)", min_value=1.0, max_value=100.0, value=25.0, step=1.0)
        max_results = st.slider("Signals to show", min_value=5, max_value=20, value=10, step=1)
        st.divider()
        st.subheader("Future Potential")
        future_risk = st.selectbox("Risk tolerance", ["Balanced", "Conservative", "Aggressive"])
        future_horizon = st.selectbox("Time horizon", ["6-24 month", "3-12 month", "2-5 year"])
        future_results = st.slider("Future names to show", min_value=3, max_value=9, value=6, step=1)
        available_sectors = ["All"] + sorted({item["sector"] for item in FUTURE_POTENTIAL_UNIVERSE})
        future_sectors = st.multiselect("Sectors", available_sectors, default=["All"])
        st.divider()
        st.caption("Analyze before you trade.")
        st.caption("Signals are informational, not financial advice.")

    if "analysis_started" not in st.session_state:
        st.session_state.analysis_started = False

    started_now = render_onboarding()
    if started_now:
        st.session_state.analysis_started = True

    if not st.session_state.analysis_started:
        st.info("Set your risk settings, then click Start Analyzing to scan the sample market universe.")
        st.caption("Current MVP mode uses expanded sample data. Live stock scanning will require a market data provider such as Alpaca or Polygon.")
        return

    risk_profile = RiskProfile(
        account_size=account_size,
        risk_per_trade_percent=risk_percent,
        max_position_percent=max_position_percent,
    )
    future_profile = FuturePotentialProfile(
        risk_tolerance=future_risk,
        time_horizon=future_horizon,
        max_results=future_results,
        sectors=future_sectors,
    )
    market_regime, plans = scan_market(risk_profile, max_results)

    trade_candidates = sum(1 for plan in plans if plan["decision"] == "Trade candidate")
    watch_only = sum(1 for plan in plans if plan["decision"] == "Watch only")
    average_score = round(sum(plan["score"] for plan in plans) / len(plans), 1)

    st.caption(
        f"Market regime: {market_regime['bias']} · Volatility: {market_regime['volatility']} · "
        f"Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )

    dashboard_tab, signals_tab, future_tab, assistant_tab = st.tabs(["Dashboard", "Signals", "Future Potential", "AI Assistant"])

    with dashboard_tab:
        render_dashboard(plans, market_regime, average_score, trade_candidates, watch_only)

    with signals_tab:
        st.markdown("### Top Opportunities")
        st.caption(f"Showing {len(plans)} ranked signals from {len(get_market_universe())} sample market candidates.")
        for plan in plans:
            render_plan(plan)

    with future_tab:
        st.markdown("### Future Potential")
        st.caption("Opportunity scouting for smaller or emerging companies. This is separate from short-term trade timing.")
        render_future_potential_panel(future_profile)

    with assistant_tab:
        render_assistant_panel()


if __name__ == "__main__":
    main()
