"""Stochastic oscillator."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class StochasticResult:
    k: pd.Series
    d: pd.Series


def compute_stochastic(
    bars: pd.DataFrame,
    k_period: int = 5,
    k_smooth: int = 3,
    d_period: int = 3,
) -> StochasticResult:
    high = bars["high"]
    low = bars["low"]
    close = bars["close"]
    hh = high.rolling(k_period, min_periods=1).max()
    ll = low.rolling(k_period, min_periods=1).min()
    denom = (hh - ll).replace(0, pd.NA)
    k_raw = 100 * (close - ll) / denom
    k_raw = k_raw.fillna(50.0)
    k = k_raw.rolling(k_smooth, min_periods=1).mean()
    d = k.rolling(d_period, min_periods=1).mean()
    return StochasticResult(k=k, d=d)
