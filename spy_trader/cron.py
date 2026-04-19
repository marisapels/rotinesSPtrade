"""Routine dispatcher."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, timedelta

from spy_trader import config
from spy_trader.aar import write_daily_aar
from spy_trader.alpaca_client import AlpacaClient
from spy_trader.calendar_feed import load_calendar_events
from spy_trader.claude_review import ClaudeReviewer
from spy_trader.dashboard import render_dashboard
from spy_trader.data import load_cached_bars, refresh_daily_cache, resample_weekly
from spy_trader.events import EventBus, JsonlEventSink
from spy_trader.fill_watcher import run_fill_watcher
from spy_trader.journal import append_trade_entry, write_pre_market_note
from spy_trader.orders import manage_position, plan_pending_order
from spy_trader.risk import OpenRisk, monthly_breaker_tripped, sum_open_risk, would_exceed_heat_cap
from spy_trader.screens import Tide, screen_one_tide, screen_three_entry_plan, screen_two_wave
from spy_trader.state import EngineState, StateStore, month_state_for_equity


def _store() -> StateStore:
    return StateStore(config.STATE_DIR / "state.json")


def _event_bus() -> EventBus:
    return EventBus([JsonlEventSink(config.DASHBOARD_DIR / "events.jsonl")])


def run_pre_market(today: date | None = None) -> EngineState:
    day = today or date.today()
    store = _store()
    state = store.load()
    bus = _event_bus()
    bus.emit("session_started", "Pre-market started", routine="pre_market")
    client = AlpacaClient()
    account = client.get_account()
    if state.month is None or not state.month.month_start.startswith(day.strftime("%Y-%m")):
        state.month = month_state_for_equity(day, account.equity)
    start = datetime.combine(day - timedelta(days=180), datetime.min.time())
    end = datetime.combine(day, datetime.min.time())
    spy = refresh_daily_cache(client, "SPY", start, end)
    sh = refresh_daily_cache(client, "SH", start, end)
    weekly = resample_weekly(spy)
    state.tide = screen_one_tide(weekly).value if not weekly.empty else Tide.FLAT.value
    open_risk_positions = [
        OpenRisk(position.symbol, position.entry_price, position.stop_price, position.shares)
        for position in state.positions
    ]
    summary: dict[str, object] = {
        "tide": state.tide,
        "calendar_events": [asdict(item) for item in load_calendar_events(day)],
        "heat": sum_open_risk(open_risk_positions),
    }
    if state.tide != Tide.FLAT.value and not state.trading_disabled:
        symbol = "SPY" if state.tide == Tide.UP.value else "SH"
        bars = spy if symbol == "SPY" else sh
        if not bars.empty:
            wave = screen_two_wave(bars)
            summary["wave_reason"] = wave.reason
            if wave.eligible and state.month is not None:
                plan = screen_three_entry_plan(symbol, bars, account.equity, account.buying_power)
                blocked = monthly_breaker_tripped(
                    state.month.month_start_equity,
                    state.month.min_equity_so_far,
                ) or would_exceed_heat_cap(
                    account.equity,
                    open_risk_positions,
                    plan.initial_risk_dollars,
                )
                if not blocked and plan.shares > 0:
                    state.pending_orders = [plan_pending_order(plan, day)]
                    bus.emit(
                        "buy_stop_placed",
                        f"Placed buy stop for {symbol}",
                        symbol=symbol,
                        trigger_price=plan.trigger_price,
                        shares=plan.shares,
                    )
                    summary["planned_order"] = asdict(plan)
    note_path = write_pre_market_note(day, summary)
    verdict = ClaudeReviewer().review_pre_market(summary)
    summary["claude_verdict"] = verdict.verdict
    summary["claude_reason"] = verdict.reason
    render_dashboard(state, {"summary": f"Pre-market note: {note_path}"})
    store.save(state)
    bus.emit("session_ended", "Pre-market completed", summary=summary)
    return state


def run_post_close(today: date | None = None) -> EngineState:
    day = today or date.today()
    store = _store()
    state = store.load()
    bus = _event_bus()
    client = AlpacaClient()
    account = client.get_account()
    if state.month is None:
        state.month = month_state_for_equity(day, account.equity)
    state.month.min_equity_so_far = min(state.month.min_equity_so_far, account.equity)
    state.month.breaker_tripped = monthly_breaker_tripped(
        state.month.month_start_equity,
        state.month.min_equity_so_far,
    )
    spy = load_cached_bars("SPY")
    sh = load_cached_bars("SH")
    managed: list[dict[str, object]] = []
    for position in state.positions:
        bars = spy if position.symbol == "SPY" else sh
        if bars.empty:
            continue
        update = manage_position(position, bars, day, Tide(state.tide))
        position.stop_price = update.stop_price
        position.target_price = update.target_price
        position.close_at_next_open = update.close_at_next_open
        managed.append(asdict(update))
        append_trade_entry(day, {"symbol": position.symbol, "stop": position.stop_price})
    write_daily_aar(day, f"Managed positions: {managed}")
    render_dashboard(state, {"summary": "Post-close reconciliation complete"})
    store.save(state)
    bus.emit("session_ended", "Post-close completed", managed=managed)
    return state


def run_weekly(today: date | None = None) -> EngineState:
    store = _store()
    state = store.load()
    spy = load_cached_bars("SPY")
    weekly = resample_weekly(spy) if not spy.empty else spy
    if not weekly.empty:
        state.tide = screen_one_tide(weekly).value
    render_dashboard(state, {"summary": "Weekly tide refresh complete"})
    store.save(state)
    return state


def run_monthly(today: date | None = None) -> EngineState:
    day = today or date.today()
    store = _store()
    state = store.load()
    client = AlpacaClient()
    account = client.get_account()
    state.month = month_state_for_equity(day, account.equity)
    render_dashboard(state, {"summary": "Monthly snapshot refreshed"})
    store.save(state)
    return state


def run_fill_watcher_routine() -> None:
    run_fill_watcher(_event_bus())


def dispatch(routine: str) -> EngineState | None:
    match routine:
        case "pre-market":
            return run_pre_market()
        case "post-close":
            return run_post_close()
        case "weekly":
            return run_weekly()
        case "monthly":
            return run_monthly()
        case "fill-watcher":
            run_fill_watcher_routine()
            return None
        case _:
            raise ValueError(f"Unknown routine: {routine}")
