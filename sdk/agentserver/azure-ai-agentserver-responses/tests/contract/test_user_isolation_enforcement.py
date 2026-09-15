# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for user ID (user isolation) enforcement across all endpoints.

When a response is created with an ``x-agent-user-id`` header,
all subsequent GET, Cancel, DELETE, and InputItems requests must include
the same key.  Mismatched or missing keys return an indistinguishable 404
to prevent cross-user information leakage.

Backward-compatible: no enforcement when the response was created without a key.
"""

from __future__ import annotations

import asyncio
import json as _json
from typing import Any
from unittest.mock import AsyncMock

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses._response_context import PlatformContext
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from tests._helpers import poll_until

# ── Shared helpers (sync, for GET / DELETE / INPUT_ITEMS) ──


async def _noop_handler(request: Any, context: Any, cancellation_signal: asyncio.Event):
    async def _events():
        if False:  # pragma: no cover
            yield None

    return _events()


def _make_client(handler=_noop_handler) -> TestClient:
    host = ResponsesAgentServerHost()
    host.response_handler(handler)
    return TestClient(host)


def _create_response(client: TestClient, *, user_id_key: str | None = None, **overrides) -> dict[str, Any]:
    """Create a response and return the parsed JSON body."""
    payload = {
        "model": "m",
        "input": [{"role": "user", "content": "hi"}],
        **overrides,
    }
    headers: dict[str, str] = {}
    if user_id_key is not None:
        headers["x-agent-user-id"] = user_id_key
    r = client.post("/responses", json=payload, headers=headers)
    assert r.status_code == 200, f"create failed: {r.status_code} {r.text}"
    return r.json()


def _wait_for_terminal(client: TestClient, response_id: str, **headers: str) -> dict[str, Any]:
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
    def __init__(self, status_code: int, body: bytes, headers: list[tuple[bytes, bytes]]) -> None:
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
        return _AsgiResponse(
            status_code=status_code,
            body=b"".join(body_parts),
            headers=response_headers,
        )

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


def _make_cancellable_bg_handler() -> Any:
    """Handler that emits created+in_progress, then blocks until cancelled."""
    started = asyncio.Event()

    async def handler(request: Any, context: Any, cancellation_signal: asyncio.Event):
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "owner_key,other_key,evict",
    [
        ("key_A", "key_B", False),
        ("key_A", None, False),
        ("key_A", "key_B", True),
        ("key_A", None, True),
        (None, "key_A", True),
    ],
)
async def test_memory_provider_isolation_before_and_after_runtime_eviction(
    owner_key: str | None, other_key: str | None, evict: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Envelope/input provider fallbacks retain the caller's partition after eviction."""
    provider = InMemoryResponseProvider()
    host = ResponsesAgentServerHost(store=provider)
    host.response_handler(_noop_handler)
    client = _AsyncAsgiClient(host)
    runtime = host._orchestrator._runtime_state
    try_evict = runtime.try_evict
    # Hold eager terminal eviction so both sides of the provider fallback are exercised.
    monkeypatch.setattr(runtime, "try_evict", AsyncMock(return_value=False))
    owner_headers = {"x-agent-user-id": owner_key} if owner_key is not None else {}
    other_headers = {"x-agent-user-id": other_key} if other_key is not None else {}
    created = await client.post(
        "/responses",
        json_body={"model": "m", "input": [{"role": "user", "content": "private input"}], "store": True},
        headers={**owner_headers, "x-agent-foundry-call-id": "creation-call"},
    )
    assert created.status_code == 200
    response_id = created.json()["id"]
    monkeypatch.setattr(runtime, "try_evict", try_evict)
    assert await runtime.get(response_id) is not None
    if evict:
        assert await runtime.try_evict(response_id)
        assert await runtime.get(response_id) is None

    path = f"/responses/{response_id}"
    for method, endpoint in [("GET", path), ("GET", f"{path}/input_items"), ("DELETE", path)]:
        denied = await client.request(method, endpoint, headers=other_headers)
        assert denied.status_code == 404, denied.body
    with pytest.raises(KeyError):
        await provider.update_response(created.json(), context=PlatformContext(user_id_key=other_key))

    later_headers = {**owner_headers, "x-agent-foundry-call-id": "later-call"}
    fetched = await client.get(path, headers=later_headers)
    assert fetched.status_code == 200
    inputs = await client.get(f"{path}/input_items", headers=later_headers)
    assert inputs.status_code == 200
    assert inputs.json()["data"][0]["content"][0]["text"] == "private input"
    deleted = await client.request("DELETE", path, headers=later_headers)
    assert deleted.status_code == 200
    with pytest.raises(KeyError):
        await provider.get_response(response_id, context=PlatformContext(user_id_key=owner_key))


# ── GET with isolation ────────────────────────────────────


class TestGetUserIsolation:
    """GET /responses/{id} with user ID enforcement.

    In-flight isolation is enforced locally by the endpoint handler.
    After eviction, the Foundry storage provider enforces isolation
    server-side (returning 400 for missing/mismatched keys).
    These tests verify the in-flight path using background responses
    that remain in runtime state.
    """

    def test_get_matching_key_returns_200(self) -> None:
        """GET with the same user ID that was used at creation → 200."""
        client = _make_client()
        resp = _create_response(client, user_id_key="key_A")
        _wait_for_terminal(client, resp["id"], **{"x-agent-user-id": "key_A"})
        r = client.get(f"/responses/{resp['id']}", headers={"x-agent-user-id": "key_A"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_get_mismatched_key_returns_404(self) -> None:
        """GET with a different user ID on in-flight response → 404."""
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
                headers={"x-agent-user-id": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.get(
                f"/responses/{response_id}",
                headers={"x-agent-user-id": "key_B"},
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
        """GET without user ID when response was created with one → 404."""
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
                headers={"x-agent-user-id": "key_A"},
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
        r = client.get(f"/responses/{resp['id']}", headers={"x-agent-user-id": "any_key"})
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
                headers={"x-agent-user-id": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.get(
                f"/responses/{response_id}",
                headers={"x-agent-user-id": "key_WRONG"},
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


class TestDeleteUserIsolation:
    """DELETE /responses/{id} with user ID enforcement.

    In-flight isolation is enforced locally; after eviction, isolation is
    enforced by the Foundry storage provider server-side.
    """

    def test_delete_matching_key_returns_200(self) -> None:
        client = _make_client()
        resp = _create_response(client, user_id_key="key_A")
        _wait_for_terminal(client, resp["id"], **{"x-agent-user-id": "key_A"})
        r = client.delete(f"/responses/{resp['id']}", headers={"x-agent-user-id": "key_A"})
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
                headers={"x-agent-user-id": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.request(
                "DELETE",
                f"/responses/{response_id}",
                headers={"x-agent-user-id": "key_B"},
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
                headers={"x-agent-user-id": "key_A"},
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


class TestCancelUserIsolation:
    """POST /responses/{id}/cancel with user ID enforcement.

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
                headers={"x-agent-user-id": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.post(
                f"/responses/{response_id}/cancel",
                headers={"x-agent-user-id": "key_A"},
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
                headers={"x-agent-user-id": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.post(
                f"/responses/{response_id}/cancel",
                headers={"x-agent-user-id": "key_B"},
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
                headers={"x-agent-user-id": "key_A"},
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


class TestInputItemsUserIsolation:
    """GET /responses/{id}/input_items with user ID enforcement.

    In-flight isolation is enforced locally; after eviction, isolation is
    enforced by the Foundry storage provider server-side.
    """

    def test_input_items_matching_key_returns_200(self) -> None:
        client = _make_client()
        resp = _create_response(client, user_id_key="key_A")
        _wait_for_terminal(client, resp["id"], **{"x-agent-user-id": "key_A"})
        r = client.get(
            f"/responses/{resp['id']}/input_items",
            headers={"x-agent-user-id": "key_A"},
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
                headers={"x-agent-user-id": "key_A"},
            )
        )
        try:
            await asyncio.wait_for(handler.started.wait(), timeout=5.0)
            r = await client.get(
                f"/responses/{response_id}/input_items",
                headers={"x-agent-user-id": "key_B"},
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
                headers={"x-agent-user-id": "key_A"},
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
