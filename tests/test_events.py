from __future__ import annotations

import json
from pathlib import Path

from spy_trader.events import EventBus, JsonlEventSink


def test_event_bus_writes_jsonl(tmp_path: Path) -> None:
    sink = JsonlEventSink(tmp_path / "events.jsonl")
    bus = EventBus([sink])
    bus.emit("kind", "message", a=1)
    lines = (tmp_path / "events.jsonl").read_text().splitlines()
    payload = json.loads(lines[0])
    assert payload["kind"] == "kind"
