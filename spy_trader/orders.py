"""Order planning, management, and simple execution glue."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from spy_trader import config
from spy_trader.indicators.channel import compute_channel
from spy_trader.risk import reached_breakeven_threshold, should_time_stop
from spy_trader.screens import EntryPlan, Tide, next_trailing_stop
from spy_trader.state import PendingOrder, Position


@dataclass(frozen=True)
class ManagedPosition:
    symbol: str
    stop_price: float
    target_price: float | None
    move_to_breakeven: bool
    close_at_next_open: bool


def plan_pending_order(entry: EntryPlan, today: date) -> PendingOrder:
    return PendingOrder(
        symbol=entry.symbol,
        trigger_price=entry.trigger_price,
        stop_price=entry.stop_price,
        shares=entry.shares,
        created_at=today.isoformat(),
    )


def pending_order_expired(created_at: date, today: date) -> bool:
    return (today - created_at).days >= config.BUY_STOP_EXPIRY_DAYS


def manage_position(
    position: Position,
    daily_bars: pd.DataFrame,
    today: date,
    tide: Tide,
) -> ManagedPosition:
    close = float(daily_bars["close"].iloc[-1])
    breakeven = reached_breakeven_threshold(position.entry_price, position.stop_price, close)
    stop_price = position.entry_price if breakeven else position.stop_price
    stop_price = max(stop_price, next_trailing_stop(daily_bars))
    channel = compute_channel(
        daily_bars["close"],
        ema_span=config.EMA_CHANNEL,
        width_pct=config.CHANNEL_WIDTH_PCT,
    )
    target = float(channel.upper.iloc[-1])
    tide_flip = (tide is Tide.DOWN and position.symbol == "SPY") or (
        tide is Tide.UP and position.symbol == "SH"
    )
    close_next_open = should_time_stop(
        entry_date=date.fromisoformat(position.entry_date),
        as_of_date=today,
        reached_one_r=breakeven,
    ) or tide_flip
    return ManagedPosition(
        symbol=position.symbol,
        stop_price=stop_price,
        target_price=target,
        move_to_breakeven=breakeven,
        close_at_next_open=close_next_open,
    )
