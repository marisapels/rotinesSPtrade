"""Telegram notifier."""

from __future__ import annotations

import os

import httpx

from spy_trader import config
from spy_trader.events import Event


class TelegramNotifier:
    def __init__(
        self,
        bot_token: str | None = None,
        chat_id: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")
        self.client = client or httpx.Client(timeout=10.0)

    def notify(self, text: str) -> None:
        if not self.bot_token or not self.chat_id:
            return
        self.client.post(
            f"{config.TELEGRAM_API_BASE}/bot{self.bot_token}/sendMessage",
            json={"chat_id": self.chat_id, "text": text},
        ).raise_for_status()

    def notify_event(self, event: Event) -> None:
        self.notify(f"[{event.kind}] {event.message}")
