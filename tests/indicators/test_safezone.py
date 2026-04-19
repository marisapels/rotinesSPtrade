from __future__ import annotations

import pandas as pd
import pytest

from spy_trader.indicators.safezone import compute_safezone_distance


def test_no_downside_penetrations_returns_zero() -> None:
    frame = pd.DataFrame({"low": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]})
    assert compute_safezone_distance(frame, lookback=10, multiplier=2.0) == 0.0


def test_average_penetration_times_multiplier() -> None:
    frame = pd.DataFrame({"low": [10, 9, 10, 8, 9, 7, 8, 6, 7, 5, 6]})
    assert compute_safezone_distance(frame, lookback=10, multiplier=2.0) == pytest.approx(3.6)
