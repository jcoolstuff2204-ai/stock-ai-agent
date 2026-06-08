"""Report generation for ranked ideas and orders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass(frozen=True)
class CycleReport:
    """Serializable EOD signal report."""

    as_of: datetime
    ranked: pd.DataFrame
    approved: pd.DataFrame
    orders: pd.DataFrame
    disclosure: str

    def summary(self) -> dict[str, object]:
        """Return a compact report summary."""
        top = self.ranked.head(5)[["symbol", "long_score", "signal", "rationale"]].to_dict("records")
        return {
            "as_of": self.as_of.isoformat(),
            "top_ideas": top,
            "approved_orders": len(self.orders),
            "disclosure": self.disclosure,
        }

