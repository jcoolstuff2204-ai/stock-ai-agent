# QuanTrade AI Agent

QuanTrade AI Agent is a personal stock research assistant for low-capital traders. It scans a U.S. stock and ETF universe, ranks promising buy/watch/avoid candidates, explains every signal, and suggests paper-trade position sizes based on account risk.

This is a research assistant and it does not place live trades. Signals are educational research only, not financial advice, and no outcome is guaranteed.

## Features

- Daily market scan from a configurable stock universe
- Ranked action labels: Strong Buy Candidate, Buy Small / Watch, Watchlist, Neutral / Hold, Avoid / Sell Candidate
- Low-capital protection rules for price, liquidity, volatility, position size, and max active positions
- Suggested entry zone, stop loss, target, and share count
- Explanation drawer with bullish factors, risk factors, and next action
- SQLite persistence for latest scans, settings, and paper trades
- yfinance data provider with deterministic mock fallback for offline demos
- React + FastAPI prototype

## Tech Stack

- Frontend: React, Vite, TypeScript, Tailwind CSS
- Backend: FastAPI, pandas, numpy, SQLite
- Data: yfinance first, mock fallback if data is unavailable
- AI layer: optional OpenAI explanation placeholder, rule-based fallback by default

## Run Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
uvicorn backend.app.main:app --reload --port 8000
```

Backend health check:

```bash
curl http://localhost:8000/health
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Docker Compose

```bash
cp .env.example .env
docker compose up
```

## Environment

Copy `.env.example` to `.env`. `OPENAI_API_KEY` is optional. Without it, the app uses rule-based explanations.

Key variables:

- `VITE_API_BASE_URL=http://localhost:8000`
- `QUANTRADE_DB_PATH=backend/quantrade.sqlite3`
- `OPENAI_API_KEY=`
- `TRADING_ENABLED=false`

## Scoring System

Promising Stock Score v1:

- 30% price momentum
- 20% volume strength
- 15% trend quality
- 15% relative strength vs SPY
- 10% volatility and risk control
- 10% liquidity quality

Action labels:

- 85-100: Strong Buy Candidate
- 70-84: Buy Small / Watch
- 55-69: Watchlist
- 40-54: Neutral / Hold
- Below 40: Avoid / Sell Candidate

## Risk Sizing

Suggested shares are calculated from:

```text
dollar_risk_allowed = account_size * risk_per_trade_percent
risk_per_share = entry_price - stop_loss_price
shares_by_risk = dollar_risk_allowed / risk_per_share
max_position_value = account_size * max_position_percent
shares_by_position_cap = max_position_value / entry_price
suggested_shares = min(shares_by_risk, shares_by_position_cap)
```

Default low-capital rules avoid stocks under $5, thin volume, extreme volatility, margin, short selling, options, and live trading.

## API

- `GET /health`
- `POST /api/scan`
- `GET /api/signals/latest`
- `GET /api/stocks/{ticker}`
- `POST /api/paper-trades`
- `GET /api/paper-trades`
- `PATCH /api/paper-trades/{id}/close`
- `GET /api/settings`
- `POST /api/settings`

## Tests

```bash
pytest backend/tests
```

## Safety

- This app is for educational and research purposes only.
- Signals are not financial advice.
- No result is guaranteed.
- Always review risk before placing any trade.
- Paper trading results may differ from live trading.

## Roadmap

- Phase 1: Rule-based stock scanner and paper trading
- Phase 2: Alpaca paper trading integration
- Phase 3: Backtesting dashboard
- Phase 4: Machine learning ranking model
- Phase 5: Broader market universe and fundamentals analysis
