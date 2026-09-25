# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for user ID (user isolation) enforcement across all endpoints.

When a response is created with an ``x-agent-user-id`` header,
all subsequent GET, Cancel, DELETE, and InputItems requests must include
the same key.  Mismatched or missing keys return an indistinguishable 404
to prevent cross-user information leakage.

These host lifecycle tests use an explicitly partitioned provider. Anonymous
responses use a distinct partition and are not visible to keyed requests.
Persistent provider implementations must independently enforce this contract.
"""

from __future__ import annotations

import asyncio
import json as _json
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import PlatformContext, ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from tests._helpers import poll_until

# ── Shared helpers (sync, for GET / DELETE / INPUT_ITEMS) ──


class _PartitionedProvider:
    """Supply isolated storage so these tests exercise host lifecycle isolation.

    Persistent provider partitioning is covered separately in PR #49025.
    """

    def __init__(self):
        self.partitions: dict[str | None, InMemoryResponseProvider] = {}

    def _partition(self, context):
        key = context.user_id_key if context is not None else None
        return self.partitions.setdefault(key, InMemoryResponseProvider())

    async def create_response(self, *args, context=None, **kwargs):
        return await self._partition(context).create_response(*args, context=context, **kwargs)

    async def get_response(self, *args, context=None, **kwargs):
        return await self._partition(context).get_response(*args, context=context, **kwargs)

    async def update_response(self, *args, context=None, **kwargs):
        return await self._partition(context).update_response(*args, context=context, **kwargs)

    async def delete_response(self, *args, context=None, **kwargs):
        return await self._partition(context).delete_response(*args, context=context, **kwargs)

    async def get_items(self, *args, context=None, **kwargs):
        return await self._partition(context).get_items(*args, context=context, **kwargs)

    async def get_input_items(self, *args, context=None, **kwargs):
        return await self._partition(context).get_input_items(*args, context=context, **kwargs)

    async def get_history_item_ids(self, *args, context=None, **kwargs):
        return await self._partition(context).get_history_item_ids(*args, context=context, **kwargs)


async def _noop_handler(request: Any, context: Any, cancellation_signal: asyncio.Event):
    async def _events():
        if False:  # pragma: no cover
            yield None

    return _events()


def _make_client(handler=_noop_handler) -> TestClient:
    host = ResponsesAgentServerHost(store=_PartitionedProvider())
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
    app = ResponsesAgentServerHost(store=_PartitionedProvider())
    app.response_handler(handler)
    return _AsyncAsgiClient(app)


@pytest.mark.asyncio
async def test_duplicate_live_response_id_is_rejected_without_replacing_owner() -> None:
    handler = _make_cancellable_bg_handler()
    client = _build_async_client(handler)
    response_id = IdGenerator.new_response_id()
    owner_headers = {"x-agent-user-id": "key_A"}

    owner_task = asyncio.create_task(
        client.post(
            "/responses",
            json_body={
                "response_id": response_id,
                "model": "test",
                "background": True,
                "stream": True,
            },
            headers=owner_headers,
        )
    )
    try:
        await asyncio.wait_for(handler.started.wait(), timeout=5.0)
        collision = await client.post(
            "/responses",
            json_body={"response_id": response_id, "model": "test", "background": True},
            headers=owner_headers,
        )
        assert collision.status_code == 409
        assert collision.json()["error"]["code"] == "response_id_conflict"
        assert collision.json()["error"]["message"] == (
            "An active execution or retained replay stream with this response ID already exists."
        )

        owner = await client.get(f"/responses/{response_id}", headers=owner_headers)
        assert owner.status_code == 200
        denied = await client.get(
            f"/responses/{response_id}",
            headers={"x-agent-user-id": "key_B"},
        )
        assert denied.status_code == 404
    finally:
        if not owner_task.done():
            owner_task.cancel()
            with pytest.raises((asyncio.CancelledError, Exception)):
                await owner_task


def test_response_id_with_retained_stream_cannot_be_reused_by_same_user() -> None:
    response_id = IdGenerator.new_response_id()

    async def completed_streaming_handler(request: Any, context: Any, cancellation_signal: asyncio.Event):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield stream.emit_created()
            yield stream.emit_completed()

        return _events()

    client = _make_client(completed_streaming_handler)
    with client.stream(
        "POST",
        "/responses",
        json={
            "response_id": response_id,
            "model": "test",
            "background": False,
            "stream": True,
            "store": True,
        },
        headers={"x-agent-user-id": "key_A"},
    ) as owner:
        assert owner.status_code == 200
        list(owner.iter_lines())

    collision = client.post(
        "/responses",
        json={
            "response_id": response_id,
            "model": "test",
            "background": False,
            "stream": False,
            "store": True,
        },
        headers={"x-agent-user-id": "key_A"},
    )

    assert collision.status_code == 409
    assert collision.json()["error"]["code"] == "response_id_conflict"
    assert collision.json()["error"]["message"] == (
        "An active execution or retained replay stream with this response ID already exists."
    )


# ── GET with isolation ────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.parametrize("first_user", ["key_A", None, ""])
@pytest.mark.parametrize("cancel_first", [True, False])
async def test_same_id_streams_cancel_replay_and_delete_independently(first_user, cancel_first) -> None:
    users = [first_user, "key_B"]
    started = {user: asyncio.Event() for user in users}
    released = {user: asyncio.Event() for user in users}
    labels = {user: f"private-output-{index}" for index, user in enumerate(users)}
    response_id = IdGenerator.new_response_id()

    async def handler(request, context, cancellation_signal):
        user = context.platform_context.user_id_key

        async def events():
            stream = ResponseEventStream(response_id=context.response_id, model=labels[user])
            yield stream.emit_created()
            yield stream.emit_in_progress()
            for event in stream.output_item_message(labels[user]):
                yield event
            started[user].set()
            while not released[user].is_set() and not cancellation_signal.is_set():
                await asyncio.sleep(0.001)
            if not cancellation_signal.is_set():
                yield stream.emit_completed()

        return events()

    host = ResponsesAgentServerHost(
        store=_PartitionedProvider(), options=ResponsesServerOptions(resilient_background=False)
    )
    host.response_handler(handler)
    client = _AsyncAsgiClient(host)
    headers = {user: ({"x-agent-user-id": user} if user is not None else {}) for user in users}
    payload = {"response_id": response_id, "model": "m", "background": True, "stream": True, "store": True}
    tasks = [asyncio.create_task(client.post("/responses", json_body=payload, headers=headers[user])) for user in users]
    try:
        await asyncio.wait_for(asyncio.gather(*(event.wait() for event in started.values())), timeout=5)
        for user in users:
            response = await client.get(f"/responses/{response_id}", headers=headers[user])
            assert response.status_code == 200
            assert response.json()["model"] == labels[user]

        duplicate = await client.post("/responses", json_body=payload, headers=headers[first_user])
        assert duplicate.status_code == 409
        if cancel_first:
            cancelled = await client.post(f"/responses/{response_id}/cancel", headers=headers[first_user])
            assert cancelled.status_code == 200
        else:
            released[first_user].set()
        other = await client.get(f"/responses/{response_id}", headers=headers["key_B"])
        assert other.json()["status"] == "in_progress"

        released["key_B"].set()
        responses = await asyncio.wait_for(asyncio.gather(*tasks), timeout=5)
        for user, response in zip(users, responses):
            assert response.status_code == 200
            assert labels[user].encode() in response.body
            assert labels[users[1] if user == users[0] else users[0]].encode() not in response.body

        async def wait_for_eviction():
            while await host._endpoint._runtime_state.list_records():
                await asyncio.sleep(0.001)

        await asyncio.wait_for(wait_for_eviction(), timeout=5)
        denied = await client.get(
            f"/responses/{response_id}?stream=true", headers={"x-agent-user-id": "unrelated-user"}
        )
        assert denied.status_code == 404
        assert all(label.encode() not in denied.body for label in labels.values())
        for user in users:
            replay = await client.get(f"/responses/{response_id}?stream=true", headers=headers[user])
            if cancel_first and user == first_user:
                # Cancellation deliberately removes only this user's replay.
                assert replay.status_code == 400
                assert labels["key_B"].encode() not in replay.body
                continue
            assert replay.status_code == 200, replay.body
            assert labels[user].encode() in replay.body
            assert labels[users[1] if user == users[0] else users[0]].encode() not in replay.body

        deleted = await client.request("DELETE", f"/responses/{response_id}", headers=headers[first_user])
        assert deleted.status_code == 200
        assert (await client.get(f"/responses/{response_id}", headers=headers[first_user])).status_code == 404
        replay = await client.get(f"/responses/{response_id}?stream=true", headers=headers["key_B"])
        assert replay.status_code == 200
        assert labels["key_B"].encode() in replay.body
    finally:
        for event in released.values():
            event.set()
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


@pytest.mark.asyncio
async def test_persisted_response_remains_accessible_while_same_id_is_live_for_another_user() -> None:
    handler = _make_cancellable_bg_handler()
    provider = _PartitionedProvider()
    response_id = IdGenerator.new_response_id()
    await provider.create_response(
        {"id": response_id, "status": "completed", "model": "owner", "output": []},
        input_items=[],
        history_item_ids=[],
        context=PlatformContext(user_id_key="key_A"),
    )
    host = ResponsesAgentServerHost(store=provider)
    host.response_handler(handler)
    client = _AsyncAsgiClient(host)
    task = asyncio.create_task(
        client.post(
            "/responses",
            json_body={"response_id": response_id, "model": "other", "background": True, "stream": True},
            headers={"x-agent-user-id": "key_B"},
        )
    )
    try:
        await asyncio.wait_for(handler.started.wait(), timeout=5)
        response = await client.get(f"/responses/{response_id}", headers={"x-agent-user-id": "key_A"})
        assert response.status_code == 200
        assert response.json()["model"] == "owner"
        deleted = await client.request("DELETE", f"/responses/{response_id}", headers={"x-agent-user-id": "key_A"})
        assert deleted.status_code == 200
        other = await client.get(f"/responses/{response_id}", headers={"x-agent-user-id": "key_B"})
        assert other.status_code == 200
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure,status", [("missing", 404), ("denied", 400), ("unavailable", 500)])
async def test_provider_failure_never_falls_through_to_retained_replay(monkeypatch, failure, status):
    from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry
    from azure.ai.agentserver.responses.hosting import _endpoint_handler
    from azure.ai.agentserver.responses.hosting._task_id import derive_lifecycle_id
    from azure.ai.agentserver.responses.store._foundry_errors import (
        FoundryApiError,
        FoundryBadRequestError,
        FoundryResourceNotFoundError,
    )

    response_id = IdGenerator.new_response_id()
    registry = _StreamsRegistry()
    registry.use_in_memory_replay(cursor_fn=lambda event: event["sequence_number"])
    monkeypatch.setattr(_endpoint_handler, "streams", registry)
    stream = await registry.get_or_create(derive_lifecycle_id(response_id, "owner"))
    await stream.emit({"sequence_number": 0, "type": "response.output_text.delta", "delta": "private-data"})
    await stream.close()
    provider = _PartitionedProvider()
    errors = {
        "missing": FoundryResourceNotFoundError("missing"),
        "denied": FoundryBadRequestError("denied"),
        "unavailable": FoundryApiError("unavailable"),
    }

    async def unavailable(*args, **kwargs):
        raise errors[failure]

    monkeypatch.setattr(provider, "get_response", unavailable)
    host = ResponsesAgentServerHost(store=provider)
    client = _AsyncAsgiClient(host)
    response = await client.get(f"/responses/{response_id}?stream=true", headers={"x-agent-user-id": "owner"})
    assert response.status_code == status
    assert b"private-data" not in response.body


@pytest.mark.asyncio
@pytest.mark.parametrize("streaming", [False, True])
async def test_reservation_only_create_cannot_access_another_users_stored_response(streaming):
    response_id = IdGenerator.new_response_id()
    provider = _PartitionedProvider()
    await provider.create_response(
        {"id": response_id, "status": "completed", "model": "owner-private", "output": []},
        input_items=[],
        history_item_ids=[],
        context=PlatformContext(user_id_key="owner"),
    )
    entered = asyncio.Event()
    released = asyncio.Event()

    async def handler(request, context, cancellation_signal):
        async def events():
            entered.set()
            await released.wait()
            stream = ResponseEventStream(response_id=context.response_id, model="ephemeral")
            yield stream.emit_created()
            yield stream.emit_completed()

        return events()

    host = ResponsesAgentServerHost(store=provider)
    host.response_handler(handler)
    client = _AsyncAsgiClient(host)
    headers = {"x-agent-user-id": "other"}
    payload = {"response_id": response_id, "model": "m", "store": False, "stream": streaming}
    task = asyncio.create_task(client.post("/responses", json_body=payload, headers=headers))
    try:
        await asyncio.wait_for(entered.wait(), timeout=5)
        assert await host._endpoint._runtime_state.get(response_id, "other") is None
        assert (await client.post("/responses", json_body=payload, headers=headers)).status_code == 409
        for method, suffix in [
            ("GET", ""),
            ("GET", "?stream=true"),
            ("GET", "/input_items"),
            ("DELETE", ""),
            ("POST", "/cancel"),
        ]:
            response = await client.request(method, f"/responses/{response_id}{suffix}", headers=headers)
            assert response.status_code == 404, response.body
            assert b"owner-private" not in response.body
        owner = await client.get(f"/responses/{response_id}", headers={"x-agent-user-id": "owner"})
        assert owner.status_code == 200
        assert owner.json()["model"] == "owner-private"
        released.set()
        assert (await asyncio.wait_for(task, timeout=5)).status_code == 200
    finally:
        released.set()
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.asyncio
async def test_recovered_streaming_tasks_use_their_durable_user_partition(monkeypatch):
    from types import SimpleNamespace
    from azure.ai.agentserver.responses.hosting import _resilient_orchestrator
    from azure.ai.agentserver.responses.hosting._resilient_input import ResilientResponseInput
    from azure.ai.agentserver.responses.models import CreateResponse

    monkeypatch.setattr(_resilient_orchestrator, "_RUNTIME_REFS", {})
    provider = _PartitionedProvider()
    response_id = IdGenerator.new_response_id()
    seen = []

    async def handler(request, context, cancellation_signal):
        async def events():
            user = context.platform_context.user_id_key
            assert context.is_recovery
            assert context.persisted_response["model"] == user
            seen.append(user)
            stream = ResponseEventStream(response_id=context.response_id, model=user)
            yield stream.emit_created()
            for event in stream.output_item_message(f"recovered-private-{user}"):
                yield event
            yield stream.emit_completed()

        return events()

    host = ResponsesAgentServerHost(store=provider)
    host.response_handler(handler)
    orchestrator = host._endpoint._orchestrator._resilient_orchestrator
    contexts = []
    for user in ["user-A", "user-B"]:
        await provider.create_response(
            {"id": response_id, "status": "in_progress", "model": user, "background": True, "output": []},
            input_items=[],
            history_item_ids=[],
            context=PlatformContext(user_id_key=user),
        )
        durable = ResilientResponseInput(
            request=CreateResponse(model=user, stream=True, store=True, background=True, input="hello"),
            response_id=response_id,
            disposition="re-invoke",
            user_id_key=user,
        )
        contexts.append(
            SimpleNamespace(
                input=durable.to_task_input(),
                entry_mode="recovered",
                is_steered_turn=False,
                pending_input_count=0,
                cancel=asyncio.Event(),
                shutdown=asyncio.Event(),
            )
        )

    await asyncio.wait_for(asyncio.gather(*(orchestrator._execute_in_task(context) for context in contexts)), timeout=5)
    assert sorted(seen) == ["user-A", "user-B"]
    client = _AsyncAsgiClient(host)
    for user, other in [("user-A", "user-B"), ("user-B", "user-A")]:
        replay = await client.get(f"/responses/{response_id}?stream=true", headers={"x-agent-user-id": user})
        assert replay.status_code == 200, replay.body
        assert f"recovered-private-{user}".encode() in replay.body
        assert f"recovered-private-{other}".encode() not in replay.body


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

    def test_get_created_without_key_is_visible_only_to_anonymous_requests(self) -> None:
        """Completed anonymous responses do not become visible to identified users."""
        client = _make_client()
        resp = _create_response(client)
        _wait_for_terminal(client, resp["id"])
        # With a key
        r = client.get(f"/responses/{resp['id']}", headers={"x-agent-user-id": "any_key"})
        assert r.status_code == 404
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
