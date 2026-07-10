# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for immutable event snapshots (US1).

Verifies that SSE events and GET responses contain point-in-time snapshot data,
not mutable references that change with subsequent mutations.

Python port of SnapshotConsistencyTests.
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
# Lightweight async ASGI client (same pattern as test_cross_api_e2e_async)
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


def _parse_sse_events(text: str) -> list[dict[str, Any]]:
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


def _make_multi_output_handler():
    """Handler that emits 2 output items sequentially for snapshot isolation testing."""

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
            yield stream.emit_created()

            msg1 = stream.add_output_item_message()
            yield msg1.emit_added()
            text1 = msg1.add_text_content()
            yield text1.emit_added()
            yield text1.emit_delta("First")
            yield text1.emit_text_done()
            yield text1.emit_done()
            yield msg1.emit_done()

            msg2 = stream.add_output_item_message()
            yield msg2.emit_added()
            text2 = msg2.add_text_content()
            yield text2.emit_added()
            yield text2.emit_delta("Second")
            yield text2.emit_text_done()
            yield text2.emit_done()
            yield msg2.emit_done()

            yield stream.emit_completed()

        return _events()

    return handler


def _make_replay_gated_handler():
    """Handler for replay snapshot test — waits for gate before completing."""
    done = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
            yield stream.emit_created()
            yield stream.emit_in_progress()

            await done.wait()

            yield stream.emit_completed()

        return _events()

    handler.done = done
    return handler


# ════════════════════════════════════════════════════════════
# T010: SSE event snapshot isolation
#
# response.created event's embedded response does not include items added
# after it was emitted. response.completed contains all output items.
# ════════════════════════════════════════════════════════════


def test_sse_events_contain_snapshot_not_live_reference() -> None:
    """T010 — SSE events reflect point-in-time snapshots.

    response.created should show in_progress with no output.
    response.completed should show completed with all output items.
    """
    from starlette.testclient import TestClient

    handler = _make_multi_output_handler()
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    client = TestClient(app)

    with client.stream("POST", "/responses", json={"model": "test", "stream": True}) as resp:
        events: list[dict[str, Any]] = []
        current_type: str | None = None
        current_data: str | None = None
        for line in resp.iter_lines():
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

    # response.created should have in_progress status
    created_event = next(e for e in events if e["type"] == "response.created")
    created_status = created_event["data"]["response"]["status"]
    assert created_status == "in_progress"

    # response.completed should have completed status with all items
    completed_event = next(e for e in events if e["type"] == "response.completed")
    completed_status = completed_event["data"]["response"]["status"]
    assert completed_status == "completed"
    completed_output = completed_event["data"]["response"]["output"]
    assert len(completed_output) >= 2, "completed should have all output items"

    # CRITICAL: response.created should have fewer outputs than completed
    created_output = created_event["data"]["response"]["output"]
    assert len(created_output) < len(completed_output), (
        f"created event should have fewer outputs ({len(created_output)}) "
        f"than completed event ({len(completed_output)}) — snapshot isolation"
    )


# ════════════════════════════════════════════════════════════
# T011 / SC-002: Replay snapshot integrity
#
# Replayed response.created has status in_progress (emission-time state),
# not completed (current state).
# ════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_sse_replay_reflects_emission_time_state() -> None:
    """T011 — replayed response.created shows in_progress (emission-time), not completed."""
    handler = _make_replay_gated_handler()
    client = _build_client(handler)
    response_id = IdGenerator.new_response_id()

    post_task = asyncio.create_task(
        client.post(
            "/responses",
            json_body={
                "response_id": response_id,
                "model": "test",
                "stream": True,
                "store": True,
                "background": True,
            },
        )
    )
    try:
        # Let handler complete
        await asyncio.sleep(0.3)
        handler.done.set()

        post_resp = await asyncio.wait_for(post_task, timeout=5.0)
        assert post_resp.status_code == 200
    finally:
        await _ensure_task_done(post_task, handler)

    # Wait for background completion
    for _ in range(50):
        get_resp = await client.get(f"/responses/{response_id}")
        if get_resp.status_code == 200 and get_resp.json().get("status") in ("completed", "failed"):
            break
        await asyncio.sleep(0.1)

    # Verify response is completed
    get_resp = await client.get(f"/responses/{response_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "completed"

    # Replay — response.created should show in_progress (emission-time state)
    replay_resp = await client.get(f"/responses/{response_id}?stream=true")
    assert replay_resp.status_code == 200

    replay_events = _parse_sse_events(replay_resp.body.decode())
    replay_created = next((e for e in replay_events if e["type"] == "response.created"), None)
    assert replay_created is not None
    replay_created_status = replay_created["data"]["response"]["status"]
    assert replay_created_status == "in_progress", (
        f"Replayed response.created should show 'in_progress' (emission-time state), "
        f"not '{replay_created_status}' (current state)"
    )
