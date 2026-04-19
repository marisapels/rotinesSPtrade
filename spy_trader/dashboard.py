"""Static dashboard renderer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from spy_trader import config
from spy_trader.state import EngineState


def _environment() -> Environment:
    template_root = Path("dashboard_template")
    return Environment(
        loader=FileSystemLoader(template_root),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


def render_dashboard(
    state: EngineState,
    context: dict[str, Any] | None = None,
    dashboard_dir: Path = config.DASHBOARD_DIR,
) -> Path:
    env = _environment()
    template = env.get_template("index.html.j2")
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    rendered = template.render(state=state, context=context or {})
    output = dashboard_dir / "index.html"
    output.write_text(rendered)
    events_path = dashboard_dir / "events.jsonl"
    if not events_path.exists():
        events_path.write_text("")
    snapshot_path = dashboard_dir / "state.json"
    snapshot_path.write_text(
        json.dumps(state.__dict__, default=lambda value: value.__dict__, indent=2)
    )
    return output
