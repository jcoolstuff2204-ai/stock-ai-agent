"""Order abstractions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderRequest:
    """Idempotent marketable-limit order request."""

    client_order_id: str
    symbol: str
    side: str
    qty: int
    limit_price: float
    order_type: str = "marketable_limit"
    time_in_force: str = "day"

