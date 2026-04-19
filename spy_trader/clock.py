"""Timezone and trading-calendar helpers."""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import pandas_market_calendars as mcal

ET = ZoneInfo("America/New_York")


def now_et() -> datetime:
    return datetime.now(tz=ET)


def trading_schedule(start: date, end: date) -> pd.DataFrame:
    calendar = mcal.get_calendar("XNYS")
    return calendar.schedule(start_date=start, end_date=end)


def is_trading_day(day: date) -> bool:
    schedule = trading_schedule(day, day)
    return not schedule.empty


def trading_days_between(start: date, end: date) -> list[date]:
    schedule = trading_schedule(start, end)
    return [index.date() for index in schedule.index]


def add_trading_days(day: date, offset: int) -> date:
    if offset == 0:
        return day
    padding = max(abs(offset) * 3, 10)
    if offset > 0:
        days = trading_days_between(day, day + pd.Timedelta(days=padding))
        filtered = [current for current in days if current > day]
        return filtered[offset - 1]
    days = trading_days_between(day - pd.Timedelta(days=padding), day)
    filtered = [current for current in days if current < day]
    return filtered[offset]
