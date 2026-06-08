"""Settings and watchlist service."""

from __future__ import annotations

import json

from backend.app.config import DEFAULT_UNIVERSE
from backend.app.db.database import get_connection
from backend.app.models.schemas import UserSettings


class SettingsService:
    """Persist user settings in SQLite."""

    def get_settings(self) -> UserSettings:
        """Return saved settings or defaults."""
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM user_settings WHERE id = 1").fetchone()
        if row is None:
            return UserSettings(universe=DEFAULT_UNIVERSE)
        data = dict(row)
        return UserSettings(
            account_size=data["account_size"],
            risk_per_trade_percent=data["risk_per_trade_percent"],
            max_position_percent=data["max_position_percent"],
            max_positions=data["max_positions"],
            min_price=data["min_price"],
            min_avg_volume=data["min_avg_volume"],
            paper_mode_enabled=bool(data["paper_mode_enabled"]),
            avoid_penny_stocks=bool(data["avoid_penny_stocks"]) if "avoid_penny_stocks" in data else True,
            universe=json.loads(data["universe_json"]),
        )

    def save_settings(self, settings: UserSettings) -> UserSettings:
        """Save settings."""
        universe = settings.universe or DEFAULT_UNIVERSE
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO user_settings
                (id, account_size, risk_per_trade_percent, max_position_percent, max_positions,
                 min_price, min_avg_volume, avoid_penny_stocks, paper_mode_enabled, universe_json)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  account_size=excluded.account_size,
                  risk_per_trade_percent=excluded.risk_per_trade_percent,
                  max_position_percent=excluded.max_position_percent,
                  max_positions=excluded.max_positions,
                  min_price=excluded.min_price,
                  min_avg_volume=excluded.min_avg_volume,
                  avoid_penny_stocks=excluded.avoid_penny_stocks,
                  paper_mode_enabled=excluded.paper_mode_enabled,
                  universe_json=excluded.universe_json
                """,
                (
                    settings.account_size,
                    settings.risk_per_trade_percent,
                    settings.max_position_percent,
                    settings.max_positions,
                    settings.min_price,
                    settings.min_avg_volume,
                    int(settings.avoid_penny_stocks),
                    int(settings.paper_mode_enabled),
                    json.dumps(universe),
                ),
            )
        data = settings.model_dump()
        data["universe"] = universe
        return UserSettings(**data)
