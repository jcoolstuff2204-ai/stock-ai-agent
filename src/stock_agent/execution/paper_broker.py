"""Paper broker adapter."""

from __future__ import annotations

import hashlib

import pandas as pd

from stock_agent.execution.orders import OrderRequest


class PaperBroker:
    """In-memory paper broker with idempotent order keys."""

    def __init__(self) -> None:
        self.submitted: dict[str, OrderRequest] = {}

    def build_orders(self, approved: pd.DataFrame) -> list[OrderRequest]:
        """Build marketable-limit buy orders for approved rows."""
        orders: list[OrderRequest] = []
        rows = approved[(approved["risk_approved"]) & (approved["target_shares"] > 0)]
        for row in rows.itertuples(index=False):
            key_src = f"{row.symbol}:{row.as_of}:{row.target_shares}:BUY"
            client_id = hashlib.sha256(key_src.encode()).hexdigest()[:24]
            orders.append(
                OrderRequest(
                    client_order_id=client_id,
                    symbol=row.symbol,
                    side="buy",
                    qty=int(row.target_shares),
                    limit_price=round(float(row.close) * 1.002, 2),
                )
            )
        return orders

    def submit_orders(self, orders: list[OrderRequest]) -> pd.DataFrame:
        """Submit paper orders idempotently."""
        for order in orders:
            self.submitted.setdefault(order.client_order_id, order)
        return pd.DataFrame([order.__dict__ for order in self.submitted.values()])

