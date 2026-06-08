"""Command line interface for QuanTrade."""

from __future__ import annotations

import argparse
import json

from stock_agent.app.run_cycle import run_signal_cycle
from stock_agent.config import Settings


def main() -> None:
    """Run the CLI."""
    parser = argparse.ArgumentParser(prog="quantrade")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("health-check")
    signals = sub.add_parser("generate-signals")
    signals.add_argument("--mode", default="eod", choices=["eod", "intraday"])
    signals.add_argument("--horizon", default="swing", choices=["day", "swing", "long"])
    sub.add_parser("paper-trade")
    sub.add_parser("report")
    sub.add_parser("ingest-data")
    sub.add_parser("build-features")
    sub.add_parser("train-model")
    sub.add_parser("backtest")
    args = parser.parse_args()

    settings = Settings.from_env()
    if args.command == "health-check":
        print(json.dumps({"ok": True, "trading_enabled": settings.trading_enabled, "broker": settings.primary_broker}))
        return
    if args.command in {"generate-signals", "paper-trade", "report"}:
        report = run_signal_cycle(settings, mode=getattr(args, "mode", "eod"), horizon=getattr(args, "horizon", "swing"))
        print(json.dumps(report.summary(), indent=2))
        return
    print(json.dumps({"ok": True, "command": args.command, "status": "scaffolded"}))


if __name__ == "__main__":
    main()

