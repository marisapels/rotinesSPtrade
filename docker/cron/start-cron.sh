#!/usr/bin/env bash
set -euo pipefail

mkdir -p /app/state/cache /app/journal /app/var/www/trader

python3 - <<'PY' > /etc/spy-trader.env
import os
import shlex

for key, value in sorted(os.environ.items()):
    print(f"export {key}={shlex.quote(value)}")
PY

chmod 600 /etc/spy-trader.env
cp /app/docker/cron/spy-trader.cron /etc/cron.d/spy-trader
chmod 0644 /etc/cron.d/spy-trader
crontab /etc/cron.d/spy-trader

touch /var/log/cron.log
exec cron -f
