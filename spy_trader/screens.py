"""Triple Screen decision logic."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import pandas as pd

from spy_trader import config
from spy_trader.indicators.force_index import compute_force_index
from spy_trader.indicators.impulse import ImpulseColor, compute_impulse_colors
from spy_trader.indicators.macd import compute_macd
from spy_trader.indicators.safezone import compute_safezone_distance
from spy_trader.indicators.stochastic import compute_stochastic
from spy_trader.sizing import compute_shares


class Tide(Enum):
    UP = "up"
    DOWN = "down"
    FLAT = "flat"


@dataclass(frozen=True)
class WaveSignal:
    eligible: bool
    force_index: float
    stochastic_k: float
    impulse: ImpulseColor
    reason: str


@dataclass(frozen=True)
class EntryPlan:
    symbol: str
    trigger_price: float
    stop_price: float
    shares: int
    risk_per_share: float
    initial_risk_dollars: float


def screen_one_tide(weekly_bars: pd.DataFrame) -> Tide:
    close = weekly_bars["close"]
    ema = close.ewm(span=config.EMA_WEEKLY, adjust=False).mean()
    histogram = compute_macd(
        close,
        fast=config.MACD[0],
        slow=config.MACD[1],
        signal=config.MACD[2],
    ).histogram
    ema_slope = ema.diff().iloc[-1]
    hist_slope = histogram.diff().iloc[-1]
    if ema_slope > 0 and hist_slope > 0:
        return Tide.UP
    if ema_slope < 0 and hist_slope < 0:
        return Tide.DOWN
    return Tide.FLAT


def screen_two_wave(daily_bars: pd.DataFrame) -> WaveSignal:
    force_index = compute_force_index(daily_bars, span=config.FORCE_INDEX_EMA)
    stochastic = compute_stochastic(daily_bars, *config.STOCHASTIC)
    impulse = compute_impulse_colors(daily_bars["close"], ema_span=config.EMA_IMPULSE)
    force_value = float(force_index.iloc[-1])
    stochastic_k = float(stochastic.k.iloc[-1])
    impulse_color = impulse.iloc[-1]
    pullback = force_value < 0 or stochastic_k < 30
    if not pullback:
        return WaveSignal(False, force_value, stochastic_k, impulse_color, "no_pullback")
    if impulse_color is ImpulseColor.RED:
        return WaveSignal(False, force_value, stochastic_k, impulse_color, "impulse_red")
    return WaveSignal(True, force_value, stochastic_k, impulse_color, "candidate")


def initial_stop_from_bars(daily_bars: pd.DataFrame) -> float:
    last_two_low = float(daily_bars["low"].iloc[-2:].min())
    swing_low = float(daily_bars["low"].iloc[-5:].min())
    return min(last_two_low, swing_low) - 0.01


def screen_three_entry_plan(
    symbol: str,
    daily_bars: pd.DataFrame,
    equity: float,
    buying_power: float,
) -> EntryPlan:
    trigger_price = float(daily_bars["high"].iloc[-1] + 0.01)
    stop_price = initial_stop_from_bars(daily_bars)
    shares = compute_shares(equity, trigger_price, stop_price, buying_power=buying_power)
    risk_per_share = trigger_price - stop_price
    return EntryPlan(
        symbol=symbol,
        trigger_price=trigger_price,
        stop_price=stop_price,
        shares=shares,
        risk_per_share=risk_per_share,
        initial_risk_dollars=shares * risk_per_share,
    )


def next_trailing_stop(daily_bars: pd.DataFrame) -> float:
    safezone = compute_safezone_distance(
        daily_bars,
        lookback=config.SAFEZONE_LOOKBACK,
        multiplier=config.SAFEZONE_MULT,
    )
    return float(daily_bars["low"].iloc[-1] - safezone)
