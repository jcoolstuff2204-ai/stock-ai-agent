"""SQLite schema."""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS scan_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scan_date TEXT NOT NULL,
  ticker TEXT NOT NULL,
  company_name TEXT NOT NULL,
  price REAL NOT NULL,
  action_label TEXT NOT NULL,
  confidence_score REAL NOT NULL,
  promising_score REAL NOT NULL,
  risk_level TEXT NOT NULL,
  entry_low REAL NOT NULL,
  entry_high REAL NOT NULL,
  stop_loss REAL NOT NULL,
  suggested_shares INTEGER NOT NULL,
  suggested_position_value REAL NOT NULL,
  main_reason TEXT NOT NULL,
  full_explanation_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paper_trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ticker TEXT NOT NULL,
  action TEXT NOT NULL,
  entry_price REAL NOT NULL,
  stop_loss REAL NOT NULL,
  target_price REAL NOT NULL,
  shares INTEGER NOT NULL,
  opened_at TEXT NOT NULL,
  closed_at TEXT,
  close_price REAL,
  status TEXT NOT NULL,
  realized_pnl REAL
);

CREATE TABLE IF NOT EXISTS user_settings (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  account_size REAL NOT NULL,
  risk_per_trade_percent REAL NOT NULL,
  max_position_percent REAL NOT NULL,
  max_positions INTEGER NOT NULL,
  min_price REAL NOT NULL,
  min_avg_volume INTEGER NOT NULL,
  avoid_penny_stocks INTEGER NOT NULL DEFAULT 1,
  paper_mode_enabled INTEGER NOT NULL,
  universe_json TEXT NOT NULL
);
"""
