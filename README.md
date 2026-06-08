# QuanTrade AI Agent

QuanTrade is a modular AI stock-scanning and signal agent. It is rebuilt as a research-grade, paper-first system with clear separation between data, features, ranking, signals, risk, execution, and reporting.

It does **not** promise profit. Signals are informational research outputs and require independent review.

## Quick Start

```bash
python -m pip install -e ".[dev]"
quantrade health-check
quantrade generate-signals --mode eod --horizon swing
streamlit run streamlit_app.py
```

## Default Scope

- U.S. equities and ETFs first
- EOD mode required
- Intraday mode scaffolded
- Long-only buy candidates plus sell/avoid signals
- Paper broker by default
- Live trading blocked unless explicitly enabled

## Architecture

See [docs/architecture.md](docs/architecture.md).

## Sample Output

```json
{
  "top_ideas": [
    {
      "symbol": "NVDA",
      "long_score": 88.1,
      "signal": "BUY_CANDIDATE",
      "rationale": "positive momentum, strong quality"
    }
  ],
  "approved_orders": 2,
  "disclosure": "Signals are informational research outputs, not financial advice..."
}
```

## Safety

- Paper trading is the default.
- Risk engine runs before every order.
- Stale data blocks orders.
- Order IDs are idempotent.
- Secrets must be environment variables.
- `.env` and `.env.local` must never be committed.

