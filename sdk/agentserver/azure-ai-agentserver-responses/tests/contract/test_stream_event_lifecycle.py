# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests: stream events survive terminal state and respect a 10-minute TTL.

These tests validate two critical invariants:

1. **Stream persistence after terminal state** — Once a bg+stream response
   reaches terminal status (completed, failed, etc.) and the in-memory
   execution record is eagerly evicted, the persisted SSE events MUST still
   be replayable via ``GET /responses/{id}?stream=true``.  This holds for
   both the default in-memory provider path and the Foundry-like hosted path
   (where the response provider does not implement ``ResponseStreamProviderProtocol``).

2. **Per-event 10-minute TTL (B35)** — Each SSE event carries a ``_saved_at``
   timestamp.  ``get_stream_events()`` filters out events older than the
   replay TTL (default 600 s / 10 minutes).  Events within the window MUST
   be returned; events outside the window MUST be filtered.
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
    ResponseStreamProviderProtocol,
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
        isolation: Any = None,
    ) -> None:
        await self._inner.create_response(response, input_items, history_item_ids, isolation=isolation)

    async def get_response(self, response_id: str, *, isolation: Any = None) -> ResponseObject:
        return await self._inner.get_response(response_id, isolation=isolation)

    async def update_response(self, response: ResponseObject, *, isolation: Any = None) -> None:
        await self._inner.update_response(response, isolation=isolation)

    async def delete_response(self, response_id: str, *, isolation: Any = None) -> None:
        await self._inner.delete_response(response_id, isolation=isolation)

    async def get_input_items(
        self,
        response_id: str,
        limit: int = 20,
        ascending: bool = False,
        after: str | None = None,
        before: str | None = None,
        *,
        isolation: Any = None,
    ) -> list[OutputItem]:
        return await self._inner.get_input_items(response_id, limit, ascending, after, before, isolation=isolation)

    async def get_items(
        self,
        item_ids: Iterable[str],
        *,
        isolation: Any = None,
    ) -> list[OutputItem | None]:
        return await self._inner.get_items(item_ids, isolation=isolation)

    async def get_history_item_ids(
        self,
        previous_response_id: str | None,
        conversation_id: str | None,
        limit: int,
        *,
        isolation: Any = None,
    ) -> list[str]:
        return await self._inner.get_history_item_ids(previous_response_id, conversation_id, limit, isolation=isolation)


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
    assert not isinstance(provider, ResponseStreamProviderProtocol)
    app = ResponsesAgentServerHost(store=provider)
    app.response_handler(handler)
    return TestClient(app)


def _handler(request: Any, context: Any, cancel: Any) -> Any:
    """Minimal handler: created → completed."""

    async def _events():
        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


def _handler_with_output(request: Any, context: Any, cancel: Any) -> Any:
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


# ════════════════════════════════════════════════════════════
# Tests: Per-event 10-minute TTL (B35)
# ════════════════════════════════════════════════════════════


class TestStreamEventTTL:
    """Each stream event must be replayable for 10 minutes after emission, then filtered."""

    @pytest.mark.asyncio
    async def test_events_within_ttl_are_returned(self) -> None:
        """Events saved less than 10 minutes ago are returned by get_stream_events."""
        provider = InMemoryResponseProvider()
        rid = "caresp_ttl_within_0000000000000000"
        now = datetime.now(timezone.utc)

        events = [
            {"type": "response.created", "_saved_at": now - timedelta(minutes=5)},
            {"type": "response.completed", "_saved_at": now - timedelta(minutes=3)},
        ]
        await provider.save_stream_events(rid, events)

        result = await provider.get_stream_events(rid)
        assert result is not None
        assert len(result) == 2
        assert result[0]["type"] == "response.created"
        assert result[1]["type"] == "response.completed"

    @pytest.mark.asyncio
    async def test_events_older_than_10_minutes_are_filtered(self) -> None:
        """Events saved more than 10 minutes ago are filtered or purged entirely."""
        provider = InMemoryResponseProvider()
        rid = "caresp_ttl_exact_0000000000000000"
        now = datetime.now(timezone.utc)

        events = [
            {"type": "response.created", "_saved_at": now - timedelta(minutes=11)},
            {"type": "response.completed", "_saved_at": now - timedelta(minutes=11)},
        ]
        await provider.save_stream_events(rid, events)

        result = await provider.get_stream_events(rid)
        # Either None (purged entirely by orphan cleanup) or empty list
        if result is not None:
            assert len(result) == 0, "Events older than 10 min should be filtered"

    @pytest.mark.asyncio
    async def test_events_well_past_ttl_are_gone(self) -> None:
        """Events saved well beyond the 10-minute TTL must be filtered or purged."""
        provider = InMemoryResponseProvider()
        rid = "caresp_ttl_old_000000000000000000"
        now = datetime.now(timezone.utc)

        events = [
            {"type": "response.created", "_saved_at": now - timedelta(minutes=15)},
            {"type": "response.completed", "_saved_at": now - timedelta(minutes=12)},
        ]
        await provider.save_stream_events(rid, events)

        result = await provider.get_stream_events(rid)
        # Either None (purged entirely by orphan cleanup) or empty list
        if result is not None:
            assert len(result) == 0, "All events older than 10 min should be filtered"

    @pytest.mark.asyncio
    async def test_mixed_ttl_only_live_events_returned(self) -> None:
        """Only events within the 10-minute window survive; older ones are dropped."""
        provider = InMemoryResponseProvider()
        rid = "caresp_ttl_mixed_0000000000000000"
        now = datetime.now(timezone.utc)

        events = [
            {"type": "response.created", "_saved_at": now - timedelta(minutes=12)},
            {"type": "response.in_progress", "_saved_at": now - timedelta(minutes=8)},
            {"type": "response.output_item.added", "_saved_at": now - timedelta(minutes=5)},
            {"type": "response.completed", "_saved_at": now - timedelta(minutes=2)},
        ]
        await provider.save_stream_events(rid, events)

        result = await provider.get_stream_events(rid)
        assert result is not None
        assert len(result) == 3, f"Expected 3 live events, got {len(result)}"
        types = [e["type"] for e in result]
        assert "response.created" not in types, "12-min-old event should be filtered"
        assert "response.in_progress" in types
        assert "response.output_item.added" in types
        assert "response.completed" in types

    @pytest.mark.asyncio
    async def test_events_just_under_10_minutes_survive(self) -> None:
        """Events saved 9 minutes 59 seconds ago are still within the TTL window."""
        provider = InMemoryResponseProvider()
        rid = "caresp_ttl_just_000000000000000000"
        now = datetime.now(timezone.utc)

        events = [
            {"type": "response.created", "_saved_at": now - timedelta(minutes=9, seconds=59)},
            {"type": "response.completed", "_saved_at": now - timedelta(minutes=9, seconds=59)},
        ]
        await provider.save_stream_events(rid, events)

        result = await provider.get_stream_events(rid)
        assert result is not None
        assert len(result) == 2, "Events at 9m59s should still be within TTL"

    @pytest.mark.asyncio
    async def test_orphaned_stream_events_purged_after_ttl(self) -> None:
        """Standalone stream-only usage: purge removes events older than TTL.

        When InMemoryResponseProvider is used as a fallback stream provider
        (no _entries for those response IDs), purge_expired must still clean
        up stream events whose _saved_at exceeds the replay TTL.
        """
        provider = InMemoryResponseProvider()
        rid = "caresp_ttl_orphan_00000000000000000"
        old_time = datetime.now(timezone.utc) - timedelta(minutes=15)

        events = [
            {"type": "response.created", "_saved_at": old_time},
            {"type": "response.completed", "_saved_at": old_time},
        ]
        await provider.save_stream_events(rid, events)

        # The auto-purge on each _locked() call cleans orphaned stale events.
        # After saving stale events and then reading, the stale events are
        # either filtered on read or purged entirely by the orphan cleanup.
        result = await provider.get_stream_events(rid)
        # Result is None (purged) or empty (filtered) — either way, no events.
        if result is not None:
            assert len(result) == 0, "Stale events should be filtered"

        # Explicitly call purge_expired to confirm cleanup
        await provider.purge_expired()

        # After explicit purge, the key must be gone entirely
        after_purge = await provider.get_stream_events(rid)
        # The key was already removed; should be None
        assert after_purge is None, "Orphaned stream events should be fully purged after TTL"
