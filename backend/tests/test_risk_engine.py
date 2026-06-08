from backend.app.models.schemas import UserSettings
from backend.app.services.risk_engine import calculate_position_size


def test_position_sizing_respects_risk_and_position_cap():
    settings = UserSettings(account_size=1000, risk_per_trade_percent=1, max_position_percent=15)
    sizing = calculate_position_size(settings, entry_price=10, stop_loss_price=9)
    assert sizing.suggested_shares == 10
    assert sizing.suggested_position_value == 100

