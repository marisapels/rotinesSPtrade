"""Portfolio risk rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from spy_trader import config


@dataclass(frozen=True)
class OpenRisk:
    symbol: str
    entry_price: float
    stop_price: float
    shares: int

    @property
    def dollars(self) -> float:
        return max(0.0, (self.entry_price - self.stop_price) * self.shares)


def sum_open_risk(positions: list[OpenRisk]) -> float:
    return sum(position.dollars for position in positions)


def would_exceed_heat_cap(
    equity: float,
    positions: list[OpenRisk],
    new_risk_dollars: float,
    heat_cap: float = config.HEAT_CAP,
) -> bool:
    return sum_open_risk(positions) + new_risk_dollars > equity * heat_cap


def monthly_breaker_tripped(
    month_start_equity: float,
    min_equity_so_far: float,
    breaker: float = config.MONTHLY_BREAKER,
) -> bool:
    if month_start_equity <= 0:
        raise ValueError("month_start_equity must be positive")
    drawdown = month_start_equity - min_equity_so_far
    return drawdown >= month_start_equity * breaker


def reached_breakeven_threshold(
    entry_price: float,
    stop_price: float,
    current_price: float,
) -> bool:
    initial_risk = entry_price - stop_price
    if initial_risk <= 0:
        return False
    return (current_price - entry_price) >= initial_risk


def should_time_stop(
    entry_date: date,
    as_of_date: date,
    reached_one_r: bool,
    limit_bars: int = config.TIME_STOP_BARS,
) -> bool:
    days_open = (as_of_date - entry_date).days
    return days_open >= limit_bars and not reached_one_r
