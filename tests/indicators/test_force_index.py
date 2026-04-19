from __future__ import annotations

import pandas as pd

from spy_trader.indicators.force_index import compute_force_index


def test_raw_fi_is_delta_close_times_volume() -> None:
    frame = pd.DataFrame(
        {"close": [100.0, 101.0, 99.0], "volume": [1_000_000, 2_000_000, 1_500_000]}
    )
    series = compute_force_index(frame, span=1)
    assert pd.isna(series.iloc[0])
    assert series.iloc[1] == 2_000_000
    assert series.iloc[2] == -3_000_000


def test_fi_crosses_zero_on_trend_flip() -> None:
    closes = list(range(100, 110)) + list(range(110, 100, -1))
    frame = pd.DataFrame({"close": closes, "volume": [1_000_000] * 20})
    series = compute_force_index(frame, span=2)
    assert series.iloc[9] > 0
    assert series.iloc[-1] < 0


def test_fi_aligns_with_input_index(bars: pd.DataFrame) -> None:
    series = compute_force_index(bars, span=2)
    assert (series.index == bars.index).all()
