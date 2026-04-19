from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from spy_trader.indicators.ema import compute_ema


def test_ema_span_1_returns_input() -> None:
    series = pd.Series([10.0, 20.0, 30.0])
    pd.testing.assert_series_equal(compute_ema(series, 1), series)


def test_ema_span_2_known_values() -> None:
    series = pd.Series([10.0, 20.0, 30.0])
    out = compute_ema(series, 2)
    expected = pd.Series([10.0, 16.6667, 25.5556])
    pd.testing.assert_series_equal(out, expected, rtol=1e-3)


def test_ema_on_flat_series_is_flat() -> None:
    out = compute_ema(pd.Series([5.0] * 50), 10)
    assert np.allclose(out.values, 5.0)


def test_ema_preserves_index(bars: pd.DataFrame) -> None:
    out = compute_ema(bars["close"], 13)
    assert (out.index == bars.index).all()


def test_ema_rejects_non_positive_span() -> None:
    with pytest.raises(ValueError, match="span must be >= 1"):
        compute_ema(pd.Series([1.0, 2.0]), 0)
