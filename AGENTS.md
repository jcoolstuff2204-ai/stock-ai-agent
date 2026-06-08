# QuanTrade AI Agent Instructions

- Keep the app modular: routes, services, models, frontend pages, and components should stay separated.
- Do not add live brokerage order placement without explicit user approval.
- Paper trading and manual review must remain the default behavior.
- All signal logic must be explainable from computed data.
- Do not remove financial-risk warnings or compliance disclaimers.
- Do not hardcode API keys, tokens, or brokerage credentials.
- Keep the frontend beginner-friendly: the main path is scan, review why, size risk, paper trade.
- Prefer simple working implementation over over-engineered architecture.
- Add short comments only where trading/risk logic would be hard to understand.
