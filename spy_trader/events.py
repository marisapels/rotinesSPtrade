"""Event dataclasses and dispatcher."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Event:
    kind: str
    message: str
    payload: dict[str, object] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
    )


class EventSink(Protocol):
    def publish(self, event: Event) -> None: ...


class JsonlEventSink:
    def __init__(self, path: Path) -> None:
        self.path = path

    def publish(self, event: Event) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as handle:
            handle.write(json.dumps(asdict(event), sort_keys=True) + "\n")


class EventBus:
    def __init__(self, sinks: list[EventSink] | None = None) -> None:
        self.sinks = sinks or []

    def emit(self, kind: str, message: str, **payload: object) -> Event:
        event = Event(kind=kind, message=message, payload=dict(payload))
        for sink in self.sinks:
            sink.publish(event)
        return event
