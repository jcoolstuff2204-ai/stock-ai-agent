"""Paper trading API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.models.schemas import PaperTrade, PaperTradeCreate
from backend.app.services.paper_trading_engine import PaperTradingEngine

router = APIRouter(prefix="/api/paper-trades", tags=["paper-trades"])


class CloseTradeRequest(BaseModel):
    """Close paper trade request."""

    close_price: float = Field(gt=0)


@router.post("", response_model=PaperTrade)
def create_trade(trade: PaperTradeCreate) -> PaperTrade:
    """Create a paper trade."""
    return PaperTradingEngine().create_trade(trade)


@router.get("", response_model=list[PaperTrade])
def list_trades() -> list[PaperTrade]:
    """List paper trades."""
    return PaperTradingEngine().list_trades()


@router.patch("/{trade_id}/close", response_model=PaperTrade)
def close_trade(trade_id: int, request: CloseTradeRequest) -> PaperTrade:
    """Close a paper trade."""
    try:
        return PaperTradingEngine().close_trade(trade_id, request.close_price)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

