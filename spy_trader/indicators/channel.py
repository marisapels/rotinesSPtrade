"""Elder channel helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from spy_trader.indicators.ema import compute_ema


@dataclass(frozen=True)
class ChannelResult:
    mid: pd.Series
    upper: pd.Series
    lower: pd.Series


def compute_channel(
    close: pd.Series,
    ema_span: int = 22,
    width_pct: float = 0.027,
) -> ChannelResult:
    mid = compute_ema(close, ema_span)
    upper = mid * (1 + width_pct)
    lower = mid * (1 - width_pct)
    return ChannelResult(mid=mid, upper=upper, lower=lower)


def fit_width_pct(
    close: pd.Series,
    ema_span: int = 22,
    lookback: int = 100,
    coverage: float = 0.95,
) -> float:
    window = close.iloc[-lookback:]
    mid = compute_ema(close, ema_span).iloc[-lookback:]
    rel = np.abs((window - mid) / mid)
    return float(rel.quantile(coverage))
