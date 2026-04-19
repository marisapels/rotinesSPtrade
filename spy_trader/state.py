"""Schema-versioned JSON-backed engine state."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from tempfile import NamedTemporaryFile

from spy_trader.screens import Tide


@dataclass
class PendingOrder:
    symbol: str
    trigger_price: float
    stop_price: float
    shares: int
    created_at: str


@dataclass
class Position:
    symbol: str
    entry_price: float
    stop_price: float
    shares: int
    entry_date: str
    target_price: float | None = None
    close_at_next_open: bool = False


@dataclass
class MonthState:
    month_start: str
    month_start_equity: float
    min_equity_so_far: float
    breaker_tripped: bool = False


@dataclass
class EngineState:
    schema_version: int = 1
    tide: str = Tide.FLAT.value
    trading_disabled: bool = False
    pending_orders: list[PendingOrder] = field(default_factory=list)
    positions: list[Position] = field(default_factory=list)
    month: MonthState | None = None


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> EngineState:
        if not self.path.exists():
            return EngineState()
        raw = json.loads(self.path.read_text())
        pending = [PendingOrder(**item) for item in raw.get("pending_orders", [])]
        positions = [Position(**item) for item in raw.get("positions", [])]
        month_raw = raw.get("month")
        month = MonthState(**month_raw) if month_raw is not None else None
        return EngineState(
            schema_version=raw.get("schema_version", 1),
            tide=raw.get("tide", Tide.FLAT.value),
            trading_disabled=raw.get("trading_disabled", False),
            pending_orders=pending,
            positions=positions,
            month=month,
        )

    def save(self, state: EngineState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", dir=self.path.parent, delete=False) as handle:
            json.dump(asdict(state), handle, indent=2, sort_keys=True)
            temp_path = Path(handle.name)
        temp_path.replace(self.path)


def month_state_for_equity(day: date, equity: float) -> MonthState:
    month_start = day.replace(day=1).isoformat()
    return MonthState(
        month_start=month_start,
        month_start_equity=equity,
        min_equity_so_far=equity,
    )
