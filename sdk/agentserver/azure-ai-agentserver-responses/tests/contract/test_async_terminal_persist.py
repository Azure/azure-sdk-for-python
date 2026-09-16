# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for the in-process async terminal-persist optimization.

The non-resilient (in-process fallback) streaming path emits the terminal
``response.completed`` event to the client and closes the wire stream BEFORE
performing the terminal provider write. This moves the ~storage-write
round-trip off the client's last-byte (TTLB) path.

Validated behavior:
- The terminal event reaches the client without waiting for a slow terminal
  provider write.
- A GET during the deferral window (before the write lands) serves the
  completed snapshot from the in-memory runtime state.
- A deferred terminal-write FAILURE surfaces via a later GET (the record is
  NOT evicted while the deferred write is pending), while the client still
  received ``response.completed``.

The resilient path keeps the buffer-then-persist-then-yield contract and is
covered by the existing resilience/persistence-failure suites.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Iterable

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.store._base import ResponseProviderProtocol
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider

from .test_persistence_failure import (
    _AsyncAsgiClient,
    _collect_sse_events,
    _simple_completed_handler,
)


class _ControllableProvider:
    """Provider wrapper whose ``update_response`` can block or fail on demand.

    ``update_response`` awaits ``release`` (when provided) before completing,
    letting a test observe the deferral window deterministically. When
    ``fail_on_update`` is set it raises after being released/awaited.
    """

    def __init__(
        self,
        inner: ResponseProviderProtocol,
        *,
        release: asyncio.Event | None = None,
        fail_on_update: bool = False,
    ) -> None:
        self._inner = inner
        self._release = release
        self.fail_on_update = fail_on_update
        self.update_started = asyncio.Event()
        self.update_completed = False

    async def create_response(
        self,
        response: Any,
        input_items: Iterable[Any] | None,
        history_item_ids: Iterable[str] | None,
        *,
        context: Any = None,
    ) -> None:
        return await self._inner.create_response(response, input_items, history_item_ids, context=context)

    async def update_response(self, response: Any, *, context: Any = None) -> None:
        self.update_started.set()
        if self._release is not None:
            await self._release.wait()
        if self.fail_on_update:
            raise RuntimeError("Simulated terminal update failure")
        self.update_completed = True
        return await self._inner.update_response(response, context=context)

    async def get_response(self, response_id: str, *, context: Any = None) -> Any:
        return await self._inner.get_response(response_id, context=context)

    async def delete_response(self, response_id: str, *, context: Any = None) -> None:
        return await self._inner.delete_response(response_id, context=context)

    async def get_history_item_ids(
        self,
        response_id: str | None,
        before: str | None,
        limit: int,
        *,
        context: Any = None,
    ) -> list[str] | None:
        return await self._inner.get_history_item_ids(response_id, before, limit, context=context)

    async def get_input_items(
        self,
        response_id: str,
        *,
        limit: int = 100,
        ascending: bool = True,
        context: Any = None,
    ) -> list[Any]:
        return await self._inner.get_input_items(response_id, limit=limit, ascending=ascending, context=context)

    async def save_stream_events(self, response_id: str, events: Any, *, context: Any = None) -> None:
        if hasattr(self._inner, "save_stream_events"):
            return await self._inner.save_stream_events(response_id, events, context=context)

    async def get_stream_events(self, response_id: str, *, context: Any = None) -> Any:
        if hasattr(self._inner, "get_stream_events"):
            return await self._inner.get_stream_events(response_id, context=context)
        return None

    async def delete_stream_events(self, response_id: str, *, context: Any = None) -> None:
        if hasattr(self._inner, "delete_stream_events"):
            return await self._inner.delete_stream_events(response_id, context=context)


def _make_app(provider: _ControllableProvider) -> ResponsesAgentServerHost:
    app = ResponsesAgentServerHost(store=provider)
    app.response_handler(_simple_completed_handler)
    return app


def _extract_response_id(events: list[dict[str, Any]]) -> str | None:
    for evt in events:
        resp = evt["data"].get("response", evt["data"])
        rid = resp.get("id")
        if rid:
            return rid
    return None


def _parse_sse_bytes(body: bytes) -> list[dict[str, Any]]:
    """Parse SSE events from a buffered response body (``_AsgiResponse.body``)."""
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None
    for raw in body.decode("utf-8").splitlines():
        line = raw.rstrip("\r")
        if not line:
            if current_type is not None:
                payload = json.loads(current_data) if current_data else {}
                events.append({"type": current_type, "data": payload})
            current_type = None
            current_data = None
            continue
        if line.startswith("event:"):
            current_type = line[len("event:") :].strip()
        elif line.startswith("data:"):
            current_data = line[len("data:") :].strip()
    if current_type is not None:
        payload = json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": payload})
    return events


class TestAsyncTerminalPersist:
    """The in-process streaming path defers the terminal write off the wire."""

    def test_terminal_completed_emitted_before_slow_write(self) -> None:
        """Client receives ``response.completed`` while the terminal write is
        still blocked — proving the last byte does not wait for the write."""
        release = asyncio.Event()
        provider = _ControllableProvider(InMemoryResponseProvider(), release=release)
        app = _make_app(provider)
        client = TestClient(app)

        response = client.post(
            "/responses",
            json={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "stream": True,
                "store": True,
            },
        )
        assert response.status_code == 200

        events = _collect_sse_events(response)
        event_types = [e["type"] for e in events]

        # The client got the success terminal even though the terminal write
        # is still blocked on ``release`` (never set before collection).
        assert "response.completed" in event_types, f"Missing response.completed in {event_types}"
        assert "response.failed" not in event_types, f"Unexpected response.failed in {event_types}"
        # The blocking write has NOT completed — the client did not wait for it.
        assert provider.update_completed is False

        # Release so the deferred persist (and app shutdown) can finish cleanly.
        release.set()

    @pytest.mark.asyncio
    async def test_get_during_deferral_window_returns_completed(self) -> None:
        """A GET issued while the terminal write is still pending serves the
        completed snapshot from in-memory runtime state."""
        release = asyncio.Event()
        provider = _ControllableProvider(InMemoryResponseProvider(), release=release)
        app = _make_app(provider)
        client = _AsyncAsgiClient(app)

        post_resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "stream": True,
                "store": True,
            },
        )
        assert post_resp.status_code == 200
        events = _parse_sse_bytes(post_resp.body)
        assert "response.completed" in [e["type"] for e in events]
        response_id = _extract_response_id(events)
        assert response_id is not None

        # Let the deferred persist begin and block on ``release``.
        for _ in range(100):
            if provider.update_started.is_set():
                break
            await asyncio.sleep(0.01)
        assert provider.update_started.is_set()
        assert provider.update_completed is False  # still within the deferral window

        # GET during the window returns the completed snapshot from memory.
        get_resp = await client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        body = get_resp.json()
        assert body["status"] == "completed"

        release.set()

    @pytest.mark.asyncio
    async def test_deferred_update_failure_surfaces_via_get(self) -> None:
        """A deferred terminal-write failure surfaces on a later GET; the
        record is not evicted, and the client still saw ``response.completed``."""
        provider = _ControllableProvider(InMemoryResponseProvider(), fail_on_update=True)
        app = _make_app(provider)
        client = _AsyncAsgiClient(app)

        post_resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "stream": True,
                "store": True,
            },
        )
        assert post_resp.status_code == 200
        events = _parse_sse_bytes(post_resp.body)
        event_types = [e["type"] for e in events]
        # Client received success terminal (failure deferred off the wire).
        assert "response.completed" in event_types
        assert "response.failed" not in event_types
        response_id = _extract_response_id(events)
        assert response_id is not None

        # Poll GET until the deferred write failure is stamped on the record.
        failed_body: dict[str, Any] = {}
        for _ in range(100):
            await asyncio.sleep(0.05)
            get_resp = await client.get(f"/responses/{response_id}")
            if get_resp.status_code == 200:
                failed_body = get_resp.json()
                if failed_body.get("status") == "failed":
                    break

        assert failed_body.get("status") == "failed", f"GET never reflected failure: {failed_body}"
        assert failed_body.get("error", {}).get("code") == "storage_error"
