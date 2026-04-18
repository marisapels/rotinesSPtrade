# SPY/SH Paper-Trading Agent — Design Spec

**Date:** 2026-04-18
**Author:** Claude (brainstormed with Maris)
**Status:** Approved design, pending implementation plan
**Source of rules:** `STRATEGY.md` at repo root (Elder Triple Screen, §8.7 regression gate applies to every change)

---

## 1. Purpose

Build an autonomous, scheduled agent that trades the S&P 500 on **Alpaca paper** using SPY for long exposure and SH for short exposure, exactly per the rules in `STRATEGY.md`. The agent must:

- Execute the Triple Screen mechanically — no model inference on the math.
- Run unattended on a fixed cron (pre-market, post-close, weekly Fri close, monthly 1st).
- Produce a complete audit trail in git (state + journal + AAR).
- Notify the user in Telegram at every lifecycle event.
- Expose a static-HTML dashboard (GitHub Pages) refreshed on every run.
- Provide well-defined Claude seams for narrative, review, and strategy-update PRs, but never let Claude write orders or move stops.
- Flip to **live** capital by changing `ALPACA_BASE_URL` and halving the risk constant — no code rewrite.

## 2. Non-goals (this spec)

- **Full backtest & walk-forward engine** (STRATEGY.md §8.1–§8.5). A stubbed interface is included so the §8.7 gate exists; the real engine is a follow-up spec.
- **Live-capital switch.** Documented procedure only; no live trading is enabled by this spec.
- **Multi-account, multi-strategy, multi-instrument generalization.** One account, SPY + SH, one Elder method.
- **Sub-minute streaming dashboard.** 15-min fill-watcher polling is the live granularity. A future spec can add a websocket consumer if needed.

## 3. Decisions (from brainstorming)

| Decision | Choice | Reason |
|---|---|---|
| Scope stage | Paper-trading agent; backtest deferred | User intends to paper-first, flip to live later |
| Autonomy | **Full auto** on paper | Paper is the test of unattended operation |
| Claude's role | **Operator / reviewer / strategy-updater** | Rules mechanical in code; Claude adds judgement at defined seams |
| Runtime | **GitHub Actions cron** | Reliable, laptop-independent, free, git-native audit |
| Language | **Python 3.11** | Industry default for quant; `alpaca-py`, `pandas` |
| Dashboard | **Static HTML → GitHub Pages**, regenerated per run | Zero infra, bookmarkable, matches run cadence |
| Notifications | **Telegram Bot API** from every lifecycle event | Push to phone, no infra |
| Live-data granularity between scheduled runs | **15-min fill-watcher** poller (09:30–16:00 ET, M–F) | Good enough for swing system; no VPS required |

## 4. Architecture

A single Python package `spy_trader/` implements the engine as a collection of small, pure, independently testable modules. Scheduled runs are CLI invocations (`python -m spy_trader.cron <routine>`) triggered by GitHub Actions cron workflows. The engine reads state from JSON files, talks to Alpaca via a thin typed wrapper, writes journal entries and AARs as markdown, emits Telegram events, regenerates the static dashboard, and commits everything to git.

Claude is invoked via the Anthropic Python SDK at four defined seams (pre-market review, daily AAR, weekly rollup, monthly review + strategy-update PR) and **never** at any seam that touches orders, stops, state transitions, or risk math.

```
  ┌──────────────────┐   ┌────────────────────┐
  │ GitHub Actions   │──▶│ spy_trader.cron     │
  │ cron workflows   │   │ routine dispatcher  │
  └──────────────────┘   └──────────┬──────────┘
                                    │
        ┌──────────┬───────────────┼────────────┬─────────────┐
        ▼          ▼               ▼            ▼             ▼
     data/      indicators/     screens/    orders/       state/
     cache      (pure fns)      (pure fns)  (business)    (JSON)
        │          │               │            │             │
        └──────────┴───────┬───────┴────────────┘             │
                           ▼                                   │
                    ┌─────────────┐       ┌──────────────────┐ │
                    │ alpaca_client│◀────▶│ Alpaca Paper API  │ │
                    └─────────────┘       └──────────────────┘ │
                                                               │
  ┌──────────┐   ┌───────────┐   ┌─────────────┐  ┌──────────┐ │
  │ journal/ │   │ notifier/ │   │ dashboard/  │  │ claude_  │ │
  │ (md)     │   │ (Telegram)│   │ docs/site/  │  │ review/  │ │
  └────┬─────┘   └─────┬─────┘   └──────┬──────┘  └────┬─────┘ │
       └───────────────┴────────────────┴──────────────┴───────┘
                           ▼
                   git commit & push (audit trail)
```

## 5. Repository layout

```
/
├── STRATEGY.md                        # Rules of record. §8.7 regression gate.
├── README.md                          # Operating manual.
├── pyproject.toml
├── requirements.txt
├── .env.example                       # ALPACA_*, ANTHROPIC_API_KEY, TELEGRAM_*
├── .github/
│   └── workflows/
│       ├── pre_market.yml             # Mon–Fri 09:15 ET
│       ├── post_close.yml             # Mon–Fri 16:15 ET
│       ├── weekly.yml                 # Fri 16:30 ET
│       ├── monthly.yml                # 1st of month 09:00 ET
│       ├── fill_watcher.yml           # Every 15 min, 09:30–16:00 ET, M–F
│       ├── pages.yml                  # Publish docs/site/ to GitHub Pages
│       └── ci.yml                     # Unit + integration tests on PR
│
├── spy_trader/
│   ├── __init__.py
│   ├── cli.py                         # argparse entry point
│   ├── cron.py                        # routine dispatcher
│   ├── config.py                      # env + constants (RISK_FRACTION, etc.)
│   ├── clock.py                       # ET-aware helpers, trading calendar
│   ├── alpaca_client.py               # account, positions, orders, bars — typed
│   ├── data.py                        # daily OHLCV fetch + parquet cache, weekly resample
│   ├── calendar_feed.py               # FOMC / CPI / NFP lookup for §9 item 8
│   ├── indicators/
│   │   ├── __init__.py
│   │   ├── ema.py                     # EMA (standard) — pure
│   │   ├── macd.py                    # MACD + histogram — pure
│   │   ├── stochastic.py              # %K/%D (5,3,3) — pure
│   │   ├── force_index.py             # FI EMA(2) — pure
│   │   ├── impulse.py                 # color from 13-EMA + MACD-hist slopes — pure
│   │   ├── channel.py                 # 22-EMA ± envelope — pure
│   │   └── safezone.py                # trailing-stop distance — pure
│   ├── screens.py                     # screen_one, screen_two, screen_three — pure
│   ├── sizing.py                      # compute_shares(equity, entry, stop) — pure
│   ├── risk.py                        # heat cap, monthly circuit breaker, time stop
│   ├── orders.py                      # plan & execute: buy-stops, stops, targets, trails
│   ├── state.py                       # JSON-backed state; schema-versioned
│   ├── journal.py                     # §6 markdown trade entries
│   ├── aar.py                         # AAR scaffold (claude fills narrative)
│   ├── claude_review.py               # Anthropic SDK calls at 4 seams
│   ├── notifier.py                    # Telegram Bot API wrapper
│   ├── events.py                      # Event dataclasses + dispatcher
│   ├── dashboard.py                   # Render docs/site/index.html
│   └── fill_watcher.py                # Intraday poller
│
├── tests/
│   ├── fixtures/
│   │   ├── spy_daily.parquet          # small SPY slice
│   │   ├── sh_daily.parquet
│   │   └── alpaca_responses/          # recorded JSON for replay
│   ├── indicators/                    # golden-file tests vs Elder examples
│   ├── screens/                       # hand-crafted bar sequences
│   ├── sizing/                        # §5.1 example assertions
│   ├── risk/                          # heat cap, drawdown transitions
│   ├── orders/                        # plan-generation tests
│   ├── state/                         # schema round-trip, migration
│   ├── notifier/                      # Telegram payload shape, mocked HTTP
│   └── integration/                   # full pre-market + post-close replay
│
├── state/
│   ├── state.json                     # positions, candidates, trading_disabled, schema_version
│   ├── month.json                     # month_start_equity, MTD drawdown
│   └── cache/
│       ├── spy_daily.parquet
│       └── sh_daily.parquet
│
├── journal/
│   ├── YYYY/MM/
│   │   ├── trades.md                  # §6 entries
│   │   ├── aar/
│   │   │   ├── YYYY-MM-DD.md          # daily AAR (§7)
│   │   │   ├── week-YYYY-MM-DD.md     # weekly rollup
│   │   │   └── month-YYYY-MM.md       # monthly review
│   │   └── pre_market/
│   │       └── YYYY-MM-DD.md          # §9 checklist snapshot + Claude verdict
│   └── incidents/
│       └── YYYY-MM-DD-<slug>.md
│
├── docs/
│   ├── superpowers/specs/
│   │   └── 2026-04-18-paper-trading-agent-design.md   # this file
│   └── site/                          # GitHub Pages root
│       ├── index.html                 # regenerated per run
│       ├── events.jsonl               # audit feed for dashboard + Telegram mirror
│       └── assets/style.css
```

## 6. Runtime flows

### 6.1 Pre-market (Mon–Fri 09:15 ET)

1. **Boot.** Emit `session_started{routine=pre_market}`. Load state.
2. **Data refresh.** Fetch daily bars for SPY and SH up to yesterday's close; merge into parquet cache.
3. **Screen One — Tide.** Read current Tide from state (refreshed Fridays). If **FLAT**, skip to step 8.
4. **Screen Two — Wave.** For the permitted instrument only (SPY if UP, SH if DOWN), on daily bars: check FI(2) < 0 OR Stoch %K < 30 AND impulse bar not red. Any instrument failing any rule emits `candidate_skipped{reason}` and continues.
5. **Screen Three — Entry plan.** For each surviving candidate, compute prior-day high + 1 tick; compute initial stop (§4.1); compute shares via `sizing.compute_shares` (§5.1). Reject if the stop is $0 or buying power insufficient.
6. **Heat check (§5.2).** If this new risk would push total open risk > 6% of equity, emit `heat_cap_blocked` and drop.
7. **Circuit breaker (§5.3).** If MTD drawdown ≥ 6%, emit `circuit_breaker_tripped` if not already; skip all new-entry logic this month.
8. **Stop verification.** For every open position, confirm the Alpaca stop order exists, symbol matches, stop price matches state. Mismatch → incident.
9. **Order actions.** For each survivor, place or roll a buy-stop order at the computed trigger, 3-day expiry; emit `buy_stop_placed` / `buy_stop_rolled`.
10. **Expire stale.** Cancel any buy-stop > 3 trading days old; emit `buy_stop_expired`.
11. **Pre-market note.** Write `journal/YYYY/MM/pre_market/YYYY-MM-DD.md` with the §9 checklist outcome, candidates, planned orders, heat, MTD drawdown, and econ-calendar hits.
12. **Claude review (seam #1).** Pass the pre-market note + econ-calendar JSON (from `calendar_feed.py`) + STRATEGY.md (cached prompt). Claude returns `{verdict: "go"|"veto-new-entries"|"halt", reason}`. If `veto-new-entries`, cancel any newly-placed buy-stops from step 9 and emit `candidate_skipped{reason=claude_veto}` for each. If `halt`, additionally set `trading_disabled=true`.
13. **Dashboard.** Regenerate `docs/site/index.html`.
14. **Close.** Emit `claude_review` and `session_ended` with one-line summary + dashboard link.
15. **Git.** Commit all state/journal/dashboard changes with message `pre-market YYYY-MM-DD`; push.

### 6.2 Post-close (Mon–Fri 16:15 ET)

1. Emit `session_started{routine=post_close}`. Load state.
2. **Fetch today's daily bar** for SPY and SH; append to cache.
3. **Fill reconciliation.** For every order filled today not yet recorded:
   - New entry: emit `trade_filled`, open a §6 journal entry, place initial stop (§4.1), record entry price, risk/share, shares.
   - Stop hit / target hit: emit corresponding event, close journal entry with exit reason + realized R, cancel any pending sibling orders.
4. **Position management loop.** For each open position:
   - If unrealized P&L ≥ 1R and stop still at initial → move to breakeven (§4.3 step 1); emit `stop_moved_to_breakeven`.
   - Compute SafeZone distance (§4.3 step 2), new trail = `today_low − SafeZone`; only ratchet up. Emit `trailing_stop_updated` on change.
   - Channel target (§4.2): if set, refresh as a limit sell at upper envelope.
   - Time stop (§4.4): if entered ≥ 10 trading days ago and never reached 1R, mark `close_at_next_open=true`; emit `time_stop_exit` tomorrow.
   - Tide-flip exit (§4.5): if the position's direction is now against the Tide, emit `tide_flipped_against_position` and schedule a clean exit next session.
5. **Equity & drawdown.** Read Alpaca account equity; update `month.json`. If MTD drawdown ≥ 6% and not already tripped, emit `circuit_breaker_tripped`.
6. **Open-risk summary.** Sum `(entry − stop) × shares` across positions; emit in `reconciliation`.
7. **Claude AAR (seam #2).** Call Claude with the day's events, trade log, state diff, rule-break candidates. Claude writes `journal/.../aar/YYYY-MM-DD.md` per §7 template and produces a structured `rule_breaks` array; any non-empty array emits `incident` events.
8. **Dashboard** regenerated. **Git** commit + push.
9. Emit `session_ended`.

### 6.3 Weekly (Fri 16:30 ET)

1. Emit `session_started{routine=weekly}`.
2. Resample daily → weekly for SPY; compute 26-EMA slope + weekly MACD histogram slope.
3. Derive Tide: UP / DOWN / FLAT per §3.1.
4. If Tide changed, emit `tide_verdict{previous, new}`.
5. Persist to state; dashboard + git.
6. **Claude weekly rollup (seam #3).** Reads the five daily AARs; writes `week-YYYY-MM-DD.md` (one-paragraph per §7).
7. Emit `session_ended`.

### 6.4 Monthly (1st of month 09:00 ET)

1. Emit `session_started{routine=monthly}`.
2. Tally last month: realized R sum, win rate, avg winner R, avg loser R, max daily drawdown, circuit-breaker fires.
3. Write `month-YYYY-MM.json` (structured metrics) and snapshot.
4. Reset `month_start_equity` to current equity.
5. **Claude monthly review (seam #4).** Reads metrics + STRATEGY.md. Writes `month-YYYY-MM.md` comparing vs §8.5 thresholds. If Claude proposes a STRATEGY.md change, it opens a git branch `strategy-update/YYYY-MM-<slug>`, commits the diff, opens a PR with body citing §8.7, and labels it `regression-required`. CI blocks merge until a `backtest_gate.json` updated-at date is newer than the PR base commit (stub enforced now; real backtest fills it later).
6. Dashboard + git + `session_ended`.

### 6.5 Fill-watcher (every 15 min, 09:30–16:00 ET, M–F)

1. Light routine: fetch `orders since last_seen_id` from Alpaca.
2. For each new filled / canceled / expired order, emit the corresponding event.
3. Do **not** modify state.json (post-close owns authoritative reconciliation).
4. Do **not** call Claude.
5. Regenerate dashboard `recent_events` section only.
6. Git commit (`fill-watcher HH:MM ET`) + push.

### 6.6 Incident (any unhandled exception in any routine)

1. Catch at `cron.py` boundary.
2. Write `journal/incidents/YYYY-MM-DD-<slug>.md` with traceback + routine + state snapshot.
3. Set `state.trading_disabled = true`.
4. Emit `incident` Telegram event with file link.
5. Exit nonzero so GitHub Actions marks the run failed (red check, visible email).
6. Human clears by committing `state.json` with `trading_disabled=false` after investigation.

## 7. Claude seams (explicit contracts)

All SDK calls use **prompt caching** on STRATEGY.md as a stable system prompt (STRATEGY.md is large and stable → high cache hit rate). Temperature 0. Structured outputs via tool-use / JSON mode where possible.

| Seam | When | Model | Max tokens | Input | Output contract |
|---|---|---|---|---|---|
| Pre-market review | Pre-market step 12 | Sonnet 4.6 | 1024 | STRATEGY.md (cached), pre-market note, econ-calendar JSON, state summary | JSON `{ verdict: "go" \| "veto-new-entries" \| "halt", reason: string ≤ 280 chars }` |
| Daily AAR | Post-close step 7 | Sonnet 4.6 | 4096 | STRATEGY.md (cached), day's events, journal entries, state diff | Markdown body per §7 template + JSON `rule_breaks: [{kind, detail}]` |
| Weekly rollup | Weekly step 6 | Sonnet 4.6 | 1024 | 5 daily AARs | Markdown paragraph per §7 |
| Monthly review + strategy PR | Monthly step 5 | Opus 4.7 | 8192 | metrics JSON, STRATEGY.md (cached), last 3 monthly rollups | Markdown review + optional `strategy_diff: { file: "STRATEGY.md", patch: string, rationale: string }` |

**Guardrails enforced by the engine, not the prompt:**

- Claude cannot cause orders, stops, or risk numbers to change. Anything with real-world side effects lives in engine code; Claude's outputs are consumed as markdown/JSON that the engine validates and writes to files.
- The pre-market review only has one way to influence execution: setting `verdict` to veto or halt. The engine implements those two effects; any other field is ignored.
- Monthly strategy PRs must pass CI `regression-required` check before merging; the engine does not merge them.

## 8. Notifications (Telegram event catalogue)

All events go through `spy_trader.events.Event` and `spy_trader.notifier.send`. Each event is also appended to `docs/site/events.jsonl` (dashboard audit feed). Message format: one-line headline + two-line body; markdown-v2 disabled to avoid escaping.

| Event | Emitted when | Body example |
|---|---|---|
| `session_started` | Top of every routine | `🟢 pre_market started · Tide=UP · equity=$50,248` |
| `session_ended` | End of every routine | `✅ pre_market done · 1 candidate, 0 orders, [dashboard](url)` |
| `tide_verdict` | Weekly refresh | `🌊 Tide: UP (was FLAT) · EMA+ MACD+` |
| `candidate_found` | Screen Two pass | `🎯 SPY candidate · FI=-0.8 %K=22 impulse=blue` |
| `candidate_skipped` | Screen Two veto | `⚠️ SPY skipped · impulse red` |
| `buy_stop_placed` | New stop order | `📥 SPY buy-stop $521.34 · risk $992 (2.0%)` |
| `buy_stop_rolled` | Rolled to new day | `♻️ SPY buy-stop rolled to $522.18` |
| `buy_stop_expired` | 3-day expiry hit | `⌛ SPY buy-stop expired (3d)` |
| `trade_filled` | Entry triggered | `🚀 SPY filled 181@$522.40 · stop $514.50` |
| `stop_moved_to_breakeven` | 1R reached | `🛡 SPY stop → breakeven $522.40` |
| `trailing_stop_updated` | SafeZone ratchet | `🪜 SPY trail $527.10 (+0.9R)` |
| `target_hit` | Channel exit | `🎉 SPY target $540.20 · +3.1R` |
| `stop_hit` | Exit on stop | `🛑 SPY stop $522.40 · 0.0R` |
| `time_stop_exit` | §4.4 | `⏱ SPY time-stop exit · -0.2R` |
| `tide_flipped_against_position` | §4.5 | `🔄 Tide flipped · closing SPY cleanly` |
| `circuit_breaker_tripped` | §5.3 | `🚨 6% MTD hit · no new entries this month` |
| `heat_cap_blocked` | §5.2 | `🚫 SPY new signal blocked · heat 6.2%` |
| `claude_review` | Pre-market seam #1 | `🤖 Claude: GO · FOMC not today` |
| `incident` | Any error | `💥 Incident · state disabled · [file](url)` |
| `reconciliation` | Post-close end | `📊 0 entries · 0 exits · open risk $612 (1.2%)` |

## 9. Dashboard

Static HTML at `docs/site/index.html`, published to GitHub Pages via `.github/workflows/pages.yml`. Regenerated by `spy_trader.dashboard.render()` at the end of every routine and every fill-watcher tick. Panels:

1. **Header.** Last-updated timestamp (ET + user-local) + routine that produced it.
2. **Tide.** Large badge (UP / DOWN / FLAT) + weekly EMA / MACD values.
3. **Open positions.** Table: symbol, shares, entry, current, live stop, target, unrealized R, bars-held.
4. **Pending buy-stops.** Table: symbol, trigger, days-to-expiry, planned shares, planned risk.
5. **Risk panel.** MTD drawdown bar (towards 6%), open-risk bar (towards 6%), circuit-breaker status.
6. **Last AAR.** Rendered markdown of `aar/today.md` (or yesterday's if not yet written).
7. **Recent trades.** Last 20 rows from journal.
8. **Event feed.** Last 50 entries from `events.jsonl` with timestamps.

No JS framework; minimal CSS in `assets/style.css`. Mobile-friendly single column.

## 10. State model

`state/state.json` — schema-versioned, single source of truth for engine-facing state.

```json
{
  "schema_version": 1,
  "trading_disabled": false,
  "tide": { "verdict": "UP", "refreshed_at": "2026-04-17T20:00:00-04:00",
            "weekly_ema26": 518.3, "weekly_macd_hist": 1.24 },
  "positions": [
    {
      "symbol": "SPY",
      "side": "long",
      "shares": 181,
      "entry_price": 522.40,
      "initial_stop": 514.50,
      "current_stop": 522.40,
      "channel_target": 540.20,
      "entered_at": "2026-04-15T13:31:02-04:00",
      "bars_held": 3,
      "peak_unrealized_r": 1.2,
      "alpaca_order_ids": { "stop": "...", "target": "..." }
    }
  ],
  "candidates": [
    {
      "symbol": "SPY",
      "trigger": 522.18,
      "planned_shares": 181,
      "planned_initial_stop": 514.90,
      "placed_at": "2026-04-18T09:16:04-04:00",
      "expires_after": "2026-04-23",
      "alpaca_order_id": "..."
    }
  ],
  "last_fill_watcher_order_id": "o_abc123"
}
```

`state/month.json`:

```json
{
  "year_month": "2026-04",
  "month_start_equity": 50000.00,
  "min_equity_so_far": 49500.00,
  "mtd_drawdown_pct": 1.0,
  "circuit_breaker_tripped": false
}
```

`state/cache/` holds parquet OHLCV caches to avoid repeated API pulls. Weekly series is always resampled on demand from daily (per STRATEGY.md §8.1).

## 11. Sizing & risk modules (contracts)

```python
# sizing.py
def compute_shares(
    equity: float, entry: float, stop: float, risk_fraction: float = 0.02
) -> int:
    """Shares such that (entry - stop) * shares ≤ equity * risk_fraction.
    Raises if entry ≤ stop or result < 1."""

# risk.py
def open_risk(positions: list[Position]) -> float:
    """Sum of (entry - current_stop) * shares across open positions."""

def heat_cap_allows(new_risk: float, positions: list[Position], equity: float,
                    cap: float = 0.06) -> bool: ...

def monthly_breaker(month: MonthState, equity: float,
                    threshold: float = 0.06) -> bool:
    """Returns True if MTD drawdown has met the 6% threshold."""

def time_stop_exit(pos: Position, bars_held: int, peak_r: float,
                   bars_limit: int = 10) -> bool: ...
```

Key configuration in `config.py`:

```python
RISK_FRACTION = 0.02         # §5.1 "2% Rule"; halve to 0.01 on live first-month
HEAT_CAP = 0.06              # §5.2
MONTHLY_BREAKER = 0.06       # §5.3
BUY_STOP_EXPIRY_DAYS = 3     # §3.3
TIME_STOP_BARS = 10          # §4.4
CHANNEL_WIDTH_PCT = 0.027    # §4.2, recompute monthly
SAFEZONE_LOOKBACK = 10       # §4.3
SAFEZONE_MULT = 2.0          # §4.3
EMA_WEEKLY = 26
EMA_IMPULSE = 13
EMA_CHANNEL = 22
STOCHASTIC = (5, 3, 3)
MACD = (12, 26, 9)
FORCE_INDEX_EMA = 2
```

Changing any of these above defaults requires updating STRATEGY.md first, which in turn triggers the §8.7 regression flag in CI.

## 12. Error handling

- **Alpaca calls:** 3 retries with exponential-backoff + jitter; final failure raises `AlpacaError`.
- **Every position must have a live stop order at the end of every post-close run.** Missing → `incident` and `trading_disabled=true`.
- **State writes are atomic** (write to `state.json.tmp`, `fsync`, rename). Corrupt state on read raises before any orders are placed.
- **Schema version** bumped by a migration file under `spy_trader/migrations/`; unknown version refuses to boot.
- **Claude seams** run in try/except; failure writes an incident but does not block engine work — the AAR file will be a scaffold with `<Claude unavailable>` and the post-close still commits.
- **Fill-watcher failures** never halt trading; they only fail their own Actions run. Post-close re-reconciles authoritatively.

## 13. Testing

- **Unit:**
  - `tests/indicators/` — golden-file tests against Elder's published examples and a checked-in SPY slice.
  - `tests/screens/` — hand-crafted bar sequences proving UP/DOWN/FLAT boundaries, impulse-color veto, stale-candidate expiry.
  - `tests/sizing/` — §5.1 worked example; edge cases (entry≤stop, shares<1, buying-power clamp).
  - `tests/risk/` — heat cap acceptance + rejection; monthly breaker activation + reset; time-stop boundary.
  - `tests/state/` — atomic write round-trip; unknown schema version refusal.
  - `tests/notifier/` — payload shape; retries; Telegram markdown safety.
- **Integration:**
  - Replay a recorded Alpaca-paper day through pre-market → fill → post-close and assert final state, journal, events, dashboard HTML.
- **CI:** every PR runs unit + integration; Claude seams dry-run stub (temperature 0 deterministic stub in CI).
- **Coverage target:** 85%+ on `indicators/`, `screens.py`, `sizing.py`, `risk.py`, `orders.py`, `state.py`.

## 14. Regression protocol (§8.7 enforcement)

- CI job `regression-guard` runs on every PR.
- If any file in `{STRATEGY.md, spy_trader/indicators/**, spy_trader/screens.py, spy_trader/sizing.py, spy_trader/risk.py, spy_trader/orders.py, spy_trader/config.py}` changes, the job looks up `state/backtest_gate.json`:
  - If `updated_at` is older than the PR's base commit, job fails with message "Per STRATEGY.md §8.7, a backtest re-run is required before merging changes to mechanical-rule code."
- The gate file is a stub today — the real backtest engine is a follow-up spec; when that lands, passing the backtest updates the gate file, unblocking the PR.
- PRs that touch only narrative code (`aar.py`, `claude_review.py`, `dashboard.py`, `notifier.py`, `events.py`) bypass the guard.

## 15. Live-capital switch (documented, not built)

When the §8 paper-trade gate (3 months or 20 trades, plus backtest acceptance) is passed:

1. Change `ALPACA_BASE_URL` secret from `https://paper-api.alpaca.markets` to `https://api.alpaca.markets`.
2. Set `RISK_FRACTION=0.01` in `config.py` for the first calendar month live.
3. Update STRATEGY.md rule-card if desired; triggers §8.7.
4. No other code changes.

## 16. Required secrets

| Name | Purpose | Where |
|---|---|---|
| `ALPACA_API_KEY` | Alpaca paper API key | GH Actions secrets |
| `ALPACA_API_SECRET` | Alpaca paper API secret | GH Actions secrets |
| `ALPACA_BASE_URL` | `https://paper-api.alpaca.markets` | GH Actions vars |
| `ANTHROPIC_API_KEY` | Claude seams | GH Actions secrets |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API | GH Actions secrets |
| `TELEGRAM_CHAT_ID` | Target chat for notifications | GH Actions secrets |

Local dev uses `.env` (gitignored) mirroring the same names.

## 17. Implementation phases (high level, for the plan)

1. **Bootstrap repo.** `pyproject.toml`, tooling, CI skeleton, `.env.example`, directory scaffolding.
2. **Deterministic core.** Indicators → screens → sizing → risk, all pure + fully unit tested.
3. **Alpaca + state.** `alpaca_client.py`, `state.py`, `data.py`, minimal order wiring with mocks.
4. **Orders + journal.** `orders.py`, `journal.py` (§6 template); post-close fill reconciliation.
5. **Notifier + events.** Telegram wrapper, event catalogue, `events.jsonl` audit feed.
6. **Dashboard.** `dashboard.render()` + Pages workflow.
7. **Claude seams.** Pre-market review, AAR, weekly, monthly + strategy PR drafter.
8. **Cron wiring.** All GitHub Actions workflows, secret provisioning docs, regression guard.
9. **Paper dry-run.** Manual trigger, observe one simulated pre-market + post-close cycle end-to-end.
10. **Go live on Alpaca paper.** Enable cron schedules; start §8.6 3-month / 20-trade paper trial.

The writing-plans skill will take this phasing and expand it into concrete, testable tasks.

---

*End of design spec. Rules of record remain in `STRATEGY.md`; this document describes how they are executed.*
