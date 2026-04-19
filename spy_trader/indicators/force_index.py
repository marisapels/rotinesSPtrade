"""Force Index, optionally EMA-smoothed."""

from __future__ import annotations

import pandas as pd

from spy_trader.indicators.ema import compute_ema


def compute_force_index(bars: pd.DataFrame, span: int = 2) -> pd.Series:
    raw = bars["close"].diff() * bars["volume"]
    if span == 1:
        return raw
    smoothed = compute_ema(raw.fillna(0.0), span)
    smoothed.iloc[0] = pd.NA
    return smoothed
