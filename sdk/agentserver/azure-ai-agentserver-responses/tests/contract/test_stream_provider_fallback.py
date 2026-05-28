# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests: SSE replay works even when the response provider lacks stream support.

When the response provider (e.g. FoundryStorageProvider) does NOT implement
``ResponseStreamProviderProtocol``, the host must automatically provision an
in-memory stream provider so that bg+stream SSE replay works after eager eviction.

These tests simulate that scenario by wrapping InMemoryResponseProvider in a
facade that only exposes ``ResponseProviderProtocol``, stripping the stream
methods.
"""

from __future__ import annotations

import json
from typing import Any, Iterable

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
# Facade that strips stream capability
# ────────────────────────────────────────


class _ResponseOnlyProvider:
    """Wraps InMemoryResponseProvider, exposing only ResponseProviderProtocol.

    Deliberately does NOT implement ResponseStreamProviderProtocol so
    that the host must fall back to a separate in-memory stream provider.
    """

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
        return await self._inner.get_input_items(
            response_id,
            limit,
            ascending,
            after,
            before,
            isolation=isolation,
        )

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
        return await self._inner.get_history_item_ids(
            previous_response_id,
            conversation_id,
            limit,
            isolation=isolation,
        )


# ────────────────────────────────────────
# Helpers
# ────────────────────────────────────────


def _build_client(handler: Any) -> TestClient:
    """Build a TestClient whose store only implements ResponseProviderProtocol."""
    provider = _ResponseOnlyProvider()
    # Sanity: confirm the facade is NOT a stream provider
    assert isinstance(provider, ResponseProviderProtocol)
    assert not isinstance(provider, ResponseStreamProviderProtocol)

    app = ResponsesAgentServerHost(store=provider)
    app.response_handler(handler)
    return TestClient(app)


def _handler(request: Any, context: Any, cancel: Any) -> Any:
    """Handler that emits created + completed."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
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


def _create_bg_stream(client: TestClient) -> str:
    """POST bg+stream, consume SSE, return response_id."""
    payload = {"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": True}
    with client.stream("POST", "/responses", json=payload) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)
    assert events, "Expected at least one SSE event"
    return events[0]["data"]["response"]["id"]


# ════════════════════════════════════════════════════════════
# Tests
# ════════════════════════════════════════════════════════════


class TestStreamProviderFallback:
    """SSE replay must work when response provider is NOT a stream provider."""

    def test_sse_replay_after_completion(self) -> None:
        """After completion + eviction, GET ?stream=true returns 200 with events.

        Simulates Foundry: the response provider stores envelopes but not
        stream events.  The host auto-provisions an in-memory stream provider.
        """
        client = _build_client(_handler)
        response_id = _create_bg_stream(client)
        _wait_for_terminal(client, response_id)

        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay_resp:
            assert replay_resp.status_code == 200, f"Expected 200 for SSE replay, got {replay_resp.status_code}"
            replay_events = _collect_sse_events(replay_resp)

        assert len(replay_events) >= 2, f"Expected >= 2 events, got {len(replay_events)}"
        assert replay_events[-1]["type"] == "response.completed"

    def test_replay_returns_200_after_completion(self) -> None:
        """GET ?stream=true returns 200 for replay after terminal state."""
        client = _build_client(_handler)
        response_id = _create_bg_stream(client)
        _wait_for_terminal(client, response_id)

        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay_resp:
            assert replay_resp.status_code == 200

    def test_cursor_replay(self) -> None:
        """starting_after cursor works with the auto-provisioned stream provider."""
        client = _build_client(_handler)
        response_id = _create_bg_stream(client)
        _wait_for_terminal(client, response_id)

        # Full replay
        with client.stream("GET", f"/responses/{response_id}?stream=true") as full_resp:
            full_events = _collect_sse_events(full_resp)

        assert len(full_events) >= 2

        first_seq = full_events[0]["data"]["sequence_number"]

        # Cursor replay — skip first event
        with client.stream("GET", f"/responses/{response_id}?stream=true&starting_after={first_seq}") as cursor_resp:
            assert cursor_resp.status_code == 200
            cursor_events = _collect_sse_events(cursor_resp)

        assert len(cursor_events) == len(full_events) - 1

    def test_delete_cleans_stream_events(self) -> None:
        """DELETE removes stream events from the auto-provisioned stream provider."""
        client = _build_client(_handler)
        response_id = _create_bg_stream(client)
        _wait_for_terminal(client, response_id)

        # Verify replay works before delete
        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay_resp:
            assert replay_resp.status_code == 200

        # Delete
        del_resp = client.delete(f"/responses/{response_id}")
        assert del_resp.status_code == 200

        # After delete → 404 for both the response and its replay stream
        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 404

        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay_resp:
            assert replay_resp.status_code == 404
