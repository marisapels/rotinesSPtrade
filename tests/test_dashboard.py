from __future__ import annotations

from pathlib import Path

from spy_trader.dashboard import render_dashboard
from spy_trader.state import EngineState


def test_dashboard_renders_html(tmp_path: Path) -> None:
    output = render_dashboard(EngineState(), {"summary": "ok"}, dashboard_dir=tmp_path)
    assert output.exists()
    assert "ok" in output.read_text()
