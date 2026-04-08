# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Deterministic synchronization helpers used by contract and integration tests."""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, Mapping

ContextProvider = Callable[[], Mapping[str, Any] | None]


def format_async_failure(
    *,
    label: str,
    timeout_s: float,
    elapsed_s: float,
    context: Mapping[str, Any] | None,
) -> str:
    """Build a stable, diagnostics-rich timeout failure message."""
    context_payload = dict(context or {})
    return f"{label} timed out after {elapsed_s:.3f}s (budget={timeout_s:.3f}s); diagnostics={context_payload}"


def poll_until(
    condition: Callable[[], bool],
    *,
    timeout_s: float,
    interval_s: float = 0.05,
    context_provider: ContextProvider | None = None,
    label: str = "poll_until condition",
) -> tuple[bool, str | None]:
    """Poll a condition until true or timeout; always returns diagnostic details on timeout."""
    start = time.monotonic()
    deadline = start + timeout_s
    last_context: Mapping[str, Any] | None = None

    while time.monotonic() < deadline:
        if condition():
            return True, None
        if context_provider is not None:
            maybe_context = context_provider()
            if maybe_context is not None:
                last_context = maybe_context
        time.sleep(interval_s)

    elapsed = time.monotonic() - start
    return False, format_async_failure(
        label=label,
        timeout_s=timeout_s,
        elapsed_s=elapsed,
        context=last_context,
    )


class EventGate:
    """Thread-safe event gate for deterministic synchronization in tests."""

    __slots__ = ("_event", "_payload")

    def __init__(self) -> None:
        self._event = threading.Event()
        self._payload: Any = None

    def signal(self, payload: Any = None) -> None:
        self._payload = payload
        self._event.set()

    def wait(self, *, timeout_s: float) -> tuple[bool, Any]:
        ok = self._event.wait(timeout_s)
        return ok, self._payload
