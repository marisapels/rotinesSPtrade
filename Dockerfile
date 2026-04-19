FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash ca-certificates curl cron tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY spy_trader ./spy_trader
COPY dashboard_template ./dashboard_template
COPY docker ./docker

RUN UV_CACHE_DIR=/tmp/uv-cache uv sync --frozen --no-dev --no-editable

RUN mkdir -p /app/state/cache /app/journal /app/var/www/trader

ENTRYPOINT ["/app/.venv/bin/python", "-m", "spy_trader.cli"]
CMD ["--help"]
