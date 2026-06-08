"""Portfolio routes placeholder for v1."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/summary")
def portfolio_summary() -> dict[str, object]:
    """Return v1 portfolio summary placeholder."""
    return {"mode": "paper", "live_trading": False, "message": "Paper portfolio tracking is available under /api/paper-trades."}

