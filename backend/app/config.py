"""Backend configuration."""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("QUANTRADE_DB_PATH", BASE_DIR / "quantrade.sqlite3"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

DEFAULT_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "AMD", "TSLA", "META", "AMZN", "GOOGL", "NFLX", "AVGO",
    "PLTR", "SOFI", "HOOD", "COIN", "SMCI", "SHOP", "CRWD", "SNOW", "UBER", "RIVN",
    "IONQ", "RKLB", "SOUN", "BBAI", "UPST", "AI", "PATH", "LCID", "F", "NU",
    "NIO", "DNA", "CHPT", "OPEN", "WULF", "MARA", "RIOT", "SPY", "QQQ",
]

DISCLOSURE = (
    "This app is for educational and research purposes only. Signals are not financial advice. "
    "No result is guaranteed. Always review risk before placing any trade. Paper trading results "
    "may differ from live trading."
)
