"""Impulse System colors."""

from __future__ import annotations

from enum import Enum

import pandas as pd

from spy_trader.indicators.ema import compute_ema
from spy_trader.indicators.macd import compute_macd


class ImpulseColor(Enum):
    GREEN = "green"
    RED = "red"
    BLUE = "blue"


def compute_impulse_colors(close: pd.Series, ema_span: int = 13) -> pd.Series:
    ema = compute_ema(close, ema_span)
    histogram = compute_macd(close).histogram
    ema_slope = ema.diff()
    hist_slope = histogram.diff()

    colors: list[ImpulseColor] = []
    for ema_delta, hist_delta in zip(ema_slope, hist_slope, strict=True):
        if pd.isna(ema_delta) or pd.isna(hist_delta):
            colors.append(ImpulseColor.BLUE)
        elif ema_delta > 0 and hist_delta > 0:
            colors.append(ImpulseColor.GREEN)
        elif ema_delta < 0 and hist_delta < 0:
            colors.append(ImpulseColor.RED)
        else:
            colors.append(ImpulseColor.BLUE)
    return pd.Series(colors, index=close.index)
