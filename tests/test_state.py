from __future__ import annotations

from pathlib import Path

from spy_trader.state import EngineState, StateStore


def test_state_store_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    store = StateStore(path)
    state = EngineState(trading_disabled=True)
    store.save(state)
    loaded = store.load()
    assert loaded.trading_disabled is True
