# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract test: isolation keys propagate to update_response in bg non-stream finalization.

When a background non-stream response is created with isolation headers
(``x-agent-user-isolation-key`` / ``x-agent-chat-isolation-key``), the
finalization ``update_response`` call in :func:`_run_background_non_stream`
must forward the same isolation context.  A missing ``isolation=`` kwarg
causes Foundry storage to return 404 (response exists in a different
partition) and the response is stuck at ``in_progress`` forever.

Regression test for: missing isolation on update_response in
_run_background_non_stream finally block.
"""

from __future__ import annotations

from typing import Any, Iterable

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._response_context import IsolationContext
from azure.ai.agentserver.responses.models._generated import OutputItem, ResponseObject
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming import ResponseEventStream
from tests._helpers import poll_until


# ─── Recording provider ───────────────────────────────────

class _RecordingProvider:
    """Wraps InMemoryResponseProvider and records isolation kwargs on every call."""

    def __init__(self) -> None:
        self._inner = InMemoryResponseProvider()
        self.create_calls: list[IsolationContext | None] = []
        self.update_calls: list[IsolationContext | None] = []

    async def create_response(
        self,
        response: ResponseObject,
        input_items: Iterable[OutputItem] | None,
        history_item_ids: Iterable[str] | None,
        *,
        isolation: Any = None,
    ) -> None:
        self.create_calls.append(isolation)
        await self._inner.create_response(response, input_items, history_item_ids, isolation=isolation)

    async def get_response(self, response_id: str, *, isolation: Any = None) -> ResponseObject:
        return await self._inner.get_response(response_id, isolation=isolation)

    async def update_response(self, response: ResponseObject, *, isolation: Any = None) -> None:
        self.update_calls.append(isolation)
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
        return await self._inner.get_history_item_ids(
            previous_response_id, conversation_id, limit, isolation=isolation
        )


# ─── Handler ──────────────────────────────────────────────

def _simple_handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
    """Handler that emits created → completed."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


# ─── Helpers ──────────────────────────────────────────────

def _build_client(provider: _RecordingProvider) -> TestClient:
    app = ResponsesAgentServerHost(store=provider)
    app.response_handler(_simple_handler)
    return TestClient(app)


def _wait_for_terminal(client: TestClient, response_id: str, headers: dict[str, str]) -> dict[str, Any]:
    latest: dict[str, Any] = {}

    def _is_terminal() -> bool:
        nonlocal latest
        r = client.get(f"/responses/{response_id}", headers=headers)
        if r.status_code != 200:
            return False
        latest = r.json()
        return latest.get("status") in {"completed", "failed", "incomplete", "cancelled"}

    ok, failure = poll_until(
        _is_terminal,
        timeout_s=5.0,
        interval_s=0.05,
        label=f"wait_for_terminal({response_id})",
    )
    assert ok, failure
    return latest


# ─── Tests ────────────────────────────────────────────────

class TestBgNonStreamIsolationPropagation:
    """Verify that isolation keys reach update_response during bg non-stream finalization."""

    def test_update_response_receives_isolation_with_both_keys(self) -> None:
        """Both user and chat isolation keys must be forwarded to update_response."""
        provider = _RecordingProvider()
        client = _build_client(provider)

        headers = {
            "x-agent-user-isolation-key": "user_123",
            "x-agent-chat-isolation-key": "chat_456",
        }
        r = client.post(
            "/responses",
            json={"model": "m", "input": "hi", "stream": False, "store": True, "background": True},
            headers=headers,
        )
        assert r.status_code == 200
        response_id = r.json()["id"]

        _wait_for_terminal(client, response_id, headers=headers)

        # FR-003: create_response at response.created time should have isolation
        assert len(provider.create_calls) >= 1
        create_iso = provider.create_calls[0]
        assert isinstance(create_iso, IsolationContext)
        assert create_iso.user_key == "user_123"
        assert create_iso.chat_key == "chat_456"

        # Finalization: update_response must also have isolation
        assert len(provider.update_calls) >= 1, "update_response was never called"
        update_iso = provider.update_calls[0]
        assert update_iso is not None, "update_response called without isolation (was None)"
        assert isinstance(update_iso, IsolationContext)
        assert update_iso.user_key == "user_123"
        assert update_iso.chat_key == "chat_456"

    def test_update_response_receives_isolation_with_user_key_only(self) -> None:
        """Only user isolation key — should still propagate."""
        provider = _RecordingProvider()
        client = _build_client(provider)

        headers = {"x-agent-user-isolation-key": "user_only"}
        r = client.post(
            "/responses",
            json={"model": "m", "input": "hi", "stream": False, "store": True, "background": True},
            headers=headers,
        )
        assert r.status_code == 200
        response_id = r.json()["id"]

        _wait_for_terminal(client, response_id, headers=headers)

        assert len(provider.update_calls) >= 1, "update_response was never called"
        update_iso = provider.update_calls[0]
        assert update_iso is not None
        assert isinstance(update_iso, IsolationContext)
        assert update_iso.user_key == "user_only"

    def test_update_response_without_isolation_headers_passes_none_keys(self) -> None:
        """No isolation headers — isolation context has None keys (but is still passed)."""
        provider = _RecordingProvider()
        client = _build_client(provider)

        r = client.post(
            "/responses",
            json={"model": "m", "input": "hi", "stream": False, "store": True, "background": True},
        )
        assert r.status_code == 200
        response_id = r.json()["id"]

        _wait_for_terminal(client, response_id, headers={})

        assert len(provider.update_calls) >= 1, "update_response was never called"
        update_iso = provider.update_calls[0]
        # Isolation context is passed but keys are None when headers absent
        assert isinstance(update_iso, IsolationContext)
        assert update_iso.user_key is None
        assert update_iso.chat_key is None
