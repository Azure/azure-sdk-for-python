# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for eager history-ID prefetch before handler invocation.

When the create request carries ``previous_response_id`` or
``conversation_id``, the endpoint handler now calls
``provider.get_history_item_ids`` **before** invoking the handler so
that a nonexistent reference surfaces as a client-facing error (404).
The fetched IDs are cached and reused by
``ResponseContext.get_history()`` to avoid a redundant provider call.
"""

from __future__ import annotations

from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.store._foundry_errors import FoundryResourceNotFoundError
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming import ResponseEventStream


# ─── Helpers / handlers ──────────────────────────────────────


def _simple_handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
    """Handler that always succeeds, no history access."""

    async def _events():
        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


def _history_reading_handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
    """Handler that awaits ``context.get_history()`` before emitting events."""

    async def _events():
        # Trigger lazy history resolution (should reuse prefetched IDs).
        await context.get_history()

        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


# ─── Tests ────────────────────────────────────────────────


class TestEagerHistoryPrefetchValidation:
    """Verify that invalid conversation references are rejected before
    the handler runs."""

    def test_nonexistent_previous_response_id_returns_404(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """POST with a nonexistent previous_response_id should return
        404 when the provider raises FoundryResourceNotFoundError."""
        provider = InMemoryResponseProvider()
        app = ResponsesAgentServerHost(store=provider)
        app.response_handler(_simple_handler)

        # Monkeypatch the provider to raise FoundryResourceNotFoundError.
        async def _raise_not_found(*args: Any, **kwargs: Any) -> list[str]:
            raise FoundryResourceNotFoundError(
                "Response 'resp_bogus' not found.",
                response_body={
                    "error": {
                        "code": "invalid_request_error",
                        "message": "Response with id 'resp_bogus' not found.",
                        "param": "response_id",
                        "type": "invalid_request_error",
                    }
                },
            )

        monkeypatch.setattr(provider, "get_history_item_ids", _raise_not_found)

        client = TestClient(app)
        bogus_id = IdGenerator.new_response_id()
        r = client.post(
            "/responses",
            json={
                "model": "m",
                "input": "hi",
                "previous_response_id": bogus_id,
            },
        )
        assert r.status_code == 404, f"Expected 404 but got {r.status_code}: {r.text}"
        body = r.json()
        assert "error" in body
        # Foundry error envelope is forwarded as-is.
        assert body["error"]["code"] == "invalid_request_error"
        assert "not found" in body["error"]["message"].lower()

    def test_nonexistent_conversation_id_returns_404(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """POST with a nonexistent conversation_id should return 404
        when the provider raises FoundryResourceNotFoundError."""
        provider = InMemoryResponseProvider()
        app = ResponsesAgentServerHost(store=provider)
        app.response_handler(_simple_handler)

        async def _raise_not_found(*args: Any, **kwargs: Any) -> list[str]:
            raise FoundryResourceNotFoundError(
                "Conversation 'conv_bogus' not found.",
                response_body={
                    "error": {
                        "code": "invalid_request_error",
                        "message": "Conversation with id 'conv_bogus' not found.",
                        "param": "conversation_id",
                        "type": "invalid_request_error",
                    }
                },
            )

        monkeypatch.setattr(provider, "get_history_item_ids", _raise_not_found)

        client = TestClient(app)
        r = client.post(
            "/responses",
            json={
                "model": "m",
                "input": "hi",
                "conversation": {"id": "conv_nonexistent"},
            },
        )
        assert r.status_code == 404, f"Expected 404 but got {r.status_code}: {r.text}"

    def test_storage_error_returns_error_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A non-404 storage error during prefetch should still return
        an error response (not crash)."""
        provider = InMemoryResponseProvider()
        app = ResponsesAgentServerHost(store=provider)
        app.response_handler(_simple_handler)

        async def _raise_generic(*args: Any, **kwargs: Any) -> list[str]:
            raise RuntimeError("storage unavailable")

        monkeypatch.setattr(provider, "get_history_item_ids", _raise_generic)

        client = TestClient(app)
        bogus_id = IdGenerator.new_response_id()
        r = client.post(
            "/responses",
            json={
                "model": "m",
                "input": "hi",
                "previous_response_id": bogus_id,
            },
        )
        # Should not crash — returns a structured error response.
        assert r.status_code in (400, 500), f"Unexpected status {r.status_code}: {r.text}"
        body = r.json()
        assert "error" in body


class TestEagerHistoryPrefetchReuse:
    """Verify that prefetched IDs are reused by ResponseContext.get_history()."""

    def test_get_history_reuses_prefetched_ids(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When get_history() is called by the handler, it should NOT
        call get_history_item_ids again — the eagerly-prefetched IDs
        should be reused.

        Uses store=False to isolate the handler path from the
        orchestrator's persistence path (which makes its own call).
        """
        provider = InMemoryResponseProvider()
        app = ResponsesAgentServerHost(store=provider)
        app.response_handler(_history_reading_handler)
        client = TestClient(app)

        # Turn 1: create a response to chain against.
        t1 = client.post(
            "/responses",
            json={"model": "m", "input": "Hello", "store": True},
        )
        assert t1.status_code == 200
        t1_id = t1.json()["id"]

        # Wrap provider to count get_history_item_ids calls.
        call_count = 0
        original = provider.get_history_item_ids

        async def _counting_wrapper(*args: Any, **kwargs: Any) -> list[str]:
            nonlocal call_count
            call_count += 1
            return await original(*args, **kwargs)

        monkeypatch.setattr(provider, "get_history_item_ids", _counting_wrapper)

        # Turn 2: chain via previous_response_id — handler calls get_history().
        # store=False so the orchestrator persistence path does not make
        # its own get_history_item_ids call, isolating the handler path.
        t2 = client.post(
            "/responses",
            json={
                "model": "m",
                "input": "Follow-up",
                "previous_response_id": t1_id,
                "store": False,
            },
        )
        assert t2.status_code == 200, f"Chain response failed: {t2.text}"

        # get_history_item_ids should be called exactly once (eager prefetch).
        # The handler's get_history() should reuse the prefetched IDs.
        assert call_count == 1, (
            f"Expected get_history_item_ids to be called once (eager), "
            f"but called {call_count} times"
        )


class TestEagerHistoryPrefetchSkipped:
    """Verify that the prefetch is skipped when no conversation refs exist."""

    def test_no_prefetch_without_conversation_refs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When neither previous_response_id nor conversation_id is set,
        get_history_item_ids should NOT be called."""
        provider = InMemoryResponseProvider()
        app = ResponsesAgentServerHost(store=provider)
        app.response_handler(_simple_handler)

        call_count = 0

        async def _counting_wrapper(*args: Any, **kwargs: Any) -> list[str]:
            nonlocal call_count
            call_count += 1
            return []

        monkeypatch.setattr(provider, "get_history_item_ids", _counting_wrapper)

        client = TestClient(app)
        r = client.post(
            "/responses",
            json={"model": "m", "input": "hi"},
        )
        assert r.status_code == 200
        assert call_count == 0, (
            f"get_history_item_ids should not be called without conversation refs, "
            f"but called {call_count} times"
        )
