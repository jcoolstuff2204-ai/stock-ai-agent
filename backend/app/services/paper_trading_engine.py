"""Paper trading service."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.db.database import get_connection
from backend.app.models.schemas import PaperTrade, PaperTradeCreate


class PaperTradingEngine:
    """SQLite-backed paper trading engine."""

    def create_trade(self, trade: PaperTradeCreate) -> PaperTrade:
        """Create a paper trade."""
        opened_at = datetime.now(timezone.utc).isoformat()
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO paper_trades
                (ticker, action, entry_price, stop_loss, target_price, shares, opened_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN')
                """,
                (trade.ticker.upper(), trade.action, trade.entry_price, trade.stop_loss, trade.target_price, trade.shares, opened_at),
            )
            trade_id = int(cur.lastrowid)
        return self.get_trade(trade_id)

    def list_trades(self) -> list[PaperTrade]:
        """List paper trades."""
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM paper_trades ORDER BY id DESC").fetchall()
        return [PaperTrade(**dict(row)) for row in rows]

    def get_trade(self, trade_id: int) -> PaperTrade:
        """Get one paper trade."""
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM paper_trades WHERE id = ?", (trade_id,)).fetchone()
        if row is None:
            raise ValueError("Trade not found.")
        return PaperTrade(**dict(row))

    def close_trade(self, trade_id: int, close_price: float) -> PaperTrade:
        """Close a paper trade and calculate P/L."""
        trade = self.get_trade(trade_id)
        pnl = (close_price - trade.entry_price) * trade.shares
        closed_at = datetime.now(timezone.utc).isoformat()
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE paper_trades
                SET closed_at = ?, close_price = ?, status = 'CLOSED', realized_pnl = ?
                WHERE id = ?
                """,
                (closed_at, close_price, round(pnl, 2), trade_id),
            )
        return self.get_trade(trade_id)

