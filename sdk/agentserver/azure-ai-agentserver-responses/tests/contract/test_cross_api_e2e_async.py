# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Cross-API E2E tests requiring concurrent HTTP operations during active handlers.

These tests use a lightweight async ASGI client that invokes the Starlette app
directly via ``await app(scope, receive, send)``, combined with
``asyncio.create_task`` for concurrency.  This enables:

* Issuing GET / Cancel requests while a streaming POST handler is still running.
* Using ``asyncio.Event`` for deterministic handler gating (same event loop).
* Pre-generating response IDs via ``IdGenerator`` to avoid parsing the SSE stream.

Tests validate: E8, E11, E20, E25, E43 from the cross-API matrix.

**Parallel-safety:** every test creates its own Starlette app, ASGI client, and
handler instances — fully isolated with no shared state, no port binding, and no
global singletons.  Safe for ``pytest-xdist`` and any concurrent test runner.
"""

from __future__ import annotations

import asyncio
import json as _json
from typing import Any

import pytest
from azure.ai.agentserver.core import AgentHost
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.hosting import ResponseHandler
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream


# ════════════════════════════════════════════════════════════
# Lightweight async ASGI test client
# ════════════════════════════════════════════════════════════


class _AsgiResponse:
    """Result of a non-streaming ASGI request."""

    def __init__(self, status_code: int, body: bytes, headers: list[tuple[bytes, bytes]]) -> None:
        self.status_code = status_code
        self.body = body
        self.headers = headers

    def json(self) -> Any:
        return _json.loads(self.body)


class _AsyncAsgiClient:
    """Minimal async ASGI client that supports concurrent in-flight requests.

    Unlike ``httpx.ASGITransport`` (which buffers the entire response body before
    returning) or Starlette ``TestClient`` (synchronous), this client calls the
    ASGI app directly.  Combined with ``asyncio.create_task``, the test can issue
    additional requests while a previous one is still being processed.

    **Thread-safety:**  instances are NOT thread-safe.  Each test should create
    its own client via ``_build_client()``.
    """

    def __init__(self, app: Any) -> None:
        self._app = app

    # ── helpers ──────────────────────────────────────────────

    @staticmethod
    def _build_scope(method: str, path: str, body: bytes) -> dict[str, Any]:
        headers: list[tuple[bytes, bytes]] = []
        query_string = b""

        if "?" in path:
            path, qs = path.split("?", 1)
            query_string = qs.encode()

        if body:
            headers = [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ]

        return {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "headers": headers,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string,
            "server": ("localhost", 80),
            "client": ("127.0.0.1", 123),
            "root_path": "",
        }

    # ── public API ──────────────────────────────────────────

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
    ) -> _AsgiResponse:
        """Send a request and collect the full response."""
        body = _json.dumps(json_body).encode() if json_body else b""
        scope = self._build_scope(method, path, body)

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
        return _AsgiResponse(
            status_code=status_code,
            body=b"".join(body_parts),
            headers=response_headers,
        )

    async def get(self, path: str) -> _AsgiResponse:
        return await self.request("GET", path)

    async def post(
        self, path: str, *, json_body: dict[str, Any] | None = None
    ) -> _AsgiResponse:
        return await self.request("POST", path, json_body=json_body)


# ════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════


def _build_client(handler: Any) -> _AsyncAsgiClient:
    """Create a fully isolated async ASGI client."""
    server = AgentHost()
    responses = ResponseHandler(server)
    responses.create_handler(handler)
    return _AsyncAsgiClient(server.app)


async def _ensure_task_done(
    task: asyncio.Task[Any],
    handler: Any,
    timeout: float = 5.0,
) -> None:
    """Release handler gates and await the task with a timeout."""
    # Release all asyncio.Event gates on the handler so it can exit.
    for attr in vars(handler):
        obj = getattr(handler, attr, None)
        if isinstance(obj, asyncio.Event):
            obj.set()
    if not task.done():
        try:
            await asyncio.wait_for(task, timeout=timeout)
        except (asyncio.TimeoutError, Exception):
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass


def _parse_sse_events(text: str) -> list[dict[str, Any]]:
    """Parse SSE events from raw text."""
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None

    for line in text.splitlines():
        if not line:
            if current_type is not None:
                payload = _json.loads(current_data) if current_data else {}
                events.append({"type": current_type, "data": payload})
            current_type = None
            current_data = None
            continue

        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()

    if current_type is not None:
        payload = _json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": payload})

    return events


# ════════════════════════════════════════════════════════════
# Handler factories  (asyncio.Event gating — same event loop as test)
# ════════════════════════════════════════════════════════════


def _make_gated_stream_handler():
    """Factory for a handler that emits created + in_progress, then blocks until ``release`` is set."""
    started = asyncio.Event()
    release = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            yield stream.emit_in_progress()
            started.set()
            while not release.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)
            yield stream.emit_completed()

        return _events()

    handler.started = started  # type: ignore[attr-defined]
    handler.release = release  # type: ignore[attr-defined]
    return handler


def _make_gated_stream_handler_with_output():
    """Factory for a handler that emits created + in_progress + a partial message, then blocks."""
    started = asyncio.Event()
    release = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
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
            yield text.emit_delta("Hello")

            started.set()
            while not release.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)

            yield text.emit_done()
            yield message.emit_content_done(text)
            yield message.emit_done()
            yield stream.emit_completed()

        return _events()

    handler.started = started  # type: ignore[attr-defined]
    handler.release = release  # type: ignore[attr-defined]
    return handler


# ════════════════════════════════════════════════════════════
# C2 — Sync streaming, stored: E8, E11
# ════════════════════════════════════════════════════════════


class TestC2StreamStoredAsync:
    """Sync streaming tests requiring concurrent access during an active stream."""

    async def test_e8_stream_get_during_stream_returns_404(self) -> None:
        """B16 — non-bg in-flight → 404."""
        handler = _make_gated_stream_handler()
        client = _build_client(handler)
        response_id = IdGenerator.new_response_id()

        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={
                    "response_id": response_id,
                    "model": "gpt-4o-mini",
                    "input": "hello",
                    "stream": True,
                    "store": True,
                    "background": False,
                },
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)

            # GET during non-bg in-flight → 404
            get_resp = await client.get(f"/responses/{response_id}")
            assert get_resp.status_code == 404

            # Release handler so it can complete
            handler.release.set()
            post_resp = await asyncio.wait_for(post_task, timeout=5.0)
            assert post_resp.status_code == 200
        finally:
            await _ensure_task_done(post_task, handler)

        # After stream ends, response should be stored
        get_after = await client.get(f"/responses/{response_id}")
        assert get_after.status_code == 200
        assert get_after.json()["status"] == "completed"

    async def test_e11_stream_cancel_during_stream_returns_400(self) -> None:
        """B1 — cancel requires background; non-bg → 400."""
        handler = _make_gated_stream_handler()
        client = _build_client(handler)
        response_id = IdGenerator.new_response_id()

        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={
                    "response_id": response_id,
                    "model": "gpt-4o-mini",
                    "input": "hello",
                    "stream": True,
                    "store": True,
                    "background": False,
                },
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)

            # Cancel non-bg in-flight → 404 (not yet stored, S7)
            cancel_resp = await client.post(f"/responses/{response_id}/cancel")
            assert cancel_resp.status_code == 404, "S7: non-background in-flight cancel must return 404 (not yet stored)"

            handler.release.set()
            await asyncio.wait_for(post_task, timeout=5.0)
        finally:
            await _ensure_task_done(post_task, handler)


# ════════════════════════════════════════════════════════════
# C4 — Background streaming, stored: E20, E25, E43
#
# The Python SDK now stores the execution record at response.created
# time for background+stream responses (S-035), enabling mid-stream
# GET, Cancel, and progressive-poll.
# ════════════════════════════════════════════════════════════


class TestC4BgStreamStoredAsync:
    """Background streaming tests requiring concurrent access during active stream."""

    async def test_e20_bg_stream_get_during_stream_returns_in_progress(self) -> None:
        """B5 — background responses accessible during in-progress."""
        handler = _make_gated_stream_handler()
        client = _build_client(handler)
        response_id = IdGenerator.new_response_id()

        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={
                    "response_id": response_id,
                    "model": "gpt-4o-mini",
                    "input": "hello",
                    "stream": True,
                    "store": True,
                    "background": True,
                },
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)

            # GET during bg in-flight → 200 with in_progress
            get_resp = await client.get(f"/responses/{response_id}")
            assert get_resp.status_code == 200
            assert get_resp.json()["status"] == "in_progress"

            handler.release.set()
            post_resp = await asyncio.wait_for(post_task, timeout=5.0)
            assert post_resp.status_code == 200
        finally:
            await _ensure_task_done(post_task, handler)

        # After stream ends, response should be completed
        get_after = await client.get(f"/responses/{response_id}")
        assert get_after.status_code == 200
        assert get_after.json()["status"] == "completed"

    async def test_e25_bg_stream_cancel_mid_stream_returns_cancelled(self) -> None:
        """B7, B11 — cancel mid-stream → cancelled with 0 output."""
        handler = _make_gated_stream_handler()
        client = _build_client(handler)
        response_id = IdGenerator.new_response_id()

        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={
                    "response_id": response_id,
                    "model": "gpt-4o-mini",
                    "input": "hello",
                    "stream": True,
                    "store": True,
                    "background": True,
                },
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)

            # Cancel bg in-flight → 200
            cancel_resp = await client.post(f"/responses/{response_id}/cancel")
            assert cancel_resp.status_code == 200
            snapshot = cancel_resp.json()
            assert snapshot["status"] == "cancelled"
            assert snapshot["output"] == []

            await asyncio.wait_for(post_task, timeout=5.0)
        finally:
            await _ensure_task_done(post_task, handler)

        # GET after cancel → cancelled
        get_resp = await client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "cancelled"
        assert get_resp.json()["output"] == []

    async def test_e43_bg_stream_get_during_stream_returns_partial_output(self) -> None:
        """B5, B23 — GET mid-stream returns partial output items."""
        handler = _make_gated_stream_handler_with_output()
        client = _build_client(handler)
        response_id = IdGenerator.new_response_id()

        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={
                    "response_id": response_id,
                    "model": "gpt-4o-mini",
                    "input": "hello",
                    "stream": True,
                    "store": True,
                    "background": True,
                },
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)

            # GET during bg in-flight → 200 with in_progress and partial output
            get_resp = await client.get(f"/responses/{response_id}")
            assert get_resp.status_code == 200
            body = get_resp.json()
            assert body["status"] == "in_progress"
            # The response should have at least one output item from the
            # output_item.added event emitted before the gate.
            assert len(body.get("output", [])) >= 1

            handler.release.set()
            post_resp = await asyncio.wait_for(post_task, timeout=5.0)
            assert post_resp.status_code == 200
        finally:
            await _ensure_task_done(post_task, handler)

        # After completion, full output should be present
        get_after = await client.get(f"/responses/{response_id}")
        assert get_after.status_code == 200
        assert get_after.json()["status"] == "completed"

    async def test_bg_stream_cancel_terminal_sse_is_response_failed_with_cancelled(self) -> None:
        """B11, B26 — cancel mid-stream → terminal SSE event is response.failed with status cancelled."""
        handler = _make_gated_stream_handler()
        client = _build_client(handler)
        response_id = IdGenerator.new_response_id()

        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={
                    "response_id": response_id,
                    "model": "gpt-4o-mini",
                    "input": "hello",
                    "stream": True,
                    "store": True,
                    "background": True,
                },
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)

            # Cancel bg in-flight → 200
            cancel_resp = await client.post(f"/responses/{response_id}/cancel")
            assert cancel_resp.status_code == 200

            post_resp = await asyncio.wait_for(post_task, timeout=5.0)
            assert post_resp.status_code == 200

            # Parse SSE events from the response body
            events = _parse_sse_events(post_resp.body.decode())

            # Find terminal events
            terminal_types = {"response.completed", "response.failed", "response.incomplete"}
            terminal_events = [e for e in events if e["type"] in terminal_types]
            assert len(terminal_events) == 1, (
                f"Expected exactly one terminal event, got: {[e['type'] for e in terminal_events]}"
            )

            terminal = terminal_events[0]
            # B26: cancelled responses emit response.failed
            assert terminal["type"] == "response.failed", (
                f"Expected response.failed for cancel per B26, got: {terminal['type']}"
            )
            # B11: status inside is "cancelled"
            assert terminal["data"]["response"].get("status") == "cancelled"
            # B11: output cleared
            assert terminal["data"]["response"].get("output") == []
        finally:
            await _ensure_task_done(post_task, handler)
