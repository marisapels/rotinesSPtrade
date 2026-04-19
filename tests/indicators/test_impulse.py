from __future__ import annotations

import pandas as pd

from spy_trader.indicators.impulse import ImpulseColor, compute_impulse_colors


def test_rising_ema_and_rising_hist_is_green() -> None:
    colors = compute_impulse_colors(pd.Series([100.0 + (i**1.2) * 0.3 for i in range(60)]))
    assert ImpulseColor.GREEN in set(colors.tolist())


def test_falling_ema_and_falling_hist_is_red() -> None:
    colors = compute_impulse_colors(pd.Series([200.0 - (i**1.2) * 0.3 for i in range(60)]))
    assert ImpulseColor.RED in set(colors.tolist())


def test_mixed_signals_are_blue() -> None:
    series = pd.Series([100.0 + i for i in range(40)] + [140.0 - i * 2 for i in range(20)])
    colors = compute_impulse_colors(series)
    assert ImpulseColor.BLUE in set(colors.iloc[40:55].tolist())


def test_returns_series_same_length_as_input(bars: pd.DataFrame) -> None:
    colors = compute_impulse_colors(bars["close"])
    assert len(colors) == len(bars)
    assert (colors.index == bars.index).all()
