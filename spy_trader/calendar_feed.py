"""Economic calendar seam."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class CalendarEvent:
    day: str
    title: str
    category: str


def load_calendar_events(day: date, path: Path | None = None) -> list[CalendarEvent]:
    file_path = path or Path("fixtures/calendar.json")
    if not file_path.exists():
        return []
    raw = json.loads(file_path.read_text())
    return [CalendarEvent(**item) for item in raw if item["day"] == day.isoformat()]
