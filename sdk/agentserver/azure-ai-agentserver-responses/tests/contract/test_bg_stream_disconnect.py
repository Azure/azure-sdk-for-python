# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for background streaming handler surviving disconnect (US3).

Verifies FR-012 (handler continues after SSE disconnect for bg+stream),
FR-013 (SSE write failure does NOT cancel handler CT).

Python port of BgStreamDisconnectTests.

NOTE: These tests use the async ASGI client with a cancellation-aware SSE reader
to simulate client disconnect behavior.
"""

from __future__ import annotations

import asyncio
import json as _json
from typing import Any

import pytest

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

# ════════════════════════════════════════════════════════════
# Async ASGI client with disconnect capability
# ════════════════════════════════════════════════════════════


class _AsgiResponse:
    def __init__(self, status_code: int, body: bytes, headers: list[tuple[bytes, bytes]]) -> None:
        self.status_code = status_code
        self.body = body
        self.headers = headers

    def json(self) -> Any:
        return _json.loads(self.body)


class _AsyncAsgiClient:
    def __init__(self, app: Any) -> None:
        self._app = app

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

    async def request(self, method: str, path: str, *, json_body: dict[str, Any] | None = None) -> _AsgiResponse:
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
        return _AsgiResponse(status_code=status_code, body=b"".join(body_parts), headers=response_headers)

    async def request_with_disconnect(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        disconnect_event: asyncio.Event | None = None,
    ) -> _AsgiResponse:
        """Send a request and disconnect mid-stream when disconnect_event is set."""
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
            if disconnect_event is not None:
                await disconnect_event.wait()
                return {"type": "http.disconnect"}
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

    async def get(self, path: str) -> _AsgiResponse:
        return await self.request("GET", path)

    async def post(self, path: str, *, json_body: dict[str, Any] | None = None) -> _AsgiResponse:
        return await self.request("POST", path, json_body=json_body)


# ════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════


def _build_client(handler: Any) -> _AsyncAsgiClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    return _AsyncAsgiClient(app)


async def _ensure_task_done(task: asyncio.Task[Any], handler: Any, timeout: float = 5.0) -> None:
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


async def _wait_for_background_completion(client: _AsyncAsgiClient, response_id: str, timeout: float = 5.0) -> None:
    for _ in range(int(timeout / 0.05)):
        resp = await client.get(f"/responses/{response_id}")
        if resp.status_code == 200:
            doc = resp.json()
            if doc.get("status") in ("completed", "failed", "incomplete", "cancelled"):
                return
        await asyncio.sleep(0.05)
    raise TimeoutError(f"Response {response_id} did not reach terminal state within {timeout}s")


def _make_multi_output_handler(total_outputs: int, signal_after: int):
    """Handler that produces N output items, signals for disconnect after M items."""
    ready_for_disconnect = asyncio.Event()
    handler_completed = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()

            for i in range(total_outputs):
                msg = stream.add_output_item_message()
                yield msg.emit_added()
                text = msg.add_text_content()
                yield text.emit_added()
                yield text.emit_delta(f"Item-{i}")
                yield text.emit_text_done()
                yield text.emit_done()
                yield msg.emit_done()

                if i == signal_after - 1:
                    ready_for_disconnect.set()
                    # Give client time to disconnect
                    await asyncio.sleep(0.3)

            yield stream.emit_completed()
            handler_completed.set()

        return _events()

    handler.ready_for_disconnect = ready_for_disconnect
    handler.handler_completed = handler_completed
    return handler


def _make_cancellation_tracking_handler():
    """Handler that tracks whether it was cancelled vs completed."""
    ready_for_disconnect = asyncio.Event()
    handler_cancelled = asyncio.Event()
    handler_completed = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            ready_for_disconnect.set()

            # Wait without checking cancellation_signal (simulates work)
            await asyncio.sleep(0.5)

            if cancellation_signal.is_set():
                handler_cancelled.set()
                return

            yield stream.emit_completed()
            handler_completed.set()

        return _events()

    handler.ready_for_disconnect = ready_for_disconnect
    handler.handler_cancelled = handler_cancelled
    handler.handler_completed = handler_completed
    return handler


def _make_slow_completing_handler():
    """Handler that takes a moment to complete (for bg+nostream regression test)."""
    handler_completed = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            await asyncio.sleep(0.2)
            yield stream.emit_completed()
            handler_completed.set()

        return _events()

    handler.handler_completed = handler_completed
    return handler


# ════════════════════════════════════════════════════════════
# T036: bg+stream — client disconnects after 3 events,
# handler produces 10 total → GET returns completed with all output
# ════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_bg_stream_client_disconnects_handler_completes_all_events() -> None:
    """T036/FR-012 — bg+stream: handler continues after client disconnect.

    Handler produces 10 output items, client disconnects after 3.
    GET after handler completes should return completed with all items.
    """
    total = 10
    disconnect_after = 3
    handler = _make_multi_output_handler(total, disconnect_after)
    client = _build_client(handler)
    response_id = IdGenerator.new_response_id()

    disconnect = asyncio.Event()
    post_task = asyncio.create_task(
        client.request_with_disconnect(
            "POST",
            "/responses",
            json_body={
                "response_id": response_id,
                "model": "test",
                "background": True,
                "stream": True,
            },
            disconnect_event=disconnect,
        )
    )
    try:
        await asyncio.wait_for(handler.ready_for_disconnect.wait(), timeout=5.0)

        # Disconnect the SSE client
        disconnect.set()
        try:
            await asyncio.wait_for(post_task, timeout=2.0)
        except (asyncio.TimeoutError, Exception):
            pass

        # Wait for handler to complete all events
        await asyncio.wait_for(handler.handler_completed.wait(), timeout=5.0)

        # Wait for orchestrator to persist terminal status
        await _wait_for_background_completion(client, response_id)

        # GET should return completed
        get_resp = await client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        doc = get_resp.json()
        assert doc["status"] == "completed", (
            f"FR-012: bg+stream handler should complete after disconnect, got status '{doc['status']}'"
        )
    finally:
        await _ensure_task_done(post_task, handler)


# ════════════════════════════════════════════════════════════
# T037: bg+stream — SSE write failure does NOT cancel handler CT
# ════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_bg_stream_sse_write_failure_does_not_cancel_handler_ct() -> None:
    """T037/FR-013 — bg+stream: SSE write failure does not trigger handler cancellation.

    After client disconnect, the handler should complete normally,
    not be cancelled by the SSE write failure.
    """
    handler = _make_cancellation_tracking_handler()
    client = _build_client(handler)
    response_id = IdGenerator.new_response_id()

    disconnect = asyncio.Event()
    post_task = asyncio.create_task(
        client.request_with_disconnect(
            "POST",
            "/responses",
            json_body={
                "response_id": response_id,
                "model": "test",
                "background": True,
                "stream": True,
            },
            disconnect_event=disconnect,
        )
    )
    try:
        await asyncio.wait_for(handler.ready_for_disconnect.wait(), timeout=5.0)

        # Disconnect
        disconnect.set()
        try:
            await asyncio.wait_for(post_task, timeout=2.0)
        except (asyncio.TimeoutError, Exception):
            pass

        # Wait for handler outcome
        done_events = [handler.handler_completed, handler.handler_cancelled]
        done, _ = await asyncio.wait(
            [asyncio.create_task(e.wait()) for e in done_events],
            timeout=3.0,
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Handler should have COMPLETED, not been CANCELLED
        assert handler.handler_completed.is_set(), (
            "FR-013: Handler should complete normally, not be cancelled by SSE disconnect"
        )
        assert not handler.handler_cancelled.is_set(), (
            "FR-013: Handler CT should NOT have been cancelled by SSE disconnect"
        )
    finally:
        await _ensure_task_done(post_task, handler)


# ════════════════════════════════════════════════════════════
# T038: bg+nostream — handler continues after disconnect (regression)
# ════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_bg_nostream_handler_continues_after_disconnect() -> None:
    """T038 — bg+nostream: handler continues to completion even after client disconnect.

    POST bg+nostream returns immediately. Handler is still running.
    After handler completes, GET returns completed.
    """
    handler = _make_slow_completing_handler()
    client = _build_client(handler)

    # POST bg+nostream returns immediately
    post_resp = await client.post(
        "/responses",
        json_body={
            "model": "test",
            "background": True,
        },
    )
    assert post_resp.status_code == 200
    response_id = post_resp.json()["id"]

    # Handler hasn't completed yet
    assert not handler.handler_completed.is_set()

    # Wait for handler to complete
    await asyncio.wait_for(handler.handler_completed.wait(), timeout=5.0)

    # Wait for orchestrator to persist terminal status
    await _wait_for_background_completion(client, response_id)

    # GET should return completed
    get_resp = await client.get(f"/responses/{response_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "completed"
