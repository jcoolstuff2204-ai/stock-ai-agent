"""QuanTrade Streamlit command center."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from stock_agent.app.run_cycle import run_signal_cycle  # noqa: E402
from stock_agent.config import Settings  # noqa: E402


st.set_page_config(page_title="QuanTrade AI Agent", layout="wide")

st.markdown(
    """
    <style>
    :root { --bg:#060913; --panel:#0f172a; --ink:#f8fafc; --muted:#94a3b8; --cyan:#00e5ff; --green:#22c55e; --red:#ef4444; }
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: radial-gradient(circle at top right, rgba(0,229,255,.12), transparent 28rem), var(--bg) !important; }
    h1,h2,h3,p,span,div,label { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    h1,h2,h3 { color: var(--ink) !important; }
    p, .stCaption { color: var(--muted); }
    [data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"] { background: var(--panel); border: 1px solid #263244; border-radius: 16px; }
    button[kind="primary"], .stButton > button { background: linear-gradient(135deg, var(--cyan), #8b5cf6) !important; color: #020617 !important; border-radius: 14px !important; border: 0 !important; font-weight: 800 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("QuanTrade AI Agent")
st.caption("Research-grade stock scanning, signal ranking, risk controls, and paper trading by default.")

with st.sidebar:
    st.subheader("Signal Cycle")
    mode = st.selectbox("Mode", ["eod", "intraday"], index=0)
    horizon = st.selectbox("Horizon", ["day", "swing", "long"], index=1)
    account_equity = st.number_input("Account equity", min_value=1000.0, value=10_000.0, step=500.0)
    risk_per_trade = st.number_input("Risk per trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1) / 100
    run = st.button("Run Signal Cycle", type="primary")

settings = Settings.from_env()
settings.risk.account_equity = account_equity
settings.risk.risk_per_trade = risk_per_trade

if not run:
    st.info("Run the EOD signal cycle to generate ranked buy candidates, sell/avoid ideas, risk decisions, and paper orders.")
    st.write(settings.compliance.disclosure)
    st.stop()

report = run_signal_cycle(settings, mode=mode, horizon=horizon)
ranked = report.ranked
approved = report.approved
orders = report.orders

buy_count = int((ranked["signal"] == "BUY_CANDIDATE").sum())
avoid_count = int((ranked["signal"] == "SELL_AVOID").sum())
approved_count = int(approved["risk_approved"].sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Mode", mode.upper())
c2.metric("Buy Candidates", buy_count)
c3.metric("Sell / Avoid", avoid_count)
c4.metric("Risk Approved", approved_count)

st.subheader("Ranked Ideas")
st.dataframe(
    ranked[["symbol", "name", "sector", "long_score", "confidence", "signal", "rationale"]].head(20),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Risk Decisions")
st.dataframe(
    approved[["symbol", "signal", "risk_approved", "risk_reason", "target_shares", "close", "atr"]].head(20),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Paper Orders")
if orders.empty:
    st.warning("No paper orders produced. This is normal when risk blocks candidates or no score clears threshold.")
else:
    st.dataframe(orders, use_container_width=True, hide_index=True)

st.caption(report.disclosure)

