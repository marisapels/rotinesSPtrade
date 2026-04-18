# A Swing Trader's Method for the S&P 500

*A strategy document in the voice of Dr. Alexander Elder, adapted for the modern retail trader operating on Alpaca using SPY for long-S&P exposure and SH for short-S&P exposure.*

---

## 1. Preface — A Letter To The Trader

Dear friend,

You have decided to trade the S&P 500. It is a good choice. The S&P is the most liquid, most studied, most efficient market available to a private trader. You will not outsmart it with a clever prediction. You will succeed only by outlasting your own impulses and obeying a small set of rules that give you a statistical edge over many hundreds of trades.

This document is that set of rules. It is not a philosophy. It is not a story. It is a method.

You will trade the S&P 500 in two directions:

- **When the trend is up, you will buy SPY.** Long SPY = long S&P.
- **When the trend is down, you will buy SH.** SH is the -1× inverse S&P 500 ETF. Buying SH *long* gives you short-S&P exposure without borrowing shares, without margin, without overnight-short fees, and without the wash-sale complications of true short sales. On Alpaca, this is the cleanest path to symmetric long-and-short participation.

Throughout this document the phrase *"going short S&P"* always means **buying SH as a long position**. The word "short" never means a real short sale.

Three things will determine whether you succeed:

- **Mind** — your discipline.
- **Method** — the Triple Screen system that follows.
- **Money** — the 2% and 6% rules, non-negotiable.

Read every section. Write the rules on an index card and tape it above your monitor. Then, and only then, open your Alpaca account.

— A.E.

---

## 2. The Three M's

### 2.1 Mind

Most traders do not lose because their analysis is wrong. They lose because their analysis is fine but their behavior is not. They move stops, they chase breakouts, they double down on losers, they revenge-trade after a bad Monday. Markets pay small rewards to the disciplined and extract large fees from the rest.

Your discipline is enforced by three artifacts in this document:

1. The **rules in §3–§5** — written so that a question can be answered *yes/no*, not *maybe*.
2. The **Trader's Journal (§6)** — every trade logged at entry and at exit.
3. The **Daily After-Action Review (§7)** — end-of-day reflection, written whether or not you traded.

If you cannot commit to all three, stop here. Trade paper money indefinitely.

### 2.2 Method

The method is the **Triple Screen Trading System**. It is a set of three time-frame filters applied in order. A trade is taken only when all three filters agree. The details are in §3.

### 2.3 Money

Two rules, and both bind:

- **The 2% Rule.** Never put more than **2% of account equity** at risk on a single trade. "At risk" means `(entry − stop) × shares`.
- **The 6% Rule.** If cumulative realized losses plus open-position drawdown in a calendar month reach **6% of month-start equity**, you stop trading for the rest of the month. No exceptions, no "just one more setup."

Details and formulas in §5.

---

## 3. The Triple Screen Trading System

The three screens work on three time frames. The longer time frame sets direction. The middle time frame finds the pullback. The shortest time frame triggers the entry. You never argue with the tide.

### 3.1 Screen One — The Tide (Weekly Chart)

**Purpose:** Determine the direction in which you are permitted to trade this week.

**Indicators (on the weekly SPY chart):**

| Indicator | Parameter | Use |
|---|---|---|
| EMA (Exponential Moving Average) | **26 weeks** | Slope defines the weekly trend |
| MACD Histogram | 12, 26, 9 | Direction of the histogram confirms the trend |

**Rules:**

1. **Tide is UP** if the 26-week EMA is rising this week **and** the weekly MACD histogram is rising (this week's bar taller than last week's, or turning up from below zero).
   → You are permitted to **buy SPY**. You may not initiate any SH position.
2. **Tide is DOWN** if the 26-week EMA is falling this week **and** the weekly MACD histogram is falling.
   → You are permitted to **buy SH** (i.e., go short S&P). You may not initiate any SPY long.
3. **Tide is FLAT / MIXED** if the EMA slope and MACD histogram disagree, or either is flat.
   → **You stand aside.** Close no positions you already hold on the basis of flatness alone, but open none.

**Refresh cadence:** once per week, after Friday's close. The tide does not change intraweek for the purpose of opening new trades.

### 3.2 Screen Two — The Wave (Daily Chart)

**Purpose:** Within the permitted direction, find a *pullback against the tide* where price is stretched and ready to snap back in the tide's direction. You buy dips in up-tides; you buy SH on rallies in down-tides.

**Indicators (on the daily SPY chart when tide is up, or daily SH chart when tide is down):**

| Indicator | Parameter | Use |
|---|---|---|
| Force Index (EMA) | **2-day EMA** | Short-term bull/bear pressure |
| Stochastic | **5, 3, 3** | Oversold / overbought oscillator |
| Impulse System | 13-period EMA slope + MACD-histogram slope | Veto filter — colors each daily bar |

**Impulse System colors (applied to each daily bar):**

- **Green** — both the 13-EMA is rising and the MACD histogram is rising. *Bulls are in control.*
- **Red** — both the 13-EMA is falling and the MACD histogram is falling. *Bears are in control.*
- **Blue** — any other combination. *Mixed.*

**Rules (tide up — buying SPY):**

1. Wait for a **pullback** on the daily SPY chart: **2-day Force Index crosses below zero** OR **Stochastic %K drops below 30**.
2. **Impulse veto:** you may not buy SPY on a day whose bar is **red**. Green or blue only.
3. When conditions 1 and 2 are satisfied, SPY becomes a **candidate long** for Screen Three.

**Rules (tide down — buying SH):**

1. Wait for a **pullback on SH** (which corresponds to a *rally in SPY*): **2-day Force Index on SH crosses below zero** OR **Stochastic %K on SH drops below 30**.
2. **Impulse veto:** you may not buy SH on a day whose SH bar is **red**. Green or blue only.
3. When conditions 1 and 2 are satisfied, SH becomes a **candidate long** for Screen Three.

Run Screen Two indicators on the instrument you will actually buy (SPY for up-tide, SH for down-tide). Do not buy SH based on SPY oscillators; SH has its own price series and its own signals.

### 3.3 Screen Three — The Entry Trigger (Daily Stop-Order)

**Purpose:** Buy only when price confirms the setup by breaking in your direction. No market-on-open entries. No anticipation.

**Rules:**

1. After Screen Two produces a candidate, note the prior day's **high** on the instrument you will buy (SPY or SH).
2. Place a **buy-stop order** one tick above that prior-day high. Tick = $0.01.
3. **Re-rack each day** the setup remains valid: cancel and reissue at the new prior-day high.
4. If the order does not trigger within **3 trading days**, **cancel and wait**. The pullback is over or has failed. Do not chase.
5. If the order triggers, immediately place the **initial stop-loss** (§4.1). An entry without a live stop is an error.

---

## 4. Entry, Stop, and Exit Rules

### 4.1 Initial Stop-Loss

- **SPY long:** stop goes **one tick below the lowest low of the past 2 trading days**, or below the most recent identifiable swing low, **whichever is lower**.
- **SH long (short-S&P):** stop goes **one tick below the lowest low of the past 2 trading days on SH**, or below the most recent SH swing low, whichever is lower.
- Distance `entry − stop` drives the position size (§5.1). You do not adjust the stop to fit a position; you adjust the position to fit the stop.

### 4.2 Profit Target — Channel Exit

Plot a **22-day EMA** with an **envelope** set so that roughly 95% of the past 100 bars fit inside. A typical value on SPY is ±2.7% from the 22-EMA; recompute monthly.

- **SPY long:** scale out or close at the **upper channel line**.
- **SH long:** scale out or close at the **upper SH channel line**.

The channel is Elder's "value zone." You buy below value and sell into the upper band where price is overextended and mean-reversion odds are highest.

### 4.3 Trailing Stop

1. When the trade has moved **one R** in your favor (where R = initial risk per share = `entry − stop`), move the stop to **breakeven**. The trade is now free.
2. After breakeven, trail the stop using the **SafeZone** method:
   - Compute the average of the last 10 days' "downside penetrations" — i.e., the distance each day's low fell below the prior day's low (only counting days where it did).
   - Multiply by 2. This is the SafeZone distance.
   - For a SPY long, trail the stop at `today's low − SafeZone`. Only move the stop **up**, never down.
   - For an SH long, trail analogously on SH price.
3. The channel-exit target (§4.2) and the trailing stop race each other. Whichever hits first, you are out.

### 4.4 Time Stop

If the trade has not moved **at least 1R in your favor within 10 trading days** of entry, close the position at the next day's open. Dead trades tie up risk budget and attention.

### 4.5 Reversal Handling

- Do **not** reverse in one action. If the weekly tide flips against an open position, exit first, re-run Screens Two and Three on the new direction, and enter the opposite side only on a fresh, qualified signal.
- You never hold SPY and SH simultaneously. They are opposite expressions of the same view.

### 4.6 Adding to Winners (Pyramiding)

- Add only to a position that is already profitable past 1R.
- Each add uses the same 2% sizing (§5.1) computed against a new, higher stop.
- Maximum three units per direction.
- Never, under any circumstances, add to a losing trade.

---

## 5. Money Management — The 2% and 6% Rules

### 5.1 Position Sizing (The 2% Rule)

For each trade, compute:

```
risk_dollars    = account_equity × 0.02
risk_per_share  = entry_price − stop_price        (positive number)
shares          = floor( risk_dollars / risk_per_share )
```

Example: equity = $50,000; 2% = $1,000; SPY entry $520.00, stop $514.50 → risk/share = $5.50 → shares = floor(1000 / 5.50) = **181 shares**.

If `shares × entry_price` exceeds available buying power, reduce share count until it fits. Never reduce the stop distance to fit the position.

### 5.2 Portfolio Heat

Sum the open risk across **all** live positions (including pyramided adds).

- **Hard cap: 6%** of account equity at any moment across all open risk.
- If a new signal would push total open risk above 6%, you do not take the new signal. The cap is not a suggestion.

### 5.3 Monthly Drawdown Circuit Breaker (The 6% Rule)

At the **start of each calendar month**, record `month_start_equity`.

At the **end of each trading day**, compute:

```
month_drawdown = month_start_equity − min(equity_so_far_this_month)
if month_drawdown ≥ 0.06 × month_start_equity:
    STOP TRADING until the first trading day of the next calendar month.
```

"Stop trading" means: **open no new positions**. You may manage existing positions (honor stops, take targets) but initiate nothing. This rule has saved more traders than any indicator ever written.

### 5.4 Resetting After the Circuit Breaker

When the next month begins:

- Reset `month_start_equity` to current equity.
- Return to normal 2% sizing. Do not double up to "make it back." That path leads to blown accounts.

---

## 6. Trader's Journal Template

Create one entry per trade. Fill the top half at entry, the bottom half at exit. Keep it in a single spreadsheet or markdown file per month.

```
-----------------------------------------------------------
TRADE #: ______      DATE OPENED: YYYY-MM-DD
INSTRUMENT:  [ ] SPY (long S&P)   [ ] SH (short S&P)

-- Screen One (Weekly Tide) --
26W EMA slope:        [ ] rising  [ ] falling  [ ] flat
Weekly MACD hist:     [ ] rising  [ ] falling  [ ] flat
Tide verdict:         [ ] UP      [ ] DOWN     [ ] STAND ASIDE

-- Screen Two (Daily Wave) --
Force Index (2-EMA):  value = _____   signal: _______________
Stochastic (5,3,3):   %K = ____    %D = ____
Impulse color:        [ ] Green  [ ] Blue  [ ] Red (VETO)

-- Screen Three (Entry) --
Prior day high:       $_______
Buy-stop placed at:   $_______    Filled at: $_______

-- Sizing --
Account equity:       $_______
Risk dollars (2%):    $_______
Stop price:           $_______
Risk per share:       $_______
Shares:               _______     Position $ value: $_______

-- Plan --
Initial stop:         $_______
Channel target:       $_______
Planned R multiple:   _______
Thesis (one sentence):
____________________________________________________________

===== EXIT =====
Date closed:          YYYY-MM-DD
Exit reason:          [ ] Channel target  [ ] Trailing stop
                      [ ] Time stop       [ ] Initial stop
                      [ ] Tide flipped    [ ] Rule break (explain)
Exit price:           $_______
Realized R:           _______
P&L $:                $_______
One-line lesson:
____________________________________________________________
-----------------------------------------------------------
```

---

## 7. Daily After-Action Review (AAR)

Complete this at the end of **every trading day**, even days you did not place an order. It takes ten minutes. It will compound into your most valuable asset.

```
AAR — YYYY-MM-DD

1. What was planned at the open
   - Tide: [UP / DOWN / FLAT]
   - Candidates on the watchlist and why:
   -

2. What actually happened
   - Trades opened today:
   - Trades closed today (and exit reason):
   - Watchlist candidates skipped (and why):

3. What went well
   - Rules I followed even when tempted otherwise:
   - Discipline points I'm proud of:

4. What didn't, and how I improve tomorrow
   - Any rule broken? (entry without Screen 2 confirmation, stop moved,
     sized > 2%, traded after 6% monthly stop, etc.):
   - Emotional tells I noticed (FOMO, revenge, boredom, euphoria):
   - Concrete adjustment for tomorrow:
```

**Weekly rollup (every Friday after the close):** skim the five daily AARs, write one paragraph naming the single most repeated mistake of the week and the single most repeated good habit.

**Monthly rollup (first weekend of the next month):** tally realized R, win rate, average winner R, average loser R, largest drawdown, and whether the 6% circuit breaker fired. Compare against §8 acceptance thresholds.

---

## 8. Backtest & Validation Plan

You do not trade this system with real money until it has passed three gates: historical backtest, walk-forward, and paper trading.

### 8.1 Data

- **Instruments:** SPY and SH, daily OHLCV.
- **History:** minimum **10 years** of SPY; for SH, use all available history (SH began trading 2006-06-21; ample for our needs).
- **Weekly series:** resample daily data to weekly (Monday–Friday bars) for Screen One. Do not use a separate weekly feed; resample from the same daily source to keep the series consistent.
- **Adjustments:** use dividend-adjusted close where available. Elder indicators are robust to small adjustments, but be consistent across tide/wave/entry calculations.

### 8.2 Split

- **In-sample (IS):** first **70%** of the dataset. Use this to confirm the default indicator parameters listed in §3. You may test ±1 perturbations around the defaults to check robustness — you may **not** parameter-hunt for the best backtest.
- **Out-of-sample (OOS):** last **30%** of the dataset. Run once, using the parameters locked in from IS. Whatever the OOS performance is, that is the honest number.

### 8.3 Simulation Rules

- Fills at next day's open after a signal (conservative vs. same-day close fills).
- Commission on Alpaca: $0. Slippage assumption: **1 tick ($0.01)** per side. Be conservative.
- Account starts at a round number (e.g., $50,000). Size every trade by the live 2% rule from the *simulated* equity curve, not from the starting balance.
- The 6% monthly circuit breaker must be active during the backtest. Its frequency is itself a diagnostic.

### 8.4 Metrics to Report

| Metric | Definition |
|---|---|
| Total return | Final equity / start equity − 1 |
| CAGR | Annualized return |
| Max drawdown | Largest peak-to-trough equity drop |
| Sharpe ratio | Annualized, risk-free = 0 |
| Profit factor | Gross profit / gross loss |
| Win rate | Winners / total closed trades |
| Avg R won / Avg R lost | In R multiples |
| Longest losing streak | Consecutive losers |
| 6% circuit-breaker frequency | Months triggered / total months |

### 8.5 Acceptance Thresholds (OOS)

Pass only if **all** of the following hold:

- Profit factor **≥ 1.5**
- Max drawdown **≤ 20%**
- Sharpe **≥ 0.8**
- 6% circuit breaker triggered in **no more than ~15%** of months
- CAGR at least equal to buy-and-hold SPY over the same OOS window, **or** CAGR within 2 percentage points of buy-and-hold with materially lower max drawdown

Fail any one and the system goes back to the bench. Do not adjust rules to pass the OOS test — that is how backtests lie.

### 8.6 Paper-Trade Gate

After a clean OOS pass:

- Run the identical rule set on **Alpaca Paper** for a minimum of **3 calendar months or 20 trades, whichever comes last**.
- The paper-trading results must be within a reasonable band of the backtest: profit factor not worse than 1.3, max drawdown not worse than 25%.
- Only then does live capital begin, and it begins at **half** your intended 2% — i.e., effectively 1% per trade — for the first full calendar month live.

### 8.7 Regression Protocol

Any future change to this document — a new parameter, a new rule, a new instrument — forces a full re-run of §8.1–§8.6 before the change goes live. Treat the strategy as production code: no silent edits.

---

## 9. Pre-Market Checklist

Run this every trading day before 09:30 ET. Ten items. Two minutes.

1. **Tide** (weekly, checked Mondays and after every Friday close): UP / DOWN / FLAT?
2. **Month-to-date drawdown**: under 6%? If not, close this checklist; you are done for the month.
3. **Open positions**: live stops verified on Alpaca? Each matches my journal?
4. **Open risk**: sum in dollars — under 6% of equity?
5. **Candidates from yesterday's Screen Two**: still valid? Buy-stops rolled to today's prior-day high?
6. **New Screen Two candidates from yesterday's close?**
7. **Impulse System color on each candidate** today: green / blue allowed, red vetoed.
8. **Economic calendar**: FOMC? CPI? NFP? If yes, consider no new entries before the release.
9. **Account buying power sufficient** for any buy-stop that may fill?
10. **Journal and AAR templates** open for the day.

If any of items 2, 3, 4 fails, do not trade.

---

## 10. Appendix

### 10.1 Indicator Glossary (Elder's core set)

- **Force Index** — `(close − prior_close) × volume`, smoothed by an EMA. A 2-day EMA is sensitive to short-term pressure; a 13-day EMA is used for medium-term conviction. Zero-line crosses mark shifts in pressure.
- **Impulse System** — colors each bar from the combination of the 13-EMA slope and the MACD-histogram slope. Green = both up (bulls in charge). Red = both down (bears in charge). Blue = mixed. Elder's rule: *never buy a red bar, never sell short a green bar*.
- **SafeZone Stop** — a volatility-adaptive trailing stop. For a long, sum the distances by which each of the last 10 days' lows penetrated the prior day's low, average them, multiply by a coefficient (default 2.0). Trail the stop that far below today's low, and only ratchet it up.
- **Elder-Ray (Bull/Bear Power)** — `Bull = high − 13-EMA`; `Bear = low − 13-EMA`. Useful for divergence work; optional in this system.
- **Channel / Envelope** — a moving average with ±X% bands set so ~95% of recent bars fit inside. Upper band = overextended = take-profit zone for longs.

### 10.2 Indicator Parameter Reference (Canonical Defaults)

| Screen | Indicator | Parameter |
|---|---|---|
| 1 (weekly) | EMA | 26 |
| 1 (weekly) | MACD | 12, 26, 9 |
| 2 (daily) | Force Index EMA | 2 |
| 2 (daily) | Stochastic | 5, 3, 3 |
| 2 (daily) | Impulse EMA | 13 |
| 2 (daily) | Impulse MACD | 12, 26, 9 |
| 4 (exits) | Channel EMA | 22 |
| 4 (exits) | Channel width | ~±2.7% on SPY, recompute monthly |
| 4 (exits) | SafeZone lookback | 10 days |
| 4 (exits) | SafeZone multiplier | 2.0 |
| 4 (exits) | Time stop | 10 trading days |

### 10.3 SPY / SH Execution Facts

- **SPY** — SPDR S&P 500 ETF Trust. Expense ratio ~0.09%. Deepest ETF liquidity on the tape. Trades 09:30–16:00 ET. Dividends quarterly (affect channel calculations — use adjusted series).
- **SH** — ProShares Short S&P 500 (-1× daily). Expense ratio ~0.88%. Adequate liquidity for retail sizing; check bid-ask spread before market orders. **Daily** reset: SH's multi-day return is **not** exactly the negative of SPY's multi-day return — path matters. For swing holds of days to weeks this is acceptable but monitor; multi-week drift vs. −SPY is a known cost of this expression.
- **Order types on Alpaca used by this system:** buy-stop (Screen Three entry), stop (initial and trailing stop-loss), limit (optional for channel target), market (last-resort exits only).
- **Paper vs. live:** the strategy is developed and validated on paper (`https://paper-api.alpaca.markets`) and only promoted to live after §8.6 is satisfied.

### 10.4 Rule Card (Index-Card Version)

*Print this. Tape it above your monitor.*

```
THE TIDE  — weekly: 26-EMA slope + weekly MACD hist agree? if not, stand aside.
THE WAVE  — daily:  pullback (2-FI < 0 or Stoch %K < 30) + Impulse not red.
THE ENTRY — daily:  buy-stop 1¢ above prior-day high. 3-day expiry.
THE STOP  — 1 tick below 2-day low. Size: shares = 2% equity / (entry − stop).
THE EXIT  — upper 22-EMA channel OR SafeZone trail OR 10-day time stop.
THE HEAT  — open risk ≤ 6% of equity. Monthly DD ≥ 6% → stop trading.
THE VEHICLE — up tide → buy SPY. Down tide → buy SH. Never both.
```

---

*End of document. Re-read it before every trading week. The rules do not get easier; you get better at them.*
