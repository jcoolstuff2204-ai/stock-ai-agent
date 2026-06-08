from datetime import datetime, timezone

from stock_agent.data.mock_provider import MockDataProvider
from stock_agent.data.universe import UniverseSelector


def test_universe_filters_thin_names():
    provider = MockDataProvider()
    market = provider.load_market_snapshot(datetime.now(timezone.utc), "eod")
    eligible = UniverseSelector().filter(market)
    assert "SMALL" not in eligible["symbol"].tolist()
    assert "NVDA" in eligible["symbol"].tolist()
