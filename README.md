# Stock AI Agent

Short-term stock market scanner and financial-assistant foundation.

The first version focuses on disciplined trade planning:

- Automatically scans a market universe.
- Filters for liquid short-term setups.
- Scores trade quality.
- Suggests when to buy, when to sell, and how much to buy.
- Calculates max loss from account risk settings.
- Uses OpenAI to explain the trade plan when enabled.

This is not financial advice. It is a decision-support tool. Start with paper trading before using any live broker connection.

## Run

### Streamlit app

```bash
streamlit run streamlit_app.py
```

### Node prototype

```bash
npm run scan
npm start
```

Then open:

```text
http://localhost:4321
```

## Current Mode

The app starts with mock market data so the scanner, scoring, and trade-plan flow can be tested immediately.

Next live integrations to add:

- Alpaca market data and paper trading.
- Polygon stock snapshots/news.
- Broker order preview and human approval.

## Deploy To Streamlit Cloud

1. Push this project to a GitHub repository.
2. Go to `https://share.streamlit.io`.
3. Choose the repository and branch.
4. Set the main file path to:

```text
streamlit_app.py
```

5. Add app secrets in Streamlit Cloud:

```toml
OPENAI_API_KEY = "your_openai_platform_key"
OPENAI_MODEL = "gpt-4.1-mini"
```

Do not upload `.env.local` to GitHub.
