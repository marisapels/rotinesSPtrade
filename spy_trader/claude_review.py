"""Anthropic review seams."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from anthropic import Anthropic

from spy_trader import config


@dataclass(frozen=True)
class ClaudeVerdict:
    verdict: str
    reason: str
    raw_text: str


class ClaudeReviewer:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None

    def review(self, prompt: str, *, model: str = config.CLAUDE_MODEL_SONNET) -> ClaudeVerdict:
        if self.client is None:
            return ClaudeVerdict("go", "Anthropic API key not configured", "skipped")
        response = self.client.messages.create(
            model=model,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if hasattr(block, "text"))
        verdict = "go"
        lowered = text.lower()
        if "halt" in lowered:
            verdict = "halt"
        elif "veto" in lowered:
            verdict = "veto-new-entries"
        return ClaudeVerdict(verdict=verdict, reason=text.strip(), raw_text=text)

    def review_pre_market(self, payload: dict[str, Any]) -> ClaudeVerdict:
        return self.review(f"Pre-market review:\n{payload}")

    def review_aar(self, payload: dict[str, Any]) -> ClaudeVerdict:
        return self.review(f"Write a short after-action review for:\n{payload}")

    def review_weekly(self, payload: dict[str, Any]) -> ClaudeVerdict:
        return self.review(f"Write a weekly rollup for:\n{payload}")

    def review_monthly(self, payload: dict[str, Any]) -> ClaudeVerdict:
        return self.review(
            f"Write a monthly review for:\n{payload}",
            model=config.CLAUDE_MODEL_OPUS,
        )
