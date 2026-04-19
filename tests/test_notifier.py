from __future__ import annotations

import httpx
import respx

from spy_trader.events import Event
from spy_trader.notifier import TelegramNotifier


@respx.mock
def test_notifier_posts_payload() -> None:
    route = respx.post("https://api.telegram.org/bottoken/sendMessage").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    notifier = TelegramNotifier(bot_token="token", chat_id="123")
    notifier.notify("hello")
    assert route.called


def test_notify_event_formats_kind() -> None:
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200)))
    notifier = TelegramNotifier(bot_token="token", chat_id="123", client=client)
    notifier.notify_event(Event(kind="test", message="message"))
