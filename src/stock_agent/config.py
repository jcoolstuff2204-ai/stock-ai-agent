"""Application configuration and compliance policy."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field


class CompliancePolicy(BaseModel):
    """Configurable compliance posture for research and signal reports."""

    jurisdiction: str = "unspecified"
    advice_mode: str = "self_directed_research"
    suitability_required: bool = False
    human_approval_required: bool = True
    disclosures_required: bool = True

    @property
    def disclosure(self) -> str:
        """Return standard disclosure text for reports."""
        return (
            "Signals are informational research outputs, not financial advice. "
            "They do not guarantee profit and require independent review."
        )


class RiskSettings(BaseModel):
    """Portfolio and execution risk limits."""

    account_equity: float = 10_000.0
    risk_per_trade: float = 0.01
    max_single_name_weight: float = Field(default=0.10, gt=0, le=1)
    max_sector_weight: float = Field(default=0.35, gt=0, le=1)
    max_adv_participation: float = Field(default=0.01, gt=0, le=1)
    max_daily_turnover: float = Field(default=0.25, gt=0, le=1)
    stale_data_minutes: int = 90
    drawdown_circuit_breaker: float = 0.08


class Settings(BaseModel):
    """Runtime settings. Live trading fails closed unless explicitly enabled."""

    app_env: str = "dev"
    timezone: str = "America/New_York"
    market_scope: str = "us_equities"
    mode: str = "eod"
    primary_data_provider: str = "mock"
    primary_broker: str = "paper"
    trading_enabled: bool = False
    duckdb_path: Path = Path("data/quantrade.duckdb")
    risk: RiskSettings = Field(default_factory=RiskSettings)
    compliance: CompliancePolicy = Field(default_factory=CompliancePolicy)

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from environment variables."""
        risk = RiskSettings(
            max_single_name_weight=float(os.getenv("MAX_SINGLE_NAME_WEIGHT", "0.10")),
            max_sector_weight=float(os.getenv("MAX_SECTOR_WEIGHT", "0.35")),
            max_adv_participation=float(os.getenv("MAX_ADV_PARTICIPATION", "0.01")),
            max_daily_turnover=float(os.getenv("MAX_DAILY_TURNOVER", "0.25")),
        )
        compliance = CompliancePolicy(
            jurisdiction=os.getenv("COMPLIANCE_JURISDICTION", "unspecified"),
            advice_mode=os.getenv("COMPLIANCE_ADVICE_MODE", "self_directed_research"),
        )
        return cls(
            app_env=os.getenv("APP_ENV", "dev"),
            timezone=os.getenv("TIMEZONE", "America/New_York"),
            market_scope=os.getenv("MARKET_SCOPE", "us_equities"),
            mode=os.getenv("MODE", "eod"),
            primary_data_provider=os.getenv("PRIMARY_DATA_PROVIDER", "mock"),
            primary_broker=os.getenv("PRIMARY_BROKER", "paper"),
            trading_enabled=os.getenv("TRADING_ENABLED", "false").lower() == "true",
            duckdb_path=Path(os.getenv("DUCKDB_PATH", "data/quantrade.duckdb")),
            risk=risk,
            compliance=compliance,
        )

    def assert_live_allowed(self) -> None:
        """Raise if live execution is not explicitly enabled."""
        if self.primary_broker != "paper" and not self.trading_enabled:
            raise RuntimeError("Live trading blocked: TRADING_ENABLED=false.")


@dataclass(frozen=True)
class RunContext:
    """Metadata attached to a signal cycle."""

    mode: str
    as_of_utc: str
    model_version: str
    feature_version: str

