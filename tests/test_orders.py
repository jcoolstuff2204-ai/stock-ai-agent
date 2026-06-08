from stock_agent.app.run_cycle import run_signal_cycle
from stock_agent.config import Settings


def test_paper_order_ids_are_unique():
    report = run_signal_cycle(Settings(), mode="eod", horizon="swing")
    if not report.orders.empty:
        assert report.orders["client_order_id"].is_unique

