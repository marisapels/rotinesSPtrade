"""Central configuration. All numeric defaults come from STRATEGY.md §10.2.

Environment variables (optional overrides): RISK_FRACTION.
Secrets (required for Alpaca / Telegram / Anthropic calls) are read from env
by the respective client modules — this file only holds numeric constants.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _float_env(name: str, default: float) -> float:
    raw = os.environ.get(name)
    return float(raw) if raw is not None else default


# --- STRATEGY.md §5 money management -----------------------------------------
RISK_FRACTION: float = _float_env("RISK_FRACTION", 0.02)  # §5.1
HEAT_CAP: float = 0.06  # §5.2
MONTHLY_BREAKER: float = 0.06  # §5.3

# --- STRATEGY.md §3 / §4 timings ---------------------------------------------
BUY_STOP_EXPIRY_DAYS: int = 3  # §3.3
TIME_STOP_BARS: int = 10  # §4.4
CHANNEL_WIDTH_PCT: float = 0.027  # §4.2
SAFEZONE_LOOKBACK: int = 10  # §4.3
SAFEZONE_MULT: float = 2.0  # §4.3

# --- STRATEGY.md §10.2 indicator parameters ---------------------------------
EMA_WEEKLY: int = 26
EMA_IMPULSE: int = 13
EMA_CHANNEL: int = 22
STOCHASTIC: tuple[int, int, int] = (5, 3, 3)
MACD: tuple[int, int, int] = (12, 26, 9)
FORCE_INDEX_EMA: int = 2

# --- Paths (dev defaults; prod overridden via env on VPS) -------------------
STATE_DIR: Path = Path(os.environ.get("STATE_DIR", "./state"))
CACHE_DIR: Path = Path(os.environ.get("CACHE_DIR", "./state/cache"))
JOURNAL_DIR: Path = Path(os.environ.get("JOURNAL_DIR", "./journal"))
DASHBOARD_DIR: Path = Path(os.environ.get("DASHBOARD_DIR", "./var/www/trader"))

# --- Alpaca -----------------------------------------------------------------
ALPACA_BASE_URL: str = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# --- Telegram ---------------------------------------------------------------
TELEGRAM_API_BASE: str = "https://api.telegram.org"

# --- Claude -----------------------------------------------------------------
CLAUDE_MODEL_SONNET: str = "claude-sonnet-4-6"
CLAUDE_MODEL_OPUS: str = "claude-opus-4-7"
