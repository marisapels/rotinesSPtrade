from __future__ import annotations

import pandas as pd

from spy_trader.indicators.channel import ChannelResult, compute_channel, fit_width_pct


def test_channel_shape(bars: pd.DataFrame) -> None:
    result = compute_channel(bars["close"], ema_span=22, width_pct=0.027)
    assert isinstance(result, ChannelResult)
    assert len(result.mid) == len(result.upper) == len(result.lower) == len(bars)


def test_upper_lower_are_symmetric_around_mid() -> None:
    result = compute_channel(pd.Series([100.0] * 60), ema_span=22, width_pct=0.05)
    assert (result.upper == 105.0).all()
    assert (result.lower == 95.0).all()


def test_fit_width_roughly_envelopes_95_pct_of_bars() -> None:
    import numpy as np

    rng = np.random.default_rng(42)
    series = pd.Series(100 + rng.normal(0, 1.5, 200).cumsum() * 0.1)
    width = fit_width_pct(series, ema_span=22, lookback=100, coverage=0.95)
    result = compute_channel(series, ema_span=22, width_pct=width)
    last100 = series.iloc[-100:]
    inside = (
        (last100 >= result.lower.iloc[-100:]) & (last100 <= result.upper.iloc[-100:])
    ).sum()
    assert inside >= 95
