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
  --midnight: #0B1020;
  --card: #111827;
  --panel: #0F172A;
  --cyan: #00E5FF;
  --purple: #7C3AED;
  --green: #22C55E;
  --red: #EF4444;
  --gray: #CBD5E1;
  --muted: #94A3B8;
  --border: #334155;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background:
    radial-gradient(circle at 18% 0%, rgba(0, 229, 255, 0.10), transparent 28%),
    radial-gradient(circle at 85% 0%, rgba(124, 58, 237, 0.16), transparent 34%),
    var(--midnight) !important;
}

[data-testid="stSidebar"] {
  background: #080D1B !important;
  border-right: 1px solid var(--border);
}

.block-container {
  max-width: 1260px;
  padding-top: 2rem;
  padding-bottom: 4rem;
}

h1, h2, h3, h4, p, label, span, div {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
}

h1, h2, h3, h4 {
  color: #FFFFFF !important;
  letter-spacing: 0 !important;
}

p, .stCaption, [data-testid="stMarkdownContainer"] {
  color: var(--gray);
}

[data-testid="stMetric"] {
  background: rgba(17, 24, 39, 0.92);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1rem;
}

[data-testid="stMetricValue"] {
  color: #FFFFFF;
  font-variant-numeric: tabular-nums;
}

button[kind="primary"], .stButton > button {
  background: var(--cyan) !important;
  color: var(--midnight) !important;
  border: 0 !important;
  border-radius: 14px !important;
  font-weight: 850 !important;
  min-height: 2.8rem;
}

button[kind="primary"] *, .stButton > button * {
  color: var(--midnight) !important;
  font-weight: 850 !important;
}

[data-baseweb="tab"] {
  color: var(--gray) !important;
  font-weight: 750 !important;
}

[data-baseweb="tab"][aria-selected="true"] {
  color: #FFFFFF !important;
}

[data-testid="stSidebar"] input,
[data-testid="stSidebar"] [data-baseweb="input"] {
  background: var(--card) !important;
  color: #FFFFFF !important;
}
</style>
"""


DEFAULT_UNIVERSES = {
    "High-liquidity leaders": [
        "NVDA", "AMD", "AAPL", "MSFT", "META", "AMZN", "GOOGL", "AVGO", "TSLA", "NFLX",
        "COIN", "MSTR", "PLTR", "SMCI", "JPM", "XOM", "SPY", "QQQ", "IWM", "MARA",
    ],
    "AI and semiconductors": [
        "NVDA", "AMD", "AVGO", "SMCI", "ARM", "TSM", "MU", "PLTR", "SOUN", "AI",
    ],
    "Future potential watchlist": [
        "RXRX", "IONQ", "SOUN", "ASTS", "RKLB", "ENVX", "CRSP", "JOBY", "HIMS", "PLTR",
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
        return "Avoid: liquidity risk"
    if score >= 80:
        return "Trade candidate"
    if score >= 68:
        return "Watch for confirmation"
    if score >= 55:
        return "Watchlist only"
    return "Avoid for now"


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
        "setup": setup,
        "entry": entry,
        "stop": stop,
        "target1": target1,
        "target2": target2,
        "sizing": sizing,
        "invalidation": f"Skip or exit if {quote['symbol']} loses VWAP near ${quote['vwap']} with heavy selling volume.",
    }


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
    st.markdown("### QuanTrade AI Agent")
    st.caption("Smarter signals. Calmer trading.")


def render_header():
    with st.container(border=True):
        left, right = st.columns([0.72, 0.28], vertical_alignment="center")
        with left:
            st.caption("AI-powered market analysis assistant")
            st.title("QuanTrade AI Agent")
            st.subheader("Analyze before you trade.")
            st.write(
                "A risk-aware trading desk for scanning stocks, building trade plans, sizing positions, "
                "tracking future opportunities, and asking an AI co-pilot for market context."
            )
            st.caption("For informational purposes only. Not financial advice.")
        with right:
            st.metric("Workflow", "Scan -> Plan -> Risk")
            st.metric("Mode", "Decision Support")


def render_plan(plan):
    color = "normal"
    if "Avoid" in plan["decision"]:
        color = "inverse"
    with st.container(border=True):
        top_left, top_right = st.columns([0.70, 0.30])
        with top_left:
            st.subheader(f"{plan['symbol']} · {plan['decision']}")
            st.caption(f"{plan['setup']} · Grade {plan['grade']} · Data: {plan['source']}")
        with top_right:
            st.metric("Trade Quality", f"{plan['score']}/100")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Entry trigger", f"${plan['entry']}")
        c2.metric("Stop", f"${plan['stop']}")
        c3.metric("Target 1", f"${plan['target1']}")
        c4.metric("Target 2", f"${plan['target2']}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Shares", plan["sizing"]["shares"])
        c2.metric("Position", f"${plan['sizing']['position_value']}")
        c3.metric("Max loss", f"${plan['sizing']['max_loss']}")
        c4.metric("Risk/share", f"${plan['sizing']['risk_per_share']}")

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
        st.subheader("Market Scan")
        universe_name = st.selectbox("Universe", list(DEFAULT_UNIVERSES.keys()))
        custom = st.text_area("Custom tickers", value=", ".join(DEFAULT_UNIVERSES[universe_name]), height=110)
        use_live_data = st.toggle("Use live Yahoo Finance data when available", value=True)
        max_results = st.slider("Trade setups to show", 3, 20, 10)
        st.divider()
        st.subheader("Risk Rules")
        account_size = st.number_input("Account size", min_value=1000.0, value=10000.0, step=500.0)
        risk_percent = st.number_input("Risk per trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
        max_position_percent = st.number_input("Max position size (%)", min_value=1.0, max_value=100.0, value=25.0, step=1.0)
        max_daily_loss_percent = st.number_input("Max daily loss (%)", min_value=0.5, max_value=10.0, value=3.0, step=0.5)
        st.divider()
        st.subheader("Future Potential")
        future_risk = st.selectbox("Future risk tolerance", ["Balanced", "Conservative", "Aggressive"])
        future_results = st.slider("Future names to show", 3, 9, 6)
        future_sectors = st.multiselect("Future sectors", ["All"] + sorted({item[2] for item in FUTURE_COMPANIES}), default=["All"])

    render_header()
    run_scan = st.button("Start Analyzing", type="primary")

    if not run_scan and "plans" not in st.session_state:
        st.info("Choose your universe and risk rules, then click Start Analyzing.")
        st.caption("QuanTrade is a decision-support assistant. It does not guarantee outcomes.")
        return

    if run_scan:
        tickers = clean_tickers(custom)
        risk_profile = RiskProfile(account_size, risk_percent, max_position_percent, max_daily_loss_percent)
        with st.spinner("Scanning market, scoring setups, and building risk-aware plans..."):
            regime, plans = scan_trades(tickers, risk_profile, use_live_data, max_results)
            futures = scan_future(future_risk, future_sectors, future_results)
        st.session_state["regime"] = regime
        st.session_state["plans"] = plans
        st.session_state["futures"] = futures
        st.session_state["risk_profile"] = risk_profile
        st.session_state["last_scan"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    regime = st.session_state["regime"]
    plans = st.session_state["plans"]
    futures = st.session_state["futures"]
    risk_profile = st.session_state["risk_profile"]

    trade_candidates = sum(1 for plan in plans if plan["decision"] == "Trade candidate")
    watch_count = sum(1 for plan in plans if "Watch" in plan["decision"])
    avoid_count = sum(1 for plan in plans if "Avoid" in plan["decision"])
    avg_score = round(sum(plan["score"] for plan in plans) / len(plans), 1) if plans else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Market Regime", regime["bias"].title())
    c2.metric("Trade Candidates", trade_candidates)
    c3.metric("Watchlist", watch_count)
    c4.metric("Avg Quality", f"{avg_score}/100")
    st.caption(f"Last scan: {st.session_state['last_scan']} · Data mode: {regime['source']}")

    command_tab, trade_tab, future_tab, risk_tab, assistant_tab, journal_tab = st.tabs(
        ["Command Center", "Trade Setups", "Future Potential", "Risk Coach", "AI Assistant", "Journal"]
    )

    with command_tab:
        st.subheader("Today’s Trading Desk")
        st.write(
            "QuanTrade separates immediate trade setups from longer-term opportunity scouting. "
            "A good result is not always a trade; sometimes the correct answer is watch, wait, or reduce size."
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("SPY", f"${regime['spy']['price']}", regime["spy"]["sector_trend"])
        c2.metric("QQQ", f"${regime['qqq']['price']}", regime["qqq"]["sector_trend"])
        c3.metric("Daily Loss Limit", f"${money(risk_profile.account_size * risk_profile.max_daily_loss_percent / 100)}")
        st.warning("Before any live trade: confirm news, earnings date, spread, liquidity, and your personal risk limit.")

    with trade_tab:
        st.subheader("Short-Term Trade Setups")
        st.caption("Entry, stop, targets, and position sizing are generated from the risk settings in the sidebar.")
        for plan in plans:
            render_plan(plan)

    with future_tab:
        st.subheader("Future Potential")
        st.caption("Smaller and emerging companies are scored for watchlist quality, not guaranteed upside.")
        for item in futures:
            render_future_card(item)

    with risk_tab:
        st.subheader("Risk Coach")
        max_daily_loss = money(risk_profile.account_size * risk_profile.max_daily_loss_percent / 100)
        per_trade = money(risk_profile.account_size * risk_profile.risk_per_trade_percent / 100)
        st.write("Risk rules QuanTrade will use:")
        st.write(f"- Risk per trade: about ${per_trade}")
        st.write(f"- Stop trading for the day near: ${max_daily_loss} loss")
        st.write(f"- Max position size: {risk_profile.max_position_percent}% of account")
        st.write("- Avoid adding to losing trades unless a separate plan was written before entry.")
        st.write("- Prefer no trade over a low-quality setup.")

    with assistant_tab:
        st.subheader("Ask QuanTrade")
        question = st.text_area(
            "Question",
            placeholder="Ask QuanTrade about a stock, crypto, risk, market trend, or your trade plan...",
            height=120,
        )
        if st.button("Ask AI Assistant", type="primary"):
            context = {
                "market_regime": regime["bias"],
                "top_trade_setups": [{"symbol": p["symbol"], "decision": p["decision"], "score": p["score"]} for p in plans[:5]],
                "future_watchlist": [{"symbol": f["symbol"], "action": f["action"], "score": f["score"]} for f in futures[:5]],
            }
            prompt = f"User question: {question}\n\nCurrent QuanTrade context:\n{json.dumps(context, indent=2)}"
            st.write(openai_brief(prompt))
        st.caption("AI responses are informational and may be wrong. Verify before acting.")

    with journal_tab:
        st.subheader("Trade Journal")
        st.write("Use this to build discipline after each trade.")
        journal_symbol = st.text_input("Ticker")
        journal_plan = st.text_area("Trade thesis / what you planned")
        journal_result = st.text_area("Result / lesson")
        if st.button("Save Journal Note"):
            if "journal" not in st.session_state:
                st.session_state["journal"] = []
            st.session_state["journal"].append(
                {
                    "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                    "symbol": journal_symbol.upper(),
                    "plan": journal_plan,
                    "result": journal_result,
                }
            )
        for note in reversed(st.session_state.get("journal", [])):
            with st.container(border=True):
                st.caption(note["time"])
                st.write(f"Ticker: {note['symbol']}")
                st.write(note["plan"])
                st.write(note["result"])


if __name__ == "__main__":
    main()
