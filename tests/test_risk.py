from datetime import datetime, timezone

import pandas as pd

from stock_agent.config import RiskSettings
from stock_agent.risk.engine import RiskEngine


def test_risk_engine_blocks_stale_data():
    rows = pd.DataFrame(
        [
            {
                "symbol": "NVDA",
                "signal": "BUY_CANDIDATE",
                "atr": 4.0,
                "close": 100.0,
                "avg_volume": 10_000_000,
            }
        ]
    )
    settings = RiskSettings(stale_data_minutes=-1)
    approved = RiskEngine(settings).approve_and_size(rows, pd.DataFrame(), datetime.now(timezone.utc))
    assert not bool(approved.loc[0, "risk_approved"])
    assert approved.loc[0, "risk_reason"] == "stale data block"

