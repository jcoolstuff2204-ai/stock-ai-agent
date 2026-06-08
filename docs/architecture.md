# QuanTrade Architecture

QuanTrade is rebuilt as a layered signal platform, not a monolithic LLM trader.

## Layers

- `config`: settings, risk limits, compliance policy, and hard live-trading gate.
- `data`: provider interfaces, mock development provider, and universe filtering.
- `features`: point-in-time feature generation.
- `models`: baseline factor ranker, with hooks for future gradient boosting.
- `signals`: policy that converts ranks into buy/watch/sell-avoid signals.
- `risk`: sizing, stale-data prevention, liquidity caps, and portfolio guardrails.
- `execution`: paper broker and idempotent order requests.
- `app`: end-to-end signal cycle.
- `streamlit_app.py`: command center UI on top of the modular engine.

## Default Workflow

1. Load market snapshot.
2. Filter universe by liquidity, price, and spread.
3. Join point-in-time fundamentals and macro context.
4. Generate technical, liquidity, quality, valuation, and risk features.
5. Rank symbols by horizon: day, swing, or long.
6. Convert ranks into buy/watch/sell-avoid signals.
7. Apply risk engine and stale-data blocks.
8. Build idempotent paper orders.
9. Export report and disclosure.

Live execution is disabled unless `TRADING_ENABLED=true` and a non-paper broker is deliberately configured.

