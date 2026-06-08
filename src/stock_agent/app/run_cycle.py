"""End-to-end EOD signal cycle."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from stock_agent.config import Settings
from stock_agent.data.mock_provider import MockDataProvider
from stock_agent.data.universe import UniverseSelector
from stock_agent.execution.paper_broker import PaperBroker
from stock_agent.features.pipeline import FeaturePipeline
from stock_agent.models.ranker import BaselineRanker
from stock_agent.reporting import CycleReport
from stock_agent.risk.engine import RiskEngine
from stock_agent.signals.policy import SignalPolicy


def run_signal_cycle(settings: Settings, mode: str = "eod", horizon: str = "swing") -> CycleReport:
    """Run ingest -> features -> rank -> signals -> risk -> paper orders."""
    as_of = datetime.now(timezone.utc)
    provider = MockDataProvider()
    universe = UniverseSelector()
    features = FeaturePipeline()
    model = BaselineRanker()
    policy = SignalPolicy()
    risk = RiskEngine(settings.risk)
    broker = PaperBroker()

    market = provider.load_market_snapshot(as_of=as_of, mode=mode)
    eligible = universe.filter(market)
    fundamentals = provider.load_fundamentals(eligible["symbol"].tolist(), as_of=as_of)
    macro = provider.load_macro(as_of=as_of)
    feature_df = features.transform(market, fundamentals, macro, eligible["symbol"].tolist(), as_of)
    ranked = model.rank(feature_df, horizon=horizon)
    signals = policy.generate(ranked, as_of)
    portfolio = pd.DataFrame(columns=["symbol", "qty", "market_value"])
    approved = risk.approve_and_size(signals, portfolio, as_of)
    orders = broker.submit_orders(broker.build_orders(approved))
    return CycleReport(as_of=as_of, ranked=signals, approved=approved, orders=orders, disclosure=settings.compliance.disclosure)

