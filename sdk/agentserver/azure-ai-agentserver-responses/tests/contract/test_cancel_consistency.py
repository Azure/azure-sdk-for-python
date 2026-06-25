# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for cancel consistency (US6, FR-014, FR-015).

Verifies FR-014 (SetCancelled applied exactly once) and
FR-015 (persisted state matches returned state on cancel).

Python port of CancelConsistencyTests.

NOTE: These tests require concurrent access during active handlers, so they use
the async ASGI client pattern.
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
# Async ASGI client
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


def _make_cancellable_bg_handler():
    """Handler that emits created+in_progress, then blocks until cancelled or released."""
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

    handler.started = started
    handler.release = release
    return handler


# ════════════════════════════════════════════════════════════
# T055: Cancel bg response — persisted state = returned state
# (0 output items, status: cancelled)
# ════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_cancel_bg_response_persisted_state_matches_returned_state() -> None:
    """T055 — cancel bg response: persisted state matches returned cancel snapshot.

    FR-015: The cancel endpoint return value must match the persisted state.
    """
    handler = _make_cancellable_bg_handler()
    client = _build_client(handler)
    response_id = IdGenerator.new_response_id()

    post_task = asyncio.create_task(
        client.post(
            "/responses",
            json_body={
                "response_id": response_id,
                "model": "test",
                "background": True,
            },
        )
    )
    try:
        await asyncio.wait_for(handler.started.wait(), timeout=5.0)

        # Cancel the response
        cancel_resp = await client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 200  # FR-015

        cancel_doc = cancel_resp.json()
        returned_status = cancel_doc["status"]
        returned_output = cancel_doc["output"]
        assert returned_status == "cancelled"
        assert returned_output == []

        # Let handler exit
        handler.release.set()
        await asyncio.wait_for(post_task, timeout=5.0)
    finally:
        await _ensure_task_done(post_task, handler)

    # Allow cleanup
    await asyncio.sleep(0.2)

    # Verify persisted state matches returned state
    get_resp = await client.get(f"/responses/{response_id}")
    assert get_resp.status_code == 200
    persisted = get_resp.json()
    assert persisted["status"] == "cancelled", (
        f"Persisted status should match cancel return: expected 'cancelled', got '{persisted['status']}'"
    )
    assert persisted["output"] == [], (
        f"Persisted output should match cancel return: expected [], got {persisted['output']}"
    )


# ════════════════════════════════════════════════════════════
# T056: Cancel bg+stream response — persisted state matches cancel return
# ════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_cancel_bg_stream_response_persisted_state_matches() -> None:
    """T056 — cancel bg+stream: persisted state matches cancel endpoint return value.

    FR-014: SetCancelled applied exactly once.
    FR-015: Persisted state = returned state.
    """
    handler = _make_cancellable_bg_handler()
    client = _build_client(handler)
    response_id = IdGenerator.new_response_id()

    post_task = asyncio.create_task(
        client.post(
            "/responses",
            json_body={
                "response_id": response_id,
                "model": "test",
                "background": True,
                "stream": True,
            },
        )
    )
    try:
        await asyncio.wait_for(handler.started.wait(), timeout=5.0)
        await asyncio.sleep(0.1)  # Let bg task process response.created

        # Cancel the response
        cancel_resp = await client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 200

        cancel_doc = cancel_resp.json()
        assert cancel_doc["status"] == "cancelled"

        # Let handler exit
        handler.release.set()
        await asyncio.wait_for(post_task, timeout=5.0)
    finally:
        await _ensure_task_done(post_task, handler)

    # Allow cleanup
    await asyncio.sleep(0.2)

    # Verify persisted state matches
    get_resp = await client.get(f"/responses/{response_id}")
    assert get_resp.status_code == 200
    persisted = get_resp.json()
    assert persisted["status"] == "cancelled", f"Persisted status should be 'cancelled', got '{persisted['status']}'"
