"""Scan API routes."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.app.config import DEFAULT_UNIVERSE, DISCLOSURE
from backend.app.db.database import get_connection
from backend.app.models.schemas import ScanRequest, ScanResponse, StockSignal
from backend.app.services.signal_engine import SignalEngine

router = APIRouter(prefix="/api", tags=["scan"])


@router.post("/scan", response_model=ScanResponse)
def run_scan(request: ScanRequest) -> ScanResponse:
    """Run a daily stock scan."""
    settings = request.settings
    if not settings.universe:
        settings.universe = DEFAULT_UNIVERSE
    try:
        results, demo_mode = SignalEngine().scan(settings)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    scan_date = datetime.now(timezone.utc)
    with get_connection() as conn:
        conn.execute("DELETE FROM scan_results")
        for item in results:
            conn.execute(
                """
                INSERT INTO scan_results
                (scan_date, ticker, company_name, price, action_label, confidence_score, promising_score,
                 risk_level, entry_low, entry_high, stop_loss, suggested_shares, suggested_position_value,
                 main_reason, full_explanation_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_date.isoformat(),
                    item.ticker,
                    item.company_name,
                    item.price,
                    item.action_label,
                    item.confidence_score,
                    item.promising_score,
                    item.risk_level,
                    item.entry_low,
                    item.entry_high,
                    item.stop_loss,
                    item.suggested_shares,
                    item.suggested_position_value,
                    item.main_reason,
                    json.dumps(item.explanation),
                ),
            )
    return ScanResponse(scan_date=scan_date, demo_data_mode=demo_mode, disclosure=DISCLOSURE, results=results)


@router.get("/signals/latest", response_model=list[StockSignal])
def latest_signals() -> list[StockSignal]:
    """Return latest persisted scan results."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM scan_results ORDER BY promising_score DESC").fetchall()
    return [
        StockSignal(
            ticker=row["ticker"],
            company_name=row["company_name"],
            price=row["price"],
            action_label=row["action_label"],
            confidence_score=row["confidence_score"],
            promising_score=row["promising_score"],
            risk_level=row["risk_level"],
            entry_low=row["entry_low"],
            entry_high=row["entry_high"],
            stop_loss=row["stop_loss"],
            target_price=round(row["price"] + (row["price"] - row["stop_loss"]) * 1.8, 2),
            suggested_shares=row["suggested_shares"],
            suggested_position_value=row["suggested_position_value"],
            main_reason=row["main_reason"],
            explanation=json.loads(row["full_explanation_json"]),
        )
        for row in rows
    ]


@router.get("/stocks/{ticker}", response_model=StockSignal)
def stock_detail(ticker: str) -> StockSignal:
    """Return latest signal details for one ticker."""
    ticker = ticker.upper()
    rows = latest_signals()
    for row in rows:
        if row.ticker == ticker:
            return row
    raise HTTPException(status_code=404, detail="Ticker not found in latest scan.")

