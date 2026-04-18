# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for chat isolation key enforcement across all endpoints.

When a response is created with an ``x-agent-chat-isolation-key`` header,
all subsequent GET, Cancel, DELETE, and InputItems requests must include
the same key.  Mismatched or missing keys return an indistinguishable 404
to prevent cross-chat information leakage.

Backward-compatible: no enforcement when the response was created without a key.
"""

from __future__ import annotations

import asyncio
import json as _json
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from tests._helpers import poll_until


# ── Shared helpers (sync, for GET / DELETE / INPUT_ITEMS) ──

def _noop_handler(request: Any, context: Any, cancellation_signal: Any):
    async def _events():
        if False:  # pragma: no cover
            yield None

    return _events()


def _make_client(handler=_noop_handler) -> TestClient:
    host = ResponsesAgentServerHost()
    host.response_handler(handler)
    return TestClient(host)


def _create_response(
    client: TestClient, *, chat_key: str | None = None, **overrides
) -> dict[str, Any]:
    """Create a response and return the parsed JSON body."""
    payload = {
        "model": "m",
        "input": [{"role": "user", "content": "hi"}],
        **overrides,
    }
    headers: dict[str, str] = {}
    if chat_key is not None:
        headers["x-agent-chat-isolation-key"] = chat_key
    r = client.post("/responses", json=payload, headers=headers)
    assert r.status_code == 200, f"create failed: {r.status_code} {r.text}"
    return r.json()


def _wait_for_terminal(
    client: TestClient, response_id: str, **headers: str
) -> dict[str, Any]:
    latest: dict[str, Any] = {}
    terminal = {"completed", "failed", "incomplete", "cancelled"}

    def _check() -> bool:
        nonlocal latest
        r = client.get(f"/responses/{response_id}", headers=headers)
        if r.status_code != 200:
            return False
        latest = r.json()
        return latest.get("status") in terminal

    poll_until(_check, timeout_s=5.0, interval_s=0.05, label="wait_terminal")
    return latest


# ── Async ASGI client (for cancel tests — needs event loop) ──


class _AsgiResponse:
    def __init__(
        self, status_code: int, body: bytes, headers: list[tuple[bytes, bytes]]
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.headers = headers

    def json(self) -> Any:
        return _json.loads(self.body)


class _AsyncAsgiClient:
    """Lightweight async ASGI client that supports custom headers."""

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
        body = _json.dumps(json_body).encode() if json_body else b""
        raw_headers = (
            [(k.lower().encode(), v.encode()) for k, v in headers.items()]
            if headers
            else []
        )
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
        return _AsgiResponse(
            status_code=status_code,
            body=b"".join(body_parts),
            headers=response_headers,
        )

    async def get(
        self, path: str, *, headers: dict[str, str] | None = None
    ) -> _AsgiResponse:
        return await self.request("GET", path, headers=headers)

    async def post(
        self,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> _AsgiResponse:
        return await self.request("POST", path, json_body=json_body, headers=headers)


def _make_cancellable_bg_handler() -> Any:
    """Handler that emits created+in_progress, then blocks until cancelled."""
    started = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            yield stream.emit_in_progress()
            started.set()
            while not cancellation_signal.is_set():
                await asyncio.sleep(0.01)

        return _events()

    handler.started = started  # type: ignore[attr-defined]
    return handler


def _build_async_client(handler: Any) -> _AsyncAsgiClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    return _AsyncAsgiClient(app)


# ── GET with isolation ────────────────────────────────────

class TestGetChatIsolation:
    """GET /responses/{id} with chat isolation key enforcement.

    In-flight isolation is enforced locally by the endpoint handler.
    After eviction, the Foundry storage provider enforces isolation
    server-side (returning 400 for missing/mismatched keys).
    These tests verify the in-flight path using background responses
    that remain in runtime state.
    """

    def test_get_matching_key_returns_200(self) -> None:
        """GET with the same chat key that was used at creation → 200."""
        client = _make_client()
        resp = _create_response(client, chat_key="key_A")
        _wait_for_terminal(client, resp["id"], **{"x-agent-chat-isolation-key": "key_A"})
        r = client.get(f"/responses/{resp['id']}", headers={"x-agent-chat-isolation-key": "key_A"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_get_mismatched_key_returns_404(self) -> None:
        """GET with a different chat key on in-flight response → 404."""
        handler = _make_cancellable_bg_handler()
        client = _build_async_client(handler)
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
                headers={"x-agent-chat-isolation-key": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.get(
                f"/responses/{response_id}",
                headers={"x-agent-chat-isolation-key": "key_B"},
            )
            assert r.status_code == 404
        finally:
            handler.started.set()
            if not post_task.done():
                post_task.cancel()
                try:
                    await post_task
                except (asyncio.CancelledError, Exception):
                    pass

    @pytest.mark.asyncio
    async def test_get_missing_key_when_created_with_key_returns_404(self) -> None:
        """GET without chat key when response was created with one → 404."""
        handler = _make_cancellable_bg_handler()
        client = _build_async_client(handler)
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
                headers={"x-agent-chat-isolation-key": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.get(f"/responses/{response_id}")
            assert r.status_code == 404
        finally:
            handler.started.set()
            if not post_task.done():
                post_task.cancel()
                try:
                    await post_task
                except (asyncio.CancelledError, Exception):
                    pass

    def test_get_created_without_key_any_request_returns_200(self) -> None:
        """GET with or without key when response was created without one → 200 (backward compat)."""
        client = _make_client()
        resp = _create_response(client)
        _wait_for_terminal(client, resp["id"])
        # With a key
        r = client.get(f"/responses/{resp['id']}", headers={"x-agent-chat-isolation-key": "any_key"})
        assert r.status_code == 200
        # Without a key
        r = client.get(f"/responses/{resp['id']}")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_get_404_error_body_is_standard(self) -> None:
        """404 from isolation mismatch has the standard error body shape."""
        handler = _make_cancellable_bg_handler()
        client = _build_async_client(handler)
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
                headers={"x-agent-chat-isolation-key": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.get(
                f"/responses/{response_id}",
                headers={"x-agent-chat-isolation-key": "key_WRONG"},
            )
            assert r.status_code == 404
            body = r.json()
            assert "error" in body
            assert body["error"]["code"] == "invalid_request_error"
        finally:
            handler.started.set()
            if not post_task.done():
                post_task.cancel()
                try:
                    await post_task
                except (asyncio.CancelledError, Exception):
                    pass


# ── DELETE with isolation ────────────────────────────────

class TestDeleteChatIsolation:
    """DELETE /responses/{id} with chat isolation key enforcement.

    In-flight isolation is enforced locally; after eviction, isolation is
    enforced by the Foundry storage provider server-side.
    """

    def test_delete_matching_key_returns_200(self) -> None:
        client = _make_client()
        resp = _create_response(client, chat_key="key_A")
        _wait_for_terminal(client, resp["id"], **{"x-agent-chat-isolation-key": "key_A"})
        r = client.delete(f"/responses/{resp['id']}", headers={"x-agent-chat-isolation-key": "key_A"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_mismatched_key_returns_404(self) -> None:
        handler = _make_cancellable_bg_handler()
        client = _build_async_client(handler)
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
                headers={"x-agent-chat-isolation-key": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.request(
                "DELETE",
                f"/responses/{response_id}",
                headers={"x-agent-chat-isolation-key": "key_B"},
            )
            assert r.status_code == 404
        finally:
            handler.started.set()
            if not post_task.done():
                post_task.cancel()
                try:
                    await post_task
                except (asyncio.CancelledError, Exception):
                    pass

    @pytest.mark.asyncio
    async def test_delete_missing_key_when_created_with_key_returns_404(self) -> None:
        handler = _make_cancellable_bg_handler()
        client = _build_async_client(handler)
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
                headers={"x-agent-chat-isolation-key": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.request("DELETE", f"/responses/{response_id}")
            assert r.status_code == 404
        finally:
            handler.started.set()
            if not post_task.done():
                post_task.cancel()
                try:
                    await post_task
                except (asyncio.CancelledError, Exception):
                    pass


# ── CANCEL with isolation (async — needs real event loop) ──


class TestCancelChatIsolation:
    """POST /responses/{id}/cancel with chat isolation key enforcement.

    Cancel tests must use async ASGI client because the handler runs as a
    background asyncio task that needs the event loop to start before the
    cancel request can observe it.
    """

    @pytest.mark.asyncio
    async def test_cancel_matching_key_succeeds(self) -> None:
        """Cancel with matching key on a background in-flight response → 200."""
        handler = _make_cancellable_bg_handler()
        client = _build_async_client(handler)
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
                headers={"x-agent-chat-isolation-key": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.post(
                f"/responses/{response_id}/cancel",
                headers={"x-agent-chat-isolation-key": "key_A"},
            )
            assert r.status_code == 200
        finally:
            handler.started.set()  # unblock if needed
            if not post_task.done():
                post_task.cancel()
                try:
                    await post_task
                except (asyncio.CancelledError, Exception):
                    pass

    @pytest.mark.asyncio
    async def test_cancel_mismatched_key_returns_404(self) -> None:
        """Cancel with wrong key → 404."""
        handler = _make_cancellable_bg_handler()
        client = _build_async_client(handler)
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
                headers={"x-agent-chat-isolation-key": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.post(
                f"/responses/{response_id}/cancel",
                headers={"x-agent-chat-isolation-key": "key_B"},
            )
            assert r.status_code == 404
        finally:
            handler.started.set()
            if not post_task.done():
                post_task.cancel()
                try:
                    await post_task
                except (asyncio.CancelledError, Exception):
                    pass

    @pytest.mark.asyncio
    async def test_cancel_missing_key_when_created_with_key_returns_404(self) -> None:
        """Cancel without any key when response was created with one → 404."""
        handler = _make_cancellable_bg_handler()
        client = _build_async_client(handler)
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
                headers={"x-agent-chat-isolation-key": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.post(f"/responses/{response_id}/cancel")
            assert r.status_code == 404
        finally:
            handler.started.set()
            if not post_task.done():
                post_task.cancel()
                try:
                    await post_task
                except (asyncio.CancelledError, Exception):
                    pass


# ── INPUT_ITEMS with isolation ────────────────────────────

class TestInputItemsChatIsolation:
    """GET /responses/{id}/input_items with chat isolation key enforcement.

    In-flight isolation is enforced locally; after eviction, isolation is
    enforced by the Foundry storage provider server-side.
    """

    def test_input_items_matching_key_returns_200(self) -> None:
        client = _make_client()
        resp = _create_response(client, chat_key="key_A")
        _wait_for_terminal(client, resp["id"], **{"x-agent-chat-isolation-key": "key_A"})
        r = client.get(
            f"/responses/{resp['id']}/input_items",
            headers={"x-agent-chat-isolation-key": "key_A"},
        )
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_input_items_mismatched_key_returns_404(self) -> None:
        handler = _make_cancellable_bg_handler()
        client = _build_async_client(handler)
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
                headers={"x-agent-chat-isolation-key": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.get(
                f"/responses/{response_id}/input_items",
                headers={"x-agent-chat-isolation-key": "key_B"},
            )
            assert r.status_code == 404
        finally:
            handler.started.set()
            if not post_task.done():
                post_task.cancel()
                try:
                    await post_task
                except (asyncio.CancelledError, Exception):
                    pass

    @pytest.mark.asyncio
    async def test_input_items_missing_key_when_created_with_key_returns_404(self) -> None:
        handler = _make_cancellable_bg_handler()
        client = _build_async_client(handler)
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
                headers={"x-agent-chat-isolation-key": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.get(f"/responses/{response_id}/input_items")
            assert r.status_code == 404
        finally:
            handler.started.set()
            if not post_task.done():
                post_task.cancel()
                try:
                    await post_task
                except (asyncio.CancelledError, Exception):
                    pass
