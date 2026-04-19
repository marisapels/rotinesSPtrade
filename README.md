# spy-trader

Autonomous Elder Triple Screen paper-trading agent for SPY / SH on Alpaca.

## What this repo is

This repository contains Part 1 of the paper-trading agent described in:

- `docs/superpowers/specs/2026-04-18-paper-trading-agent-design.md`
- `docs/superpowers/plans/2026-04-18-paper-trading-agent-part1-core.md`
- `STRATEGY.md`

The current implementation gives you a locally runnable `spy_trader` package with:

- deterministic indicator, screening, sizing, and risk logic
- JSON-backed local state
- markdown journal and AAR writers
- Telegram and Claude seams
- static dashboard generation
- manual routines via CLI

It does not yet include the dedicated end-to-end integration harness from Task 33, and it is not yet wired to VPS `systemd` timers from Part 2.

## Requirements

- macOS or Linux
- Python 3.11
- `uv`
- Docker and Docker Compose (optional, for containerized runs)
- Alpaca paper account credentials

Optional:

- Telegram bot credentials
- Anthropic API key

## Install

From the repo root:

```bash
cd /Users/marisapels/Documents/rotinesSPtrade
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv sync --all-groups
```

If Python 3.11 is not installed, install it first. On macOS with Homebrew:

```bash
brew install python@3.11
```

## Environment

Create the env file:

```bash
cp .env.example .env
```

Fill in at least the Alpaca paper credentials:

```env
ALPACA_API_KEY=...
ALPACA_API_SECRET=...
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

Optional values:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
ANTHROPIC_API_KEY=...
GITHUB_TOKEN=...
UV_NO_EDITABLE=1
```

Notes:

- Use Alpaca paper credentials, not live credentials.
- If Telegram or Anthropic keys are missing, those integrations are skipped rather than blocking local runs.

## Verify the project

Run these commands:

```bash
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run pytest -q
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run ruff check .
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run mypy spy_trader
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run spy-trader --help
```

Expected result:

- tests pass
- lint passes
- mypy passes
- CLI shows the available routines

## Local runtime directories

Create the runtime folders once:

```bash
mkdir -p state state/cache journal var/www/trader
```

These are local development paths. In production, the design expects VPS paths such as `/var/lib/trader` and `/var/www/trader`.

## CLI routines

Available routines:

```bash
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run spy-trader pre-market
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run spy-trader post-close
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run spy-trader weekly
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run spy-trader monthly
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run spy-trader fill-watcher
```

What they do:

- `pre-market`: refreshes cached data, evaluates tide/wave/entry logic, may create pending orders, writes a pre-market note, updates dashboard and events
- `post-close`: reconciles positions, applies management logic, writes daily AAR output, updates dashboard and events
- `weekly`: recalculates the weekly tide
- `monthly`: refreshes month-start tracking
- `fill-watcher`: emits the fill watcher event path

## First local run

Run the pre-market routine:

```bash
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run spy-trader pre-market
```

Then inspect the generated files:

- `state/state.json`
- `journal/`
- `var/www/trader/index.html`
- `var/www/trader/events.jsonl`

You can open the dashboard file in a browser:

- [Dashboard](/Users/marisapels/Documents/rotinesSPtrade/var/www/trader/index.html)

## Files to inspect after each run

State:

- [state/state.json](/Users/marisapels/Documents/rotinesSPtrade/state/state.json)

Journal output:

- [journal](/Users/marisapels/Documents/rotinesSPtrade/journal)

Dashboard:

- [var/www/trader/index.html](/Users/marisapels/Documents/rotinesSPtrade/var/www/trader/index.html)

Event log:

- [var/www/trader/events.jsonl](/Users/marisapels/Documents/rotinesSPtrade/var/www/trader/events.jsonl)

## Typical local workflow

1. Sync dependencies.
2. Update `.env`.
3. Run tests.
4. Create runtime directories if missing.
5. Run `pre-market`.
6. Inspect `state`, `journal`, dashboard HTML, and event log.
7. Run `post-close`.
8. Inspect outputs again.

Example:

```bash
cd /Users/marisapels/Documents/rotinesSPtrade
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv sync --all-groups
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run pytest -q
mkdir -p state state/cache journal var/www/trader
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run spy-trader pre-market
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run spy-trader post-close
```

## Current implementation notes

The current repo is usable for local paper-trading development, but keep these limits in mind:

- some broker-facing flows are thin wrappers rather than battle-tested production automation
- the dedicated `tests/integration/` replay harness from the plan is not implemented yet
- Part 2 deployment assets like `systemd` timers and VPS runtime wiring are not the focus of the current local workflow

## Troubleshooting

If `uv run spy-trader --help` fails:

- rerun `UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv sync --all-groups`
- some environments skip the editable install `.pth` shim because it is created as a hidden file

If Alpaca calls fail:

- verify `ALPACA_API_KEY`
- verify `ALPACA_API_SECRET`
- verify `ALPACA_BASE_URL=https://paper-api.alpaca.markets`
- confirm you are using paper credentials

If the dashboard file is missing:

- create `var/www/trader`
- rerun a routine

If Telegram messages do not send:

- verify `TELEGRAM_BOT_TOKEN`
- verify `TELEGRAM_CHAT_ID`
- check network access

If Claude review is skipped:

- verify `ANTHROPIC_API_KEY`

## Development commands

Install dependencies:

```bash
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv sync --all-groups
```

Run tests:

```bash
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run pytest -q
```

Run lint:

```bash
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run ruff check .
```

Run mypy:

```bash
UV_NO_EDITABLE=1 UV_CACHE_DIR=.uv-cache uv run mypy spy_trader
```

Use the Makefile:

```bash
make install
make test
make lint
make typecheck
make check
```

## Docker

The repo now includes a Docker-based paper-trading setup with three services:

- `trader`: ad hoc routine runner
- `scheduler`: autonomous cron-driven routine scheduler
- `dashboard`: static nginx server for `var/www/trader/index.html`

The containerized runtime uses these persistent host-mounted paths:

- `./state`
- `./journal`
- `./var/www/trader`

The trading containers run with `TZ=America/New_York` and execute the CLI via
`python -m spy_trader.cli` to avoid local console-script issues.

### Build

Create the runtime directories once:

```bash
mkdir -p state state/cache journal var/www/trader
```

Build the image:

```bash
docker compose build
```

### Manual Docker runs

Run a single routine on demand:

```bash
docker compose run --rm trader pre-market
docker compose run --rm trader post-close
docker compose run --rm trader weekly
docker compose run --rm trader monthly
docker compose run --rm trader fill-watcher
```

### Autonomous Docker runs

Start the autonomous scheduler and dashboard:

```bash
docker compose up -d scheduler dashboard
```

Check logs:

```bash
docker compose logs -f scheduler
docker compose logs -f dashboard
```

Stop them:

```bash
docker compose down
```

### Docker schedule

The scheduler container runs these routines in `America/New_York`:

- `pre-market`: Monday-Friday 09:15
- `fill-watcher`: every 2 minutes Monday-Friday from 09:00-15:59, plus once at 16:00
- `post-close`: Monday-Friday 16:15
- `weekly`: Friday 16:30
- `monthly`: day 1 at 09:00

### Docker dashboard

After `scheduler` or a manual routine run has generated output, open:

- `http://localhost:8080/`

The dashboard serves the generated files from:

- [var/www/trader/index.html](/Users/marisapels/Documents/rotinesSPtrade/var/www/trader/index.html)

### Docker env

`compose.yaml` reads your local `.env` file. At minimum, set:

```env
ALPACA_API_KEY=...
ALPACA_API_SECRET=...
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

Optional integrations still work the same way in Docker:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
ANTHROPIC_API_KEY=...
GITHUB_TOKEN=...
```

## GitHub CD

The repo now includes a GitHub Actions deployment workflow at
[.github/workflows/cd.yml](/Users/marisapels/Documents/rotinesSPtrade/.github/workflows/cd.yml).

What it does on every push to `main`:

- runs lint, mypy, and tests
- builds the Docker image
- pushes the image to GitHub Container Registry as:
  - `ghcr.io/marisapels/rotinessptrade:latest`
  - `ghcr.io/marisapels/rotinessptrade:sha-<commit>`
- SSHes into the VPS
- pulls the new image
- restarts `scheduler` and `dashboard`

### VPS prerequisites

On the VPS, install:

- Docker Engine
- Docker Compose plugin
- git

Clone the repo once:

```bash
sudo mkdir -p /opt/rotinesSPtrade
sudo chown "$USER":"$USER" /opt/rotinesSPtrade
git clone https://github.com/marisapels/rotinesSPtrade.git /opt/rotinesSPtrade
cd /opt/rotinesSPtrade
mkdir -p state state/cache journal var/www/trader
```

Create the VPS `.env` file in the repo root:

```env
ALPACA_API_KEY=...
ALPACA_API_SECRET=...
ALPACA_BASE_URL=https://paper-api.alpaca.markets
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
ANTHROPIC_API_KEY=...
GITHUB_TOKEN=...
```

The deploy script used by GitHub Actions is:

- [deploy/vps/deploy.sh](/Users/marisapels/Documents/rotinesSPtrade/deploy/vps/deploy.sh)

### GitHub secrets

Add these repository secrets before enabling the workflow:

- `VPS_HOST`: VPS hostname or IP
- `VPS_USER`: SSH user on the VPS
- `VPS_SSH_KEY`: private key for the deploy user
- `VPS_PORT`: optional SSH port, usually `22`
- `VPS_APP_DIR`: deployment directory, for example `/opt/rotinesSPtrade`
- `GHCR_USERNAME`: GitHub username that can read the package on the VPS
- `GHCR_TOKEN`: GitHub token or PAT with `read:packages`

### First deploy

After the repo is cloned on the VPS and secrets are set, push to `main` or run
the `CD` workflow manually from GitHub Actions.

The VPS will then:

- `git pull --ff-only`
- `docker login ghcr.io`
- `docker compose pull`
- `docker compose up -d scheduler dashboard`

### Notes

- The VPS deploy uses the same [compose.yaml](/Users/marisapels/Documents/rotinesSPtrade/compose.yaml) file as local Docker runs.
- `trader` is available on the VPS for ad hoc manual routines, but the CD workflow only restarts `scheduler` and `dashboard`.
- The current deploy flow assumes the VPS checkout is a clean deployment checkout on `main`.

## Next step

If you want to see the engine operate with your local `.env`, run:

```bash
mkdir -p state state/cache journal var/www/trader
UV_CACHE_DIR=.uv-cache uv run spy-trader pre-market
```

Then inspect the state, event log, and dashboard files listed above.
