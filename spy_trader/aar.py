"""After-action review helpers."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from spy_trader import config
from spy_trader.journal import write_aar


def write_daily_aar(day: date, body: str, root: Path = config.JOURNAL_DIR) -> Path:
    return write_aar(day, "Daily AAR", body, root=root)


def write_weekly_aar(day: date, body: str, root: Path = config.JOURNAL_DIR) -> Path:
    return write_aar(day, "Weekly Rollup", body, root=root)


def write_monthly_aar(day: date, body: str, root: Path = config.JOURNAL_DIR) -> Path:
    return write_aar(day, "Monthly Review", body, root=root)
