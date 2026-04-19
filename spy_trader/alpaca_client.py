"""Thin typed Alpaca wrapper."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, cast

import pandas as pd
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient

from spy_trader import config


@dataclass(frozen=True)
class AccountSnapshot:
    equity: float
    buying_power: float
    cash: float


@dataclass(frozen=True)
class PositionSnapshot:
    symbol: str
    qty: int
    avg_entry_price: float
    current_price: float


class AlpacaClient:
    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str = config.ALPACA_BASE_URL,
    ) -> None:
        self.api_key = api_key or os.environ.get("ALPACA_API_KEY", "")
        self.api_secret = api_secret or os.environ.get("ALPACA_API_SECRET", "")
        self.base_url = base_url
        self._trading = TradingClient(self.api_key, self.api_secret, paper="paper" in base_url)
        self._data = StockHistoricalDataClient(self.api_key, self.api_secret)

    def get_account(self) -> AccountSnapshot:
        account = cast(Any, self._trading.get_account())
        return AccountSnapshot(
            equity=float(account.equity),
            buying_power=float(account.buying_power),
            cash=float(account.cash),
        )

    def get_positions(self) -> list[PositionSnapshot]:
        positions = cast(list[Any], self._trading.get_all_positions())
        return [
            PositionSnapshot(
                symbol=position.symbol,
                qty=int(float(position.qty)),
                avg_entry_price=float(position.avg_entry_price),
                current_price=float(position.current_price),
            )
            for position in positions
        ]

    def get_daily_bars(self, symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start,
            end=end,
        )
        response = self._data.get_stock_bars(request)
        rows: list[dict[str, Any]] = []
        for bar in response[symbol]:
            rows.append(
                {
                    "timestamp": pd.Timestamp(bar.timestamp),
                    "open": float(bar.open),
                    "high": float(bar.high),
                    "low": float(bar.low),
                    "close": float(bar.close),
                    "volume": int(bar.volume),
                }
            )
        frame = pd.DataFrame(rows)
        if frame.empty:
            return frame
        return frame.set_index("timestamp").sort_index()
