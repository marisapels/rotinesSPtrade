"""MACD + signal + histogram."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from spy_trader.indicators.ema import compute_ema


@dataclass(frozen=True)
class MACDResult:
    macd_line: pd.Series
    signal: pd.Series
    histogram: pd.Series


def compute_macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> MACDResult:
    fast_ema = compute_ema(close, fast)
    slow_ema = compute_ema(close, slow)
    macd_line = fast_ema - slow_ema
    signal_line = compute_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return MACDResult(macd_line=macd_line, signal=signal_line, histogram=histogram)
