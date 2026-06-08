from backend.app.models.schemas import UserSettings
from backend.app.services.signal_engine import SignalEngine


def test_signal_score_calculation_uses_mock_data():
    settings = UserSettings(universe=["NVDA", "AAPL"], min_avg_volume=1)
    results, demo = SignalEngine().scan(settings)
    assert results
    assert demo in [True, False]
    assert 0 <= results[0].promising_score <= 100

