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
  --rh-bg: #05070D;
  --rh-card: #0D111C;
  --rh-panel: #111827;
  --rh-ink: #F8FAFC;
  --rh-muted: #94A3B8;
  --rh-line: #263244;
  --rh-green: #22C55E;
  --rh-red: #F43F5E;
  --rh-yellow: #F59E0B;
  --rh-cyan: #00E5FF;
  --rh-purple: #8B5CF6;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background:
    radial-gradient(circle at top left, rgba(0, 229, 255, 0.10), transparent 34rem),
    radial-gradient(circle at top right, rgba(139, 92, 246, 0.16), transparent 34rem),
    var(--rh-bg) !important;
}

[data-testid="stSidebar"] {
  background: #080B12 !important;
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
  background: linear-gradient(135deg, var(--rh-cyan), var(--rh-purple)) !important;
  color: #020617 !important;
  border: 0 !important;
  border-radius: 14px !important;
  font-weight: 850 !important;
  min-height: 2.8rem;
}

button[kind="primary"] *, .stButton > button * {
  color: #020617 !important;
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
  background: #0D111C !important;
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
  background: rgba(0, 229, 255, 0.08);
  border: 1px solid rgba(0, 229, 255, 0.22);
  border-radius: 16px;
  color: #CFFAFE;
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
  color: #22C55E;
  font-weight: 850;
}

.qt-rating-wait {
  color: #FACC15;
  font-weight: 850;
}

.qt-rating-sell {
  color: #FB7185;
  font-weight: 850;
}

.qt-app-title {
  color: var(--rh-ink);
  font-size: 2.45rem;
  line-height: 1.1;
  font-weight: 900;
  margin: 0.2rem 0 0.35rem;
}

.qt-muted {
  color: var(--rh-muted);
}

.qt-brief {
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.16), rgba(139, 92, 246, 0.20)), #0D111C;
  color: #FFFFFF;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  padding: 1.35rem 1.45rem;
  margin: 0.35rem 0 1.2rem;
}

.qt-brief h2, .qt-brief p, .qt-brief div {
  color: #FFFFFF !important;
}

.qt-brief-sub {
  color: #B9C3BE !important;
  font-size: 1rem;
  margin-top: 0.4rem;
}

.qt-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.28rem 0.7rem;
  margin: 0.16rem 0.2rem 0.16rem 0;
  font-size: 0.78rem;
  font-weight: 850;
}

.qt-pill-buy {
  background: rgba(34, 197, 94, 0.16);
  color: #86EFAC;
}

.qt-pill-watch {
  background: rgba(245, 158, 11, 0.16);
  color: #FCD34D;
}

.qt-pill-avoid {
  background: rgba(244, 63, 94, 0.16);
  color: #FDA4AF;
}

.qt-queue-card {
  border: 1px solid var(--rh-line);
  background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015)), var(--rh-card);
  border-radius: 18px;
  padding: 1rem;
  min-height: 10.5rem;
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.18);
}

.qt-card-symbol {
  color: var(--rh-ink);
  font-size: 1.35rem;
  font-weight: 900;
}

.qt-card-score {
  color: var(--rh-ink);
  font-size: 2rem;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
}

.qt-alert-row {
  border: 1px solid var(--rh-line);
  border-radius: 16px;
  background: var(--rh-card);
  padding: 0.85rem 1rem;
  margin: 0.55rem 0;
}

.qt-alert-title {
  color: var(--rh-ink);
  font-weight: 900;
}

.qt-alert-body {
  color: var(--rh-muted);
  margin-top: 0.15rem;
}

.qt-pillar {
  border: 1px solid var(--rh-line);
  border-radius: 18px;
  background: rgba(13, 17, 28, 0.82);
  padding: 1rem;
  min-height: 9.5rem;
}

.qt-pillar-title {
  color: var(--rh-ink);
  font-size: 1.05rem;
  font-weight: 900;
}

.qt-ai-card {
  border: 1px solid rgba(0, 229, 255, 0.24);
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.10), rgba(139, 92, 246, 0.14)), #0D111C;
  padding: 1.1rem;
  margin: 0.75rem 0 1rem;
}

.qt-ai-question {
  color: #E2E8F0;
  font-weight: 850;
}

.qt-ai-summary {
  color: #F8FAFC;
  font-size: 1.05rem;
  line-height: 1.55;
  margin-top: 0.45rem;
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
    "Auto: Stocks ETF crypto intelligence": [
        "SPY", "QQQ", "IWM", "SMH", "ARKK", "IBB", "NVDA", "AAPL", "MSFT", "TSLA",
        "COIN", "MSTR", "MARA", "RIOT", "CLSK", "BTC-USD", "ETH-USD", "SOL-USD",
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


SAMPLE_FUNDAMENTALS = {
    "NVDA": {"revenue_growth": 126.0, "eps_growth": 145.0, "gross_margin": 75.0, "operating_margin": 61.0, "net_margin": 53.0, "fcf_margin": 43.0, "debt_to_equity": 0.2, "current_ratio": 4.3, "roe": 91.0, "pe": 43.0, "ps": 24.0, "pb": 37.0},
    "AMD": {"revenue_growth": 13.7, "eps_growth": 24.0, "gross_margin": 50.0, "operating_margin": 6.0, "net_margin": 5.0, "fcf_margin": 8.0, "debt_to_equity": 0.05, "current_ratio": 2.8, "roe": 3.0, "pe": 49.0, "ps": 11.0, "pb": 4.8},
    "AAPL": {"revenue_growth": 2.0, "eps_growth": 7.0, "gross_margin": 46.0, "operating_margin": 31.0, "net_margin": 26.0, "fcf_margin": 24.0, "debt_to_equity": 1.7, "current_ratio": 0.9, "roe": 154.0, "pe": 30.0, "ps": 8.0, "pb": 47.0},
    "MSFT": {"revenue_growth": 15.0, "eps_growth": 20.0, "gross_margin": 69.0, "operating_margin": 45.0, "net_margin": 36.0, "fcf_margin": 31.0, "debt_to_equity": 0.3, "current_ratio": 1.3, "roe": 37.0, "pe": 34.0, "ps": 12.0, "pb": 11.0},
    "META": {"revenue_growth": 22.0, "eps_growth": 73.0, "gross_margin": 81.0, "operating_margin": 38.0, "net_margin": 35.0, "fcf_margin": 33.0, "debt_to_equity": 0.1, "current_ratio": 2.7, "roe": 34.0, "pe": 25.0, "ps": 9.0, "pb": 8.0},
    "AMZN": {"revenue_growth": 11.0, "eps_growth": 82.0, "gross_margin": 49.0, "operating_margin": 10.0, "net_margin": 8.0, "fcf_margin": 6.0, "debt_to_equity": 0.5, "current_ratio": 1.1, "roe": 19.0, "pe": 33.0, "ps": 3.2, "pb": 8.0},
    "GOOGL": {"revenue_growth": 14.0, "eps_growth": 39.0, "gross_margin": 59.0, "operating_margin": 32.0, "net_margin": 27.0, "fcf_margin": 22.0, "debt_to_equity": 0.1, "current_ratio": 2.0, "roe": 29.0, "pe": 23.0, "ps": 6.4, "pb": 6.7},
    "TSLA": {"revenue_growth": 1.0, "eps_growth": -18.0, "gross_margin": 18.0, "operating_margin": 8.0, "net_margin": 7.0, "fcf_margin": 3.0, "debt_to_equity": 0.2, "current_ratio": 1.7, "roe": 12.0, "pe": 62.0, "ps": 7.1, "pb": 9.0},
    "PLTR": {"revenue_growth": 21.0, "eps_growth": 45.0, "gross_margin": 81.0, "operating_margin": 16.0, "net_margin": 16.0, "fcf_margin": 34.0, "debt_to_equity": 0.05, "current_ratio": 5.5, "roe": 12.0, "pe": 85.0, "ps": 25.0, "pb": 16.0},
    "SPY": {"revenue_growth": 0.0, "eps_growth": 0.0, "gross_margin": 0.0, "operating_margin": 0.0, "net_margin": 0.0, "fcf_margin": 0.0, "debt_to_equity": 0.0, "current_ratio": 0.0, "roe": 0.0, "pe": 22.0, "ps": 2.8, "pb": 4.5, "is_fund": True},
    "QQQ": {"revenue_growth": 0.0, "eps_growth": 0.0, "gross_margin": 0.0, "operating_margin": 0.0, "net_margin": 0.0, "fcf_margin": 0.0, "debt_to_equity": 0.0, "current_ratio": 0.0, "roe": 0.0, "pe": 31.0, "ps": 5.6, "pb": 8.1, "is_fund": True},
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


def parse_portfolio(text):
    holdings = {}
    for part in text.replace("\n", ",").split(","):
        token = part.strip()
        if not token:
            continue
        pieces = token.replace(":", " ").split()
        symbol = pieces[0].upper()
        amount = 0.0
        if len(pieces) > 1:
            amount = safe_number(pieces[1].replace("$", "").replace(",", ""), 0.0)
        holdings[symbol] = amount
    return holdings


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


def fallback_fundamentals(symbol):
    base = SAMPLE_FUNDAMENTALS.get(
        symbol,
        {
            "revenue_growth": 6.0,
            "eps_growth": 4.0,
            "gross_margin": 42.0,
            "operating_margin": 12.0,
            "net_margin": 8.0,
            "fcf_margin": 7.0,
            "debt_to_equity": 0.7,
            "current_ratio": 1.4,
            "roe": 11.0,
            "pe": 28.0,
            "ps": 4.0,
            "pb": 5.0,
        },
    )
    return {
        **base,
        "fundamental_source": "sample fallback",
        "financial_notes": "Live company financials were unavailable, so QuanTrade used conservative fallback estimates.",
    }


def safe_number(value, default=0.0):
    try:
        if value is None:
            return default
        if pd is not None and pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def latest_statement_value(frame, names):
    if pd is None or frame is None or getattr(frame, "empty", True):
        return None
    for name in names:
        if name in frame.index:
            row = frame.loc[name].dropna()
            if not row.empty:
                return safe_number(row.iloc[0], None)
    return None


def statement_growth(frame, names):
    if pd is None or frame is None or getattr(frame, "empty", True):
        return None
    for name in names:
        if name in frame.index:
            row = frame.loc[name].dropna()
            if len(row) >= 2:
                current = safe_number(row.iloc[0], None)
                previous = safe_number(row.iloc[1], None)
                if current is not None and previous not in [None, 0]:
                    return ((current - previous) / abs(previous)) * 100
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_live_fundamentals(symbol):
    if yf is None or pd is None:
        return None
    try:
        ticker = yf.Ticker(symbol)
        info = {}
        try:
            info = ticker.info or {}
        except Exception:
            info = {}

        income = getattr(ticker, "financials", None)
        balance = getattr(ticker, "balance_sheet", None)
        cashflow = getattr(ticker, "cashflow", None)

        revenue = latest_statement_value(income, ["Total Revenue", "Operating Revenue"])
        gross_profit = latest_statement_value(income, ["Gross Profit"])
        operating_income = latest_statement_value(income, ["Operating Income", "Operating Income Loss"])
        net_income = latest_statement_value(income, ["Net Income", "Net Income Common Stockholders"])
        operating_cash = latest_statement_value(cashflow, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"])
        capex = latest_statement_value(cashflow, ["Capital Expenditure", "Capital Expenditures"])
        total_debt = latest_statement_value(balance, ["Total Debt", "Long Term Debt"])
        equity = latest_statement_value(balance, ["Stockholders Equity", "Total Equity Gross Minority Interest"])
        current_assets = latest_statement_value(balance, ["Current Assets", "Total Current Assets"])
        current_liabilities = latest_statement_value(balance, ["Current Liabilities", "Total Current Liabilities Net Minority Interest"])

        free_cash_flow = safe_number(operating_cash) + safe_number(capex)
        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")
        revenue_growth = safe_number(revenue_growth, None)
        earnings_growth = safe_number(earnings_growth, None)

        if revenue_growth is not None:
            revenue_growth *= 100
        else:
            revenue_growth = statement_growth(income, ["Total Revenue", "Operating Revenue"])

        if earnings_growth is not None:
            earnings_growth *= 100
        else:
            earnings_growth = statement_growth(income, ["Net Income", "Net Income Common Stockholders"])

        result = {
            "revenue_growth": safe_number(revenue_growth, 0.0),
            "eps_growth": safe_number(earnings_growth, 0.0),
            "gross_margin": safe_number((gross_profit / revenue) * 100 if revenue else info.get("grossMargins", 0) * 100, 0.0),
            "operating_margin": safe_number((operating_income / revenue) * 100 if revenue else info.get("operatingMargins", 0) * 100, 0.0),
            "net_margin": safe_number((net_income / revenue) * 100 if revenue else info.get("profitMargins", 0) * 100, 0.0),
            "fcf_margin": safe_number((free_cash_flow / revenue) * 100 if revenue else 0.0, 0.0),
            "debt_to_equity": safe_number((total_debt / equity) if equity else info.get("debtToEquity", 0) / 100, 0.0),
            "current_ratio": safe_number((current_assets / current_liabilities) if current_liabilities else info.get("currentRatio", 0), 0.0),
            "roe": safe_number(info.get("returnOnEquity", 0) * 100, 0.0),
            "pe": safe_number(info.get("trailingPE") or info.get("forwardPE"), 0.0),
            "ps": safe_number(info.get("priceToSalesTrailing12Months"), 0.0),
            "pb": safe_number(info.get("priceToBook"), 0.0),
            "is_fund": bool(info.get("quoteType") in ["ETF", "MUTUALFUND"]),
            "fundamental_source": "live yfinance fundamentals",
            "financial_notes": "Financial metrics are derived from Yahoo Finance statements and profile data when available.",
        }

        has_useful_data = any(abs(result[key]) > 0 for key in ["revenue_growth", "gross_margin", "net_margin", "roe", "pe"])
        return result if has_useful_data else None
    except Exception:
        return None


def get_fundamentals(symbol, use_live_data):
    if use_live_data:
        fundamentals = fetch_live_fundamentals(symbol)
        if fundamentals:
            return fundamentals
    return fallback_fundamentals(symbol)


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


def score_metric(value, good, excellent, reverse=False):
    value = safe_number(value)
    if reverse:
        if value <= excellent:
            return 95
        if value <= good:
            return 80
        return clamp_score(80 - (value - good) * 4)
    if value >= excellent:
        return 95
    if value >= good:
        return 80
    return clamp_score(45 + (value / max(good, 1)) * 35)


def score_business_quality(fundamentals):
    if fundamentals.get("is_fund"):
        valuation = score_metric(fundamentals.get("pe"), 30, 18, reverse=True)
        return {
            "quality_score": 70,
            "quality_grade": "B",
            "quality_label": "ETF / basket",
            "financial_scores": {
                "Growth": 65,
                "Profitability": 70,
                "Cash Flow": 70,
                "Balance Sheet": 70,
                "Valuation": valuation,
            },
            "financial_grades": {
                "Growth": "B-",
                "Profitability": "B",
                "Cash Flow": "B",
                "Balance Sheet": "B",
                "Valuation": factor_grade(valuation),
            },
        }

    growth = clamp_score(
        score_metric(fundamentals.get("revenue_growth"), 10, 25) * 0.55
        + score_metric(fundamentals.get("eps_growth"), 8, 25) * 0.45
    )
    profitability = clamp_score(
        score_metric(fundamentals.get("gross_margin"), 40, 65) * 0.25
        + score_metric(fundamentals.get("operating_margin"), 12, 28) * 0.25
        + score_metric(fundamentals.get("net_margin"), 8, 22) * 0.25
        + score_metric(fundamentals.get("roe"), 12, 30) * 0.25
    )
    cash_flow = score_metric(fundamentals.get("fcf_margin"), 6, 18)
    balance_sheet = clamp_score(
        score_metric(fundamentals.get("current_ratio"), 1.2, 2.0) * 0.45
        + score_metric(fundamentals.get("debt_to_equity"), 1.0, 0.25, reverse=True) * 0.55
    )
    valuation = clamp_score(
        score_metric(fundamentals.get("pe"), 35, 18, reverse=True) * 0.45
        + score_metric(fundamentals.get("ps"), 10, 3, reverse=True) * 0.35
        + score_metric(fundamentals.get("pb"), 8, 2.5, reverse=True) * 0.20
    )
    quality_score = clamp_score(
        growth * 0.24 + profitability * 0.26 + cash_flow * 0.20 + balance_sheet * 0.18 + valuation * 0.12
    )
    label = "High quality" if quality_score >= 82 else "Solid" if quality_score >= 70 else "Speculative" if quality_score >= 55 else "Weak"

    scores = {
        "Growth": growth,
        "Profitability": profitability,
        "Cash Flow": cash_flow,
        "Balance Sheet": balance_sheet,
        "Valuation": valuation,
    }
    return {
        "quality_score": quality_score,
        "quality_grade": factor_grade(quality_score),
        "quality_label": label,
        "financial_scores": scores,
        "financial_grades": {name: factor_grade(value) for name, value in scores.items()},
    }


HORIZON_CONFIGS = {
    "Day Trade": {
        "label": "Intraday / same-day",
        "holding_period": "Minutes to one session",
        "score_weights": {"trade": 0.82, "quality": 0.18},
        "min_trade_signal": 72,
        "min_business_quality": 40,
        "risk_multiplier": 0.45,
        "target_r_multiple": 1.2,
        "stop_atr_multiplier": 0.45,
        "prefer": ["liquidity", "momentum", "vwap"],
    },
    "Swing Trade": {
        "label": "Multi-day / multi-week",
        "holding_period": "5 to 20 trading days",
        "score_weights": {"trade": 0.62, "quality": 0.38},
        "min_trade_signal": 62,
        "min_business_quality": 55,
        "risk_multiplier": 1.0,
        "target_r_multiple": 1.8,
        "stop_atr_multiplier": 0.70,
        "prefer": ["momentum", "support/resistance", "business quality"],
    },
    "Long-Term Invest": {
        "label": "Multi-quarter investing",
        "holding_period": "3 to 12+ months",
        "score_weights": {"trade": 0.28, "quality": 0.72},
        "min_trade_signal": 45,
        "min_business_quality": 72,
        "risk_multiplier": 1.4,
        "target_r_multiple": 2.8,
        "stop_atr_multiplier": 1.20,
        "prefer": ["business quality", "cash flow", "valuation"],
    },
}


def horizon_config(horizon):
    return HORIZON_CONFIGS.get(horizon, HORIZON_CONFIGS["Swing Trade"])


def opportunity_score(trade_score, quality_score, horizon="Swing Trade"):
    weights = horizon_config(horizon)["score_weights"]
    return clamp_score(trade_score * weights["trade"] + quality_score * weights["quality"])


def interpret_screen_prompt(prompt, horizon):
    text = f"{prompt} {horizon}".lower()
    config = horizon_config(horizon)
    settings = {
        "horizon": horizon,
        "holding_period": config["holding_period"],
        "min_trade_signal": config["min_trade_signal"],
        "min_business_quality": config["min_business_quality"],
        "prefer": list(config["prefer"]),
        "avoid": [],
        "timeframe": config["label"],
        "strict_confirmation": False,
    }
    if any(word in text for word in ["strong business", "quality", "cash flow", "fundamental", "profitable"]):
        settings["min_business_quality"] = 70
        settings["prefer"].append("business quality")
    if any(word in text for word in ["breakout", "momentum", "relative volume", "rvol"]):
        settings["min_trade_signal"] = 70
        settings["prefer"].append("momentum")
        settings["strict_confirmation"] = True
    if any(word in text for word in ["pullback", "support", "dip"]):
        settings["prefer"].append("pullback")
    if any(word in text for word in ["small cap", "speculative", "future"]):
        settings["min_business_quality"] = 45
        settings["prefer"].append("future potential")
    if any(word in text for word in ["defensive", "safe", "low risk", "protect"]):
        settings["min_trade_signal"] = 65
        settings["min_business_quality"] = 70
        settings["avoid"].append("high volatility")
        settings["strict_confirmation"] = True
    if horizon == "Day Trade":
        settings["strict_confirmation"] = True
        settings["avoid"].append("low liquidity")
    if horizon == "Long-Term Invest":
        settings["strict_confirmation"] = False
        settings["avoid"].append("weak fundamentals")
    if any(word in text for word in ["crypto", "bitcoin", "ethereum", "etf"]):
        settings["prefer"].append("cross asset")
    return settings


def playbook_adjustment(plan, settings):
    adjustment = 0
    factors = plan["factor_scores"]
    quality = plan["business_quality"]
    fundamentals = plan["fundamentals"]
    theme = plan_theme(plan["symbol"])

    if "business quality" in settings["prefer"]:
        adjustment += 8 if quality["quality_score"] >= 75 else -6
        adjustment += 4 if safe_number(fundamentals.get("fcf_margin")) > 10 else 0
    if "momentum" in settings["prefer"]:
        adjustment += 8 if factors["Momentum"] >= 76 and plan["relative_volume"] >= 1.0 else -5
        adjustment += 4 if plan["price"] >= plan["resistance"] * 0.985 else 0
    if "pullback" in settings["prefer"]:
        near_support = (plan["price"] - plan["support"]) / max(plan["price"], 0.01) <= 0.06
        adjustment += 8 if near_support and plan["price"] > plan["sma50"] else -3
    if "future potential" in settings["prefer"]:
        adjustment += 6 if theme in ["AI/Semiconductors", "Crypto-linked", "Crypto", "Other"] else 0
        adjustment -= 5 if quality["quality_score"] < 45 else 0
    if "cross asset" in settings["prefer"]:
        adjustment += 6 if theme in ["Crypto", "Crypto-linked", "ETF/Core"] else 0
    if "high volatility" in settings["avoid"]:
        atr_percent = (plan["atr"] / max(plan["price"], 0.01)) * 100
        adjustment -= 10 if atr_percent > 6 else 0
    if "low liquidity" in settings["avoid"]:
        adjustment -= 12 if plan["average_volume"] < 10_000_000 else 0
    if "weak fundamentals" in settings["avoid"]:
        adjustment -= 15 if quality["quality_score"] < 65 else 0
    if settings["horizon"] == "Day Trade":
        adjustment += 8 if factors["Liquidity"] >= 76 and plan["relative_volume"] >= 1.1 else -6
        adjustment -= 8 if plan["sizing"]["risk_per_share"] <= 0 else 0
    if settings["horizon"] == "Long-Term Invest":
        adjustment += 10 if quality["quality_score"] >= 78 else -8
        adjustment += 5 if safe_number(fundamentals.get("fcf_margin")) >= 10 else -4
    if settings["strict_confirmation"] and plan["decision"] not in ["BUY SETUP", "WAIT FOR TRIGGER"]:
        adjustment -= 10
    return adjustment


def apply_workflow_scoring(plans, screen_prompt, playbook):
    settings = interpret_screen_prompt(screen_prompt, playbook)
    qualified = []
    for plan in plans:
        adjusted = clamp_score(plan["opportunity_score"] + playbook_adjustment(plan, settings))
        plan["workflow_score"] = adjusted
        plan["screen_match"] = (
            plan["score"] >= settings["min_trade_signal"]
            and plan["business_quality"]["quality_score"] >= settings["min_business_quality"]
        )
        plan["screen_settings"] = settings
        qualified.append(plan)
    qualified.sort(key=lambda item: (item["screen_match"], item["workflow_score"]), reverse=True)
    return qualified


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


def position_size(entry, stop, risk_profile, horizon="Swing Trade"):
    risk_budget = risk_profile.account_size * risk_profile.risk_per_trade_percent / 100
    risk_budget *= horizon_config(horizon)["risk_multiplier"]
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


def build_trade_plan(quote, fundamentals, regime, risk_profile, horizon="Swing Trade"):
    config = horizon_config(horizon)
    score = score_trade(quote, regime)
    factors = score_factors(quote, regime)
    quality = score_business_quality(fundamentals)
    total_score = opportunity_score(score, quality["quality_score"], horizon)
    entry = money(max(quote["price"], quote["resistance"] + 0.03)) if quote["price"] > quote["sma20"] else quote["price"]
    stop = money(min(quote["support"], entry - quote["atr"] * config["stop_atr_multiplier"]))
    risk = entry - stop
    target1 = money(entry + risk * config["target_r_multiple"])
    target2 = money(entry + risk * (config["target_r_multiple"] + 1.0))
    sizing = position_size(entry, stop, risk_profile, horizon)
    decision = trade_decision(score, quote)
    setup = "Breakout continuation" if quote["price"] >= quote["resistance"] * 0.985 else "Trend pullback" if quote["price"] > quote["sma20"] else "Needs confirmation"

    return {
        **quote,
        "score": score,
        "opportunity_score": total_score,
        "grade": trade_grade(score),
        "decision": decision,
        "rating": quan_rating(score, decision),
        "horizon": horizon,
        "holding_period": config["holding_period"],
        "business_quality": quality,
        "fundamentals": fundamentals,
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


def scan_trades(tickers, risk_profile, use_live_data, max_results, screen_prompt="", horizon="Swing Trade"):
    regime = market_regime(use_live_data)
    plans = []
    for symbol in tickers:
        quote = get_quote(symbol, use_live_data)
        fundamentals = get_fundamentals(symbol, use_live_data)
        plans.append(build_trade_plan(quote, fundamentals, regime, risk_profile, horizon))
    plans = apply_workflow_scoring(plans, screen_prompt, horizon)
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
                        "content": (
                            "You are QuanTrade, a cautious market-intelligence assistant for stocks, ETFs, and crypto. "
                            "Use the provided scan, portfolio, and signal inbox first. Separate trade setup, business quality, "
                            "portfolio risk, and uncertainty. Never promise profit or give guaranteed financial advice."
                        ),
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
    st.caption("QuanTrade AI Agent")
    st.markdown('<div class="qt-app-title">Discover, analyse, and act in one trading workspace.</div>', unsafe_allow_html=True)
    st.caption("AI stock screening, ticker intelligence, portfolio-aware signals, and risk-aware next steps. Informational only, not financial advice.")


def render_platform_pillars():
    cols = st.columns(3)
    pillars = [
        ("Discover", "Ask in plain English, scan market universes, and surface qualified ideas without starting from a ticker."),
        ("Analyse", "Combine trade timing, financial quality, chart levels, risk flags, and portfolio context into one stock workbench."),
        ("Act", "Turn the insight into entry trigger, stop, target, position size, and a clear reason to skip."),
    ]
    for col, (title, body) in zip(cols, pillars):
        with col:
            st.markdown(
                f"""
                <div class="qt-pillar">
                  <div class="qt-section-kicker">Platform Pillar</div>
                  <div class="qt-pillar-title">{title}</div>
                  <div class="qt-alert-body">{body}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_ai_showcase(plans):
    if not plans:
        return
    leader = plans[0]
    quality = leader["business_quality"]
    st.markdown(
        f"""
        <div class="qt-ai-card">
          <div class="qt-section-kicker">AI Showcase</div>
          <div class="qt-ai-question">Investor question: “What matters most about {leader['symbol']} right now?”</div>
          <div class="qt-ai-summary">
            {leader['symbol']} ranks {leader['opportunity_score']}/100. Trade signal is {leader['score']}/100 and
            business quality is {quality['quality_grade']} ({quality['quality_score']}/100). QuanTrade says
            <strong>{leader['decision']}</strong>: only consider action near ${leader['entry']} with risk controlled near ${leader['stop']}.
          </div>
          <span class="qt-pill qt-pill-watch">{leader.get('horizon', 'Swing Trade')}</span>
          <span class="qt-pill qt-pill-buy">Opportunity {leader['opportunity_score']}</span>
          <span class="qt-pill qt-pill-watch">Business {quality['quality_grade']}</span>
          <span class="qt-pill qt-pill-watch">Target ${leader['target1']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def today_answer(regime, plans):
    buy_plans = [plan for plan in plans if plan["decision"] == "BUY SETUP"]
    watch_plans = [plan for plan in plans if plan["decision"] in ["WAIT FOR TRIGGER", "HOLD / WATCH"]]
    if regime["participation"] == "defensive":
        return "Defensive", "Protect capital. Only review exceptional setups and avoid weak charts."
    if buy_plans:
        leader = buy_plans[0]
        return "Selective Buy Mode", f"Best candidate is {leader['symbol']}, but only above ${leader['entry']} with a stop near ${leader['stop']}."
    if watch_plans:
        leader = watch_plans[0]
        return "Wait For Confirmation", f"{leader['symbol']} is closest, but the agent wants confirmation before any new trade."
    return "No Trade", "The scan does not show a clean opportunity. Waiting is the trade."


def render_today_answer(regime, plans, risk_profile):
    answer, detail = today_answer(regime, plans)
    buy_count = sum(1 for plan in plans if plan["decision"] == "BUY SETUP")
    watch_count = sum(1 for plan in plans if plan["decision"] in ["WAIT FOR TRIGGER", "HOLD / WATCH"])
    avoid_count = sum(1 for plan in plans if plan["decision"] == "SELL / AVOID")
    risk_budget = money(risk_profile.account_size * risk_profile.risk_per_trade_percent / 100)

    st.markdown(
        f"""
        <div class="qt-brief">
          <div class="qt-section-kicker">Today's Answer</div>
          <h2>{answer}</h2>
          <p class="qt-brief-sub">{detail}</p>
          <div>
            <span class="qt-pill qt-pill-buy">Buy setups: {buy_count}</span>
            <span class="qt-pill qt-pill-watch">Watch: {watch_count}</span>
            <span class="qt-pill qt-pill-avoid">Avoid: {avoid_count}</span>
            <span class="qt-pill qt-pill-watch">Risk/trade: ${risk_budget}</span>
            <span class="qt-pill qt-pill-watch">Market: {regime['participation'].title()}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_opportunity_queue(plans):
    st.markdown('<div class="qt-section-kicker">Opportunity Queue</div>', unsafe_allow_html=True)
    st.subheader("What deserves attention now")
    top_plans = plans[:3]
    cols = st.columns(3)
    for col, plan in zip(cols, top_plans):
        pill_class = "qt-pill-buy" if plan["decision"] == "BUY SETUP" else "qt-pill-avoid" if plan["decision"] == "SELL / AVOID" else "qt-pill-watch"
        with col:
            st.markdown(
                f"""
                <div class="qt-queue-card">
                  <div class="qt-card-symbol">{plan['symbol']}</div>
                  <div class="qt-muted">{plan['name']}</div>
                  <div class="qt-card-score">{plan['opportunity_score']}</div>
                  <span class="qt-pill qt-pill-watch">{plan.get('horizon', 'Swing Trade')}</span>
                  <span class="qt-pill {pill_class}">{plan['decision']}</span>
                  <div class="qt-muted">Entry ${plan['entry']} · Stop ${plan['stop']}</div>
                  <div class="qt-muted">Business {plan['business_quality']['quality_grade']} · {plan['rating']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


THEME_MAP = {
    "NVDA": "AI/Semiconductors", "AMD": "AI/Semiconductors", "AVGO": "AI/Semiconductors", "TSM": "AI/Semiconductors",
    "SMCI": "AI/Semiconductors", "ARM": "AI/Semiconductors", "MU": "AI/Semiconductors", "INTC": "AI/Semiconductors",
    "AAPL": "Mega-cap tech", "MSFT": "Mega-cap tech", "META": "Mega-cap tech", "AMZN": "Mega-cap tech", "GOOGL": "Mega-cap tech",
    "COIN": "Crypto-linked", "MSTR": "Crypto-linked", "MARA": "Crypto-linked", "RIOT": "Crypto-linked", "CLSK": "Crypto-linked",
    "BTC-USD": "Crypto", "ETH-USD": "Crypto", "SOL-USD": "Crypto",
    "JPM": "Financials", "BAC": "Financials", "GS": "Financials", "XOM": "Energy",
    "SPY": "ETF/Core", "QQQ": "ETF/Core", "IWM": "ETF/Core", "DIA": "ETF/Core", "SMH": "ETF/Core",
}


def plan_theme(symbol):
    return THEME_MAP.get(symbol, "Other")


def build_signal_inbox(plans, portfolio):
    alerts = []
    portfolio_symbols = set(portfolio.keys())
    plan_by_symbol = {plan["symbol"]: plan for plan in plans}

    for symbol in portfolio_symbols:
        plan = plan_by_symbol.get(symbol)
        if not plan:
            alerts.append(
                {
                    "type": "Holding not scanned",
                    "symbol": symbol,
                    "tone": "watch",
                    "title": f"{symbol}: not in this scan",
                    "body": "Add it to custom tickers if you want a current trade and business-quality read.",
                }
            )
            continue
        if plan["decision"] == "SELL / AVOID":
            tone = "avoid"
            body = f"Your holding is flagged avoid/reduce. Review stop risk near ${plan['stop']} and avoid adding exposure."
        elif plan["decision"] == "BUY SETUP":
            tone = "buy"
            body = f"Your holding has a buy setup, valid only above ${plan['entry']} with risk controlled near ${plan['stop']}."
        else:
            tone = "watch"
            body = f"Your holding is watch-only. QuanTrade wants confirmation before new exposure."
        alerts.append({"type": "Portfolio", "symbol": symbol, "tone": tone, "title": f"{symbol}: {plan['decision']}", "body": body})

    top_buy = [plan for plan in plans if plan["decision"] == "BUY SETUP" and plan["symbol"] not in portfolio_symbols]
    for plan in top_buy[:3]:
        alerts.append(
            {
                "type": "Opportunity",
                "symbol": plan["symbol"],
                "tone": "buy",
                "title": f"{plan['symbol']}: new candidate",
                "body": f"Opportunity {plan['opportunity_score']}/100. Entry ${plan['entry']}, stop ${plan['stop']}, business grade {plan['business_quality']['quality_grade']}.",
            }
        )

    theme_counts = {}
    for symbol in portfolio_symbols:
        theme = plan_theme(symbol)
        theme_counts[theme] = theme_counts.get(theme, 0) + 1
    for theme, count in sorted(theme_counts.items(), key=lambda item: item[1], reverse=True):
        if count >= 3 and theme != "Other":
            alerts.append(
                {
                    "type": "Concentration",
                    "symbol": theme,
                    "tone": "watch",
                    "title": f"{theme}: concentration check",
                    "body": f"You listed {count} names in this theme. Limit new trades in the same group unless risk is reduced elsewhere.",
                }
            )
            break

    if not alerts:
        best = plans[0]
        alerts.append(
            {
                "type": "Market",
                "symbol": best["symbol"],
                "tone": "watch",
                "title": "No portfolio entered",
                "body": f"QuanTrade is running in discovery mode. Top scanned name is {best['symbol']} at {best['opportunity_score']}/100.",
            }
        )
    return alerts[:6]


def render_signal_inbox(plans, portfolio):
    alerts = build_signal_inbox(plans, portfolio)
    st.markdown('<div class="qt-section-kicker">Signal Inbox</div>', unsafe_allow_html=True)
    st.subheader("What changed for you")
    for alert in alerts:
        pill_class = "qt-pill-buy" if alert["tone"] == "buy" else "qt-pill-avoid" if alert["tone"] == "avoid" else "qt-pill-watch"
        st.markdown(
            f"""
            <div class="qt-alert-row">
              <span class="qt-pill {pill_class}">{alert['type']}</span>
              <div class="qt-alert-title">{alert['title']}</div>
              <div class="qt-alert-body">{alert['body']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_screener_table(plans):
    rows = []
    for index, plan in enumerate(plans, start=1):
        factors = plan["factor_grades"]
        quality = plan["business_quality"]
        rows.append(
            {
                "Rank": index,
                "Ticker": plan["symbol"],
                "Company": plan["name"],
                "Workflow": plan.get("workflow_score", plan["opportunity_score"]),
                "Match": "Yes" if plan.get("screen_match", True) else "No",
                "Opportunity": plan["opportunity_score"],
                "Rating": plan["rating"],
                "Trade Signal": plan["score"],
                "Business Quality": f"{quality['quality_grade']} ({quality['quality_score']})",
                "Action": plan["decision"],
                "Momentum": factors["Momentum"],
                "Risk": factors["Risk"],
                "Buy Above": f"${plan['entry']}",
                "Stop": f"${plan['stop']}",
                "Target 1": f"${plan['target1']}",
                "Why": " · ".join(plan_reasons(plan)),
            }
        )

    st.markdown('<div class="qt-section-kicker">AI Stock Picker</div>', unsafe_allow_html=True)
    st.subheader("Ranked opportunities")
    st.markdown(
        '<div class="qt-screener-note">This table is the main workflow: rank first, then open one ticker below for a full decision page.</div>',
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
                st.metric("Opportunity", f"{plan['opportunity_score']}/100")
            c1, c2, c3 = st.columns(3)
            c1.metric("Trigger", f"${plan['entry']}")
            c2.metric("Stop", f"${plan['stop']}")
            c3.metric("Target", f"${plan['target1']}")
            st.caption(f"Invalidation: {plan['invalidation']}")


def action_brief(plan, regime, risk_profile):
    horizon = plan.get("horizon", "Swing Trade")
    if horizon == "Long-Term Invest":
        if plan["business_quality"]["quality_score"] >= 72 and plan["decision"] != "SELL / AVOID":
            action = f"Research {plan['symbol']} for staged accumulation; do not chase without valuation and market confirmation."
        elif plan["decision"] == "SELL / AVOID":
            action = f"Do not add {plan['symbol']} to the long-term portfolio now."
        else:
            action = f"Keep {plan['symbol']} on the long-term watchlist until quality or price improves."
    elif horizon == "Day Trade":
        if plan["decision"] == "BUY SETUP":
            action = f"Intraday only: consider {plan['symbol']} above ${plan['entry']} if volume confirms and VWAP holds."
        elif plan["decision"] == "WAIT FOR TRIGGER":
            action = f"Wait for {plan['symbol']} to break above ${plan['entry']} with strong relative volume."
        else:
            action = f"No day trade in {plan['symbol']} unless the chart resets and confirms."
    else:
        if plan["decision"] == "BUY SETUP":
            action = f"Buy only if {plan['symbol']} confirms above ${plan['entry']}."
        elif plan["decision"] == "WAIT FOR TRIGGER":
            action = f"Wait for {plan['symbol']} to reclaim or break above ${plan['entry']} with volume."
        elif plan["decision"] == "HOLD / WATCH":
            action = f"Watch {plan['symbol']}; do not open a fresh trade yet."
        else:
            action = f"Avoid new buying in {plan['symbol']} for now."

    blockers = []
    if not plan.get("screen_match", True):
        settings = plan.get("screen_settings", {})
        blockers.append(
            f"Does not fully match screen thresholds: trade signal >= {settings.get('min_trade_signal', 55)}, "
            f"business quality >= {settings.get('min_business_quality', 50)}."
        )
    if regime["participation"] == "defensive":
        blockers.append("Market mode is defensive.")
    if plan["business_quality"]["quality_score"] < 55:
        blockers.append("Business quality is weak/speculative.")
    if plan["factor_scores"]["Risk"] < 55:
        blockers.append("Technical risk score is low.")

    next_steps = [
        f"Horizon: {horizon} ({plan.get('holding_period', 'multi-day')}).",
        action,
        f"Risk size: {plan['sizing']['shares']} shares, max loss about ${plan['sizing']['max_loss']}.",
        f"Invalidation: {plan['invalidation']}",
    ]
    if blockers:
        next_steps.insert(1, f"Blocker: {blockers[0]}")
    return next_steps


def render_action_brief(plan, regime, risk_profile):
    st.subheader("Action Brief")
    st.caption("Clear next steps generated from the selected playbook, screen, and risk rules.")
    for step in action_brief(plan, regime, risk_profile):
        st.write(f"- {step}")


def render_screen_logic(plan):
    settings = plan.get("screen_settings", {})
    st.subheader("Screen Logic")
    c1, c2, c3 = st.columns(3)
    c1.metric("Workflow Score", f"{plan.get('workflow_score', plan['opportunity_score'])}/100")
    c2.metric("Screen Match", "Yes" if plan.get("screen_match", True) else "No")
    c3.metric("Horizon", settings.get("horizon", plan.get("horizon", "Swing Trade")))
    st.write(f"Holding period: {settings.get('holding_period', plan.get('holding_period', 'multi-day'))}")
    st.write(f"Strict confirmation: {'Yes' if settings.get('strict_confirmation') else 'No'}")
    st.write(f"Minimum trade signal: {settings.get('min_trade_signal', 55)}")
    st.write(f"Minimum business quality: {settings.get('min_business_quality', 50)}")
    prefer = settings.get("prefer") or ["balanced ranking"]
    avoid = settings.get("avoid") or ["none"]
    st.caption(f"Preferred: {', '.join(prefer)}. Avoid: {', '.join(avoid)}.")


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


def render_portfolio_context(portfolio, plans):
    st.subheader("Portfolio Context")
    if not portfolio:
        st.info("Add holdings or watchlist symbols in the sidebar to personalize alerts.")
        return

    plan_by_symbol = {plan["symbol"]: plan for plan in plans}
    covered = [symbol for symbol in portfolio if symbol in plan_by_symbol]
    missing = [symbol for symbol in portfolio if symbol not in plan_by_symbol]
    exposure = sum(value for value in portfolio.values() if value > 0)
    themes = {}
    for symbol in portfolio:
        theme = plan_theme(symbol)
        themes[theme] = themes.get(theme, 0) + 1

    c1, c2, c3 = st.columns(3)
    c1.metric("Tracked Symbols", len(portfolio))
    c2.metric("Scanned Holdings", len(covered))
    c3.metric("Stated Exposure", f"${money(exposure)}" if exposure else "Not entered")

    if covered:
        rows = []
        for symbol in covered:
            plan = plan_by_symbol[symbol]
            rows.append(
                {
                    "Ticker": symbol,
                    "Decision": plan["decision"],
                    "Opportunity": plan["opportunity_score"],
                    "Trade Signal": plan["score"],
                    "Business": f"{plan['business_quality']['quality_grade']} ({plan['business_quality']['quality_score']})",
                    "Stop": f"${plan['stop']}",
                }
            )
        if pd is not None:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            for row in rows:
                st.write(row)

    if missing:
        st.caption(f"Not in current scan: {', '.join(missing)}. Add them to custom tickers for full analysis.")
    main_theme = max(themes.items(), key=lambda item: item[1])
    if main_theme[1] >= 3 and main_theme[0] != "Other":
        st.warning(f"Concentration check: {main_theme[1]} tracked names are in {main_theme[0]}. Avoid stacking correlated trades.")


def render_playbook_workspace(screen_prompt, horizon, strategy_mode, plans, futures):
    st.subheader("Market Playbook")
    st.caption("A reusable workflow brief based on the current screen and ranking logic.")
    settings = interpret_screen_prompt(f"{screen_prompt}. Playbook: {strategy_mode}.", horizon)
    matched = [plan for plan in plans if plan.get("screen_match", True)]
    buy = [plan for plan in matched if plan["decision"] == "BUY SETUP"]
    watch = [plan for plan in matched if plan["decision"] in ["WAIT FOR TRIGGER", "HOLD / WATCH"]]

    st.markdown(
        f"""
        <div class="qt-ai-card">
          <div class="qt-section-kicker">Saved Screen</div>
          <div class="qt-ai-question">{screen_prompt}</div>
          <div class="qt-ai-summary">
            Horizon: {horizon}. Playbook: {strategy_mode}. Holding period: {settings['holding_period']}.
            Minimum trade signal {settings['min_trade_signal']};
            minimum business quality {settings['min_business_quality']}. Preferred factors:
            {', '.join(settings['prefer'] or ['balanced ranking'])}.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Matched Ideas", len(matched))
    c2.metric("Buy Setups", len(buy))
    c3.metric("Watchlist", len(watch))

    st.write("Workflow:")
    st.write("- Discover: run this screen on the selected universe.")
    st.write("- Analyse: open the top matched ticker in Stock Workbench.")
    st.write("- Act: trade only if the Action Brief has no blocker and the entry trigger confirms.")
    st.write("- Review: add missed portfolio symbols to custom tickers next scan.")

    if futures:
        st.divider()
        st.subheader("Longer-Term Ideas")
        st.caption("These are watchlist candidates, not urgent trade signals.")
        for item in futures:
            render_future_card(item)


def percent_text(value):
    return f"{round(safe_number(value), 1)}%"


def ratio_text(value):
    return f"{round(safe_number(value), 2)}"


def render_stock_detail(plan, regime):
    quality = plan["business_quality"]
    fundamentals = plan["fundamentals"]

    st.markdown('<div class="qt-section-kicker">Stock Detail</div>', unsafe_allow_html=True)
    left, right = st.columns([0.68, 0.32], vertical_alignment="center")
    with left:
        st.subheader(f"{plan['symbol']} · {plan['name']}")
        st.write(f"Decision: **{plan['decision']}** · Rating: **{plan['rating']}**")
        st.caption(f"{participation_label(plan)} · {plan['setup']} · {plan['regime_rule']}")
    with right:
        st.metric("Opportunity Score", f"{plan['opportunity_score']}/100")

    detail_tabs = st.tabs(["Action Brief", "Trade Plan", "Financials", "Signals", "Risk", "Screen Logic"])

    with detail_tabs[0]:
        render_action_brief(plan, regime, st.session_state.get("risk_profile"))

    with detail_tabs[1]:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Buy Trigger", f"${plan['entry']}")
        c2.metric("Stop", f"${plan['stop']}")
        c3.metric("Target 1", f"${plan['target1']}")
        c4.metric("Target 2", f"${plan['target2']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Shares", plan["sizing"]["shares"])
        c2.metric("Position", f"${plan['sizing']['position_value']}")
        c3.metric("Max Loss", f"${plan['sizing']['max_loss']}")
        c4.metric("Risk / Share", f"${plan['sizing']['risk_per_share']}")
        st.write(plan["action_note"])
        st.caption(plan["invalidation"])

    with detail_tabs[2]:
        st.subheader(f"Business Quality: {quality['quality_grade']} · {quality['quality_label']}")
        c1, c2, c3, c4, c5 = st.columns(5)
        grades = quality["financial_grades"]
        c1.metric("Growth", grades["Growth"])
        c2.metric("Profitability", grades["Profitability"])
        c3.metric("Cash Flow", grades["Cash Flow"])
        c4.metric("Balance Sheet", grades["Balance Sheet"])
        c5.metric("Valuation", grades["Valuation"])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Revenue Growth", percent_text(fundamentals["revenue_growth"]))
        m2.metric("EPS / Earnings Growth", percent_text(fundamentals["eps_growth"]))
        m3.metric("Gross Margin", percent_text(fundamentals["gross_margin"]))
        m4.metric("Net Margin", percent_text(fundamentals["net_margin"]))
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("FCF Margin", percent_text(fundamentals["fcf_margin"]))
        m2.metric("Debt / Equity", ratio_text(fundamentals["debt_to_equity"]))
        m3.metric("Current Ratio", ratio_text(fundamentals["current_ratio"]))
        m4.metric("ROE", percent_text(fundamentals["roe"]))
        m1, m2, m3 = st.columns(3)
        m1.metric("P/E", ratio_text(fundamentals["pe"]))
        m2.metric("P/S", ratio_text(fundamentals["ps"]))
        m3.metric("P/B", ratio_text(fundamentals["pb"]))
        st.caption(f"{fundamentals['financial_notes']} Source: {fundamentals['fundamental_source']}.")

    with detail_tabs[3]:
        c1, c2, c3, c4, c5 = st.columns(5)
        grades = plan["factor_grades"]
        c1.metric("Momentum", grades["Momentum"])
        c2.metric("Technical", grades["Technical"])
        c3.metric("Liquidity", grades["Liquidity"])
        c4.metric("Risk", grades["Risk"])
        c5.metric("Timing", grades["Timing"])
        st.write("Signal reasons:")
        for reason in plan_reasons(plan):
            st.write(f"- {reason}")
        st.caption(f"Market mode: {regime['participation'].title()} · {regime['rule']}")

    with detail_tabs[4]:
        atr_percent = (plan["atr"] / max(plan["price"], 0.01)) * 100
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ATR", f"${plan['atr']}")
        c2.metric("ATR %", percent_text(atr_percent))
        c3.metric("Relative Volume", ratio_text(plan["relative_volume"]))
        c4.metric("Avg Volume", f"{int(plan['average_volume']):,}")
        st.write("Risk controls:")
        st.write("- Avoid chasing above the trigger if the move is already extended.")
        st.write("- Do not increase size after a losing trade.")
        st.write("- If price loses VWAP with heavy volume, the setup is invalid.")
        st.write("- If market mode turns defensive, reduce or skip new exposure.")

    with detail_tabs[5]:
        render_screen_logic(plan)
        st.write(
            f"QuanTrade ranks {plan['symbol']} at {plan['opportunity_score']}/100 because the trade signal is "
            f"{plan['score']}/100 and business quality is {quality['quality_score']}/100. "
            f"The current decision is {plan['decision'].lower()}. "
            f"The setup should only be acted on if price confirms near ${plan['entry']} and risk is controlled near ${plan['stop']}."
        )
        st.caption("This explanation is informational only. Verify data and make your own trading decision.")


def render_plan(plan):
    is_buy = plan["decision"] == "BUY SETUP"
    is_sell = plan["decision"] == "SELL / AVOID"
    with st.container(border=True):
        top_left, top_right = st.columns([0.70, 0.30])
        with top_left:
            st.subheader(f"{plan['symbol']}")
            st.markdown(f"**{plan['rating']} · {plan['decision']}**")
            st.caption(
                f"{plan['setup']} · Opportunity {plan['opportunity_score']}/100 · "
                f"Business {plan['business_quality']['quality_grade']} · Data: {plan['source']}"
            )
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

        q1, q2, q3 = st.columns(3)
        q1.metric("Trade Signal", f"{plan['score']}/100")
        q2.metric("Business Quality", f"{plan['business_quality']['quality_score']}/100")
        q3.metric("Financial Grade", plan["business_quality"]["quality_grade"])

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
        st.subheader("AI Screening")
        horizon = st.selectbox("Horizon", ["Day Trade", "Swing Trade", "Long-Term Invest"], index=1)
        screen_prompt = st.text_area(
            "Plain-English screen",
            value="Find risk-aware candidates with strong business quality and clear entry levels.",
            height=86,
        )
        strategy_mode = st.selectbox("Playbook", ["Balanced", "Breakout", "Pullback", "Small-cap discovery", "Defensive watchlist"])
        universe_index = 1 if "Auto: Broad opportunity scan" in DEFAULT_UNIVERSES else 0
        universe_name = st.selectbox("Market universe", list(DEFAULT_UNIVERSES.keys()), index=universe_index)
        st.caption(f"{len(DEFAULT_UNIVERSES[universe_name])} symbols will be ranked by trade signal and business quality.")
        use_live_data = st.toggle("Use live Yahoo Finance data when available", value=True)
        max_results = st.slider("Ranked results to show", 5, 40, 15)
        rating_filter = st.selectbox("Minimum rating", ["All ratings", "Buy or better", "Strong Buy only"])
        show_avoid = st.toggle("Show sell/avoid names", value=True)
        with st.expander("Advanced: scan my own tickers"):
            use_custom_tickers = st.checkbox("Override market scan with custom tickers", value=False)
            custom = st.text_area("Custom tickers", value=", ".join(DEFAULT_UNIVERSES[universe_name]), height=90)
        st.divider()
        st.subheader("Portfolio Context")
        portfolio_text = st.text_area(
            "Holdings / watchlist",
            value="NVDA 2500, AAPL 1500, SPY 3000",
            height=82,
            help="Optional. Use symbols only or symbol + dollar amount, for example: NVDA 2500, AAPL 1500.",
        )
        st.divider()
        st.subheader("Risk Rules")
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
    run_scan = st.button("Scan Today's Market", type="primary")

    if not run_scan and "plans" not in st.session_state:
        st.markdown(
            """
            <div class="qt-brief">
              <div class="qt-section-kicker">Start Here</div>
              <h2>Start with a screen, finish with a decision</h2>
              <p class="qt-brief-sub">QuanTrade will discover qualified ideas, analyse the top tickers, and turn the strongest setups into entry levels, stops, targets, and portfolio-aware next steps.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("QuanTrade is a decision-support assistant. It does not guarantee outcomes.")
        return

    if run_scan:
        tickers = clean_tickers(custom) if use_custom_tickers else DEFAULT_UNIVERSES[universe_name]
        risk_profile = RiskProfile(account_size, risk_percent, max_position_percent, max_daily_loss_percent)
        with st.spinner("Scanning market, scoring setups, and building risk-aware plans..."):
            combined_prompt = f"{screen_prompt}. Playbook: {strategy_mode}."
            regime, plans = scan_trades(tickers, risk_profile, use_live_data, max_results, combined_prompt, horizon)
            futures = scan_future(future_risk, future_sectors, future_results)
        st.session_state["regime"] = regime
        st.session_state["plans"] = plans
        st.session_state["futures"] = futures
        st.session_state["risk_profile"] = risk_profile
        st.session_state["last_scan"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        st.session_state["scan_universe"] = "Custom tickers" if use_custom_tickers else universe_name
        st.session_state["strategy_mode"] = strategy_mode
        st.session_state["horizon"] = horizon
        st.session_state["screen_prompt"] = screen_prompt
        st.session_state["portfolio"] = parse_portfolio(portfolio_text)
        st.session_state["scanned_count"] = len(tickers)

    regime = st.session_state["regime"]
    raw_plans = st.session_state["plans"]
    plans = [plan for plan in raw_plans if passes_rating_filter(plan, rating_filter)]
    if not show_avoid:
        plans = [plan for plan in plans if plan["decision"] != "SELL / AVOID"]
    futures = st.session_state["futures"]
    risk_profile = st.session_state["risk_profile"]
    portfolio = st.session_state.get("portfolio", parse_portfolio(portfolio_text))

    avg_score = round(sum(plan["opportunity_score"] for plan in plans) / len(plans), 1) if plans else 0

    st.caption(
        f"Scanned: {st.session_state.get('scan_universe', universe_name)} · "
        f"Horizon: {st.session_state.get('horizon', horizon)} · "
        f"Playbook: {st.session_state.get('strategy_mode', strategy_mode)} · "
        f"Screen: {st.session_state.get('screen_prompt', screen_prompt)} · "
        f"{st.session_state.get('scanned_count', len(raw_plans))} symbols · Average Opportunity Score: {avg_score}/100 · "
        f"Last scan: {st.session_state['last_scan']} · Data mode: {regime['source']}"
    )

    if not plans:
        st.warning("No names match the current rating filter. Change Minimum rating or show sell/avoid names.")
        return

    render_platform_pillars()
    buy_plans = [plan for plan in plans if plan["decision"] == "BUY SETUP"]
    wait_plans = [plan for plan in plans if plan["decision"] in ["WAIT FOR TRIGGER", "HOLD / WATCH"]]
    sell_plans = [plan for plan in plans if plan["decision"] == "SELL / AVOID"]

    render_today_answer(regime, plans, risk_profile)
    render_ai_showcase(plans)
    render_opportunity_queue(plans)
    render_signal_inbox(plans, portfolio)

    st.divider()
    opportunities_tab, workbench_tab, risk_tab, discover_tab, assistant_tab = st.tabs(
        ["Discover", "Analyse", "Act", "Playbooks", "Ask AI"]
    )

    with opportunities_tab:
        render_screener_table(plans)
        st.divider()
        st.subheader("Market Movers")
        st.caption("High activity names from the current scan, ranked by relative volume.")
        render_market_movers(plans)

    with workbench_tab:
        selected_symbol = st.selectbox(
            "Stock to inspect",
            [plan["symbol"] for plan in plans],
            index=0,
            help="Open one stock and review the full decision page.",
        )
        selected_plan = next(plan for plan in plans if plan["symbol"] == selected_symbol)
        render_stock_detail(selected_plan, regime)

    with risk_tab:
        render_portfolio_guard(risk_profile, buy_plans)
        st.divider()
        render_portfolio_context(portfolio, plans)
        st.divider()
        render_smart_signals(plans)

    with discover_tab:
        render_playbook_workspace(
            st.session_state.get("screen_prompt", screen_prompt),
            st.session_state.get("horizon", horizon),
            st.session_state.get("strategy_mode", strategy_mode),
            plans,
            futures,
        )

    with assistant_tab:
        st.subheader("Ask QuanTrade Intelligence")
        question = st.text_area(
            "Question",
            placeholder="Ask what changed, what matters in your portfolio, or compare stocks, ETFs, and crypto from this scan...",
            height=120,
        )
        if st.button("Ask AI Assistant", type="primary"):
            signal_inbox = build_signal_inbox(plans, portfolio)
            context = {
                "market_regime": regime["bias"],
                "participation": regime["participation"],
                "rule": regime["rule"],
                "screen_prompt": st.session_state.get("screen_prompt", screen_prompt),
                "horizon": st.session_state.get("horizon", horizon),
                "playbook": st.session_state.get("strategy_mode", strategy_mode),
                "portfolio": portfolio,
                "signal_inbox": signal_inbox,
                "buy_setups": [
                    {
                        "symbol": p["symbol"],
                        "rating": p["rating"],
                        "opportunity_score": p["opportunity_score"],
                        "trade_signal": p["score"],
                        "business_quality": p["business_quality"]["quality_score"],
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
                        "opportunity_score": p["opportunity_score"],
                        "trade_signal": p["score"],
                        "business_quality": p["business_quality"]["quality_score"],
                        "factor_grades": p["factor_grades"],
                    }
                    for p in wait_plans[:5]
                ],
                "sell_avoid": [
                    {
                        "symbol": p["symbol"],
                        "rating": p["rating"],
                        "opportunity_score": p["opportunity_score"],
                        "trade_signal": p["score"],
                        "business_quality": p["business_quality"]["quality_score"],
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
