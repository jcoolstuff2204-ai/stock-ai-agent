"""Pydantic request and response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UserSettings(BaseModel):
    """Low-capital account and scan settings."""

    account_size: float = Field(default=1000, gt=0)
    risk_per_trade_percent: float = Field(default=1.0, gt=0, le=10)
    max_position_percent: float = Field(default=15.0, gt=0, le=100)
    max_positions: int = Field(default=5, ge=1, le=25)
    min_price: float = Field(default=5.0, ge=0)
    min_avg_volume: int = Field(default=500_000, ge=0)
    avoid_penny_stocks: bool = True
    paper_mode_enabled: bool = True
    universe: list[str] = Field(default_factory=list)


class ScanRequest(BaseModel):
    """Request body for POST /api/scan."""

    settings: UserSettings = Field(default_factory=UserSettings)


class PositionSizing(BaseModel):
    """Risk-controlled position sizing output."""

    suggested_shares: int
    suggested_position_value: float
    dollar_risk_allowed: float
    risk_per_share: float
    no_trade_reason: str | None = None


class StockSignal(BaseModel):
    """A ranked stock signal."""

    ticker: str
    company_name: str
    price: float
    action_label: str
    confidence_score: float
    promising_score: float
    risk_level: str
    entry_low: float
    entry_high: float
    stop_loss: float
    target_price: float
    suggested_shares: int
    suggested_position_value: float
    main_reason: str
    explanation: dict[str, Any]
    demo_data: bool = False
    do_not_trade: bool = False


class ScanResponse(BaseModel):
    """Scan response."""

    scan_date: datetime
    demo_data_mode: bool
    disclosure: str
    results: list[StockSignal]


class PaperTradeCreate(BaseModel):
    """Create a paper trade."""

    ticker: str
    action: str = "BUY"
    entry_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    target_price: float = Field(gt=0)
    shares: int = Field(gt=0)


class PaperTrade(BaseModel):
    """Paper trade record."""

    id: int
    ticker: str
    action: str
    entry_price: float
    stop_loss: float
    target_price: float
    shares: int
    opened_at: str
    closed_at: str | None
    close_price: float | None
    status: str
    realized_pnl: float | None

