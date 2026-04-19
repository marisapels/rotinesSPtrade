"""Command-line entry point."""

from __future__ import annotations

import argparse

from spy_trader.cron import dispatch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="spy-trader")
    parser.add_argument(
        "routine",
        choices=["pre-market", "post-close", "weekly", "monthly", "fill-watcher"],
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    dispatch(args.routine)


if __name__ == "__main__":
    main()
