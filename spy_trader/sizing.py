"""Position sizing helpers."""

from __future__ import annotations

import math

from spy_trader import config


def compute_shares(
    equity: float,
    entry_price: float,
    stop_price: float,
    *,
    buying_power: float | None = None,
    risk_fraction: float = config.RISK_FRACTION,
) -> int:
    risk_per_share = entry_price - stop_price
    if equity <= 0:
        raise ValueError("equity must be positive")
    if risk_per_share <= 0:
        raise ValueError("entry_price must be above stop_price")
    shares = math.floor((equity * risk_fraction) / risk_per_share)
    if buying_power is not None and entry_price > 0:
        shares = min(shares, math.floor(buying_power / entry_price))
    return max(0, shares)
