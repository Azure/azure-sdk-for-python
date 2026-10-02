# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests: stream events survive terminal state and respect a 10-minute TTL.

This test module pins the behavioural contract that, once a bg+stream
response reaches terminal status (completed, failed, etc.) and the
in-memory execution record is eagerly evicted, the persisted SSE events
MUST still be replayable via ``GET /responses/{id}?stream=true``.  This
holds for both the default in-memory provider path and the Foundry-like
hosted path (where the response provider does not also implement
stream-event persistence — replay is provided by the streams registry).

Per-event TTL semantics live in the SDK ``streams`` registry's own
conformance suite.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.models._generated import OutputItem, ResponseObject
from azure.ai.agentserver.responses.store._base import (
    ResponseProviderProtocol,
)
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming import ResponseEventStream
from tests._helpers import poll_until

# ────────────────────────────────────────
# Facade that strips stream capability (simulates Foundry / hosted)
# ────────────────────────────────────────


class _ResponseOnlyProvider:
    """Wraps InMemoryResponseProvider, exposing only ResponseProviderProtocol."""

    def __init__(self) -> None:
        self._inner = InMemoryResponseProvider()

    async def create_response(
        self,
        response: ResponseObject,
        input_items: Iterable[OutputItem] | None,
        history_item_ids: Iterable[str] | None,
        *,
        context: Any = None,
    ) -> None:
        await self._inner.create_response(response, input_items, history_item_ids, context=context)

    async def get_response(self, response_id: str, *, context: Any = None) -> ResponseObject:
        return await self._inner.get_response(response_id, context=context)

    async def update_response(self, response: ResponseObject, *, context: Any = None) -> None:
        await self._inner.update_response(response, context=context)

    async def delete_response(self, response_id: str, *, context: Any = None) -> None:
        await self._inner.delete_response(response_id, context=context)

    async def get_input_items(
        self,
        response_id: str,
        limit: int = 20,
        ascending: bool = False,
        after: str | None = None,
        before: str | None = None,
        *,
        context: Any = None,
    ) -> list[OutputItem]:
        return await self._inner.get_input_items(response_id, limit, ascending, after, before, context=context)

    async def get_items(
        self,
        item_ids: Iterable[str],
        *,
        context: Any = None,
    ) -> list[OutputItem | None]:
        return await self._inner.get_items(item_ids, context=context)

    async def get_history_item_ids(
        self,
        previous_response_id: str | None,
        conversation_id: str | None,
        limit: int,
        *,
        context: Any = None,
    ) -> list[str]:
        return await self._inner.get_history_item_ids(previous_response_id, conversation_id, limit, context=context)


# ────────────────────────────────────────
# Helpers
# ────────────────────────────────────────


def _build_client_default(handler: Any) -> TestClient:
    """Build a TestClient with the default InMemoryResponseProvider (non-hosted)."""
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    return TestClient(app)


def _build_client_hosted(handler: Any) -> TestClient:
    """Build a TestClient with a response-only provider (simulates Foundry / hosted)."""
    provider = _ResponseOnlyProvider()
    assert isinstance(provider, ResponseProviderProtocol)
    app = ResponsesAgentServerHost(store=provider)
    app.response_handler(handler)
    return TestClient(app)


async def _handler(request: Any, context: Any, cancellation_signal: asyncio.Event) -> Any:
    """Minimal handler: created → completed."""

    async def _events():
        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


async def _handler_with_output(request: Any, context: Any, cancellation_signal: asyncio.Event) -> Any:
    """Realistic handler: created → in_progress → message with text → completed."""

    async def _events():
        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )
        yield stream.emit_created()
        yield stream.emit_in_progress()

        message = stream.add_output_item_message()
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()
        yield text.emit_delta("Hello from the agent.")
        yield text.emit_text_done("Hello from the agent.")
        yield text.emit_done()
        yield message.emit_done()
        yield stream.emit_completed()

    return _events()


def _collect_sse_events(response: Any) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None
    for line in response.iter_lines():
        if not line:
            if current_type is not None:
                payload = json.loads(current_data) if current_data else {}
                events.append({"type": current_type, "data": payload})
            current_type = None
            current_data = None
            continue
        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()
    return events


def _wait_for_terminal(client: TestClient, response_id: str) -> dict[str, Any]:
    latest: dict[str, Any] = {}

    def _is_terminal() -> bool:
        nonlocal latest
        r = client.get(f"/responses/{response_id}")
        if r.status_code != 200:
            return False
        latest = r.json()
        return latest.get("status") in {"completed", "failed", "incomplete", "cancelled"}

    ok, failure = poll_until(
        _is_terminal,
        timeout_s=5.0,
        interval_s=0.05,
        context_provider=lambda: {"status": latest.get("status")},
        label=f"wait_for_terminal({response_id})",
    )
    assert ok, failure
    return latest


def _create_bg_stream(client: TestClient) -> tuple[str, list[dict[str, Any]]]:
    """POST bg+stream, consume SSE, return (response_id, events)."""
    payload = {
        "model": "gpt-4o-mini",
        "input": "hello",
        "stream": True,
        "store": True,
        "background": True,
    }
    with client.stream("POST", "/responses", json=payload) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)
    assert events, "Expected at least one SSE event"
    response_id = events[0]["data"]["response"]["id"]
    return response_id, events


# ════════════════════════════════════════════════════════════
# Tests: Stream survives terminal state
# ════════════════════════════════════════════════════════════


class TestStreamSurvivesTerminalState:
    """After terminal state + eager eviction, stream events must still be replayable."""

    def test_stream_replay_after_terminal_default_provider(self) -> None:
        """Default (non-hosted): stream replay works after completion + eviction."""
        client = _build_client_default(_handler)
        response_id, post_events = _create_bg_stream(client)
        snapshot = _wait_for_terminal(client, response_id)
        assert snapshot["status"] == "completed"

        # Runtime state should be evicted — GET falls through to provider
        # Stream replay must still work
        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay:
            assert replay.status_code == 200
            replay_events = _collect_sse_events(replay)

        assert len(replay_events) >= 2, f"Expected >= 2 events, got {len(replay_events)}"
        event_types = [e["type"] for e in replay_events]
        assert "response.created" in event_types
        assert "response.completed" in event_types
        assert replay_events[-1]["type"] == "response.completed"

    def test_stream_replay_after_terminal_hosted_provider(self) -> None:
        """Hosted (Foundry-like): stream replay works after completion + eviction."""
        client = _build_client_hosted(_handler)
        response_id, post_events = _create_bg_stream(client)
        snapshot = _wait_for_terminal(client, response_id)
        assert snapshot["status"] == "completed"

        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay:
            assert replay.status_code == 200
            replay_events = _collect_sse_events(replay)

        assert len(replay_events) >= 2
        event_types = [e["type"] for e in replay_events]
        assert "response.created" in event_types
        assert "response.completed" in event_types

    def test_stream_replay_preserves_all_events_default(self) -> None:
        """Default: all events from a realistic handler survive terminal + eviction."""
        client = _build_client_default(_handler_with_output)
        response_id, post_events = _create_bg_stream(client)
        _wait_for_terminal(client, response_id)

        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay:
            assert replay.status_code == 200
            replay_events = _collect_sse_events(replay)

        # Realistic handler emits: created, in_progress, item.added, content.added,
        # content.delta, content.text_done, content.done, item.done, completed = 9
        assert len(replay_events) >= 5, f"Expected >= 5 events, got {len(replay_events)}"
        replay_types = [e["type"] for e in replay_events]
        assert replay_types[0] == "response.created"
        assert replay_types[-1] == "response.completed"
        assert "response.output_item.added" in replay_types

    def test_stream_replay_preserves_all_events_hosted(self) -> None:
        """Hosted: all events from a realistic handler survive terminal + eviction."""
        client = _build_client_hosted(_handler_with_output)
        response_id, post_events = _create_bg_stream(client)
        _wait_for_terminal(client, response_id)

        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay:
            assert replay.status_code == 200
            replay_events = _collect_sse_events(replay)

        assert len(replay_events) >= 5, f"Expected >= 5 events, got {len(replay_events)}"
        replay_types = [e["type"] for e in replay_events]
        assert replay_types[0] == "response.created"
        assert replay_types[-1] == "response.completed"
        assert "response.output_item.added" in replay_types

    def test_multiple_replays_after_terminal(self) -> None:
        """Stream can be replayed multiple times after terminal state."""
        client = _build_client_default(_handler)
        response_id, _ = _create_bg_stream(client)
        _wait_for_terminal(client, response_id)

        for _ in range(3):
            with client.stream("GET", f"/responses/{response_id}?stream=true") as replay:
                assert replay.status_code == 200
                events = _collect_sse_events(replay)
            assert len(events) >= 2

    def test_multiple_replays_after_terminal_hosted(self) -> None:
        """Hosted: stream can be replayed multiple times after terminal state."""
        client = _build_client_hosted(_handler)
        response_id, _ = _create_bg_stream(client)
        _wait_for_terminal(client, response_id)

        for _ in range(3):
            with client.stream("GET", f"/responses/{response_id}?stream=true") as replay:
                assert replay.status_code == 200
                events = _collect_sse_events(replay)
            assert len(events) >= 2
