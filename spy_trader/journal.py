"""Markdown journal writers."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from spy_trader import config


def _month_dir(day: date, root: Path = config.JOURNAL_DIR) -> Path:
    return root / f"{day.year:04d}" / f"{day.month:02d}"


def write_pre_market_note(day: date, note: dict[str, Any], root: Path = config.JOURNAL_DIR) -> Path:
    path = _month_dir(day, root) / "pre_market" / f"{day.isoformat()}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Pre-Market {day.isoformat()}", ""]
    for key, value in note.items():
        lines.append(f"- **{key}**: {value}")
    path.write_text("\n".join(lines) + "\n")
    return path


def append_trade_entry(day: date, payload: dict[str, Any], root: Path = config.JOURNAL_DIR) -> Path:
    path = _month_dir(day, root) / "trades.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text() if path.exists() else "# Trades\n\n"
    lines = [existing.rstrip(), f"## {day.isoformat()} {payload.get('symbol', '')}".rstrip()]
    for key, value in payload.items():
        lines.append(f"- **{key}**: {value}")
    path.write_text("\n".join(lines) + "\n")
    return path


def write_aar(day: date, title: str, body: str, root: Path = config.JOURNAL_DIR) -> Path:
    path = _month_dir(day, root) / "aar" / f"{day.isoformat()}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{body}\n")
    return path


def serialize_dataclass_payload(payload: Any) -> dict[str, Any]:
    return asdict(payload)
