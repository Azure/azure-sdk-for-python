# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for connection termination behavior (US3).

Validates that client disconnects are handled correctly for each mode:
- Non-bg streaming disconnect → handler cancelled
- Bg non-streaming → POST returns immediately, handler continues

Python port of ConnectionTerminationTests.

NOTE: The T067 (non-bg disconnect → cancelled) relies on HTTP connection
lifecycle that Starlette TestClient cannot model (no TCP disconnect).
We test what we can: bg non-streaming handler continuation.
"""

from __future__ import annotations

import asyncio
import json as _json
from typing import Any

import pytest

from azure.ai.agentserver.responses import ResponsesAgentServerHost
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
    app.create_handler(handler)
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


# ════════════════════════════════════════════════════════════
# T069: bg non-streaming → POST returns immediately, handler continues
# ════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_bg_non_streaming_post_returns_handler_continues() -> None:
    """T069 — bg non-streaming: POST returns immediately with in_progress, handler continues."""
    handler_completed = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            # Simulate work
            await asyncio.sleep(0.3)
            yield stream.emit_completed()
            handler_completed.set()

        return _events()

    client = _build_client(handler)

    post_resp = await client.post(
        "/responses",
        json_body={"model": "test", "background": True},
    )

    # POST returns immediately with in_progress
    assert post_resp.status_code == 200
    doc = post_resp.json()
    assert doc["status"] == "in_progress"
    response_id = doc["id"]

    # Handler hasn't completed yet
    assert not handler_completed.is_set()

    # Wait for handler to complete
    await asyncio.wait_for(handler_completed.wait(), timeout=5.0)
    await asyncio.sleep(0.1)  # let cleanup finish

    # GET should return completed response
    await _wait_for_background_completion(client, response_id)
    get_resp = await client.get(f"/responses/{response_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "completed"


# ════════════════════════════════════════════════════════════
# T067: non-bg streaming disconnect → handler cancelled (skip)
#
# NOTE: This test is skipped because the Starlette TestClient and our
# async ASGI client cannot model the TCP disconnect lifecycle required
# to test this behavior. The original test relies on HTTP connection
# cancellation token propagation which doesn't map to ASGI's receive()
# disconnect model in the same way.
# ════════════════════════════════════════════════════════════


@pytest.mark.skip(reason="Starlette/ASGI TestClient cannot model TCP disconnect lifecycle for non-bg streaming")
@pytest.mark.asyncio
async def test_non_bg_streaming_disconnect_results_in_cancelled() -> None:
    """T067 — non-bg streaming: client disconnect → handler cancelled, status: cancelled.

    This test cannot be implemented with Starlette TestClient because:
    1. Non-bg streaming ties the SSE response to the HTTP connection
    2. Disconnect requires the HTTP framework to propagate cancellation through
       the ASGI lifecycle, which TestClient doesn't model
    """
    pass
