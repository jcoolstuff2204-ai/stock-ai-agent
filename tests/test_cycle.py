from stock_agent.app.run_cycle import run_signal_cycle
from stock_agent.config import Settings


def test_e2e_eod_cycle_produces_ranked_signals():
    report = run_signal_cycle(Settings(), mode="eod", horizon="swing")
    assert not report.ranked.empty
    assert {"symbol", "long_score", "signal", "rationale"}.issubset(report.ranked.columns)
    assert "Signals are informational" in report.disclosure

