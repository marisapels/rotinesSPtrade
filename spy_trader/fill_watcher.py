"""Intraday fill watcher stub."""

from __future__ import annotations

from spy_trader.events import EventBus


def run_fill_watcher(event_bus: EventBus) -> None:
    event_bus.emit("fill_watcher", "Fill watcher executed")
