"""SafeZone trailing distance."""

from __future__ import annotations

import pandas as pd


def compute_safezone_distance(
    bars: pd.DataFrame,
    lookback: int = 10,
    multiplier: float = 2.0,
) -> float:
    lows = bars["low"]
    penetrations = (lows.shift(1) - lows).clip(lower=0)
    recent = penetrations.iloc[-lookback:]
    if recent.empty:
        return 0.0
    non_zero = recent[recent > 0]
    if non_zero.empty:
        return 0.0
    return float(non_zero.mean() * multiplier)
