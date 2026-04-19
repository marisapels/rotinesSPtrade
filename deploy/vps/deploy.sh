#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/rotinesSPtrade}"
IMAGE_TAG="${IMAGE_TAG:?IMAGE_TAG is required}"
GHCR_USERNAME="${GHCR_USERNAME:?GHCR_USERNAME is required}"
GHCR_TOKEN="${GHCR_TOKEN:?GHCR_TOKEN is required}"
COMPOSE_FILE="${COMPOSE_FILE:-compose.yaml}"

cd "$APP_DIR"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git fetch origin main
  git checkout main
  git pull --ff-only origin main
fi

mkdir -p state state/cache journal var/www/trader

printf '%s\n' "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin

export TRADER_IMAGE="$IMAGE_TAG"

docker compose -f "$COMPOSE_FILE" pull trader scheduler dashboard
docker compose -f "$COMPOSE_FILE" up -d scheduler dashboard

docker image prune -f
