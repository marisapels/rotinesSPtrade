"""Daily OHLCV cache and resampling helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from spy_trader import config
from spy_trader.alpaca_client import AlpacaClient


def cache_path(symbol: str, cache_dir: Path = config.CACHE_DIR) -> Path:
    return cache_dir / f"{symbol.lower()}_daily.parquet"


def load_cached_bars(symbol: str, cache_dir: Path = config.CACHE_DIR) -> pd.DataFrame:
    path = cache_path(symbol, cache_dir)
    if not path.exists():
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    return pd.read_parquet(path)


def save_cached_bars(symbol: str, bars: pd.DataFrame, cache_dir: Path = config.CACHE_DIR) -> Path:
    path = cache_path(symbol, cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    bars.sort_index().to_parquet(path)
    return path


def refresh_daily_cache(
    client: AlpacaClient,
    symbol: str,
    start: datetime,
    end: datetime,
    cache_dir: Path = config.CACHE_DIR,
) -> pd.DataFrame:
    cached = load_cached_bars(symbol, cache_dir)
    fresh = client.get_daily_bars(symbol, start, end)
    if cached.empty:
        merged = fresh
    else:
        merged = pd.concat([cached, fresh]).sort_index()
        merged = merged[~merged.index.duplicated(keep="last")]
    save_cached_bars(symbol, merged, cache_dir)
    return merged


def resample_weekly(daily_bars: pd.DataFrame) -> pd.DataFrame:
    return daily_bars.resample("W-FRI").agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
    ).dropna()
