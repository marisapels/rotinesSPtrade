from __future__ import annotations

import pandas as pd
import pytest

from spy_trader.indicators.stochastic import StochasticResult, compute_stochastic


def test_stochastic_returns_k_and_d_aligned(bars: pd.DataFrame) -> None:
    result = compute_stochastic(bars, k_period=5, k_smooth=3, d_period=3)
    assert isinstance(result, StochasticResult)
    assert (result.k.index == bars.index).all()
    assert (result.d.index == bars.index).all()


def test_stochastic_at_high_equals_100() -> None:
    frame = pd.DataFrame(
        {
            "high": [10, 10, 10, 10, 10, 12],
            "low": [9, 9, 9, 9, 9, 9],
            "close": [10, 10, 10, 10, 10, 12],
        }
    )
    result = compute_stochastic(frame, k_period=5, k_smooth=1, d_period=1)
    assert result.k.iloc[-1] == pytest.approx(100.0)


def test_stochastic_at_low_equals_zero() -> None:
    frame = pd.DataFrame(
        {
            "high": [12, 12, 12, 12, 12, 12],
            "low": [10, 10, 10, 10, 10, 8],
            "close": [11, 11, 11, 11, 11, 8],
        }
    )
    result = compute_stochastic(frame, k_period=5, k_smooth=1, d_period=1)
    assert result.k.iloc[-1] == pytest.approx(0.0)


def test_stochastic_k_bounded_0_to_100(bars: pd.DataFrame) -> None:
    result = compute_stochastic(bars, 5, 3, 3)
    bounded = result.k.dropna()
    assert (bounded >= 0).all()
    assert (bounded <= 100).all()
