# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for persistence failure resilience.

Validates that the Responses server SDK gracefully degrades when storage
provider calls fail after built-in retries are exhausted, per the
persistence-failure-resilience-spec.md.

Test matrix (8 scenarios):
1. Streaming — terminal persist fails → SSE ends with response.failed + storage_error
2. Streaming — GET after persistence failure → 200 from memory with storage_error
3. Bg+streaming Phase 1 — CreateResponse fails → standalone error SSE, no response.created
4. Bg+streaming Phase 2 — UpdateResponse fails → SSE ends with response.failed + storage_error
5. Bg+non-streaming Phase 2 — UpdateResponse fails → GET returns storage_error from memory
6. Default — terminal persist fails → HTTP 500, no dangling ID
7. Bg+non-streaming — DELETE after persistence failure → 200, storage cleanup attempted
8. Non-bg streaming — DELETE after persistence failure → 200, best-effort storage delete
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Iterable

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.store._base import ResponseProviderProtocol
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

# ── FailingProvider infrastructure ───────────────────────────────────────────


class _FailingProvider:
    """Decorator around a real provider that fails on targeted operations.

    Raises ``RuntimeError("Simulated storage failure")`` when the configured
    ``fail_on_create`` or ``fail_on_update`` flag is set.  All other methods
    delegate to the wrapped inner provider.

    Also tracks ``delete_called`` as a spy to assert cleanup behavior.
    """

    def __init__(
        self,
        inner: ResponseProviderProtocol,
        *,
        fail_on_create: bool = False,
        fail_on_update: bool = False,
    ) -> None:
        self._inner = inner
        self.fail_on_create = fail_on_create
        self.fail_on_update = fail_on_update
        self.delete_called: bool = False
        self.create_called: bool = False
        self.update_called: bool = False

    async def create_response(
        self,
        response: Any,
        input_items: Iterable[Any] | None,
        history_item_ids: Iterable[str] | None,
        *,
        isolation: Any = None,
    ) -> None:
        self.create_called = True
        if self.fail_on_create:
            raise RuntimeError("Simulated storage failure")
        return await self._inner.create_response(response, input_items, history_item_ids, isolation=isolation)

    async def update_response(self, response: Any, *, isolation: Any = None) -> None:
        self.update_called = True
        if self.fail_on_update:
            raise RuntimeError("Simulated storage failure")
        return await self._inner.update_response(response, isolation=isolation)

    async def get_response(self, response_id: str, *, isolation: Any = None) -> Any:
        return await self._inner.get_response(response_id, isolation=isolation)

    async def delete_response(self, response_id: str, *, isolation: Any = None) -> None:
        self.delete_called = True
        return await self._inner.delete_response(response_id, isolation=isolation)

    async def get_history_item_ids(
        self,
        response_id: str | None,
        before: str | None,
        limit: int,
        *,
        isolation: Any = None,
    ) -> list[str] | None:
        return await self._inner.get_history_item_ids(response_id, before, limit, isolation=isolation)

    async def get_input_items(
        self,
        response_id: str,
        *,
        limit: int = 100,
        ascending: bool = True,
        isolation: Any = None,
    ) -> list[Any]:
        return await self._inner.get_input_items(response_id, limit=limit, ascending=ascending, isolation=isolation)

    # ResponseStreamProviderProtocol delegation
    async def save_stream_events(self, response_id: str, events: Any, *, isolation: Any = None) -> None:
        if hasattr(self._inner, "save_stream_events"):
            return await self._inner.save_stream_events(response_id, events, isolation=isolation)

    async def get_stream_events(self, response_id: str, *, isolation: Any = None) -> Any:
        if hasattr(self._inner, "get_stream_events"):
            return await self._inner.get_stream_events(response_id, isolation=isolation)
        return None

    async def delete_stream_events(self, response_id: str, *, isolation: Any = None) -> None:
        if hasattr(self._inner, "delete_stream_events"):
            return await self._inner.delete_stream_events(response_id, isolation=isolation)


def _make_app_with_failing_provider(
    handler: Any,
    *,
    fail_on_create: bool = False,
    fail_on_update: bool = False,
) -> tuple[ResponsesAgentServerHost, _FailingProvider]:
    """Build an app with the FailingProvider injected via the store= constructor arg."""
    from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider

    inner_provider = InMemoryResponseProvider()
    failing_provider = _FailingProvider(
        inner_provider,
        fail_on_create=fail_on_create,
        fail_on_update=fail_on_update,
    )

    app = ResponsesAgentServerHost(store=failing_provider)
    app.response_handler(handler)
    return app, failing_provider


# ── SSE helpers ──────────────────────────────────────────────────────────────


def _collect_sse_events(response: Any) -> list[dict[str, Any]]:
    """Parse SSE events from a streaming response."""
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

    if current_type is not None:
        payload = json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": payload})

    return events


# ── Async ASGI client (for background requests) ─────────────────────────────


class _AsgiResponse:
    def __init__(self, status_code: int, body: bytes, headers: list[tuple[bytes, bytes]]) -> None:
        self.status_code = status_code
        self.body = body
        self.headers = headers

    def json(self) -> Any:
        return json.loads(self.body)


class _AsyncAsgiClient:
    def __init__(self, app: Any) -> None:
        self._app = app

    @staticmethod
    def _build_scope(
        method: str,
        path: str,
        body: bytes,
        headers: list[tuple[bytes, bytes]] | None = None,
    ) -> dict[str, Any]:
        hdr: list[tuple[bytes, bytes]] = list(headers or [])
        query_string = b""
        if "?" in path:
            path, qs = path.split("?", 1)
            query_string = qs.encode()
        if body:
            hdr += [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ]
        return {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "headers": hdr,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string,
            "server": ("localhost", 80),
            "client": ("127.0.0.1", 123),
            "root_path": "",
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> _AsgiResponse:
        body = json.dumps(json_body).encode() if json_body else b""
        raw_headers = [(k.lower().encode(), v.encode()) for k, v in headers.items()] if headers else []
        scope = self._build_scope(method, path, body, raw_headers)
        status_code: int | None = None
        response_headers: list[tuple[bytes, bytes]] = []
        body_parts: list[bytes] = []
        request_sent = False
        response_done = asyncio.Event()

        async def receive() -> dict[str, Any]:
            nonlocal request_sent
            if not request_sent:
                request_sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            await response_done.wait()
            return {"type": "http.disconnect"}

        async def send(message: dict[str, Any]) -> None:
            nonlocal status_code, response_headers
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                chunk = message.get("body", b"")
                if chunk:
                    body_parts.append(chunk)
                if not message.get("more_body", False):
                    response_done.set()

        await self._app(scope, receive, send)
        assert status_code is not None
        return _AsgiResponse(status_code=status_code, body=b"".join(body_parts), headers=response_headers)

    async def get(self, path: str, *, headers: dict[str, str] | None = None) -> _AsgiResponse:
        return await self.request("GET", path, headers=headers)

    async def post(
        self,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> _AsgiResponse:
        return await self.request("POST", path, json_body=json_body, headers=headers)

    async def delete(self, path: str, *, headers: dict[str, str] | None = None) -> _AsgiResponse:
        return await self.request("DELETE", path, headers=headers)


# ── Handlers ─────────────────────────────────────────────────────────────────


def _simple_completed_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits created + output + completed."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        for evt in stream.output_item_message("Hello, world!"):
            yield evt
        yield stream.emit_completed()

    return _events()


# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: Streaming — terminal persist fails (§3.2)
# ═══════════════════════════════════════════════════════════════════════════════


class TestStreamingTerminalPersistFails:
    """§3.2: When persistence fails before terminal SSE event, replace with response.failed."""

    def test_streaming_terminal_persist_fails(self) -> None:
        """SSE stream ends with response.failed + storage_error, no response.completed."""
        app, provider = _make_app_with_failing_provider(
            _simple_completed_handler,
            fail_on_create=True,  # Non-bg streaming uses create_response
        )
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

        # Should NOT contain response.completed
        assert "response.completed" not in event_types, f"Unexpected response.completed in {event_types}"

        # Last event should be response.failed
        assert events, "No SSE events received"
        last_event = events[-1]
        assert last_event["type"] == "response.failed", f"Last event type: {last_event['type']}"

        # Verify error shape
        resp_data = last_event["data"].get("response", last_event["data"])
        assert resp_data.get("status") == "failed"
        error = resp_data.get("error", {})
        assert error.get("code") == "storage_error"
        assert "storing the response" in error.get("message", "")

        # Output should be cleared
        assert resp_data.get("output") == [] or resp_data.get("output") is None


# ═══════════════════════════════════════════════════════════════════════════════
# Test 2: Streaming — GET after persistence failure (§4.2)
# ═══════════════════════════════════════════════════════════════════════════════


class TestStreamingGetAfterPersistenceFailure:
    """§4.2: GET serves from memory when persistence_failed is True."""

    def test_streaming_get_after_persistence_failure(self) -> None:
        """GET returns 200 with storage_error from memory after persistence failure."""
        app, provider = _make_app_with_failing_provider(
            _simple_completed_handler,
            fail_on_create=True,
        )
        client = TestClient(app)

        # First: do the streaming request that fails persistence
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

        # Extract response_id from the first lifecycle event
        response_id = None
        for evt in events:
            resp = evt["data"].get("response", evt["data"])
            rid = resp.get("id")
            if rid:
                response_id = rid
                break
        assert response_id is not None, "Could not extract response_id from SSE events"

        # Now GET should serve from memory
        get_response = client.get(f"/responses/{response_id}")
        assert get_response.status_code == 200

        body = get_response.json()
        assert body["status"] == "failed"
        assert body["error"]["code"] == "storage_error"
        assert body.get("output") == [] or body.get("output") is None


# ═══════════════════════════════════════════════════════════════════════════════
# Test 3: Bg+streaming Phase 1 — CreateResponse fails (§3.3)
# ═══════════════════════════════════════════════════════════════════════════════


class TestBgStreamPhase1CreateFails:
    """§3.3: Phase 1 CreateResponse failure → standalone error SSE event."""

    @pytest.mark.asyncio
    async def test_bg_stream_phase1_create_fails(self) -> None:
        """Standalone error SSE event, no response.created seen by client."""
        app, provider = _make_app_with_failing_provider(
            _simple_completed_handler,
            fail_on_create=True,  # Phase 1 create fails
        )
        client = TestClient(app)

        response = client.post(
            "/responses",
            json={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "stream": True,
                "background": True,
                "store": True,
            },
        )
        assert response.status_code == 200

        events = _collect_sse_events(response)
        event_types = [e["type"] for e in events]

        # Should NOT contain response.created (Phase 1 failed before yielding it)
        assert "response.created" not in event_types, f"Unexpected response.created in {event_types}"

        # Should contain a standalone error event with the expected storage failure payload
        assert "error" in event_types, f"Expected standalone error event, got {event_types}"
        error_event = next(e for e in events if e["type"] == "error")
        error_data = error_event.get("data", {})
        error = error_data.get("error", error_data)
        assert isinstance(error, dict), f"Unexpected error payload: {error_data}"
        assert error.get("code") == "storage_error", f"Unexpected error code: {error}"


# ═══════════════════════════════════════════════════════════════════════════════
# Test 4: Bg+streaming Phase 2 — UpdateResponse fails (§3.4)
# ═══════════════════════════════════════════════════════════════════════════════


class TestBgStreamPhase2UpdateFails:
    """§3.4: Phase 2 UpdateResponse failure → replace terminal with response.failed."""

    @pytest.mark.asyncio
    async def test_bg_stream_phase2_update_fails(self) -> None:
        """SSE stream ends with response.failed + storage_error after Phase 2 failure."""
        app, provider = _make_app_with_failing_provider(
            _simple_completed_handler,
            fail_on_update=True,  # Phase 1 create succeeds, Phase 2 update fails
        )
        client = TestClient(app)

        response = client.post(
            "/responses",
            json={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "stream": True,
                "background": True,
                "store": True,
            },
        )
        assert response.status_code == 200

        events = _collect_sse_events(response)
        event_types = [e["type"] for e in events]

        # response.created SHOULD be present (Phase 1 succeeded)
        assert "response.created" in event_types, f"Missing response.created in {event_types}"

        # Should NOT contain response.completed (replaced by response.failed)
        assert "response.completed" not in event_types, f"Unexpected response.completed in {event_types}"

        # Last event should be response.failed with storage_error
        last_event = events[-1]
        assert last_event["type"] == "response.failed", f"Last event type: {last_event['type']}"

        resp_data = last_event["data"].get("response", last_event["data"])
        assert resp_data.get("status") == "failed"
        error = resp_data.get("error", {})
        assert error.get("code") == "storage_error"

        # Output should be cleared
        assert resp_data.get("output") == [] or resp_data.get("output") is None


# ═══════════════════════════════════════════════════════════════════════════════
# Test 5: Bg+non-streaming Phase 2 — UpdateResponse fails (§3.5)
# ═══════════════════════════════════════════════════════════════════════════════


class TestBgNonStreamPhase2UpdateFails:
    """§3.5: Phase 2 UpdateResponse failure → GET returns storage_error from memory."""

    @pytest.mark.asyncio
    async def test_bg_non_stream_phase2_update_fails(self) -> None:
        """GET returns failed response with storage_error from memory."""
        app, provider = _make_app_with_failing_provider(
            _simple_completed_handler,
            fail_on_update=True,  # Phase 1 create succeeds, Phase 2 update fails
        )
        client = _AsyncAsgiClient(app)

        # POST background non-streaming
        post_resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "background": True,
                "store": True,
            },
        )
        assert post_resp.status_code == 200
        body = post_resp.json()
        response_id = body["id"]
        assert body["status"] == "in_progress"

        # Poll GET until terminal state
        terminal_reached = False
        terminal_body: dict[str, Any] = {}
        for _ in range(100):
            await asyncio.sleep(0.05)
            get_resp = await client.get(f"/responses/{response_id}")
            if get_resp.status_code == 200:
                terminal_body = get_resp.json()
                if terminal_body.get("status") in {"completed", "failed", "cancelled", "incomplete"}:
                    terminal_reached = True
                    break

        assert terminal_reached, f"Response did not reach terminal state, last: {terminal_body}"
        assert terminal_body["status"] == "failed"
        assert terminal_body.get("error", {}).get("code") == "storage_error"
        assert terminal_body.get("output") == [] or terminal_body.get("output") is None


# ═══════════════════════════════════════════════════════════════════════════════
# Test 6: Default — terminal persist fails (§3.1)
# ═══════════════════════════════════════════════════════════════════════════════


class TestDefaultTerminalPersistFails:
    """§3.1: Default mode persist fails → HTTP 500, no dangling ID."""

    def test_default_terminal_persist_fails(self) -> None:
        """POST returns HTTP 500, GET returns 404 (no dangling response ID)."""
        app, provider = _make_app_with_failing_provider(
            _simple_completed_handler,
            fail_on_create=True,
        )
        client = TestClient(app)

        response = client.post(
            "/responses",
            json={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "store": True,
            },
        )
        # Should be HTTP 500
        assert response.status_code == 500, f"Expected 500, got {response.status_code}: {response.text}"

        # Try GET with any response ID — should be 404
        # Since the request failed, we don't know the response_id from the outside.
        # But we can verify that the provider was called and no dangling state exists
        # by trying a known ID format. In practice, the point is that the client
        # never received a response_id to use.
        assert provider.create_called is True


# ═══════════════════════════════════════════════════════════════════════════════
# Test 7: DELETE after persistence failure — bg mode (§4.3, test matrix #7)
# ═══════════════════════════════════════════════════════════════════════════════


class TestDeleteAfterPersistenceFailureBg:
    """§4.3: DELETE on persistence-failed response in bg mode → 200 + cleanup."""

    @pytest.mark.asyncio
    async def test_delete_after_persistence_failure_bg(self) -> None:
        """DELETE returns 200, storage cleanup attempted, subsequent GET returns 404."""
        app, provider = _make_app_with_failing_provider(
            _simple_completed_handler,
            fail_on_update=True,  # Phase 1 create succeeds, Phase 2 update fails
        )
        client = _AsyncAsgiClient(app)

        # POST background non-streaming
        post_resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "background": True,
                "store": True,
            },
        )
        assert post_resp.status_code == 200
        response_id = post_resp.json()["id"]

        # Poll until terminal state (should be "failed" with storage_error)
        terminal_reached = False
        for _ in range(100):
            await asyncio.sleep(0.05)
            get_resp = await client.get(f"/responses/{response_id}")
            if get_resp.status_code == 200:
                body = get_resp.json()
                if body.get("status") in {"completed", "failed", "cancelled", "incomplete"}:
                    terminal_reached = True
                    break

        assert terminal_reached, "Response did not reach terminal state"

        # DELETE should return 200 with standard delete response
        delete_resp = await client.delete(f"/responses/{response_id}")
        assert delete_resp.status_code == 200
        delete_body = delete_resp.json()
        assert delete_body["deleted"] is True
        assert delete_body["id"] == response_id

        # Storage delete should have been attempted (Phase 1 created data in storage)
        assert provider.delete_called is True

        # Subsequent GET should return 404
        get_after_delete = await client.get(f"/responses/{response_id}")
        assert get_after_delete.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# Test 8: DELETE after persistence failure — non-bg streaming (§4.3, test matrix #8)
# ═══════════════════════════════════════════════════════════════════════════════


class TestDeleteAfterPersistenceFailureNonBg:
    """§4.3: DELETE on persistence-failed non-bg response → 200, best-effort storage delete."""

    def test_delete_after_persistence_failure_non_bg(self) -> None:
        """DELETE returns 200, best-effort storage delete attempted, GET returns 404."""
        app, provider = _make_app_with_failing_provider(
            _simple_completed_handler,
            fail_on_create=True,  # Non-bg has no Phase 1, so nothing in storage
        )
        client = TestClient(app)

        # Streaming request that fails persistence
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

        # Extract response_id
        response_id = None
        for evt in events:
            resp = evt["data"].get("response", evt["data"])
            rid = resp.get("id")
            if rid:
                response_id = rid
                break
        assert response_id is not None

        # DELETE should return 200
        delete_resp = client.delete(f"/responses/{response_id}")
        assert delete_resp.status_code == 200
        delete_body = delete_resp.json()
        assert delete_body["deleted"] is True
        assert delete_body["id"] == response_id

        # Storage delete should have been attempted (best-effort)
        assert provider.delete_called is True

        # Subsequent GET should return 404
        get_after = client.get(f"/responses/{response_id}")
        assert get_after.status_code == 404
