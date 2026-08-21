"""Shared GitHub Models HTTP client (OpenAI-compatible).

All model calls funnel through here so auth, retry/backoff, and JSON-mode handling
live in one place. The judge/theme modules depend only on the ``Completer`` callable
so they remain HTTP-free and unit-testable.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

import httpx

from analyzer.github.client import resolve_token

logger = logging.getLogger(__name__)

MODELS_URL = "https://models.inference.ai.azure.com/chat/completions"
DEFAULT_TIMEOUT = 60.0
MAX_RETRIES = 4

# A Completer takes (system_prompt, user_prompt) and returns the raw model content.
Completer = Callable[[str, str], str]


class LLMError(RuntimeError):
    """Raised when the Models endpoint fails irrecoverably."""


class GitHubModelsClient:
    """Minimal client for the GitHub Models chat-completions endpoint."""

    def __init__(
        self,
        model: str,
        *,
        token: str | None = None,
        client: httpx.Client | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._model = model
        self._token = resolve_token(token)
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout)
        self._max_retries = max_retries
        self._sleep = sleep

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> GitHubModelsClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def complete(self, system: str, user: str) -> str:
        """Send a JSON-mode chat completion and return the message content."""
        payload = {
            "model": self._model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        attempt = 0
        while True:
            resp = self._client.post(MODELS_URL, json=payload, headers=headers)
            if resp.status_code == 401:
                raise LLMError("GitHub Models authentication failed (HTTP 401)")
            if resp.status_code in (429, 503) or resp.status_code >= 500:
                if attempt < self._max_retries:
                    wait = self._retry_after(resp, attempt)
                    logger.warning("Models HTTP %s; backing off %.1fs", resp.status_code, wait)
                    self._sleep(wait)
                    attempt += 1
                    continue
            if resp.status_code >= 400:
                raise LLMError(f"Models HTTP {resp.status_code}: {resp.text[:200]}")
            data = resp.json()
            try:
                return str(data["choices"][0]["message"]["content"])
            except (KeyError, IndexError, TypeError) as exc:
                raise LLMError(f"Unexpected Models response shape: {exc}") from exc

    @staticmethod
    def _retry_after(resp: httpx.Response, attempt: int) -> float:
        ra = resp.headers.get("Retry-After")
        if ra and ra.isdigit():
            return float(ra)
        return float(2**attempt)


def make_completer(model: str, *, token: str | None = None) -> Completer:
    """Build a :data:`Completer` bound to a long-lived Models client."""
    client = GitHubModelsClient(model, token=token)
    return client.complete
