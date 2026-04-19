"""Exponential Moving Average."""

from __future__ import annotations

import pandas as pd


def compute_ema(series: pd.Series, span: int) -> pd.Series:
    if span < 1:
        raise ValueError("span must be >= 1")
    return series.ewm(span=span, adjust=False).mean()
