# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for handler-driven persistence (US1).

Verifies FR-001 (no persistence before handler runs),
FR-002 (bg=true: Create at response.created, Update at terminal),
FR-003 (bg=false: single Create at terminal state).

Python port of HandlerDrivenPersistenceTests.

NOTE: The reference tests use a RecordingProvider (spy) to verify exactly when
CreateResponseAsync and UpdateResponseAsync are called. The Python SDK uses
the in-memory FoundryStorageProvider (default) which we probe via GET to
confirm persistence timing.
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


async def _wait_for_background_completion(client: _AsyncAsgiClient, response_id: str, timeout: float = 5.0) -> None:
    for _ in range(int(timeout / 0.05)):
        resp = await client.get(f"/responses/{response_id}")
        if resp.status_code == 404:
            await asyncio.sleep(0.05)
            continue
        doc = resp.json()
        if doc.get("status") in ("completed", "failed", "incomplete", "cancelled"):
            return
        await asyncio.sleep(0.05)
    raise TimeoutError(f"Response {response_id} did not reach terminal state within {timeout}s")


def _make_delaying_handler():
    """Handler that signals when started, then waits for a gate before yielding any events.

    Used to test FR-001: no persistence before handler runs.
    """
    started = asyncio.Event()
    gate = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            started.set()
            await gate.wait()
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            yield stream.emit_completed()

        return _events()

    handler.started = started
    handler.gate = gate
    return handler


def _make_simple_handler():
    """Handler that emits created + completed immediately."""

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            yield stream.emit_completed()

        return _events()

    return handler


# ════════════════════════════════════════════════════════════
# T015: bg+stream — provider NOT called until response.created
#
# FR-001: No persistence before handler emits response.created.
# Verifies that GET returns 404 before response.created is emitted.
# ════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_bg_stream_not_persisted_until_response_created() -> None:
    """T015/FR-001 — bg+stream: response not accessible before response.created."""
    handler = _make_delaying_handler()
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
        await asyncio.sleep(0.1)

        # GET before response.created — should NOT be accessible yet
        get_resp = await client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 404, (
            f"FR-001: response should not be persisted before response.created, got status {get_resp.status_code}"
        )

        # Release handler → response.created will be yielded
        handler.gate.set()
        await asyncio.wait_for(post_task, timeout=5.0)
    finally:
        await _ensure_task_done(post_task, handler)

    # After handler completes, response should be accessible
    await _wait_for_background_completion(client, response_id)
    get_after = await client.get(f"/responses/{response_id}")
    assert get_after.status_code == 200


# ════════════════════════════════════════════════════════════
# T016: bg+nostream — provider NOT called until response.created
# ════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_bg_nostream_not_persisted_until_response_created() -> None:
    """T016/FR-001 — bg+nostream: response not accessible before response.created."""
    handler = _make_delaying_handler()
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
        await asyncio.sleep(0.1)

        # GET before response.created — should NOT be accessible
        get_resp = await client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 404, (
            f"FR-001: response should not be persisted before response.created, got status {get_resp.status_code}"
        )

        # Release handler
        handler.gate.set()
        await asyncio.wait_for(post_task, timeout=5.0)
    finally:
        await _ensure_task_done(post_task, handler)

    # After handler completes, response should be accessible
    await _wait_for_background_completion(client, response_id)
    get_after = await client.get(f"/responses/{response_id}")
    assert get_after.status_code == 200


# ════════════════════════════════════════════════════════════
# T017: bg=true — exactly 1 Create + 1 Update
#
# FR-002: bg mode persists Create at response.created, Update at terminal.
# We verify via GET that the response is accessible during in-progress
# and that after completion the status is updated.
# ════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_bg_mode_response_accessible_during_and_after_handler() -> None:
    """T017/FR-002 — bg mode: response accessible at in_progress and completed."""
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
        await asyncio.wait_for(started.wait(), timeout=5.0)

        # During handler execution — response should be accessible as in_progress
        get_mid = await client.get(f"/responses/{response_id}")
        assert get_mid.status_code == 200
        assert get_mid.json()["status"] == "in_progress"

        # Release handler
        release.set()
        await asyncio.wait_for(post_task, timeout=5.0)
    finally:
        for attr in ("started", "release"):
            obj = getattr(handler, attr, None)
            if isinstance(obj, asyncio.Event):
                obj.set()
        if not post_task.done():
            post_task.cancel()
            try:
                await post_task
            except (asyncio.CancelledError, Exception):
                pass

    # After completion — response updated to completed
    await _wait_for_background_completion(client, response_id)
    get_final = await client.get(f"/responses/{response_id}")
    assert get_final.status_code == 200
    assert get_final.json()["status"] == "completed"


# ════════════════════════════════════════════════════════════
# T018: bg=false — single Create at terminal (no mid-flight GET)
#
# FR-003: non-bg mode does a single Create at terminal. Not accessible mid-flight.
# ════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_non_bg_not_accessible_until_terminal() -> None:
    """T018/FR-003 — non-bg: response only accessible after terminal state."""
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
            await release.wait()
            yield stream.emit_completed()

        return _events()

    handler.started = started
    handler.release = release

    client = _build_client(handler)
    response_id = IdGenerator.new_response_id()

    post_task = asyncio.create_task(
        client.post(
            "/responses",
            json_body={
                "response_id": response_id,
                "model": "test",
                "stream": False,
                "background": False,
            },
        )
    )
    try:
        await asyncio.wait_for(started.wait(), timeout=5.0)

        # During non-bg handler execution — response should NOT be accessible
        get_mid = await client.get(f"/responses/{response_id}")
        assert get_mid.status_code == 404, (
            f"FR-003: non-bg response should not be accessible mid-flight, got {get_mid.status_code}"
        )

        release.set()
        post_resp = await asyncio.wait_for(post_task, timeout=5.0)
        assert post_resp.status_code == 200
    finally:
        started.set()
        release.set()
        if not post_task.done():
            post_task.cancel()
            try:
                await post_task
            except (asyncio.CancelledError, Exception):
                pass

    # After terminal — response is accessible as completed
    get_after = await client.get(f"/responses/{response_id}")
    assert get_after.status_code == 200
    assert get_after.json()["status"] == "completed"
