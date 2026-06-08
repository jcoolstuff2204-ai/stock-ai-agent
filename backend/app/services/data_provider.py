"""Stock data provider with yfinance and mock fallback."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

try:
    import yfinance as yf
except Exception:  # pragma: no cover - optional local dependency
    yf = None


MOCK_INFO = {
    "NVDA": "NVIDIA Corporation",
    "AMD": "Advanced Micro Devices",
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "PLTR": "Palantir Technologies",
    "SOFI": "SoFi Technologies",
    "HOOD": "Robinhood Markets",
    "SPY": "SPDR S&P 500 ETF",
    "QQQ": "Invesco QQQ Trust",
}


@dataclass
class PriceHistory:
    """Price history plus demo-data marker."""

    ticker: str
    company_name: str
    history: pd.DataFrame
    demo_data: bool


class StockDataProvider:
    """Fetch stock price history from yfinance or deterministic mock data."""

    def get_price_history(self, ticker: str, period: str = "1y") -> PriceHistory:
        """Return OHLCV history for one ticker."""
        ticker = ticker.upper().strip()
        if yf is not None:
            try:
                stock = yf.Ticker(ticker)
                history = stock.history(period=period, auto_adjust=False)
                if history is not None and len(history) >= 60:
                    info = {}
                    try:
                        info = stock.fast_info or {}
                    except Exception:
                        info = {}
                    name = str(info.get("longName") or info.get("shortName") or MOCK_INFO.get(ticker, ticker))
                    return PriceHistory(ticker, name, history.reset_index(), False)
            except Exception:
                pass
        return PriceHistory(ticker, MOCK_INFO.get(ticker, ticker), self._mock_history(ticker), True)

    def get_batch_price_history(self, tickers: list[str], period: str = "1y") -> list[PriceHistory]:
        """Return history for many tickers."""
        return [self.get_price_history(ticker, period) for ticker in tickers]

    def get_spy_benchmark(self) -> PriceHistory:
        """Return SPY benchmark history."""
        return self.get_price_history("SPY")

    def get_company_info(self, ticker: str) -> dict[str, str]:
        """Return best-effort company info."""
        return {"ticker": ticker.upper(), "company_name": MOCK_INFO.get(ticker.upper(), ticker.upper())}

    @staticmethod
    def _mock_history(ticker: str) -> pd.DataFrame:
        """Create deterministic mock OHLCV data for offline mode."""
        seed = sum(ord(ch) for ch in ticker)
        rng = np.random.default_rng(seed)
        days = 260
        base = max(6, (seed % 180) + 8)
        trend = ((seed % 17) - 5) / 10_000
        returns = rng.normal(trend, 0.025, days)
        close = base * np.cumprod(1 + returns)
        volume_base = 600_000 + (seed % 90) * 150_000
        volume = volume_base * rng.uniform(0.65, 1.8, days)
        dates = pd.date_range(end=pd.Timestamp.utcnow().normalize(), periods=days, freq="B")
        return pd.DataFrame(
            {
                "Date": dates,
                "Open": close * rng.uniform(0.99, 1.01, days),
                "High": close * rng.uniform(1.00, 1.04, days),
                "Low": close * rng.uniform(0.96, 1.00, days),
                "Close": close,
                "Volume": volume.astype(int),
            }
        )

