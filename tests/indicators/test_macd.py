from __future__ import annotations

import numpy as np
import pandas as pd

from spy_trader.indicators.macd import MACDResult, compute_macd


def test_macd_returns_three_aligned_series(bars: pd.DataFrame) -> None:
    result = compute_macd(bars["close"], fast=12, slow=26, signal=9)
    assert isinstance(result, MACDResult)
    assert (result.macd_line.index == bars.index).all()
    assert (result.signal.index == bars.index).all()
    assert (result.histogram.index == bars.index).all()


def test_macd_histogram_equals_line_minus_signal(bars: pd.DataFrame) -> None:
    result = compute_macd(bars["close"], 12, 26, 9)
    pd.testing.assert_series_equal(
        result.histogram,
        result.macd_line - result.signal,
        check_names=False,
    )


def test_macd_on_rising_series_histogram_turns_positive_then_fades() -> None:
    series = pd.Series([100.0 + i for i in range(30)] + [130.0] * 120)
    result = compute_macd(series, 12, 26, 9)
    assert result.histogram.iloc[29] > 0
    assert abs(result.histogram.iloc[-1]) < abs(result.histogram.iloc[29])


def test_macd_on_flat_series_is_zero() -> None:
    result = compute_macd(pd.Series([50.0] * 100), 12, 26, 9)
    assert np.allclose(result.macd_line.values, 0.0, atol=1e-9)
    assert np.allclose(result.histogram.values, 0.0, atol=1e-9)
