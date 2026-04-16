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

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._id_generator import IdGenerator
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

    async def post(self, path: str, *, json_body: dict[str, Any] | None = None) -> _AsgiResponse:
        return await self.request("POST", path, json_body=json_body)


# ════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════


def _build_client(handler: Any) -> _AsyncAsgiClient:
    """Create a fully isolated async ASGI client."""
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    return _AsyncAsgiClient(app)


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

            yield text.emit_text_done()
            yield text.emit_done()
            yield message.emit_done()
            yield stream.emit_completed()

        return _events()

    handler.started = started  # type: ignore[attr-defined]
    handler.release = release  # type: ignore[attr-defined]
    return handler


def _make_item_lifecycle_gated_handler():
    """Factory for ItemLifecycleGatedStream.

    Emits two message output items with fine-grained gates:
    - item_added: fires after first item emit_added (item in_progress, empty content)
    - item_done: fires after first item emit_done (item completed, text="Hello")
    - item2_done: fires after second item emit_done (2 completed items)

    Each gate has a corresponding ``_checked`` event that the test must set
    to let the handler continue.
    """
    item_added = asyncio.Event()
    item_added_checked = asyncio.Event()
    item_done = asyncio.Event()
    item_done_checked = asyncio.Event()
    item2_done = asyncio.Event()
    item2_done_checked = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            yield stream.emit_in_progress()

            # First item — gate after Added (in_progress, empty content)
            msg1 = stream.add_output_item_message()
            yield msg1.emit_added()

            item_added.set()
            while not item_added_checked.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)

            # Continue to completion of first item
            text1 = msg1.add_text_content()
            yield text1.emit_added()
            yield text1.emit_delta("Hello")
            yield text1.emit_text_done()
            yield text1.emit_done()
            yield msg1.emit_done()

            item_done.set()
            while not item_done_checked.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)

            # Second item — emit fully, gate after Done
            msg2 = stream.add_output_item_message()
            yield msg2.emit_added()
            text2 = msg2.add_text_content()
            yield text2.emit_added()
            yield text2.emit_delta("World")
            yield text2.emit_text_done()
            yield text2.emit_done()
            yield msg2.emit_done()

            item2_done.set()
            while not item2_done_checked.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)

            yield stream.emit_completed()

        return _events()

    handler.item_added = item_added  # type: ignore[attr-defined]
    handler.item_added_checked = item_added_checked  # type: ignore[attr-defined]
    handler.item_done = item_done  # type: ignore[attr-defined]
    handler.item_done_checked = item_done_checked  # type: ignore[attr-defined]
    handler.item2_done = item2_done  # type: ignore[attr-defined]
    handler.item2_done_checked = item2_done_checked  # type: ignore[attr-defined]
    return handler


def _make_two_item_gated_bg_handler():
    """Factory for TwoItemGatedStream for progressive polling (E44).

    Emits two message output items with gates between them:
    - item1_emitted: fires after first item is fully done (completed with text="Hello")
    - item2_emitted: fires after second item is fully done (completed with text="World")

    Each gate has a corresponding ``_checked`` event the test must set.
    """
    item1_emitted = asyncio.Event()
    item1_checked = asyncio.Event()
    item2_emitted = asyncio.Event()
    item2_checked = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            yield stream.emit_in_progress()

            # First message output item
            msg1 = stream.add_output_item_message()
            yield msg1.emit_added()
            text1 = msg1.add_text_content()
            yield text1.emit_added()
            yield text1.emit_delta("Hello")
            yield text1.emit_text_done()
            yield text1.emit_done()
            yield msg1.emit_done()

            item1_emitted.set()
            while not item1_checked.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)

            # Second message output item
            msg2 = stream.add_output_item_message()
            yield msg2.emit_added()
            text2 = msg2.add_text_content()
            yield text2.emit_added()
            yield text2.emit_delta("World")
            yield text2.emit_text_done()
            yield text2.emit_done()
            yield msg2.emit_done()

            item2_emitted.set()
            while not item2_checked.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)

            yield stream.emit_completed()

        return _events()

    handler.item1_emitted = item1_emitted  # type: ignore[attr-defined]
    handler.item1_checked = item1_checked  # type: ignore[attr-defined]
    handler.item2_emitted = item2_emitted  # type: ignore[attr-defined]
    handler.item2_checked = item2_checked  # type: ignore[attr-defined]
    return handler
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
            assert cancel_resp.status_code == 404, (
                "S7: non-background in-flight cancel must return 404 (not yet stored)"
            )

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

    async def test_e26_bg_stream_cancel_then_sse_replay_terminal_event(self) -> None:
        """B26 — SSE replay after cancel contains terminal event response.failed with status cancelled.

        Unlike test_bg_stream_cancel_terminal_sse_is_response_failed_with_cancelled
        which checks the *live* SSE stream, this test verifies the stored *replay*
        endpoint (GET ?stream=true) returns the correct terminal event.
        """
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

            await asyncio.wait_for(post_task, timeout=5.0)
        finally:
            await _ensure_task_done(post_task, handler)

        # SSE replay after cancel → should have response.failed terminal event
        replay_resp = await client.get(f"/responses/{response_id}?stream=true")
        assert replay_resp.status_code == 200

        replay_events = _parse_sse_events(replay_resp.body.decode())
        assert len(replay_events) >= 1, "Replay should have at least 1 event"

        # B26: terminal event for cancelled response is response.failed
        last_event = replay_events[-1]
        assert last_event["type"] == "response.failed", (
            f"Expected response.failed terminal in replay, got: {last_event['type']}"
        )

        # The response inside should have status: cancelled
        if "response" in last_event["data"]:
            assert last_event["data"]["response"]["status"] == "cancelled"

    async def test_e43_bg_stream_get_during_stream_item_lifecycle(self) -> None:
        """B5, B23 — GET mid-stream returns progressive item lifecycle.

        Validates the full 4-phase lifecycle (E43):
        Phase 1: After item Added → 1 item, status=in_progress, empty content
        Phase 2: After item Done → 1 item, status=completed, text="Hello"
        Phase 3: After 2nd item Done → 2 items, both completed
        Phase 4: After completion → 2 items, both completed (final snapshot)
        """
        handler = _make_item_lifecycle_gated_handler()
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
            # ── Phase 1: After EmitAdded (before EmitDone) ──
            await asyncio.wait_for(handler.item_added.wait(), timeout=5.0)

            get1 = await client.get(f"/responses/{response_id}")
            assert get1.status_code == 200
            doc1 = get1.json()
            assert doc1["status"] == "in_progress"
            output1 = doc1["output"]
            assert len(output1) == 1
            item1_added = output1[0]
            assert item1_added["type"] == "message"
            # Item is in_progress — content should be empty
            assert item1_added["status"] == "in_progress"
            assert len(item1_added["content"]) == 0

            handler.item_added_checked.set()

            # ── Phase 2: After EmitDone — item is completed with full text ──
            await asyncio.wait_for(handler.item_done.wait(), timeout=5.0)

            get2 = await client.get(f"/responses/{response_id}")
            assert get2.status_code == 200
            doc2 = get2.json()
            assert doc2["status"] == "in_progress"
            output2 = doc2["output"]
            assert len(output2) == 1
            item1_done = output2[0]
            assert item1_done["status"] == "completed"
            content_done = item1_done["content"]
            assert len(content_done) == 1
            assert content_done[0]["type"] == "output_text"
            assert content_done[0]["text"] == "Hello"

            handler.item_done_checked.set()

            # ── Phase 3: Second item done — output should have 2 completed items ──
            await asyncio.wait_for(handler.item2_done.wait(), timeout=5.0)

            get3 = await client.get(f"/responses/{response_id}")
            assert get3.status_code == 200
            doc3 = get3.json()
            assert doc3["status"] == "in_progress"
            output3 = doc3["output"]
            assert len(output3) == 2
            assert output3[0]["status"] == "completed"
            assert output3[1]["status"] == "completed"
            assert output3[1]["content"][0]["text"] == "World"

            handler.item2_done_checked.set()

            post_resp = await asyncio.wait_for(post_task, timeout=5.0)
            assert post_resp.status_code == 200

            # ── Phase 4: After completion — final snapshot ──
            get_final = await client.get(f"/responses/{response_id}")
            assert get_final.status_code == 200
            doc_final = get_final.json()
            assert doc_final["status"] == "completed"
            assert len(doc_final["output"]) == 2
        finally:
            await _ensure_task_done(post_task, handler)

    async def test_e44_bg_progressive_polling_output_grows(self) -> None:
        """B5, B10 — background progressive polling shows output accumulation.

        Validates the full 3-phase progressive polling (E44):
        Phase 1: After item1 done → 1 completed item with text="Hello"
        Phase 2: After item2 done → 2 completed items with text="Hello" and "World"
        Phase 3: After completion → 2 items, full content preserved

        Note: The Python server updates the stored record progressively only
        for bg+stream responses (S-035), so this test uses stream=True.
        The sync E44 test verifies the final-state-only path for bg non-streaming.
        """
        handler = _make_two_item_gated_bg_handler()
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
            # Wait for first item to be fully emitted (done)
            await asyncio.wait_for(handler.item1_emitted.wait(), timeout=5.0)

            # Poll: should see 1 completed output item with text "Hello"
            poll1 = await client.get(f"/responses/{response_id}")
            assert poll1.status_code == 200
            doc1 = poll1.json()
            assert doc1["status"] == "in_progress"
            output1 = doc1["output"]
            assert len(output1) == 1
            assert output1[0]["status"] == "completed"
            assert output1[0]["content"][0]["text"] == "Hello"

            # Release gate for second item
            handler.item1_checked.set()

            # Wait for second item
            await asyncio.wait_for(handler.item2_emitted.wait(), timeout=5.0)

            # Poll: should see 2 completed output items
            poll2 = await client.get(f"/responses/{response_id}")
            assert poll2.status_code == 200
            doc2 = poll2.json()
            assert doc2["status"] == "in_progress"
            output2 = doc2["output"]
            assert len(output2) == 2
            assert output2[0]["status"] == "completed"
            assert output2[0]["content"][0]["text"] == "Hello"
            assert output2[1]["status"] == "completed"
            assert output2[1]["content"][0]["text"] == "World"

            # Release final gate
            handler.item2_checked.set()

            post_resp = await asyncio.wait_for(post_task, timeout=5.0)
            assert post_resp.status_code == 200

            # Final poll: completed with 2 items, full content preserved
            poll_final = await client.get(f"/responses/{response_id}")
            assert poll_final.status_code == 200
            doc_final = poll_final.json()
            assert doc_final["status"] == "completed"
            output_final = doc_final["output"]
            assert len(output_final) == 2
            assert output_final[0]["content"][0]["text"] == "Hello"
            assert output_final[1]["content"][0]["text"] == "World"
        finally:
            await _ensure_task_done(post_task, handler)
