from __future__ import annotations

import pandas as pd

from spy_trader.risk import OpenRisk, monthly_breaker_tripped, sum_open_risk, would_exceed_heat_cap
from spy_trader.screens import Tide, screen_one_tide, screen_three_entry_plan, screen_two_wave
from spy_trader.sizing import compute_shares


def test_compute_shares_matches_strategy_example() -> None:
    assert compute_shares(50_000, 520.0, 514.5) == 181


def test_heat_cap_uses_open_risk_sum() -> None:
    positions = [OpenRisk("SPY", 520.0, 514.5, 100)]
    assert sum_open_risk(positions) == 550.0
    assert would_exceed_heat_cap(10_000, positions, 100.0) is True


def test_monthly_breaker_trip() -> None:
    assert monthly_breaker_tripped(50_000, 46_900) is True


def test_screen_one_detects_uptrend(bars: pd.DataFrame) -> None:
    weekly = bars.resample("W-FRI").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    )
    assert screen_one_tide(weekly) is Tide.UP


def test_screen_two_and_three_produce_candidate() -> None:
    frame = pd.DataFrame(
        {
            "open": [10, 11, 12, 11, 10, 11],
            "high": [11, 12, 13, 12, 11, 12],
            "low": [9, 10, 11, 10, 9, 10],
            "close": [10, 11, 12, 11, 10, 11.5],
            "volume": [1_000_000] * 6,
        }
    )
    wave = screen_two_wave(frame)
    assert isinstance(wave.eligible, bool)
    plan = screen_three_entry_plan("SPY", frame, equity=50_000, buying_power=50_000)
    assert plan.trigger_price > plan.stop_price
    assert plan.shares >= 0
